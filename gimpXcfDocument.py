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
from binaryIO import *
from gimpIOBase import *
from gimpImageInternals import *


class GimpLayer(GimpIOBase):
	"""
	Represents a single layer in a gimp image
	"""

	COLOR_MODES=['RGB color without alpha','RGB color with alpha',
		'Grayscale without alpha','Grayscale with alpha',
		'Indexed without alpha','Indexed with alpha']
	PIL_MODE_TO_LAYER_MODE={'L':2,'LA':3,'RGB':0,'RGBA':1}

	def __init__(self,parent,name=None,image=None):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.colorMode=0
		self.name=name
		self._imageHeierarchy=None
		self._imageHeierarchyPtr=None
		self._mask=None
		self._maskPtr=None
		self._data=None
		if image is not None:
			self.image=image # done last as it resets some of the above defaults

	def _decode_(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		#print 'Decoding Layer at',index
		self.width=io.u32
		self.height=io.u32
		self.colorMode=io.u32 # one of self.COLOR_MODES
		self.name=io.sz754
		self._propertiesDecode_(io)
		self._imageHeierarchyPtr=self._pointerDecode_(io)
		self._maskPtr=self._pointerDecode_(io)
		self._mask=None
		self._data=data
		return io.index

	def toBytes(self):
		"""
		encode to byte array
		"""
		dataAreaIO=IO()
		io=IO()
		io.u32=self.width
		io.u32=self.height
		io.u32=self.colorMode
		io.sz754=self.name
		dataAreaIndex=io.index+self._POINTER_SIZE_*2
		io.addBytes(self._pointerEncode_(dataAreaIndex))
		dataAreaIO.addBytes(self._propertiesEncode_())
		io.addBytes(self._pointerEncode_(dataAreaIndex))
		if self.mask is not None:
			dataAreaIO.addBytes(self.mask.toBytes())
		io.addBytes(self._pointerEncode_(dataAreaIndex+dataAreaIO.index))
		io.addBytes(dataAreaIO)
		return io.data

	@property
	def mask(self):
		"""
		Get the layer mask
		"""
		if self._mask is None and self._maskPtr is not None and self._maskPtr!=0:
			self._mask=GimpChannel(self)
			self._mask.fromBytes(self._data,self._maskPtr)
		return self._mask

	@property
	def image(self):
		"""
		get the layer image

		NOTE: can return None!
		"""
		if self.imageHierarchy is None:
			return None
		return self.imageHierarchy.image
	@image.setter
	def image(self,image):
		"""
		set the layer image

		NOTE: resets layer width, height, and colorMode
		"""
		self.height=image.height
		self.width=image.width
		if image.mode not in self.PIL_MODE_TO_LAYER_MODE:
			raise NotImplementedError('No way of handlng PIL image mode "'+image.mode+'"')
		self.colorMode=self.PIL_MODE_TO_LAYER_MODE[image.mode]
		if not self.name and isinstance(image,str):
			# try to use a filename as the name
			self.name=image.rsplit('\\',1)[-1].rsplit('/',1)[-1]
		self.imageHierarchy=GimpImageHierarchy(self)
		self.imageHierarchy.image=image

	@property
	def imageHierarchy(self):
		"""
		Get the image hierarchy objects

		This is mainly needed for deciphering image, and therefore,
		of little use to you, the user.

		NOTE: can return None if it has been fully read into an image
		"""
		if self._imageHeierarchy is None and self._imageHeierarchyPtr>0:
			self._imageHeierarchy=GimpImageHierarchy(self)
			self._imageHeierarchy.fromBytes(self._data,self._imageHeierarchyPtr)
		return self._imageHeierarchy

	def _forceFullyLoaded(self):
		"""
		make sure everything is fully loaded from the file
		"""
		if self.mask is not None:
			self.mask._forceFullyLoaded()
		_=self.image # make sure the image is loaded so we can delete the hierarchy nonsense
		self._imageHeierarchy=None
		self._data=None

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


class Precision:
	"""
	Since the precision code is so unusual, I decided to create a class
	to parse it.
	"""

	def __init__(self):
		self.bits=8
		self.gamma=True
		self.numberFormat=int

	def decode(self,gimpVersion,io):
		"""
		decode the precision code from the file
		"""
		if gimpVersion<4:
			self.bits=8
			self.gamma=True
			self.numberFormat=int
		else:
			code=io.u32
			if gimpVersion==4:
				self.gamma=(True,True,False,False,False)[code]
				self.bits=(8,16,32,16,32)[code]
				self.numberFormat=(int,int,int,float,float)[code]
			elif gimpVersion in (5,6):
				self.gamma=(code%100!=0)
				code=int(code/100)
				self.bits=(8,16,32,16,32)[code]
				self.numberFormat=(int,int,int,float,float)[code]
			else: # gimpVersion 7 or above
				self.gamma=(code%100!=0)
				code=int(code/100)
				self.bits=(8,16,32,16,32,64)[code]
				self.numberFormat=(int,int,int,float,float,float)[code]

	def encode(self,gimpVersion,io):
		"""
		encode this to the file

		NOTE: will not mess with development versions 5 or 6
		"""
		if gimpVersion<4:
			if self.bits!=8 or not(self.gamma) or self.numberFormat!=int:
				raise Exception('Illegal precision ('+str(self)+') for gimp version '+str(gimpVersion))
		else:
			if gimpVersion==4:
				if self.bits==64:
					raise Exception('Illegal precision ('+str(self)+') for gimp version '+str(gimpVersion))
				if self.numberFormat==int:
					code=(8,16,32).index(self.bits)
				else:
					code=(16,32).index(self.bits)+2
				code=code*100
				if self.gamma:
					code+=50
			elif gimpVersion in (5,6):
				raise NotImplementedError('Cannot save to gimp developer version '+str(gimpVersion))
			else: # version 7 or above
				if self.numberFormat==int:
					code=(8,16,32).index(self.bits)
				else:
					code=(16,32,64).index(self.bits)+2
				code=code*100
				if self.gamma:
					code+=50
			io.u32=code

	def requiredGimpVersion(self):
		"""
		return the lowest gimp version that supports this precision
		"""
		if self.bits==8 and self.gamma and self.numberFormat==int:
			return 0
		if self.bits==64:
			return 7
		return 4

	def __repr__(self):
		ret=[]
		ret.append(str(self.bits)+"-bit")
		ret.append('gamma' if self.gamma else 'linear')
		ret.append('integer' if self.numberFormat is int else float)
		return ' '.join(ret)


class GimpDocument(GimpIOBase):
	"""
	Pure python implementation of the gimp file format

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/xcf.txt
	"""

	def __init__(self,filename):
		GimpIOBase.__init__(self,self)
		self.dirty=False # a file-changed indicator.  # TODO: Not fully implemented.
		self._layers=None
		self._layerPtr=[]
		self.channels=[]
		self._channelPtr=[]
		self.version=None
		self.width=0
		self.height=0
		self.baseColorMode=0
		self.precision=None # Precision object
		self._data=None
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

	def _decode_(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		if io.getBytes(9)!="gimp xcf ".encode('ascii'):
			raise Exception('Not a valid GIMP file')
		version=io.cString
		if version=='file':
			self.version=0
		else:
			self.version=int(version[1:])
		self.width=io.u32
		self.height=io.u32
		self.baseColorMode=io.u32
		self.precision=Precision()
		self.precision.decode(self.version,io)
		self._propertiesDecode_(io)
		self._layerPtr=[]
		self._layers=[]
		while True:
			ptr=self._pointerDecode_(io)
			if ptr==0:
				break
			self._layerPtr.append(ptr)
			l=GimpLayer(self)
			l._decode_(io.data,ptr)
			self._layers.append(l)
		self._channelPtr=[]
		self.channels=[]
		while True:
			ptr=self._pointerDecode_(io)
			if ptr==0:
				break
			self._channelPtr.append(ptr)
			c=GimpChannel(self)
			c.fromBytes(io.data,ptr)
			self.channels.append(c)
		return io.index

	def toBytes(self):
		"""
		encode to a byte array
		"""
		io=IO()
		io.addBytes("gimp xcf ")
		io.addBytes(str(self.version)+'\0')
		io.u32=self.width
		io.u32=self.height
		io.u32=self.baseColorMode
		if self.precision is None:
			self.precision=Precision()
		self.precision.encode(self.version,io)
		io.addBytes(self._propertiesEncode_())
		dataAreaIdx=io.index+self._POINTER_SIZE_*(len(self.layers)+len(self.channels))
		dataAreaIo=IO()
		for layer in self.layers:
			io.pointer=dataAreaIdx+dataAreaIo.index
			dataAreaIo.addBytes(layer.toBytes())
		for channel in self.channels:
			io.pointer=dataAreaIdx+dataAreaIo.index
			dataAreaIo.addBytes(channel.toBytes())
		return io.data

	def _forceFullyLoaded(self):
		"""
		make sure everything is fully loaded from the file
		"""
		for layer in self.layers:
			layer._forceFullyLoaded()
		for chan in self.channels:
			chan._forceFullyLoaded()
		# no longer try to get the data from file
		self._layerPtr=None
		self._channelPtr=None
		self._data=None

	@property
	def layers(self):
		"""
		Decode the image's layers if necessary

		TODO: need to do the same thing with self.Channels
		"""
		if self._layers is None:
			self._layers=[]
			for ptr in self._layerPtr:
				l=GimpLayer(self)
				l.fromBytes(self._data,ptr)
				self._layers.append(l)
			# add a reference back to this object so it doesn't go away while array is in use
			self._layers.parent=self
			# override some internal methods so we can do more with them
			self._layers._actualDelitem_=self._layers.__delitem__
			self._layers.__delitem__=self.deleteLayer
			self._layers._actualSetitem_=self._layers.__delitem__
			self._layers.__setitem__=self.setLayer
		return self._layers

	def getLayer(self,index):
		"""
		return a given layer
		"""
		return self.layers[index]
	def setLayer(self,index,layer):
		"""
		assign to a given layer
		"""
		self._forceFullyLoaded()
		self.dirty=True
		self._layerPtr=None # no longer try to use the pointers to get data
		self.layers._actualSetitem(index,layer)

	def newLayer(self,name,image,index=-1):
		"""
		create a new layer based on a PIL image

		:param name: a name for the new layer
		:param index: where to insert the new layer (default=top)
		:return: newly created GimpLayer object
		"""
		layer=GimpLayer(self,name,image)
		self.insertLayer(layer,index)
		return layer

	def newLayerFromClipboard(self,name='pasted',index=-1):
		"""
		Create a new image from the system clipboard.

		:param name: a name for the new layer (default="pasted")
		:param index: where to insert the new layer (default=top)
		:return: newly created GimpLayer object

		NOTE: requires pillow PIL implementation
		NOTE: only works on OSX and Windows
		"""
		import PIL.ImageGrab
		image=PIL.ImageGrab.grabclipboard()
		return self.newLayer(name,image,index)

	def addLayer(self,layer):
		"""
		append a layer object to the document

		:param layer: the new layer to append
		"""
		self.insertLayer(layer,-1)
	def appendLayer(self,layer):
		"""
		append a layer object to the document

		:param layer: the new layer to append
		"""
		self.insertLayer(layer,-1)

	def insertLayer(self,layer,index=-1):
		"""
		insert a layer object at a specific position

		:param layer: the new layer to insert
		:param index: where to insert the new layer (default=top)
		"""
		self.layers.insert(index,layer)

	def deleteLayer(self,index):
		"""
		delete a layer
		"""
		self.__delitem__(index)

	# make this class act like this class is an array of layers
	def __len__(self):
		return len(self.layers)
	def __getitem__(self,index):
		return self.layers[index]
	def __setitem__(self,index,layer):
		self.setLayer(layer,index)
	def __delitem__(self,index):
		self.deleteLayer(index)
	def __inc__(self,amt):
		self.appendLayer(amt)
		return self

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
		self._forceFullyLoaded()
		if toFilename is None:
			toFilename=self.filename
		if not hasattr(toFilename,'write'):
			f=open(toFilename,'wb')
		f.write(self.toBytes())
		self.dirty=False

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
		ret.append('Precision: '+str(self.precision))
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
					print(g)
				elif arg[0]=='--showLayer':
					if arg[1]=='*':
						for n in range(len(g.layers)):
							i=g.layers[n].image
							if i is None:
								print('No image for layer',n)
							else:
								print('showing layer',n)
								i.show()
					else:
						i=g.layers[int(arg[1])].image
						if i is None:
							print('No image for layer',int(arg[1]))
						else:
							print('showing layer',arg[1])
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
								print('No image for layer',n)
							else:
								fn2=filename.replace('*',str(n))
								print('saving layer',fn2)
								i.save(fn2)
					else:
						i=g.layers[int(layer)].image
						if i is None:
							print('No image for layer',layer)
						else:
							i.save(filename.replace('*',layer))
				elif arg[0]=='--save':
					if len(arg)>1:
						g.save(arg[1])
					else:
						g.save()
				else:
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				g=GimpDocument(arg)
	if printhelp:
		print('Usage:')
		print('  gimpXcfDocument.py file.xcf [options]')
		print('Options:')
		print('   -h, --help ............ this help screen')
		print('   --dump ................ dump info about this file')
		print('   --showLayer=n ......... show layer(s) (use * for all)')
		print('   --saveLayer=n,out.jpg . save layer(s) out to file')
		print('   --save[=file.xcf] ..... save gimp xcf file')
		print('   --register ............ register this extension')