#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp xcf file format


Currently supports:
	Loading xcf files
	Getting image hierarchy and info
	Getting image for each layer (PIL image)
Currently not supporting:
	Saving
	Programatically alter documents (add layer, etc)
	Rendering a final, compositied image
"""
import struct
import zlib
import PIL.Image
from binaryIO import *
from gimpIOBase import *
from gimpImageInternals import *
	

class GimpLayer(GimpIOBase):
	"""
	Represents a single layer in a gimp image
	"""

	COLOR_MODES=['RGB color without alpha','RGB color with alpha','Grayscale without alpha','Grayscale with alpha','Indexed without alpha','Indexed with alpha']

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.colorMode=0
		self.name=None
		self._imageHeierarchy=None
		self._imageHeierarchyPtr=None
		self._mask=None
		self._maskPtr=None

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		#print 'Decoding Layer at',idx
		self.width=self._u32_()
		self.height=self._u32_()
		self.colorMode=self._u32_() # one of self.COLOR_MODES
		self.name=self._sz754_()
		self._propertiesDecode_()
		self._imageHeierarchyPtr=self._pointer_()
		self._maskPtr=self._pointer_()
		self._mask=None
		return self._idx

	@property
	def mask(self):
		"""
		Get the layer mask
		"""
		if self._mask is None and self._maskPtr is not None and self._maskPtr!=0:
			self._mask=GimpChannel(self)
			self._mask._decode_(self._data,self._maskPtr)
		return self._mask

	@property
	def image(self):
		"""
		get a final, compiled image

		NOTE: can return None!
		"""
		if self.imageHierarchy is None:
			return None
		return self.imageHierarchy.image

	@property
	def imageHierarchy(self):
		"""
		Get the image hierarchy objects

		This is mainly needed for deciphering image, and therefore,
		of little use to you, the user.
		"""
		if self._imageHeierarchy is None and self._imageHeierarchyPtr>0:
			self._imageHeierarchy=GimpImageHierarchy(self)
			self._imageHeierarchy._decode_(self._data,self._imageHeierarchyPtr)
		return self._imageHeierarchy

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Name: '+str(self.name))
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		ret.append('colorMode: '+self.COLOR_MODES[self.colorMode])
		ret.append(GimpIOBase.__repr__(self,indent))
		m=self.mask
		if m is not None:
			ret.append('Mask:')
			ret.append(m.__repr__(indent+'\t'))
		return indent+(('\n'+indent).join(ret))


class GimpDocument(GimpIOBase):
	"""
	Pure python implementation of the gimp file format

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/xcf.txt
	"""

	PRECISION_CODE={
		100:'8-bit linear integer',
		150:'8-bit gamma integer',
		200:'16-bit linear integer',
		250:'16-bit gamma integer',
		300:'32-bit linear integer',
		350:'32-bit gamma integer',
		500:'16-bit linear floating point',
		550:'16-bit gamma floating point',
		600:'32-bit linear floating point',
		650:'32-bit gamma floating point',
		700:'64-bit linear floating point',
		750:'64-bit gamma floating point',
		0:'8-bit gamma integer',
		1:'16-bit gamma integer',
		2:'32-bit linear integer',
		3:'16-bit linear floating point',
		4:'32-bit linear floating point',
	}

	def __init__(self,filename):
		GimpIOBase.__init__(self,self)
		self._layers =None
		self._layerPtr=[]
		self.channels=[]
		self._channelPtr=[]
		self.version=None
		self.width=0
		self.height=0
		self.baseColorMode=0
		self.precision=0 # one of self.PRECISION_CODE
		if filename is not None:
			self.load(filename)

	def load(self,filename):
		"""
		load a gimp file

		:param filename: can be a file name or a file-like object
		"""
		if hasattr(filename,'read'):
			self.filename=filename.name
			f=filename
		else:
			self.filename=filename
			f=open(filename,'rb')
		data=f.read()
		f.close()
		self._decode_(data)

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		if self._asciiz_(9)!="gimp xcf ":
			raise Exception('Not a valid GIMP file')
		version=self._asciiz_()
		if version=='file':
			self.version=0
		else:
			self.version=int(version[1:])
		#print 'Gimp version',self.version,self._POINTER_SIZE_
		self.width=self._u32_()
		self.height=self._u32_()
		self.baseColorMode=self._u32_()
		self.precision=self._u32_()
		self._propertiesDecode_()
		self._layerPtr=[]
		self._layers=[]
		while True:
			ptr=self._pointer_()
			if ptr==0:
				break
			self._layerPtr.append(ptr)
			l=GimpLayer(self)
			l._decode_(self._data,ptr)
			self._layers.append(l)
		self._channelPtr=[]
		self.channels=[]
		while True:
			ptr=self._pointer_()
			if ptr==0:
				break
			self._channelPtr.append(ptr)
			c=GimpChannel(self)
			c._decode_(self._data,ptr)
			self.channels.append(c)
		return self._idx

	@property
	def layers(self):
		"""
		Decode the image's layers if necessary
		"""
		if self._layers is None:
			self._layers=[]
			for ptr in self._layerPtr:
				l=GimpLayer(self)
				l._decode_(self._data,ptr)
				self._layers.append(l)
		return self._layers

	def __len__(self):
		return len(self.layers)
	def __getitem__(self,idx):
		return self.layers.__getitem__(idx)

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		raise NotImplementedError()

	def save(self,toFilename=None,toExtension=None):
		"""
		save this gimp image to a file
		"""
		raise NotImplementedError()

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		if self.filename is not None:
			ret.append('Filename: '+self.filename)
		ret.append('Version: '+str(self.version))
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		ret.append('Base Color Mode: '+self.COLOR_MODES[self.baseColorMode])
		ret.append('Precision: '+self.PRECISION_CODE[self.precision])
		ret.append(GimpIOBase.__repr__(self))
		if self._layerPtr:
			ret.append('Layers: ')
			for l in self.layers:
				ret.append(l.__repr__('\t'))
		if self._channelPtr:
			ret.append('Channels: ')
			for ch in self.channels:
				ret.append(ch.__repr__('\t'))
		return '\n'.join(ret)


if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	printhelp=False
	if len(sys.argv)<2:
		printhelp=True
	else:
		g=None
		for arg in sys.argv[1:]:
			if arg.startswith('-'):
				arg=[a.strip() for a in arg.split('=',1)]
				if arg[0] in ['-h','--help']:
					printhelp=True
				elif arg[0]=='--dump':
					print g
				elif arg[0]=='--showLayer':
					if arg[1]=='*':
						for n in range(len(g.layers)):
							i=g.layers[n].image
							if i is None:
								print 'No image for layer',n
							else:
								print 'showing layer',n
								i.show()
					else:
						i=g.layers[int(arg[1])].image
						if i is None:
							print 'No image for layer',int(arg[1])
						else:
							print 'showing layer',arg[1]
							i.show()
				elif arg[0]=='--saveLayer':
					layer=arg[1].split(',',1)
					if len(layer)>1:
						filename=layer[1]
					else:
						filename='layer *.png'
					layer=arg[1][0]
					if layer=='*':
						if filename.find('*')<0:
							filename='.'.join(filename.split('.',1).insert(1,'*'))
						for n in range(len(g.layers)):
							i=g.layers[n].image
							if i is None:
								print 'No image for layer',n
							else:
								fn2=filename.replace('*',str(n))
								print 'saving layer',fn2
								i.save(fn2)
					else:
						i=g.layers[int(layer)].image
						if i is None:
							print 'No image for layer',layer
						else:
							i.save(filename.replace('*',layer))
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				g=GimpDocument(arg)
	if printhelp:
		print 'Usage:'
		print '  gimpXcfDocument.py file.xcf [options]'
		print 'Options:'
		print '   -h, --help ............ this help screen'
		print '   --dump ................ dump info about this file'
		print '   --showLayer=n ......... show layer(s) (use * for all)'
		print '   --saveLayer=n,out.jpg . save layer(s) out to file'
		print '   --register ............ register this extension'