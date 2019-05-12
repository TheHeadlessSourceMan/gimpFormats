#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp vbr brush format
"""
import struct
import PIL.Image
	

class GimpVbrBrush(object):
	"""
	Pure python implementation of the gimp vbr brush format

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/vbr.txt
	"""

	BRUSH_SHAPES=["circle","square","diamond"]

	def __init__(self,filename):
		self.version=1.0
		self.name=''
		self.spacing=0
		self.radius=50
		self.hardness=1
		self.aspectRatio=1
		self.angle=0
		self.brushShape=None # one of the strings in self.BRUSH_SHAPES
		self.spikes=None
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
			f=open(filename,'r')
		data=f.read()
		f.close()
		self._decode_(data)

	def _decode_(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		data=[s.strip() for s in data.split('\n')]
		if data[0]!="GIMP-VBR":
			raise Exception('File format error.  Magic value mismatch.')
		self.version=float(data[1])
		if self.version==1.0:
			self.name=data[2].decode('UTF-8') # max len 255 bytes
			self.spacing=float(data[3])
			self.radius=float(data[4])
			self.hardness=float(data[5])
			self.aspectRatio=float(data[6])
			self.angle=float(data[7])
		elif self.version==1.5:
			self.name=data[2].decode('UTF-8') # max len 255 bytes
			self.brushShape=data[3] # one of the strings in self.BRUSH_SHAPES
			self.spacing=float(data[4])
			self.radius=float(data[5])
			self.spikes=float(data[6])
			self.hardness=float(data[7])
			self.aspectRatio=float(data[8])
			self.angle=float(data[9])
		else:
			raise Exception('Unknown version '+str(self.version))

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
		ret.append('Spacing: '+str(self.spacing))
		ret.append('Radius: '+str(self.radius))
		ret.append('Hardness: '+str(self.hardness))
		ret.append('Aspect ratio: '+str(self.aspectRatio))
		ret.append('Angle: '+str(self.angle))
		ret.append('Brush Shape: '+str(self.brushShape))
		ret.append('Spikes: '+str(self.spikes))
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
					print g
				else:
					print 'ERR: unknown argument "'+arg[0]+'"'
			else:
				g=GimpVbrBrush(arg)
	if printhelp:
		print 'Usage:'
		print '  gimpVbrBrush.py file.xcf [options]'
		print 'Options:'
		print '   -h, --help ............ this help screen'
		print '   --dump ................ dump info about this file'
		print '   --register ............ register this extension'