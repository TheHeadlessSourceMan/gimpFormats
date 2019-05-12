#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Parasites are arbitrary (meta)data strings that can be attached to a document tree item

They are used to store things like last-used plugin settings, gamma adjuetments, etc.

Format of known parasites:
	https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/parasites.txt
"""
from binaryIO import *


#TODO: how to best use these for our puproses??
KNOWN_DOCUMENT_PARASITES=["jpeg-save-defaults","png-save-defaults","<plug-in>/_fu_data","exif-orientation-rotate"]
KNOWN_IMAGE_PARASITES=["gimp-comment","gimp-brush-name","gimp-brush-pipe-name","gimp-brush-pipe-parameters","gimp-image-grid","gimp-pattern-name","tiff-save-options","jpeg-save-options","jpeg-exif-data","jpeg-original-settings","gamma","chromaticity","rendering-intent","hot-spot","exif-data","gimp-metadata","icc-profile","icc-profile-name","decompose-data","print-settings","print-page-setup","dcm/XXXX-XXXX-AA"]
KNOWN_LAYER_PARASITES=["gimp-text-layer","gfig"]


class GimpParasite(object):
	"""
	Parasites are arbitrary (meta)data strings that can be attached to a document tree item

	They are used to store things like last-used plugin settings, gamma adjuetments, etc.

	Format of known parasites:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/parasites.txt
	"""

	def __init__(self):
		self.name=''
		self.flags=0
		self.data=None

	def fromBytes(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		self.name=io.sz754
		self.flags=io.u32
		dataLength=io.u32
		self.data=io.getBytes(dataLength)
		return io.index
		
	def toBytes(self):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO()
		io.sz754=self.name
		io.u32=self.flags
		io.u32=len(self.data)
		io.addBytes(self.data)
		return io.data

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Name: '+str(self.name))
		ret.append('Flags: '+str(self.flags))
		ret.append('Data Len: '+str(len(self.data)))
		return indent+(('\n'+indent).join(ret))