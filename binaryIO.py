#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Base binary I/O helper.  

Does boilerplate things like reading the next uint32 from the document
"""
import struct


class BinIOBase(object):
	"""
	Base binary I/O helper.  Does boilerplate
	things like reading the next uint32 from the document
	"""

	def __init__(self):
		self._idx=0
		self._data=None

	def _decode_(self,data,idx=0):
		"""
		performs a binary file decode

		IMPORTANT: you should overwrite this for your format,
			but you MUST call the base class!
		"""
		self._idx=idx
		self._data=data

	def _u32_(self):
		"""
		read the next uint32 and advance the index
		"""
		d=struct.unpack('>I',self._data[self._idx:self._idx+4])[0]
		self._idx+=4
		return d
	def _i32_(self):
		"""
		read the next signed int32 and advance the index
		"""
		d=struct.unpack('>i',self._data[self._idx:self._idx+4])[0]
		self._idx+=4
		return d
	def _float_(self):
		"""
		read the next 32 bit float and advance the index
		"""
		d=struct.unpack('>f',self._data[self._idx:self._idx+4])[0]
		self._idx+=4
		return d

	def _bytes_(self,nbytes=1):
		"""
		grab some raw bytes and advance the index
		"""
		d=self._data[self._idx:self._idx+nbytes]
		self._idx+=nbytes
		return d

	def _sz754_(self):
		"""
		Read the next string conforming to IEEE 754 and advance the index

		Note, string format is:
			uint32   n+1  Number of bytes that follow, including the zero byte
			byte[n]  ...  String data in Unicode, encoded using UTF-8
			byte     0    Zero marks the end of the string.
		or simply uint32=0 for empty string
		"""
		nchars=self._u32_()
		if nchars==0:
			return ''
		d=self._data[self._idx:self._idx+nchars-1]
		self._idx+=nchars
		return d

	def _asciiz_(self,nChars=0):
		"""
		Read the next ascii c-string and advance the index

		:param nChars: the number of chars to read
			(if 0, read util nul character)
		"""
		if nChars>0:
			d=self._data[self._idx:self._idx+nChars]
			self._idx+=nChars
		else:
			d=[]
			while True:
				c=self._data[self._idx]
				self._idx+=1
				if c=='\0':
					d=''.join(d)
					break
				d.append(c)
		return d
