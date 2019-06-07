#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Gimp color gradient
"""
from .binaryIO import *


class GradientSegment:
	"""
	Single segment within a gradient
	"""

	BLEND_FUNCTIONS=[
		"linear","curved","sinusoidal","spherical (increasing)",
		"spherical (decreasing)","step"]
	COLOR_TYPES=["RGB","HSV CCW","HSV CW"]
	ENDPOINT_COLOR_TYPES=[
		"fixed","foreground","foreground transparent",
		"background","background transparent"]

	def __init__(self):
		self.leftPosition=0
		self.middlePosition=0.5
		self.rightPosition=1.0
		self.leftColor=(0,0,0,0)
		self.rightColor=(255,255,255,0)
		self.blendFunc=None # one of self.BLEND_FUNCTIONS
		self.colorType=None # one of self.COLOR_TYPES
		self.leftColorType=None # one of self.ENDPOINT_COLOR_TYPES
		self.rightColorType=None # one of self.ENDPOINT_COLOR_TYPES

	def getColor(self,percent):
		"""
		given a decimal percent (1.0 = 100%) retrieve
		the appropriate color for this point in the gradient
		"""
		raise NotImplementedError()

	def _decode_(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		data=data.split(' ')
		if len(data)<11 or len(data)>15:
			raise Exception('Data table is unexpected size. '+str(len(data)))
		self.leftPosition=float(data[0])
		self.middlePosition=float(data[1])
		self.rightPosition=float(data[2])
		self.leftColor=(float(data[3]),float(data[4]),float(data[5]),float(data[6]))
		self.rightColor=(float(data[7]),float(data[8]),float(data[9]),float(data[10]))
		if len(data)>=12:
			self.blendFunc=int(data[11])
			if len(data)>=13:
				self.colorType=int(data[12])
				if len(data)>=14:
					self.leftColorType=int(data[13])
					if len(data)>=15:
						self.rightColorType=int(data[14])

	def toBytes(self):
		"""
		encode this to a byte array
		"""
		ret=[]
		ret.append("%06f"%self.leftPosition)
		ret.append("%06f"%self.middlePosition)
		ret.append("%06f"%self.rightPosition)
		for chan in self.leftColor:
			ret.append("%06f"%chan)
		for chan in self.rightColor:
			ret.append("%06f"%chan)
		if self.blendFunc is not None:
			ret.append("%d"%self.blendFunc)
			if self.colorType is not None:
				ret.append("%d"%self.colorType)
				if self.leftColorType is not None:
					ret.append("%d"%self.leftColorType)
					if self.rightColorType is not None:
						ret.append("%d"%self.rightColorType)
		return (' '.join(ret))

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Left Position: '+str(self.leftPosition))
		ret.append('Middle Position: '+str(self.middlePosition))
		ret.append('Right Position: '+str(self.rightPosition))
		ret.append('Left Color: '+str(self.leftColor))
		ret.append('Right Color: '+str(self.rightColor))
		ret.append('Blend Function: '+self.BLEND_FUNCTIONS[self.blendFunc])
		ret.append('Color Type: '+self.COLOR_TYPES[self.colorType])
		ret.append('Left Color Type: '+self.ENDPOINT_COLOR_TYPES[self.leftColorType])
		ret.append('Right Color Type: '+self.ENDPOINT_COLOR_TYPES[self.rightColorType])
		return ('\n'+indent).join(ret)


class GimpGgrGradient:
	"""
	Gimp golor gradient

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/ggr.txt
	"""

	def __init__(self,filename=None):
		self.filename=None
		self.segments=[]
		self.name=''
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
		data=data.decode('utf-8').split('\n')
		data=[l.strip() for l in data]
		if data[0]!='GIMP Gradient':
			raise Exception('File format error.  Magic value mismatch.')
		self.name=data[1].split(':',1)[-1].strip()
		numSegments=int(data[2])
		for i in range(numSegments):
			gs=GradientSegment()
			gs._decode_(data[i+3])
			self.segments.append(gs)

	def toBytes(self):
		"""
		encode this to a byte array
		"""
		ret=['GIMP Gradient']
		ret.append('Name: '+self.name)
		ret.append(str(len(self.segments)))
		for segment in self.segments:
			ret.append(segment.toBytes())
		return ('\n'.join(ret)+'\n').encode('utf-8')

	def save(self,toFilename=None,toExtension=None):
		"""
		save this gimp image to a file
		"""
		if not hasattr(toFilename,'write'):
			f=open(toFilename,'wb')
		f.write(self.toBytes())

	def getColor(self,percent):
		"""
		given a decimal percent (1.0 = 100%) retrieve
		the appropriate color for this point in the gradient
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
		for s in self.segments:
			ret.append(s.__repr__(indent+'\t'))
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
					print(g)
				else:
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				g=GimpGgrGradient(arg)
	if printhelp:
		print('Usage:')
		print('  gimpGgrGradient.py file.xcf [options]')
		print('Options:')
		print('   -h, --help ............ this help screen')
		print('   --dump ................ dump info about this file')
		print('   --register ............ register this extension')