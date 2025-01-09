#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Base binary I/O helper.

Does boilerplate things like reading the next uint32 from the document
"""
import typing
import struct


class GimpIOException(Exception):
    """
    An exception to be thrown when a
    problem with IO is encountered
    """
    def __init__(self,io:'IO',message):
        msg='At index %d: %s'%(io.index,message)
        Exception.__init__(self,msg)

class IO:
    """
    Class to handle i/o to a byte buffer or file-like object
    """

    def __init__(self,
        data:typing.Union[None,bytes,bytearray]=None,
        idx:int=0,
        littleEndian:bool=False, # pylint: disable=used-before-assignment
        boolSize:int=8,
        stringEncoding:str='U'):
        """
        :param data: can be a data buffer or a file-like object
        :param idx: start reading/writing the data at the given index
        :param littleEndian: whether the default is big-endian or little-endian
        :param boolSize: how many default bits to use for a bool 8,16,32,or 64
        :param stringEncoding: default string encoding
            A=Ascii, U=UTF-8, W-Unicode wide
        """
        self._data:typing.Optional[bytes]=None
        if data is None:
            self.data=bytearray()
        elif isinstance(data,(bytes,bytearray)):
            self.data=bytearray(data)
        else:
            if hasattr(data,'encode'):
                data=data.encode(data)
            else:
                data=bytearray(str(data).encode('UTF-8'))
            self.data=bytearray(data)
        self.contexts:typing.List[int]=[]
        self.index:int=idx
        self.littleEndian:bool=littleEndian
        self.boolSize:int=boolSize
        self.stringEncoding:str=stringEncoding # A=Ascii,U=UTF-8,W-Unicode wide

    @property
    def data(self)->bytes:
        """
        The actual data bytes
        """
        if self._data is None:
            return bytes()
        return self._data
    @data.setter
    def data(self,data:bytes):
        if not hasattr(data,"__getitem__"):
            dataType=str(type(data))
            raise Exception(f'ERR: incorrect type for data buffer {dataType}')
        self._data=data

    def beginContext(self,newIndex:int)->None:
        """
        Start a new context where the index can be changed all you want,
        and when endContext() is called, it will be restored
        to the current position
        """
        self.contexts.append(newIndex)
    def endContext(self)->None:
        """
        Restore the index to the previous location where it was
        when beginContext() was called
        """
        self.index=self.contexts.pop()

    def _write(self,
        size:int,fmt:str,data:int
        )->None:
        """
        general formatted write
        """
        if self.index+size>=len(self.data):
            self.data=self.data+bytes((self.index+size)-len(self.data))
        try:
            struct.pack_into(fmt,self.data,self.index,data)
            self.index+=size
        except struct.error as e:
            raise Exception(type(data),fmt,size) from e

    @property
    def bool(self):
        """
        a boolean true/false type
        """
        if self.boolSize==8:
            return self.bool8
        if self.boolSize==16:
            return self.bool16
        if self.boolSize==32:
            return self.bool32
        if self.boolSize==64:
            return self.bool64
        raise Exception("Unknown bool size "+str(self.boolSize))
    @bool.setter
    def bool(self,val:bool):
        if self.boolSize==8:
            self.bool8=val
        elif self.boolSize==16:
            self.bool16=val
        elif self.boolSize==32:
            self.bool32=val
        elif self.boolSize==64:
            self.bool64=val
        else:
            raise Exception(f'Unknown bool size {self.boolSize}')

    @property
    def bool8(self):
        """
        8-bit bool
        """
        return self.u8!=0
    @bool8.setter
    def bool8(self,val:bool): # type:ignore
        self.u8=val
    @property
    def bool16(self):
        """
        16-bit bool
        """
        return self.u16!=0
    @bool16.setter
    def bool16(self,val:bool): # type:ignore
        self.u16=val
    @property
    def bool32(self):
        """
        32-bit bool
        """
        return self.u32!=0
    @bool32.setter
    def bool32(self,val:bool): # type:ignore
        self.u32=val
    @property
    def bool64(self):
        """
        64-bit bool
        """
        return self.u64!=0
    @bool64.setter
    def bool64(self,val:bool): # type:ignore
        self.u64=val

    @property
    def byte(self):
        """
        A signed 8-bit byte
        """
        return self.i8
    @byte.setter
    def byte(self,byte):
        self.i8=byte
    @property
    def unsignedByte(self):
        """
        An unsigned 8-bit byte
        """
        return self.u8
    @unsignedByte.setter
    def unsignedByte(self,byte):
        self.u8=byte
    @property
    def word(self):
        """
        A signed 16-bit word
        """
        return self.i16
    @word.setter
    def word(self,word):
        self.i16=word
    @property
    def unsignedWord(self):
        """
        An unsigned 16-bit word
        """
        return self.u16
    @unsignedWord.setter
    def unsignedWord(self,unsignedWord):
        self.u16=unsignedWord
    @property
    def dword(self):
        """
        A signed 32-bit double-word
        """
        return self.i32
    @dword.setter
    def dword(self,dword):
        self.i32=dword
    @property
    def unsignedDword(self):
        """
        An unsigned 32-bit double-word
        """
        return self.u32
    @unsignedDword.setter
    def unsignedDword(self,unsignedDword):
        self.u32=unsignedDword
    @property
    def qword(self):
        """
        A signed 64-bit quad-word
        """
        return self.i64
    @qword.setter
    def qword(self,qword):
        self.i64=qword
    @property
    def unsignedQword(self):
        """
        An unsigned 64-bit quad-word
        """
        return self.u64
    @unsignedQword.setter
    def unsignedQword(self,unsignedQword):
        self.u64=unsignedQword

    @property
    def i8(self):
        """
        8-bit signed int
        """
        if self.littleEndian:
            return self.i8le
        return self.i8be
    @i8.setter
    def i8(self,i8):
        if self.littleEndian:
            self.i8le=i8
        else:
            self.i8be=i8
    @property
    def u8(self):
        """
        8-bit unsigned int
        """
        if self.littleEndian:
            return self.u8le
        return self.u8be
    @u8.setter
    def u8(self,u8):
        if self.littleEndian:
            self.u8le=u8
        else:
            self.u8be=u8
    @property
    def i16(self):
        """
        8-bit signed int
        """
        if self.littleEndian:
            return self.i16le
        return self.i16be
    @i16.setter
    def i16(self,i16):
        if self.littleEndian:
            self.i16le=i16
        else:
            self.i16be=i16
    @property
    def u16(self):
        """
        16-bit unsigned int
        """
        if self.littleEndian:
            return self.i16le
        return self.i16be
    @u16.setter
    def u16(self,u16):
        if self.littleEndian:
            self.u16le=u16
        else:
            self.u16be=u16
    @property
    def i32(self):
        """
        32-bit signed int
        """
        if self.littleEndian:
            return self.i32le
        return self.i32be
    @i32.setter
    def i32(self,i32):
        if self.littleEndian:
            self.i32le=i32
        else:
            self.i32be=i32
    @property
    def u32(self):
        """
        32-bit unsigned int
        """
        if self.littleEndian:
            return self.i32le
        return self.i32be
    @u32.setter
    def u32(self,u32):
        if self.littleEndian:
            self.u32le=u32
        else:
            self.u32be=u32
    @property
    def i64(self):
        """
        64-bit signed int
        """
        if self.littleEndian:
            return self.i64le
        return self.i64be
    @i64.setter
    def i64(self,i64):
        if self.littleEndian:
            self.i64le=i64
        else:
            self.i64be=i64
    @property
    def u64(self):
        """
        64-bit unsigned int
        """
        if self.littleEndian:
            return self.i64le
        return self.i64be
    @u64.setter
    def u64(self,u64):
        if self.littleEndian:
            self.u64le=u64
        else:
            self.u64be=u64
    @property
    def float32(self):
        """
        32-bit floating point decimal
        """
        if self.littleEndian:
            return self.float32le
        return self.float32be
    @float32.setter
    def float32(self,float32):
        if self.littleEndian:
            self.float32le=float32
        else:
            self.float32be=float32
    @property
    def float64(self):
        """
        64-bit floating point decimal
        """
        if self.littleEndian:
            return self.float64le
        return self.float64be
    @float64.setter
    def float64(self,float64):
        if self.littleEndian:
            self.float64le=float64
        else:
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
        self._write(1,'>B',u8be)
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
        self._write(1,'<B',u8le)
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
        self._write(1,'<b',i8le)
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
        self._write(1,'>b',i8be)

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
        self._write(2,'>H',u16be)
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
        self._write(2,'<H',u16le)
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
        self._write(2,'<h',i16le)
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
        self._write(2,'>h',i16be)

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
        self._write(4,'>I',int(u32be))
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
        self._write(4,'<I',u32le)
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
        self._write(4,'<i',i32le)
    @property
    def i32be(self):
        """
        read the next signed int32 and advance the index
        """
        try:
            d=struct.unpack('>i',self.data[self.index:self.index+4])[0]
        except Exception as e:
            arrayLen=len(self.data[self.index:self.index+4])
            msg=f'Err reading 4 bytes from array of {arrayLen}'
            raise GimpIOException(self,msg) from e
        self.index+=4
        return d
    @i32be.setter
    def i32be(self,i32be):
        self._write(4,'>i',int(i32be))

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
        self._write(8,'>Q',u64be)
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
        self._write(8,'<Q',u64le)
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
        self._write(8,'<q',i64le)
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
        self._write(8,'>q',i64be)

    @property
    def float(self):
        """
        A 32-bit floating point value
        """
        return self.float32
    @float.setter
    def float(self,f):
        self.float32=f
    @property
    def double(self):
        """
        A 64-bit floating point value
        """
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
        self._write(4,'>f',float32be)
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
        self._write(4,'<f',float32le)
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
        self._write(8,'>d',float64be)
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
        self._write(8,'<d',float64le)

    def getBytes(self,nbytes:int)->bytes:
        """
        grab some raw bytes and advance the index
        """
        d=self.data[self.index:self.index+nbytes]
        self.index+=nbytes
        return d
    def addBytes(self,data:typing.Union[str,'IO',bytes])->None:
        """
        add some raw bytes and advance the index

        alias for setBytes()

        :param bytes: can be a string, bytearray, or another IO object
        """
        self.setBytes(data)
    def setBytes(self,data:typing.Union[bytearray,'IO',str,bytes])->None:
        """
        add some raw bytes and advance the index

        alias for addBytes()

        :param bytes: can be a string, bytearray, or another IO object
        """
        if isinstance(data,IO):
            data=data.data
        if isinstance(data,str):
            data=data.encode("utf-8",errors="ignore")
        elif isinstance(data,bytearray):
            data=bytes(data)
        if self.index>=len(self.data):
            # if we're at the end, simply extend the buffer
            self.data=self.data+data
            self.index+=len(data)
        else:
            if self.index+len(data)>=len(self.data):
                numBytes=(self.index+len(data))-len(self.data)
                self.data=self.data+bytes(numBytes)
            self.data=self.data[0:self.index]+data+self.data[self.index:]

    def _sz754(self,encoding:str)->str:
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
            return d.decode('ascii',errors='replace')
        if encoding=='U':
            return d.decode('UTF-8',errors='replace')
        if encoding=='W':
            return d.decode('UTF-16',errors='replace')
        raise Exception()
    def _sz754set(self,sz754,encoding:str):
        _=encoding # TODO: expand to handle encoding
        self.u32=len(sz754)
        self.setBytes(sz754)
        self.u8=0
    @property
    def sz754(self):
        """
        IEEE 754
        """
        return self._sz754(self.stringEncoding)
    @sz754.setter
    def sz754(self,sz754):
        return self._sz754set(sz754,self.stringEncoding)
    @property
    def sz754A(self):
        """
        IEEE 754 - ASCII
        """
        return self._sz754('A')
    @sz754A.setter
    def sz754A(self,sz754):
        return self._sz754set(sz754,'A')
    @property
    def sz754W(self):
        """
        IEEE 754 - 16-bit unicode
        """
        return self._sz754('W')
    @sz754W.setter
    def sz754W(self,sz754):
        return self._sz754set(sz754,'W')
    @property
    def sz754U(self):
        """
        IEEE 754 - UTF-8
        """
        return self._sz754('U')
    @sz754U.setter
    def sz754U(self,sz754):
        return self._sz754set(sz754,'U')

    def _readUntil(self,
        until:typing.Union[str,bytes],
        encoding:str='A'
        )->str:
        """
        :param until: must be within the ascii character set
        """
        d=[]
        if encoding=='A':
            encoding='ascii'
        elif encoding=='U':
            encoding='UTF-8'
        elif encoding=='W':
            encoding='UCS-2'
        else:
            raise Exception('bogus encoding')
        if not isinstance(until,bytes):
            until=until.encode('ascii',errors='ignore') # always ascii
        while True:
            c=self.data[self.index]
            self.index+=1
            if encoding=='W': # get one more byte
                d.append(c)
                c=self.data[self.index]
                self.index+=1
            if c==until:
                break
            d.append(c)
        return bytes(d).decode(encoding,errors='replace')

    @property
    def textLine(self):
        """
        A line of text
        """
        ret=self._readUntil('\n',self.stringEncoding)
        if ret[-1]=='\r':
            ret=ret[-1]
        return ret
    @textLine.setter
    def textLine(self,text):
        self.setBytes(text)
        if not text or text[-1]!='\n':
            self.setBytes('\n')
    @property
    def textLineA(self):
        """
        A line of text in ASCII format
        """
        ret=self._readUntil('\n','A')
        if ret[-1]=='\r':
            ret=ret[-1]
        return ret
    @textLineA.setter
    def textLineA(self,text):
        self.setBytes(text)
        if not text or text[-1]!='\n':
            self.setBytes('\n')
    @property
    def textLineW(self):
        """
        A line of text in 16-bit unicode format
        """
        ret=self._readUntil('\n','W')
        if ret[-1]=='\r':
            ret=ret[-1]
        return ret
    @textLineW.setter
    def textLineW(self,text):
        self.setBytes(text)
        if not text or text[-1]!='\n':
            self.setBytes('\0\n')
    @property
    def textLineU(self):
        """
        A line of text in UTF-8 format
        """
        ret=self._readUntil('\n','U')
        if ret[-1]=='\r':
            ret=ret[-1]
        return ret
    @textLineU.setter
    def textLineU(self,text):
        self.setBytes(text)
        if not text or text[-1]!='\n':
            self.setBytes('\n')

    @property
    def cString(self):
        """
        A c-style null-terminated string
        """
        return self._readUntil('\0',self.stringEncoding)
    @cString.setter
    def cString(self,text):
        self.setBytes(text)
        self.setBytes('\0')
    @property
    def cStringA(self):
        """
        A c-style null-terminated string
        in ASCII format
        """
        return self._readUntil('\0','A')
    @cStringA.setter
    def cStringA(self,text):
        self.setBytes(text)
        self.setBytes('\0')
    @property
    def cStringW(self):
        """
        A c-style null-terminated string
        in 16-bit unicode format
        """
        return self._readUntil('\0','W')
    @cStringW.setter
    def cStringW(self,text):
        self.setBytes(text)
        self.setBytes('\0\0')
    @property
    def cStringU(self):
        """
        A c-style null-terminated string
        in UTF-8 format
        """
        return self._readUntil('\0','U')
    @cStringU.setter
    def cStringU(self,text):
        self.setBytes(text)
        self.setBytes('\0')
