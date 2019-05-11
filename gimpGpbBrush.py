#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the OLD gimp gpb brush format
"""
import struct
import PIL.Image
from binaryIO import *
from gimpGbrBrush import *
from gimpPatPattern import *
	

class GimpGpbBrush(BinIOBase):
	"""
	Pure python implementation of the OLD gimp gpb brush format

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/vbr.txt
	"""

	def __init__(self,filename):
		BinIOBase.__init__(self)
		self.brush=GimpGbrBrush()
		self.pattern=GimpPatPattern()

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
		self._idx=self.brush._decode_(data,self._idx)
		self._idx=self.pattern._decode_(data,self._idx)
		return self._idx

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
		ret.append(self.brush.__repr__(indent+'\t'))
		ret.append(self.pattern.__repr__(indent+'\t'))
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
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				g=GimGpbBrush(arg)
	if printhelp:
		print 'Usage:'
		print '  gimpGpbBrush.py file.xcf [options]'
		print 'Options:'
		print '   -h, --help ............ this help screen'
		print '   --dump ................ dump info about this file'
		print '   --register ............ register this extension'