#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gtp tool preset format
"""


class ParenFileValue:
	"""
	A parentheses-based file format
	(possibly "scheme" language?)
	"""

	def __init__(self):
		self.name=None
		self.values=[]

	def _addValue(self,bufArray):
		if self.name is None: # first value is the name
			self.name=bufArray
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
		ret.append('Value Type: '+str(self.name))
		for v in self.values:
			if isinstance(v,ParenFileValue):
				ret.append(v.__repr__(indent+'\t'))
			else:
				ret.append(str(v))
		return ('\n'+indent).join(ret)

def parenFileDecode(data,index=0):
	"""
	Decode a parentheses-based file format
	(possibly "scheme" language?)
	"""
	values=[]
	maxIndex=len(data)
	def pDec(data,index=0):
		"""
		helper routine to parse a single value
		"""
		pval=ParenFileValue()
		ws=[' ','\t','\r','\n']
		if index==0:
			while index<maxIndex:
				c=data[index]
				index+=1
				if c=='(':
					break
		building=[]
		while index<maxIndex:
			while index<maxIndex: # skip any whitespace
				c=data[index]
				if c!=' ':
					break
				index+=1
			while c not in ws and c!=')':
				if index>=maxIndex:
					break
				building.append(c)
				c=data[index]
				index+=1
			pval.name=''.join(building)
			building=[]
			while index<maxIndex: # for each value
				pval._addValue(building)
				building=[]
				while index<maxIndex: # skip any whitespace
					c=data[index]
					if c not in ws:
						break
					index+=1
				if c==')': # finished
					pval._addValue(building)
					return index+1,pval
				if c=='(': # child value
					index,v=pDec(data,index+1)
					pval.values.append(v)
				elif c=='"': # parse a whole string
					building.append(c)
					while True:
						index+=1
						if index>=maxIndex:
							break
						c=data[index]
						building.append(c)
						if c=='"':
							break
					pval._addValue(building)
					building=[]
					index+=1
				else:
					building.append(c)
					index+=1
		return index,pval
	while index<maxIndex:
		index,pval=pDec(data,index)
		values.append(pval)
	return index,values

def parenFileEncode(values):
	"""
	encode a values tree to a buffer
	"""
	ret=[]
	ret.append('# GIMP tool preset file')
	ret.append('')
	for val in values:
		if val.name is not None:
			ret.append(str(val))
	ret.append('')
	ret.append('# end of GIMP tool preset file')
	ret.append('')
	return '\n'.join(ret)


class GimpGtpToolPreset:
	"""
	Pure python implementation of the gimp gtp tool preset format
	"""

	def __init__(self,filename=None):
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

	def _decode_(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		index,self.values=parenFileDecode(data,index)
		return index

	def toBytes(self):
		"""
		encode to a byte array
		"""
		return parenFileEncode(self.values).encode('utf-8')

	def save(self,toFilename=None,toExtension=None):
		"""
		save this gimp tool preset to a file
		"""
		asImage=False
		if toExtension is None:
			if toFilename is not None:
				toExtension=toFilename.rsplit('.',1)
				if len(toExtension)>1:
					toExtension=toExtension[-1]
				else:
					toExtension=None
		if not hasattr(toFilename,'write'):
			f=open(toFilename,'wb')
		f.write(self.toBytes())

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
					print(g)
				else:
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				g=GimpGtpToolPreset(arg)
	if printhelp:
		print('Usage:')
		print('  gimpGtpToolPreset.py file.xcf [options]')
		print('Options:')
		print('   -h, --help ............ this help screen')
		print('   --dump ................ dump info about this file')
		print('   --register ............ register this extension')
