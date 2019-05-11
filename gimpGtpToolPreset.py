#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gtp tool preset format
"""
import struct
import PIL.Image
from binaryIO import *
	
class ParenFileValue(object):
	
	def __init__(self):
		self.valueType=None
		self.values=[]
		
	def _addValue(self,bufArray):
		if bufArray:
			bufArray=''.join(bufArray)
			if bufArray in ('yes','no'): # boolean
				self.values.append(bufArray=='yes')
			elif bufArray[0].isdigit():
				self.values.append(float(bufArray))
			elif bufArray[0]=='"':
				self.values.append(bufArray[1:-1])
			else:
				raise Exception('What kind of value is "'+bufArray+'"?')
				
	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Value Type: '+self.valueType)
		for v in self.values:
			if isinstance(v,ParenFileValue):
				ret.append(v.__repr__(indent+'\t'))
			else:
				ret.append(str(v))
		return ('\n'+indent).join(ret)
		
def parenFileDecode(data,idx=0):
	values=[]
	def pDec(data,idx=0):
		pval=ParenFileValue()
		ws=[' ','\t','\r','\n']
		if idx==0:
			while True:
				c=data[idx]
				idx+=1
				if c=='(':
					break
		building=[]
		while True:
			while True: # skip any whitespace
				c=data[idx]
				if c!=' ':
					break
				idx+=1
			while c not in ws and c!=')':
				building.append(c)
				c=data[idx]
				idx+=1
			pval.valueType=''.join(building)
			building=[]
			while True: # for each value
				pval._addValue(building)
				building=[]
				while True: # skip any whitespace
					c=data[idx]
					if c not in ws:
						break
					idx+=1
				if c==')': # finished
					pval._addValue(building)
					return idx+1,pval
				elif c=='(': # child value
					idx,v=pDec(data,idx+1)
					pval.values.append(v)
				elif c=='"': # parse a whole string
					building.append(c)
					while True:
						idx+=1
						c=data[idx]
						building.append(c)
						if c=='"':
							break
					pval._addValue(building)
					building=[]
					idx+=1
				else:
					building.append(c)
					idx+=1
	while True:
		idx,pval=pDec(data,idx)
		values.append(pval)
	return idx,values

class GimpGtpToolPreset(BinIOBase):
	"""
	Pure python implementation of the gimp gtp tool preset format
	"""

	def __init__(self,filename):
		BinIOBase.__init__(self)
		self.filename=None
		self.values=[]
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

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		BinIOBase._decode_(self,data,idx)
		self._idx,values=parenFileDecode(data)
		self.values=values
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
		for v in self.values:
			ret.append(v.__repr__(indent+'\t'))
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
				g=GimpGtpToolPreset(arg)
	if printhelp:
		print 'Usage:'
		print '  gimpGtpToolPreset.py file.xcf [options]'
		print 'Options:'
		print '   -h, --help ............ this help screen'
		print '   --dump ................ dump info about this file'
		print '   --register ............ register this extension'