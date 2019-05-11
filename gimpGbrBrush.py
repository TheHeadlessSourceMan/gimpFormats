#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gbr brush format
"""
import struct
import PIL.Image
from binaryIO import *
	

class GimpGbrBrush(BinIOBase):
	"""
	Pure python implementation of the gimp gbr brush format

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/gbr.txt
	"""
	
	COLOR_MODES=[None,'L','LA','RGB','RGBA'] # only L or RGB allowed

	def __init__(self,filename=None):
		BinIOBase.__init__(self)
		self.filename=None
		self.version=2
		self.width=0
		self.height=0
		self.bpp=1
		self.mode=self.COLOR_MODES[self.bpp]
		self.name=''
		self.rawImage=None
		self.spacing=0
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
		BinIOBase._decode_(self,data,idx)
		headerSize=self._u32_()
		self.version=self._u32_()
		if self.version!=2:
			raise Exception('ERR: unknown brush version '+str(self.version))
		self.width=self._u32_()
		self.height=self._u32_()
		self.bpp=self._u32_() # only allows grayscale or RGB
		self.mode=self.COLOR_MODES[self.bpp]
		magic=self._asciiz_(4)
		if magic!='GIMP':
			raise Exception('File format error.  Magic value mismatch.')
		self.spacing=self._u32_()
		nameLen=headerSize-self._idx
		self.name=self._asciiz_(nameLen).decode('UTF-8')
		self.rawImage=self._asciiz_(self.width*self.height*self.bpp)
		return self._idx

	@property
	def size(self):
		return (self.width,self.height)

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		if self.rawImage is None:
			return None
		return PIL.Image.frombytes(self.mode,self.size,self.rawImage,decoder_name='raw')

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
		ret.append('Name: '+str(self.name))
		ret.append('Version: '+str(self.version))
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		ret.append('Spacing: '+str(self.spacing))
		ret.append('BPP: '+str(self.bpp))
		ret.append('Mode: '+str(self.mode))
		return ('\n'+indent).join(ret)


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
				elif arg[0]=='--show':
					g.image.show()
				elif arg[0]=='--save':
					g.image.save(arg[1])
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				g=GimpGbrBrush(arg)
	if printhelp:
		print 'Usage:'
		print '  gimpGbrBrush.py file.xcf [options]'
		print 'Options:'
		print '   -h, --help ............ this help screen'
		print '   --dump ................ dump info about this file'
		print '   --show ................ show the brush image'
		print '   --save=out.jpg ........ save out the brush image'
		print '   --register ............ register this extension'