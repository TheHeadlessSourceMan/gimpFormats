#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Gimp Image Pipe Format

The gih format is use to store a series of brushes, and some extra info 
for how to use them. 
"""
import struct
import PIL.Image
from binaryIO import *
from gimpGbrBrush import *
	

class GimpGihBrushSet(object):
	"""
	Gimp Image Pipe Format

	The gih format is use to store a series of brushes, and some extra info 
	for how to use them. 

	See:
		https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/gih.txt
	"""

	def __init__(self,filename):
		self.filename=None
		self.name=''
		self.params={}
		self.brushes=[]
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
		io=IO(data,index)
		name=io.textLine
		secondLine=io.textLine.split(' ')
		self.params={}
		numBrushes=int(secondLine[0])
		# everything that's left is a gimp-image-pipe-parameters parasite 
		for i in range(1,len(secondLine)): 
			param=secondLine[i].split(':',1)
			self.params[param[0].strip()]=param[1].strip()
		self.brushes=[]
		for i in numBrushes:
			b=GimpGbrBrush()
			io.index=b._decode_(io.data,io.index)
			self.brushes.append(b)
		return io.index
		
	def toBytes(self):
		"""
		encode this object to a byte array
		"""
		io=IO()
		io.textLine=name
		# add the second line of data
		secondLine=[str(len(self.brushes))]
		for k,v in self.params.items:
			secondLine.append(k+':'+str(v))
		io.textLine=' '.join(secondLine)
		# add the brushes
		self.brushes=[]
		for brush in brushes:
			io.addBytes(brush.toBytes())
		return io.data

	def save(self,toFilename=None,toExtension=None):
		"""
		save this gimp image to a file
		"""
		if not hasattr(toFilename,'write'):
			f=open(toFilename,'wb')
		f.write(self.toBytes())
		
	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		if self.filename is not None:
			ret.append('Filename: '+self.filename)
		ret.append('Name: '+str(self.name))
		for k,v in list(self.params.items()):
			ret.append(k+': '+str(v))
		for i in range(len(self.brushes)):
			ret.append('Brush '+str(i))
			ret.append(self.brushes[i].__repr__(indent+'\t'))
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
				elif arg[0]=='--show':
					if arg[1]=='*':
						for i in range(len(g.brushes)):
							g.brushes[i].image.show()
					else:
						g.brushes[int(arg[1])].image.show()
				elif arg[0]=='--save':
					index,filename=arg[1].split(',',1)
					if filename.find('*')<0:
						filename='*.'.join(filename.split('.',1))
					if index=='*':
						for i in range(len(g.brushes)):
							fn2=filename.replace('*',str(i))
							g.brushes[i].image.save(fn2)
					else:
						fn2=filename.replace('*',i)
						g.brushes[int(index)].image.save(fn2)
				else:
					print('ERR: unknown argument "'+arg[0]+'"')
			else:
				g=GimpGihBrushSet(arg)
	if printhelp:
		print('Usage:')
		print('  gimpGihBrushSet.py file.xcf [options]')
		print('Options:')
		print('   -h, --help ............ this help screen')
		print('   --dump ................ dump info about this file')
		print('   --show=n .............. show the brush image(s) n=* for all')
		print('   --save=n,out.jpg ...... save out the brush image(s)')
		print('   --register ............ register this extension')