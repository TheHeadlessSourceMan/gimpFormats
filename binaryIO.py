#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Base binary I/O helper.  

Does boilerplate things like reading the next uint32 from the document
"""
import struct


class IO(object):
	"""
	Class to handle i/o to a byte buffer or file-like object
	"""
	
	def __init__(self,data=0,idx=0,littleEndian=False,boolSize=8,stringEncoding='U'):
		"""
		:param data: can be a data buffer or a file-like object
		:param idx: start reading/writing the data at the given index
		:param littleEndian: whether the default is big-endian or little-endian
		:param boolSize: how many default bits to use for a bool (8,16,32,or 64)
		:param stringEncoding: default string encoding A=Ascii, U=UTF-8, W-Unicode wide
		"""
		self.data=data
		self.index=idx
		self._contexts=[]
		self.littleEndian=littleEndian
		self.boolSize=boolSize
		self.stringEncoding=stringEncoding # A=Ascii, U=UTF-8, W-Unicode wide
	
	def beginContext(self,newIndex):
		"""
		Start a new context where the index can be changed all you want,
		and when endContext() is called, it will be restored to the current position
		"""
		self.contexts.append(newIndex)
	def endContext(self):
		"""
		Restore the index to the previous location where it was when beginContext() was called
		"""
		self.index=self.contexts.pop()

	@property
	def bool(self):
		if self.boolSize==8:
			return self.bool8
		if self.boolSize==16:
			return self.bool16
		if self.boolSize==32:
			return self.bool32
		if self.boolSize==64:
			return self.bool64
		raise Exception("Unknown bool size")
	@bool.setter
	def bool(self,bool):
		if self.boolSize==8:
			self.bool8=bool
		if self.boolSize==16:
			self.bool16=bool
		if self.boolSize==32:
			self.bool32=bool
		if self.boolSize==64:
			self.bool64=bool
		raise Exception("Unknown bool size")
	
	@property	
	def bool8(self):
		return self.u8!=0
	@bool8.setter
	def bool8(self,bool):
		self.u8=bool
	@property
	def bool16(self):
		return self.u16!=0 
	@bool16.setter
	def bool16(self,bool):
		self.u16=bool
	@property
	def bool32(self):
		return self.u32!=0 
	@bool32.setter
	def bool32(self,bool):
		self.u32=bool
	@property
	def bool64(self):
		return self.u64!=0 
	@bool64.setter
	def bool64(self,bool):
		self.u64=bool

	@property
	def byte(self):
		return self.i8
	@byte.setter
	def byte(self,byte):
		self.i8=byte
	@property
	def unsignedByte(self):
		return self.u8
	@unsignedByte.setter
	def unsignedByte(self,byte):
		self.u8=byte
	@property
	def word(self):
		return self.i16
	@word.setter
	def word(self,word):
		self.i16=word
	@property
	def unsignedWord(self):
		return self.u16
	@unsignedWord.setter
	def unsignedWord(self,unsignedWord):
		self.u16=unsignedWord
	@property
	def dword(self):
		return self.i32
	@dword.setter
	def dword(self,dword):
		self.i32=dword
	@property
	def unsignedDword(self):
		return self.u32
	@unsignedDword.setter
	def unsignedDword(self,unsignedDword):
		self.u32=unsignedDword
	@property
	def qword(self):
		return self.i64
	@qword.setter
	def qword(self,qword):
		self.i64=qword
	@property
	def unsignedQword(self):
		return self.u64
	@unsignedQword.setter
	def unsignedQword(self,unsignedQword):
		self.u64=unsignedQword
		
	@property
	def i8(self):
		if self.littleEndian:
			return self.i8le
		return self.i8be
	@i8.setter
	def i8(self,i8):
		if self.littleEndian:
			self.i8le=i8
		self.i8be=i8
	@property
	def u8(self):
		if self.littleEndian:
			return self.u8le
		return self.u8be
	@u8.setter
	def u8(self,u8):
		if self.littleEndian:
			self.u8le=u8
		self.u8be=u8
	@property
	def i16(self):
		if self.littleEndian:
			return self.i16le
		return self.i16be
	@i16.setter
	def i16(self,i16):
		if self.littleEndian:
			self.i16le=i16
		self.i16be=i16
	@property
	def u16(self):
		if self.littleEndian:
			return self.i16le
		return self.i16be
	@u16.setter
	def u16(self,u16):
		if self.littleEndian:
			self.u16le=u16
		self.u16be=u16
	@property
	def i32(self):
		if self.littleEndian:
			return self.i32le
		return self.i32be
	@i32.setter
	def i32(self,i32):
		if self.littleEndian:
			self.i32le=i32
		self.i32be=i32
	@property
	def u32(self):
		if self.littleEndian:
			return self.i32le
		return self.i32be
	@u32.setter
	def u32(self,u32):
		if self.littleEndian:
			self.u32le=u32
		self.u32be=u32
	@property
	def i64(self):
		if self.littleEndian:
			return self.i64le
		return self.i64be
	@i64.setter
	def i64(self,i64):
		if self.littleEndian:
			self.i64le=i64
		self.i64be=i64
	@property
	def u64(self):
		if self.littleEndian:
			return self.i64le
		return self.i64be
	@u64.setter
	def u64(self,u64):
		if self.littleEndian:
			self.u64le=u64
		self.u64be=u64
	@property
	def float32(self):
		if self.littleEndian:
			return self.float32le
		return self.float32be
	@float32.setter
	def float32(self,float32):
		if self.littleEndian:
			self.float32le=float32
		self.float32be=float32
	@property
	def float64(self):
		if self.littleEndian:
			return self.float64le
		return self.float64be
	@float64.setter
	def float64(self,float64):
		if self.littleEndian:
			self.float64le=float64
		self.float64be=float64
		
	@property
	def u8be(self):
		"""
		read the next uint8 and advance the index
		"""
		d=struct.unpack('>B',self.data[self.index:self.index+1])[0]
		self.index+=1
		return d
	@u8be.setter
	def u8be(self,u8be):
		pack_into('>B',self.data,self.index,u8be)
		self.index+=1
	@property
	def u8le(self):
		"""
		read the next uint8 and advance the index
		"""
		d=struct.unpack('<B',self.data[self.index:self.index+1])[0]
		self.index+=1
		return d
	@u8le.setter
	def u8le(self,u8le):
		pack_into('<B',self.data,self.index,u8le)
		self.index+=1
	@property
	def i8le(self):
		"""
		read the next signed int8 and advance the index
		"""
		d=struct.unpack('<b',self.data[self.index:self.index+1])[0]
		self.index+=1
		return d
	@i8le.setter
	def i8le(self,i8le):
		pack_into('<b',self.data,self.index,i8le)
		self.index+=1
	@property
	def i8be(self):
		"""
		read the next signed int8 and advance the index
		"""
		d=struct.unpack('>b',self.data[self.index:self.index+1])[0]
		self.index+=1
		return d
	@i8be.setter
	def i8be(self,i8be):
		pack_into('>b',self.data,self.index,i8be)
		self.index+=1
		
	@property
	def u16be(self):
		"""
		read the next uint16 and advance the index
		"""
		d=struct.unpack('>H',self.data[self.index:self.index+2])[0]
		self.index+=2
		return d
	@u16be.setter
	def u16be(self,u16be):
		pack_into('>H',self.data,self.index,u16be)
		self.index+=2
	@property
	def u16le(self):
		"""
		read the next uint16 and advance the index
		"""
		d=struct.unpack('<H',self.data[self.index:self.index+2])[0]
		self.index+=2
		return d
	@u16le.setter
	def u16le(self,u16le):
		pack_into('<H',self.data,self.index,u16le)
		self.index+=2
	@property
	def i16le(self):
		"""
		read the next signed int16 and advance the index
		"""
		d=struct.unpack('<h',self.data[self.index:self.index+2])[0]
		self.index+=2
		return d
	@i16le.setter
	def i16le(self,i16le):
		pack_into('<h',self.data,self.index,i16le)
		self.index+=2
	@property
	def i16be(self):
		"""
		read the next signed int16 and advance the index
		"""
		d=struct.unpack('>h',self.data[self.index:self.index+2])[0]
		self.index+=2
		return d
	@i16be.setter
	def i16be(self,i16be):
		pack_into('>h',self.data,self.index,i16be)
		self.index+=2
		
	@property
	def u32be(self):
		"""
		read the next uint32 and advance the index
		"""
		d=struct.unpack('>I',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@u32be.setter
	def u32be(self,u32be):
		pack_into('>I',self.data,self.index,u32be)
		self.index+=4
	@property
	def u32le(self):
		"""
		read the next uint32 and advance the index
		"""
		d=struct.unpack('<I',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@u32le.setter
	def u32le(self,u32le):
		pack_into('<I',self.data,self.index,u32le)
		self.index+=4
	@property
	def i32le(self):
		"""
		read the next signed int32 and advance the index
		"""
		d=struct.unpack('<i',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@i32le.setter
	def i32le(self,i32le):
		pack_into('<i',self.data,self.index,i32le)
		self.index+=4
	@property
	def i32be(self):
		"""
		read the next signed int32 and advance the index
		"""
		d=struct.unpack('>i',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@i32be.setter
	def i32be(self,i32be):
		pack_into('>i',self.data,self.index,i32be)
		self.index+=4
		
	@property
	def u64be(self):
		"""
		read the next uint64 and advance the index
		"""
		d=struct.unpack('>Q',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@u64be.setter
	def u64be(self,u64be):
		pack_into('>Q',self.data,self.index,u64be)
		self.index+=8
	@property
	def u64le(self):
		"""
		read the next uint64 and advance the index
		"""
		d=struct.unpack('<Q',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@u64le.setter
	def u64le(self,u64le):
		pack_into('<Q',self.data,self.index,u64le)
		self.index+=8
	@property
	def i64le(self):
		"""
		read the next signed int64 and advance the index
		"""
		d=struct.unpack('<q',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@i64le.setter
	def i64le(self,i64le):
		pack_into('<q',self.data,self.index,i64le)
		self.index+=8
	@property
	def i64be(self):
		"""
		read the next signed int64 and advance the index
		"""
		d=struct.unpack('>q',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@i64be.setter
	def i64be(self,i64be):
		pack_into('>q',self.data,self.index,i64be)
		self.index+=8
		
	@property
	def float(self):
		return self.float32
	@float.setter
	def float(self,f):
		self.float32=f
	@property
	def double(self):
		return self.float64
	@double.setter
	def double(self,f):
		self.float64=f
	@property
	def float32be(self):
		"""
		read the next 32 bit float and advance the index
		"""
		d=struct.unpack('>f',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@float32be.setter
	def float32be(self,float32be):
		pack_into('>f',self.data,self.index,float32be)
		self.index+=4
	@property
	def float32le(self):
		"""
		read the next 32 bit float and advance the index
		"""
		d=struct.unpack('<f',self.data[self.index:self.index+4])[0]
		self.index+=4
		return d
	@float32le.setter
	def float32le(self,float32le):
		pack_into('<f',self.data,self.index,float32le)
		self.index+=4
	@property
	def float64be(self):
		"""
		read the next 64 bit float and advance the index
		"""
		d=struct.unpack('>d',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@float64be.setter
	def float64be(self,float64be):
		pack_into('>d',self.data,self.index,float64be)
		self.index+=8
	@property
	def float64le(self):
		"""
		read the next 64 bit float and advance the index
		"""
		d=struct.unpack('<d',self.data[self.index:self.index+8])[0]
		self.index+=8
		return d
	@float64le.setter
	def float64le(self,float64le):
		pack_into('<d',self.data,self.index,float64le)
		self.index+=8

	def getBytes(self,nbytes):
		"""
		grab some raw bytes and advance the index
		"""
		d=self.data[self.index:self.index+nbytes]
		self.index+=nbytes
		return d
	def addBytes(self,bytes):
		"""
		add some raw bytes and advance the index
		
		alias for setBytes()
		
		:param bytes: can be a string, bytearray, or another IO object
		"""
		self.setBytes(bytes)
	def setBytes(self,bytes):
		"""
		add some raw bytes and advance the index
		
		alias for addBytes()
		
		:param bytes: can be a string, bytearray, or another IO object
		"""
		if isinstance(bytes,IO):
			bytes=io.data
		nbytes=len(bytes)
		d=self.data[self.index].extend(bytes)
		self.index+=nbytes

	def _sz754(self,encoding):
		"""
		Read the next string conforming to IEEE 754 and advance the index

		Note, string format is:
			uint32   n+1  Number of bytes that follow, including the zero byte
			byte[n]  ...  String data in Unicode, encoded using UTF-8
			byte     0    Zero marks the end of the string.
		or simply uint32=0 for empty string
		"""
		nchars=self.u32
		if nchars==0:
			return ''
		d=self.data[self.index:self.index+nchars-1]
		self.index+=nchars
		if encoding=='A':
			return d
		if encoding=='U':
			return d.decode('UTF-8',errors='replace')
		if encoding=='W':
			return d.decode('UTF-16',errors='replace')
		raise Exception()
	def _sz754set(self,sz754,encoding):
		pack_into('<d',self.data,self.index,float64le)
		self.u32=len(sz754)
		self.setBytes(sz754)
		self.u8=0
	@property
	def sz754(self):
		return self._sz754(self.stringEncoding)
	@sz754.setter
	def sz754(self,sz754):
		return self._sz754set(sz754,self.stringEncoding)
	@property
	def sz754A(self):
		return self._sz754('A')
	@sz754A.setter
	def sz754A(self,sz754):
		return self._sz754set(sz754,'A')
	@property
	def sz754W(self):
		return self._sz754('W')
	@sz754W.setter
	def sz754W(self,sz754):
		return self._sz754set(sz754,'W')
	@property
	def sz754U(self):
		return self._sz754('U')
	@sz754U.setter
	def sz754U(self,sz754):
		return self._sz754set(sz754,'U')
	
	def _readUntil(self,until,encoding='A'):
		d=[]
		while True:
			c=self.data[self.index]
			self.index+=1
			if encoding=='W':
				d.append(c)
				c=self.data[self.index]
				self.index+=1
			if c==until:
				d=''.join(d)
				break
			d.append(c)
		if encoding=='A':
			return d
		if encoding=='U':
			return d.decode('UTF-8',errors='replace')
		if encoding=='W':
			return d.decode('UTF-16',errors='replace')
		raise Exception()
		
	@property
	def textLine(self):
		ret=self._readUntil('\n',self.stringEncoding)
		if ret[-1]=='\r':
			ret=ret[-1]
		return ret
	@textLine.setter
	def textLine(self,text):
		setBytes(text)
		if text[-1]!='\n':
			setBytes('\n')
	@property
	def textLineA(self):
		ret=self._readUntil('\n','A')
		if ret[-1]=='\r':
			ret=ret[-1]
		return ret
	@textLineA.setter
	def textLineA(self,text):
		setBytes(text)
		if text[-1]!='\n':
			setBytes('\n')
	@property
	def textLineW(self):
		ret=self._readUntil('\n','W')
		if ret[-1]=='\r':
			ret=ret[-1]
		return ret
	@textLineW.setter
	def textLineW(self,text):
		setBytes(text)
		if text[-1]!='\n':
			setBytes('\0\n')
	@property
	def textLineU(self):
		ret=self._readUntil('\n','U')
		if ret[-1]=='\r':
			ret=ret[-1]
		return ret
	@textLineU.setter
	def textLineU(self,text):
		setBytes(text)
		if text[-1]!='\n':
			setBytes('\n')
		
	@property
	def cString(self):
		return self._readUntil('\0',self.stringEncoding)
	@cString.setter
	def cString(self,text):
		setBytes(text)
		setBytes('\0')
	@property
	def cStringA(self):
		return self._readUntil('\0','A')
	@cString.setter
	def cString(self,text):
		setBytes(text)
		setBytes('\0')
	@property
	def cStringW(self):
		return self._readUntil('\0','W')
	@cString.setter
	def cString(self,text):
		setBytes(text)
		setBytes('\0\0')
	@property
	def cStringU(self):
		return self._readUntil('\0','U')
	@cString.setter
	def cString(self,text):
		setBytes(text)
		setBytes('\0')
		
