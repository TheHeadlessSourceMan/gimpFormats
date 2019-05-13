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

	def __init__(self,parent,name='',image=None):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.name=name
		self._imageHeierarchy=None
		self._imageHeierarchyPtr=None
		if image is not None: # this is last because image can reset values
			self.image=image

  	def fromBytes(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		#print 'Decoding channel at',index
		self.width=io.u32
		self.height=io.u32
		self.name=io.sz754
		self._propertiesDecode_(io)
		self._imageHeierarchyPtr=self._pointerDecode_(io)
		self._data=io.data
		return io.index

	def toBytes(self):
		"""
		encode this object to a byte buffer
		"""
		io=IO()
		io.u32=self.width
		io.u32=self.height
		io.sz754=self.name
		io.addBytes(self._propertiesEncode_())
		ih=self._imageHeierarchyPtr
		if ih==None:
			ih=0
		io.addBytes(self._pointerEncode_(ih))
		return io.data

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		return self.imageHierarchy.image
	@image.setter
	def image(self,image):
		"""
		get a final, compiled image
		"""
		self.width=image.width
		self.height=image.height
		if not self.name and isinstance(image,basestring):
			# try to use a filename as the name
			self.name=image.rsplit('\\',1)[-1].rsplit('/',1)[-1]
		self._imageHierarchy=GimpImageHierarchy(self,image)
		
	def _forceFullyLoaded(self):
		"""
		make sure everything is fully loaded from the file
		"""
		_=self.image # make sure the image is loaded so we can delete the hierarchy nonsense
		self._imageHeierarchyPtr=None
		self._data=None

	@property
	def imageHierarchy(self):
		"""
		Get teh image hierarchy

		This is mainly used for decoding the image, so
		not much use to you.
		"""
		if self._imageHeierarchy is None:
			self._imageHeierarchy=GimpImageHierarchy(self)
			self._imageHeierarchy.fromBytes(self._data,self._imageHeierarchyPtr)
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

	def __init__(self,parent,image=None):
		GimpIOBase.__init__(self,parent)
		self.width=0
		self.height=0
		self.bpp=0 # Number of bytes per pixel given
		self._levelPtrs=[]
		self._levels=None
		self._data=None
		if image is not None: # NOTE: can override earlier parameters
			self.image=image

	def fromBytes(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		#print 'Decoding channel at',index
		self.width=io.u32
		self.height=io.u32
		self.bpp=io.u32
		if self.bpp<1 or self.bpp>4:
			msg="""'Unespected bytes-per-pixel for image data ("""+str(self.bpp)+""").
				Probably means file corruption."""
			raise Exception(msg)
		while True:
			ptr=self._pointerDecode_(io)
			if ptr==0:
				break
			self._levelPtrs.append(ptr)
		if self._levelPtrs: # remove "dummy" level pointers
			self._levelPtrs=[self._levelPtrs[0]]
		self._data=data
		return io.index
		
	def toBytes(self):
		"""
		encode this object to a byte buffer
		"""
		dataIO=IO()
		io=IO()
		io.u32=self.width
		io.u32=self.height
		io.u32=io.bpp
		dataIndex=io.index+root._POINTER_SIZE_*(len(self.levels)+1)
		for level in self.levels:
			io.addBytes(self._pointerEncode_(dataIndex+data.index))
			dataIO.addBytes(level.toBytes())
		io.addBytes(self._pointerEncode_(0))
		io.addBytes(dataIO.data)
		return io.data

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
				l.fromBytes(self._data,ptr)
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
	@image.setter
	def image(self):
		"""
		set the image
		"""
		self.width=image.width
		self.height=image.height
		if image.mode not in ['L','LA','RGB','RGBA']:
			raise NotImplementedError('Unsupported PIL image type')
		self.bpp=len(image.mode)
		self._levelPtrs=None
		self._levels=[GimpImageLevel(self,image)]

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
		self._tiles=None # tile PIL images
		self._image=None
		
	def fromBytes(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		#print 'Decoding image level at',io.index
		self.width=io.u32
		self.height=io.u32
		if self.width!=self.parent.width or self.height!=self.parent.height:
			currentSize='('+str(self.width)+','+str(self.height)+')'
			expectedSize='('+str(self.parent.width)+','+str(self.parent.height)+')'
			msg=' Usually this implies file corruption.'
			raise Exception('Image data size mismatch. '+currentSize+'!='+expectedSize+msg)
		self._tiles=[]
		self._image=None
		for y in range(0,self.height,64):
			for x in range(0,self.width,64):
				ptr=self._pointerDecode_(io)
				size=(min(self.width-x,64),min(self.height-y,64))
				totalBytes=size[0]*size[1]*self.bpp
				if self.doc.compression==0: # none
					data=io.data[ptr:ptr+totalBytes]
				elif self.doc.compression==1: # RLE
					data=self._decodeRLE(io.data,size[0]*size[1],self.bpp,ptr)
				elif self.doc.compression==2: # zip
					data=zlib.decompress(io.data[ptr:ptr+totalBytes+24]) # guess how many bytes are needed
				else:
					raise Exception('ERR: unsupported compression mode '+str(self.doc.compression))
				subImage=PIL.Image.frombytes(self.mode,size,str(data),decoder_name='raw')
				self._tiles.append(subImage)
		_=self._pointerDecode_(io) # list ends with nul character
		return io.index
		
	def toBytes(self):
		"""
		encode this object to a byte buffer
		"""
		dataIO=IO()
		io=IO()
		io.u32=self.width
		io.u32=self.height
		dataIndex=io.index+root._POINTER_SIZE_*(len(self.tiles)+1)
		for tile in self.tiles:
			io.addBytes(self._pointerEncode_(dataIndex+data.index))
			data=tile.tobytes()
			if self.doc.compression==0: # none
				pass
			elif self.doc.compression==1: # RLE
				data=self._encodeRLE(data,self.bpp)
			elif self.doc.compression==2: # zip
				data=zlib.compress(data)
			else:
				raise Exception('ERR: unsupported compression mode '+str(self.doc.compression))
			dataIO.addBytes(data)
		io.addBytes(self._pointerEncode_(0))
		io.addBytes(dataIO.data)
		return io.data

	def _decodeRLE(self,data,pixels,bpp,index=0):
		"""
		decode RLE encoded image data
		"""
		ret=[[] for chan in range(bpp)]
		for chan in range(bpp):
			n=0
			while n<pixels:
				opcode=ord(data[index]); index+=1
				if opcode>=0 and opcode<=126: # a short run of identical bytes
					val=ord(data[index]); index+=1
					for _ in range(opcode+1):
						ret[chan].append(val)
						n+=1
				elif opcode==127: # A long run of identical bytes
					m=ord(data[index]); index+=1
					b=ord(data[index]); index+=1
					val=ord(data[index]); index+=1
					amt=m*256+b
					for _ in range(amt):
						ret[chan].append(val)
						n+=1
				elif opcode==128: # A long run of different bytes
					m=ord(data[index]); index+=1
					b=ord(data[index]); index+=1
					amt=m*256+b
					for _ in range(amt):
						val=ord(data[index]); index+=1
						ret[chan].append(val)
						n+=1
				elif opcode>=129 and opcode<=255: # a short run of different bytes
					amt=256-opcode
					for _ in range(amt):
						val=ord(data[index]); index+=1
						ret[chan].append(val)
						n+=1
				else:
					print 'Unreachable branch',opcode
					raise Exception()
		# flatten/weave the individual channels into one strream
		flat=bytearray()
		for i in range(pixels):
			for chan in range(bpp):
				flat.append(ret[chan][i])
		return flat
		
	def _encodeRLE(self,data,bpp):
		"""
		encode image to RLE  image data
		"""
		def countSame(data,startIdx):
			"""
			count how many times bytes are identical
			"""
			l=len(data)
			if idx>=l:
				return 0
			c=data[idx]
			idx=startIdx+1
			while idx<l and data[idx]==c:
				idx+=1
			return idx-startIdxdef
		def countDifferent(data,startIdx):
			"""
			count how many times bytes are different
			"""
			l=len(data)
			if idx>=l:
				return 0
			c=data[idx]
			idx=startIdx+1
			while idx<l and data[idx]!=c:
				idx+=1
				c=data[idx]
			return idx-startIdx
		def rleEncodeChan(data):
			"""
			rle encode a single channel of data
			"""
			ret=[]
			idx=0
			while idx<len(data):
				nRepeats=countSame(data,0)
				if nRepeats==1: # different bytes
					nDifferences=countDifferent(data,1)
					if nDifferences<=127: # short run of different bytes
						ret.append(129+nRepeats-1)
						ret.append(data[idx])
						idx+=nDifferences
					else: # long run of different bytes
						ret.append(128)
						ret.append(floor(nDifferences/256.0))
						ret.append(nDifferences%256)
						ret.append(data[idx])
						idx+=nDifferences
				elif nRepeats<=127: # short run of same bytes
					ret.append(nRepeats-1)
					ret.append(data[idx])
					idx+=nRepeats
				else: # long run of same bytes
					ret.append(127)
					ret.append(floor(nRepeats/256.0))
					ret.append(nRepeats%256)
					ret.append(data[idx])
					idx+=nRepeats
			return ret
		# if there is only one channel, encode and return it directly
		if bpp==1:
			return rleEncodeChan(data)
		# split into channels
		dataByChannel=[]
		for chan in range(bpp):
			chanData=[]
			for index in range(chan,bpp,len(data)):
				chanData.append(data[index])
			dataByChannel.append(chanData)
		# encode each channel
		for index in dataByChannel:
			dataByChannel[index]=rleEncodeChan(dataByChannel[index])
		# join and return
		return ''.join(dataByChannel)
	
	@property
	def bpp(self):
		return self.parent.bpp
		
	@property
	def mode(self):
		MODES=[None,'L','LA','RGB','RGBA']
		return MODES[self.bpp]
		
	@property
	def tiles(self):
		if self._tiles is not None:
			return self._tiles
		if self.image is not None:
			return self._imgToTiles(self.image)
		return None

	def _imgToTiles(self,image):
		"""
		break an image into a series of tiles, each<=64x64
		"""
		ret=[]
		for y in range(0,self.height,64):
			for x in range(0,self.width,64):
				bounds=(x,y,min(self.width-x,64),min(self.height-y,64))
				ret.append(image.crop(bounds))
		return ret

	@property
	def image(self):
		"""
		get a final, compiled image
		"""
		if self._image==None:
			self._image=PIL.Image.new(self.mode,(self.width,self.height),color=None)
			tileNum=0
			for y in range(0,self.height,64):
				for x in range(0,self.width,64):
					subImage=self.tiles[tileNum]
					tileNum+=1
					self._image.paste(subImage,(x,y))
			self._tiles=None # TODO: do I want to keep the tiles for any reason??
		return self._image
	@image.setter
	def image(self,image):
		self._image=image
		self._tiles=None
		self.width=image.width
		self.height=image.height
		self.tiles=None

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Size: '+str(self.width)+' x '+str(self.height))
		return indent+(('\n'+indent).join(ret))