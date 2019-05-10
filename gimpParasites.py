#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
arbitrary data that can be attached to any tree item

List of known parasites: #TODO: integrate these!
	https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/parasites.txt
"""
from binaryIO import *


class GimpParasite(BinIOBase):
	"""
	arbitrary data that can be attached to any tree item

	List of known parasites: #TODO: integrate these!
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/parasites.txt
	"""

	def __init__(self):
		BinIOBase.__init__(self)
		self.name=''
		self.flags=0
		self.data=None

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		BinIOBase._decode_(self,data,idx)
		self.name=self._sz754_()
		self.flags=self._u32_()
		dataLength=self._u32_()
		self.data=self._bytes_(dataLength)
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Name: '+str(self.name))
		ret.append('Flags: '+str(self.flags))
		ret.append('Data Len: '+str(len(self.data)))
		return indent+(('\n'+indent).join(ret))