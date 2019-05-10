#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains stuff around the internal image storage mechaanism
of gimp files.

Generally speaking, the user should not care about anything
in this file.
"""
import zlib
import PIL.Image
from gimpIOBase import *


class GimpChannel(GimpIOBase):
	"""
	Represents a single channel or mask in a gimp image
	"""

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.name=''
		self._imageHeierarchy=None
		self._imageHeierarchyPtr=None

  	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		if idx==0:
			raise Exception()
		#print 'Decoding channel at',idx
		self.width=self._u32_()
		self.height=self._u32_()
		self.name=self._sz754_()
		self._propertiesDecode_()
		self._imageHeierarchyPtr=self._pointer_()

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		return self.imageHierarchy.image

	@property
	def imageHierarchy(self):
		"""
		Get teh image hierarchy

		This is mainly used for decoding the image, so
		not much use to you.
		"""
		if self._imageHeierarchy is None:
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
		ret.append(GimpIOBase.__repr__(self,indent))
		return indent+(('\n'+indent).join(ret))


class GimpImageHierarchy(GimpIOBase):
	"""
	Gets packed pixels from a gimp image

	NOTE: This was originally designed to be a hierarchy, like
		an image pyramid, through in practice they only use the
		top level of the pyramid (64x64) and ignore the rest.
	"""

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.bpp=0 # Number of bytes per pixel given
		self._levelPtrs=[]
		self._levels=None

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		self.width=self._u32_()
		self.height=self._u32_()
		self.bpp=self._u32_()
		if self.bpp<1 or self.bpp>4:
			msg="""'Unespected bytes-per-pixel for image data ("""+str(self.bpp)+""").
				Probably means file corruption."""
			raise Exception(msg)
		while True:
			ptr=self._pointer_()
			if ptr==0:
				break
			self._levelPtrs.append(ptr)
		if self._levelPtrs: # remove "dummy" level pointers
			self._levelPtrs=[self._levelPtrs[0]]

	@property
	def levels(self):
		"""
		Get the levels within this hierarchy

		Presently hierarchy is not really used by gimp,
		so this returns an array of one item
		"""
		if self._levels is None:
			for ptr in self._levelPtrs:
				l=GimpImageLevel(self)
				l._decode_(self._data,ptr)
				self._levels=[l]
		return self._levels

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		if not self.levels:
			return None
		return self.levels[0].image

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		ret.append('Bytes Per Pixel: '+str(self.bpp))
		return indent+(('\n'+indent).join(ret))


class GimpImageLevel(GimpIOBase):
	"""
	Gets packed pixels from a gimp image

	This represents a single level in an imageHierarchy
	"""

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self._tilePtrs=[]

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		#print 'Decoding image level at',self._idx
		self.width=self._u32_()
		self.height=self._u32_()
		if self.width!=self.parent.width or self.height!=self.parent.height:
			currentSize='('+str(self.width)+','+str(self.height)+')'
			expectedSize='('+str(self.parent.width)+','+str(self.parent.height)+')'
			msg=' Usually this implies file corruption.'
			raise Exception('Image data size mismatch. '+currentSize+'!='+expectedSize+msg)
		while True:
			ptr=self._pointer_()
			if ptr==0:
				break
			self._tilePtrs.append(ptr)

	def _unRLE(self,data,pixels,bpp,idx=0):
		"""
		decode RLE encoded image data
		"""
		ret=[[] for chan in range(bpp)]
		for chan in range(bpp):
			n=0
			while n<pixels:
				opcode=ord(data[idx]); idx+=1
				if opcode>=0 and opcode<=126: # a short run of identical bytes
					val=ord(data[idx]); idx+=1
					for _ in range(opcode+1):
						ret[chan].append(val)
						n+=1
				elif opcode==127: # A long run of identical bytes
					m=ord(data[idx]); idx+=1
					b=ord(data[idx]); idx+=1
					val=ord(data[idx]); idx+=1
					amt=m*256+b
					for _ in range(amt):
						ret[chan].append(val)
						n+=1
				elif opcode==128: # A long run of different bytes
					m=ord(data[idx]); idx+=1
					b=ord(data[idx]); idx+=1
					amt=m*256+b
					for _ in range(amt):
						val=ord(data[idx]); idx+=1
						ret[chan].append(val)
						n+=1
				elif opcode>=129 and opcode<=255: # a short run of different bytes
					amt=256-opcode
					for _ in range(amt):
						val=ord(data[idx]); idx+=1
						ret[chan].append(val)
						n+=1
		# flatten/weave the individual channels into one strream
		flat=bytearray()
		for i in range(pixels):
			for chan in range(bpp):
				flat.append(ret[chan][i])
		return flat

	def _imgForTilePtr(self,ptr,size,bpp,mode):
		"""
		get the image per a given tile
		"""
		totalBytes=size[0]*size[1]*bpp
		if self.doc.compression==0: # none
			data=self._data[ptr:ptr+totalBytes]
		elif self.doc.compression==1: # RLE
			data=self._unRLE(self._data,size[0]*size[1],bpp,ptr)
		elif self.doc.compression==2: # zip
			data=zlib.decompress(data[ptr:ptr+totalBytes+24]) # WARN: this could be a costly thing to do!
		else:
			raise Exception('ERR: unsupported compression mode '+str(self.doc.compression))
		return PIL.Image.frombytes(mode,size,str(data),decoder_name='raw')

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		bpp=self.parent.bpp
		if bpp==4:
			mode='RGBA'
		elif bpp==3:
			mode='RGB'
		elif bpp==2:
			mode='LA'
		elif bpp==1:
			mode='L'
		else:
			raise Exception("Don't know what "+str(bpp)+" bytes per pixel means!")
		result=PIL.Image.new(mode,(self.width,self.height),color=None)
		tileNum=0
		for y in range(0,self.height,64):
			for x in range(0,self.width,64):
				size=(min(self.width-x,64),min(self.height-y,64))
				subImage=self._imgForTilePtr(self._tilePtrs[tileNum],size,bpp,mode); tileNum+=1
				result.paste(subImage,(x,y))
		return result

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		return indent+(('\n'+indent).join(ret))