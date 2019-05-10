#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A specialized binary file base for Gimp files
"""
import struct
from binaryIO import *
from gimpParasites import *


class GimpIOBase(BinIOBase):
	"""
	A specialized binary file base for Gimp files
	"""
	COLOR_MODES=['RGB','Grayscale','Indexed']
	UNITS=['Inches','Millimeters','Points','Picas']
	UNITS_TO_MM=[25.4,1,127/360.0,127/30.0]
	COMPOSITE_MODES=['Union','Clip to backdrop','Clip to layer','Intersection']
	COMPOSITE_SPACES=['RGB (linear)','RGB (perceptual)','LAB']
	TAG_COLORS=['None','Blue','Green','Yellow','Orange','Brown','Red','Violet','Gray']
	COMPRESSION_MODES=['None','RLE','Zlib','Fractal']

	BLEND_MODES=[
		'Normal (legacy)',
		'Dissolve (legacy)',
		'Behind (legacy)',
		'Multiply (legacy)',
		'Screen (legacy)',
		'Old broken Overlay',
		'Difference (legacy)',
		'Addition (legacy)',
		'Subtract (legacy)',
		'Darken only (legacy)',
		'Lighten only (legacy)',
		'Hue (HSV) (legacy)',
		'Saturation (HSV) (legacy)',
		'Color (HSL) (legacy)',
		'Value (HSV) (legacy)',
		'Divide (legacy)',
		'Dodge (legacy)',
		'Burn (legacy)',
		'Hard Light (legacy)',
		'Soft light (legacy)',
		'Grain extract (legacy)',
		'Grain merge (legacy)',
		'Color erase (legacy)',
		'Overlay',
		'Hue (LCH)',
		'Chroma (LCH)',
		'Color (LCH)',
		'Lightness (LCH)',
		'Normal',
		'Behind',
		'Multiply',
		'Screen',
		'Difference',
		'Addition',
		'Substract',
		'Darken only',
		'Lighten only',
		'Hue (HSV)',
		'Saturation (HSV)',
		'Color (HSL)',
		'Value (HSV)',
		'Divide',
		'Dodge',
		'Burn',
		'Hard light',
		'Soft light',
		'Grain extract',
		'Grain merge',
		'Vivid light',
		'Pin light',
		'Linear light',
		'Hard mix',
		'Exclusion',
		'Linear burn',
		'Luma/Luminance darken only',
		'Luma/Luminance lighten only',
		'Luminance',
		'Color erase',
		'Erase',
		'Merge',
		'Split',
		'Pass through']


	PROP_END                =  0
	PROP_COLORMAP           =  1
	PROP_ACTIVE_LAYER       =  2
	PROP_ACTIVE_CHANNEL     =  3
	PROP_SELECTION          =  4
	PROP_FLOATING_SELECTION =  5
	PROP_OPACITY            =  6
	PROP_MODE               =  7
	PROP_VISIBLE            =  8
	PROP_LINKED             =  9
	PROP_LOCK_ALPHA         = 10
	PROP_APPLY_MASK         = 11
	PROP_EDIT_MASK          = 12
	PROP_SHOW_MASK          = 13
	PROP_SHOW_MASKED        = 14
	PROP_OFFSETS            = 15
	PROP_COLOR              = 16
	PROP_COMPRESSION        = 17
	PROP_GUIDES             = 18
	PROP_RESOLUTION         = 19
	PROP_TATTOO             = 20
	PROP_PARASITES          = 21
	PROP_UNIT               = 22
	PROP_PATHS              = 23
	PROP_USER_UNIT          = 24
	PROP_VECTORS            = 25
	PROP_TEXT_LAYER_FLAGS   = 26
	PROP_OLD_SAMPLE_POINTS  = 27
	PROP_LOCK_CONTENT       = 28
	PROP_GROUP_ITEM         = 29
	PROP_ITEM_PATH          = 30
	PROP_GROUP_ITEM_FLAGS   = 31
	PROP_LOCK_POSITION      = 32
	PROP_FLOAT_OPACITY      = 33
	PROP_COLOR_TAG          = 34
	PROP_COMPOSITE_MODE     = 35
	PROP_COMPOSITE_SPACE    = 36
	PROP_BLEND_SPACE        = 37
	PROP_FLOAT_COLOR        = 38
	PROP_SAMPLE_POINTS      = 39

	def __init__(self,parent):
		BinIOBase.__init__(self)
		self.parent=parent
		self.parasites=[]
		self.guidelines=[]
		self.itemPath=None
		self.vectors=[]
		self.colorMap=[]
		self.userUnits=None
		self.samplePoints=[]
		self.selected=False
		self.isSelection=False
		self.selectionAttachedTo=None
		self.blendMode=None # one of self.BLEND_MODES
		self.visible=None
		self.isLinked=None
		self.lockAlpha=None
		self.applyMask=None
		self.editingMask=None
		self.showMask=None
		self.showMasked=None
		self.xOffset=None
		self.yOffset=None
		self.compression=None # one of self.COMPRESSION_MODES
		self.horizontalResolution=None
		self.verticalResolution=None
		self.uniqueId=None
		self.units=None # one of self.UNITS
		self.textLayerFlags=None
		self.locked=None
		self.isGroup=None
		self.groupItemFlags=None
		self.positionLocked=None
		self.opacity=None
		self.colorTag=None # one of self.TAG_COLORS
		self.compositeMode=None # one of self.COMPOSITE_MODES
		self.compositeSpace=None # one of self.COMPOSITE_SPACES
		self.blendSpace=None
		self.color=None
		self.vectorsVersion=0
		self.activeVectorIndex=0
		self.paths=[]

	@property
	def _POINTER_SIZE_(self):
		"""
		Determine the size of the "pointer" datatype
		based on the document version

		NOTE: prior to version 11, it was 32-bit,
			since then it is 64-bit, thus supporting
			larger image files
		"""
		if self.doc.version>=11:
			return 64
		return 32

	@property
	def doc(self):
		"""
		Get the main document object
		"""
		item=self
		while item.parent!=item:
			item=item.parent
		return item
	@property
	def root(self):
		"""
		Get the root of the file object tree
		(Which is the same as self.doc)
		"""
		return self.doc

	@property
	def tattoo(self):
		"""
		This is the gimp nomenclature for the item's unique id
		"""
		return self.uniqueId
	@tattoo.setter
	def tattoo(self,tattoo):
		"""
		This is the gimp nomenclature for the item's unique id
		"""
		self.uniqueId=tattoo

	def _pointer_(self,data=None):
		"""
		decode a "pointer" in the file

		:param data: if specified, extract a pointer from this data
			otherwhise extract from current data and increment index
		"""
		if data is None:
			if self._POINTER_SIZE_==32:
				d=struct.unpack('>I',self._data[self._idx:self._idx+4])[0]
				self._idx+=4
			else:
				d=struct.unpack('>Q',self._data[self._idx:self._idx+8])[0]
				self._idx+=8
		else:
			if self._POINTER_SIZE_==32:
				d=struct.unpack('>I',data[self._idx:self._idx+4])[0]
			else:
				d=struct.unpack('>Q',data[self._idx:self._idx+8])[0]
		if d>len(self.root._data):
			raise IndexError('Pointer '+str(d)+' is larger than file size '+str(len(self.root._data)))
		return d

	def _parasitesDecode_(self,data):
		"""
		decode list of parasites
		"""
		idx=0
		while idx<len(data):
			p=GimpParasite()
			idx=p._decode_(data,idx)
			self.parasites.append(p)
		return idx

	def _guidelinesDecode_(self,data):
		"""
		decode guidelines
		"""
		idx=0
		while idx<len(data):
			position=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
			isVertical=struct.unpack('>B',data[idx])[0]==2; idx+=1
			self.guidelines.append((isVertical,position))

	def _itemPathDecode_(self,data):
		"""
		decode item path
		"""
		idx=0
		path=[]
		while idx<len(data):
			p=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
			path.append(p)
		self.itemPath=path

	def _vectorsDecode_(self,data):
		"""
		decode vectors
		"""
		idx=0
		self.vectorsVersion=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
		self.activeVectorIndex=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
		numPaths=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
		for _ in range(numPaths):
			gv=GimpVector(self)
			gv._decode_(data)
			self.vectors.append(gv)

	@property
	def activeVector(self):
		"""
		get the vector that is currently active
		"""
		return self.vectors[self.activeVectorIndex]

	@property
	def expanded(self):
		"""
		is the group layer expanded
		"""
		return self.groupItemFlags&0x00000001>0
	@expanded.setter
	def expanded(self,expanded):
		"""
		is the group layer expanded
		"""
		if expanded:
			self.groupItemFlags|=0x00000001
		else:
			self.groupItemFlags&=(~0x00000001)

	def _colormapDecode_(self,data):
		"""
		decode colormap/palette
		"""
		_=struct.unpack('>I',data[0:4])[0] # number of colors
		idx=4
		colors=[]
		while idx<len(data):
			r=struct.unpack('>B',data[idx])[0]; idx+=1
			g=struct.unpack('>B',data[idx])[0]; idx+=1
			b=struct.unpack('>B',data[idx])[0]; idx+=1
			colors.append((r,g,b))
		self.colorMap=colors

	def _userUnitsDecode_(self,data):
		"""
		decode a set of user-defined measurement units
		"""
		u=GimpUserUnits()
		u._decode_(data)
		self.userUnits=u

	def _samplePointsDecode_(self,data):
		"""
		decode a series of points
		"""
		idx=0
		samplePoints=[]
		while idx<len(data):
			x=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
			y=struct.unpack('>I',data[idx:idx+4])[0]; idx+=4
			samplePoints.append((x,y))
		self.samplePoints=samplePoints

	def _propertyDecode_(self,propertyType,data):
		"""
		decode a single property
		"""
		#print 'DECODING PROPERTY',propertyType,len(data)
		if propertyType==self.PROP_COLORMAP:
			self._colormapDecode_(data)
		elif propertyType==self.PROP_ACTIVE_LAYER:
			self.selected=True
		elif propertyType==self.PROP_ACTIVE_CHANNEL:
			self.selected=True
		elif propertyType==self.PROP_SELECTION:
			self.isSelection=True
		elif propertyType==self.PROP_FLOATING_SELECTION:
			self.selectionAttachedTo=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_OPACITY:
			self.opacity=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_MODE:
			self.blendMode=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_VISIBLE:
			self.visible=True
		elif propertyType==self.PROP_LINKED:
			self.isLinked=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_LOCK_ALPHA:
			self.lockAlpha=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_APPLY_MASK:
			self.applyMask=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_EDIT_MASK:
			self.editingMask=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_SHOW_MASK:
			self.showMask=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_SHOW_MASKED:
			self.showMasked=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_OFFSETS:
			self.xOffset=struct.unpack('>i',data[0:4])[0]
			self.yOffset=struct.unpack('>i',data[4:8])[0]
		elif propertyType==self.PROP_COLOR:
			r=struct.unpack('>B',data[0])[0]
			g=struct.unpack('>B',data[1])[0]
			b=struct.unpack('>B',data[2])[0]
			self.color=[r,g,b]
		elif propertyType==self.PROP_COMPRESSION:
			self.compression=struct.unpack('>B',data[0])[0]
		elif propertyType==self.PROP_GUIDES:
			self._guidelinesDecode_(self,data)
		elif propertyType==self.PROP_RESOLUTION:
			self.horizontalResolution=struct.unpack('>f',data[0:4])[0]
			self.verticalResolution=struct.unpack('>f',data[4:8])[0]
		elif propertyType==self.PROP_TATTOO:
			self.uniqueId=data.encode('hex')
		elif propertyType==self.PROP_PARASITES:
			self._parasitesDecode_(data)
		elif propertyType==self.PROP_UNIT:
			self.units=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_PATHS:
			numPaths=struct.unpack('>I',data[0:4])[0]; idx=4
			for _ in range(numPaths):
				nRead,path=self._pathDecode_(data[idx:])
				self.paths.append(path)
				idx+=nRead
		elif propertyType==self.PROP_USER_UNIT:
			self._userUnitsDecode_(data)
		elif propertyType==self.PROP_VECTORS:
			self._vectorsDecode_(data)
		elif propertyType==self.PROP_TEXT_LAYER_FLAGS:
			self.textLayerFlags=int(data)
		elif propertyType==self.PROP_OLD_SAMPLE_POINTS:
			raise Exception("ERR: old sample points structure not supported")
		elif propertyType==self.PROP_LOCK_CONTENT:
			self.locked=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_GROUP_ITEM:
			self.isGroup=True
		elif propertyType==self.PROP_ITEM_PATH:
			self._itemPathDecode_(data)
		elif propertyType==self.PROP_GROUP_ITEM_FLAGS:
			self.groupItemFlags=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_LOCK_POSITION:
			self.positionLocked=struct.unpack('>I',data[0:4])[0]==1
		elif propertyType==self.PROP_FLOAT_OPACITY:
			self.opacity=struct.unpack('>f',data[0:4])[0]
		elif propertyType==self.PROP_COLOR_TAG:
			self.colorTag=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_COMPOSITE_MODE:
			self.compositeMode=struct.unpack('>i',data[0:4])[0]
		elif propertyType==self.PROP_COMPOSITE_SPACE:
			self.compositeSpace=struct.unpack('>i',data[0:4])[0]
		elif propertyType==self.PROP_BLEND_SPACE:
			self.blendSpace=struct.unpack('>I',data[0:4])[0]
		elif propertyType==self.PROP_FLOAT_COLOR:
			r=struct.unpack('>f',data[0:4])[0]
			g=struct.unpack('>f',data[4:8])[0]
			b=struct.unpack('>f',data[8:12])[0]
			self.color=[r,g,b]
		elif propertyType==self.PROP_SAMPLE_POINTS:
			self._samplePointsDecode_(data)
		else:
			raise Exception('Unknown property id '+str(propertyType))
		return self._idx

	def _propertiesDecode_(self):
		"""
		decode a list of properties
		"""
		while True:
			try:
				propertyType=self._u32_()
				dataLength=self._u32_()
			except struct.error: # end of data, so that's that.
				break
			if propertyType==0:
				break
			self._propertyDecode_(propertyType,self._bytes_(dataLength))
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		if self.itemPath is not None:
			ret.append('Item Path: '+str(self.itemPath))
		if self.selected is not None:
			ret.append('Selected: '+str(self.selected))
		if self.isSelection is not None:
			ret.append('is Selection: '+str(self.isSelection))
		if self.selectionAttachedTo is not None:
			ret.append('Selection Attached To: '+str(self.selectionAttachedTo))
		if self.blendMode is not None:
			ret.append('Blend Mode: '+self.BLEND_MODES[self.blendMode])
		if self.visible is not None:
			ret.append('Visible: '+str(self.visible))
		if self.isLinked is not None:
			ret.append('Linked: '+str(self.isLinked))
		if self.lockAlpha is not None:
			ret.append('Alpha Locked: '+str(self.lockAlpha))
		if self.applyMask is not None:
			ret.append('Apply Mask: '+str(self.applyMask))
		if self.editingMask is not None:
			ret.append('Editing Mask: '+str(self.editingMask))
		if self.showMask is not None:
			ret.append('Show Mask: '+str(self.showMask))
		if self.showMasked is not None:
			ret.append('Show Masked: '+str(self.showMasked))
		if self.xOffset is not None:
			ret.append('Offset: '+str(self.xOffset)+' x '+str(self.yOffset))
		if self.compression is not None:
			ret.append('Compression: '+self.COMPRESSION_MODES[self.compression])
		if self.horizontalResolution is not None:
			res=str(self.horizontalResolution)+'ppi x '+str(self.verticalResolution)+'ppi'
			ret.append('Resolution: '+res)
		if self.uniqueId is not None:
			ret.append('Unique ID (tattoo): '+str(self.uniqueId))
		if self.units is not None:
			ret.append('Units: '+self.UNITS[self.units])
		if self.textLayerFlags is not None:
			ret.append('Text Layer Flags: '+str(self.textLayerFlags))
		if self.locked is not None:
			ret.append('Locked: '+str(self.locked))
		if self.isGroup is not None:
			ret.append('Is Group: '+str(self.isGroup))
		if self.groupItemFlags is not None:
			ret.append('Group Items Flag: '+str(self.groupItemFlags))
		if self.positionLocked is not None:
			ret.append('Position Locked: '+str(self.positionLocked))
		if self.opacity is not None:
			ret.append('Opacity: '+str(self.opacity))
		if self.colorTag is not None:
			ret.append('Tag Color: '+self.TAG_COLORS[self.colorTag])
		if self.compositeMode is not None:
			auto=('Auto ' if self.compositeMode<0 else '') # negative values are "Auto"
			ret.append('Composite Mode: '+auto+self.COMPOSITE_MODES[abs(self.compositeMode)])
		if self.compositeSpace is not None:
			auto=('Auto ' if self.compositeSpace<0 else '') # negative values are "Auto"
			ret.append('Composite Space: '+auto+self.COMPOSITE_SPACES[abs(self.compositeSpace)])
		if self.blendSpace is not None:
			ret.append('Blend Space: '+str(self.blendSpace))
		if self.color is not None:
			ret.append('Color: ('+str(self.color[0])+','+str(self.color[1])+','+str(self.color[2])+')')
		if self.userUnits is not None:
			ret.append('User Units: ')
			ret.append(self.userUnits.__repr__(indent+'\t'))
		if self.parasites:
			ret.append('Parasites: ')
			for item in self.parasites:
				ret.append(item.__repr__(indent+'\t'))
		if self.guidelines:
			ret.append('Guidelines: ')
			for item in self.guidelines:
				ret.append(item.__repr__(indent+'\t'))
		if self.samplePoints:
			ret.append('Sample Points: ')
			for item in self.samplePoints:
				ret.append('('+str(item[0])+','+str(item[1])+')')
		if self.vectors:
			ret.append('Vectors: ')
			for item in self.vectors:
				ret.append(item.__repr__(indent+'\t'))
		if self.colorMap:
			ret.append('Color Map: ')
			for i in range(len((self.colorMap))):
				color=self.colorMap[i]
				ret.append(i+': ('+str(color[0])+','+str(color[1])+','+str(color[2])+')')
		return indent+(('\n'+indent).join(ret))
		
		
class GimpUserUnits(BinIOBase):
	"""
	user-defined measurement units
	"""

	def __init__(self):
		BinIOBase.__init__(self)
		self.factor=0
		self.numDigits=0
		self.id=''
		self.symbol=''
		self.abbrev=''
		self.sname=''
		self.pname=''

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		self.factor=self._float_()
		self.numDigits=self._u32_()
		self.id=self._sz754_()
		self.symbol=self._sz754_()
		self.abbrev=self._sz754_()
		self.sname=self._sz754_()
		self.pname=self._sz754_()
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Factor: '+str(self.factor))
		ret.append('Num Digits: '+str(self.numDigits))
		ret.append('ID: '+str(self.id))
		ret.append('Symbol: '+str(self.symbol))
		ret.append('Abbreviation: '+str(self.abbrev))
		ret.append('Singular Name: '+str(self.sname))
		ret.append('Plural Name: '+str(self.pname))
		return indent+(('\n'+indent).join(ret))