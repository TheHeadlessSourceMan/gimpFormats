#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A specialized binary file base for Gimp files
"""
import struct
from binaryIO import *
from gimpParasites import *


class GimpIOBase(object):
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
	PROP_NUM_PROPS          = 40

	def __init__(self,parent):
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
	def _pointerDecode_(self,io):
		if self._POINTER_SIZE_==64:
			return io.u64
		return io.u32
	def _pointerEncode_(self,ptr,io=None):
		if type(ptr) is not int:
			raise Exception('pointer is wrong type = '+str(type(ptr)))
		if io is None:
			io=IO()
		if self._POINTER_SIZE_==64:
			io.u64=ptr
		else:
			io.u32=ptr
		return io.data

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

	def _parasitesDecode_(self,data):
		"""
		decode list of parasites
		"""
		index=0
		while index<len(data):
			p=GimpParasite()
			index=p.fromBytes(data,index)
			self.parasites.append(p)
		return index
		
	def _parasitesEncode_(self):
		"""
		encode list of parasites
		"""
		io=IO()
		for parasite in self.parasites:
			io.addBytes(parasite.toBytes())
		return io.data

	def _guidelinesDecode_(self,data):
		"""
		decode guidelines
		"""
		index=0
		while index<len(data):
			position=struct.unpack('>I',data[index:index+4])[0]; index+=4
			isVertical=struct.unpack('>B',data[index])[0]==2; index+=1
			self.guidelines.append((isVertical,position))

	def _itemPathDecode_(self,data):
		"""
		decode item path
		"""
		index=0
		path=[]
		while index<len(data):
			p=struct.unpack('>I',data[index:index+4])[0]; index+=4
			path.append(p)
		self.itemPath=path

	def _vectorsDecode_(self,data):
		"""
		decode vectors
		"""
		index=0
		self.vectorsVersion=struct.unpack('>I',data[index:index+4])[0]; index+=4
		self.activeVectorIndex=struct.unpack('>I',data[index:index+4])[0]; index+=4
		numPaths=struct.unpack('>I',data[index:index+4])[0]; index+=4
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
		index=4
		colors=[]
		while index<len(data):
			r=struct.unpack('>B',data[index])[0]; index+=1
			g=struct.unpack('>B',data[index])[0]; index+=1
			b=struct.unpack('>B',data[index])[0]; index+=1
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
		index=0
		samplePoints=[]
		while index<len(data):
			x=struct.unpack('>I',data[index:index+4])[0]; index+=4
			y=struct.unpack('>I',data[index:index+4])[0]; index+=4
			samplePoints.append((x,y))
		self.samplePoints=samplePoints

	def _propertyDecode_(self,propertyType,data):
		"""
		decode a single property
		"""
		io=IO(data,boolSize=32)
		#print 'DECODING PROPERTY',propertyType,len(data)
		if propertyType==self.PROP_COLORMAP:
			self._colormapDecode_(io)
		elif propertyType==self.PROP_ACTIVE_LAYER:
			self.selected=True
		elif propertyType==self.PROP_ACTIVE_CHANNEL:
			self.selected=True
		elif propertyType==self.PROP_SELECTION:
			self.isSelection=True
		elif propertyType==self.PROP_FLOATING_SELECTION:
			self.selectionAttachedTo=io.u32
		elif propertyType==self.PROP_OPACITY:
			self.opacity=io.u32
		elif propertyType==self.PROP_MODE:
			self.blendMode=io.u32
		elif propertyType==self.PROP_VISIBLE:
			self.visible=True
		elif propertyType==self.PROP_LINKED:
			self.isLinked=io.bool
		elif propertyType==self.PROP_LOCK_ALPHA:
			self.lockAlpha=io.bool
		elif propertyType==self.PROP_APPLY_MASK:
			self.applyMask=io.bool
		elif propertyType==self.PROP_EDIT_MASK:
			self.editingMask=io.bool
		elif propertyType==self.PROP_SHOW_MASK:
			self.showMask=io.bool
		elif propertyType==self.PROP_SHOW_MASKED:
			self.showMasked=io.bool
		elif propertyType==self.PROP_OFFSETS:
			self.xOffset=io.i32
			self.yOffset=io.i32
		elif propertyType==self.PROP_COLOR:
			r=io.byte
			g=io.byte
			b=io.byte
			self.color=[r,g,b]
		elif propertyType==self.PROP_COMPRESSION:
			self.compression=io.byte
		elif propertyType==self.PROP_GUIDES:
			self._guidelinesDecode_(self,data)
		elif propertyType==self.PROP_RESOLUTION:
			self.horizontalResolution=io.float32
			self.verticalResolution=io.float32
		elif propertyType==self.PROP_TATTOO:
			self.uniqueId=data.encode('hex')
		elif propertyType==self.PROP_PARASITES:
			self._parasitesDecode_(data)
		elif propertyType==self.PROP_UNIT:
			self.units=io.u32
		elif propertyType==self.PROP_PATHS:
			numPaths=io.u32
			for _ in range(numPaths):
				nRead,path=self._pathDecode_(data[index:])
				self.paths.append(path)
				index+=nRead
		elif propertyType==self.PROP_USER_UNIT:
			self._userUnitsDecode_(data)
		elif propertyType==self.PROP_VECTORS:
			self._vectorsDecode_(data)
		elif propertyType==self.PROP_TEXT_LAYER_FLAGS:
			self.textLayerFlags=int(data)
		elif propertyType==self.PROP_OLD_SAMPLE_POINTS:
			raise Exception("ERR: old sample points structure not supported")
		elif propertyType==self.PROP_LOCK_CONTENT:
			self.locked=io.bool
		elif propertyType==self.PROP_GROUP_ITEM:
			self.isGroup=True
		elif propertyType==self.PROP_ITEM_PATH:
			self._itemPathDecode_(data)
		elif propertyType==self.PROP_GROUP_ITEM_FLAGS:
			self.groupItemFlags=io.u32
		elif propertyType==self.PROP_LOCK_POSITION:
			self.positionLocked=io.bool
		elif propertyType==self.PROP_FLOAT_OPACITY:
			self.opacity=io.float32
		elif propertyType==self.PROP_COLOR_TAG:
			self.colorTag=io.u32
		elif propertyType==self.PROP_COMPOSITE_MODE:
			self.compositeMode=io.i32
		elif propertyType==self.PROP_COMPOSITE_SPACE:
			self.compositeSpace=io.i32
		elif propertyType==self.PROP_BLEND_SPACE:
			self.blendSpace=io.u32
		elif propertyType==self.PROP_FLOAT_COLOR:
			r=io.float32
			g=io.float32
			b=io.float32
			self.color=[r,g,b]
		elif propertyType==self.PROP_SAMPLE_POINTS:
			self._samplePointsDecode_(data)
		else:
			raise Exception('Unknown property id '+str(propertyType))
		return io.index
		
	def _propertyEncode_(self,propertyType):
		"""
		encode a single property
		
		If the property is the same as the default, or not specified, returns empty array
		"""
		io=IO(boolSize=32)
		if propertyType==self.PROP_COLORMAP:
			if self.colorMap is not None and self.colorMap:
				io.u32=self.PROP_COLORMAP
				io.addBytes(self._colormapEncode_())
		elif propertyType==self.PROP_ACTIVE_LAYER:
			if self.selected is not None and self.selected:
				io.u32=self.PROP_ACTIVE_LAYER
		elif propertyType==self.PROP_ACTIVE_CHANNEL:
			if self.selected is not None and self.selected:
				io.u32=self.PROP_ACTIVE_LAYER
		elif propertyType==self.PROP_SELECTION:
			if self.isSelection is not None and self.isSelection:
				io.u32=self.PROP_SELECTION
		elif propertyType==self.PROP_FLOATING_SELECTION:
			if self.selectionAttachedTo is not None:
				io.u32=self.PROP_FLOATING_SELECTION
				io.u32=self.selectionAttachedTo
		elif propertyType==self.PROP_OPACITY:
			if self.opacity is not None and type(self.opacity)!=float:
				io.u32=self.PROP_OPACITY
				io.u32=self.opacity
		elif propertyType==self.PROP_MODE:
			if self.blendMode is not None:
				io.u32=self.PROP_MODE
				io.u32=self.blendMode
		elif propertyType==self.PROP_VISIBLE:
			if self.visible is not None and self.visible:
				io.u32=self.PROP_VISIBLE
		elif propertyType==self.PROP_LINKED:
			if self.isLinked is not None and self.isLinked:
				io.u32=self.PROP_LINKED
				io.bool=self.isLinked
		elif propertyType==self.PROP_LOCK_ALPHA:
			if self.lockAlpha is not None and self.lockAlpha:
				io.u32=self.PROP_LOCK_ALPHA
				io.bool=self.lockAlpha
		elif propertyType==self.PROP_APPLY_MASK:
			if self.applyMask is not None:
				io.u32=self.PROP_APPLY_MASK
				io.bool=self.applyMask
		elif propertyType==self.PROP_EDIT_MASK:
			if self.editingMask is not None and self.editingMask:
				io.u32=self.PROP_EDIT_MASK
				io.bool=self.editingMask
		elif propertyType==self.PROP_SHOW_MASK:
			if self.showMask is not None and self.showMask:
				io.u32=self.PROP_SHOW_MASK
				io.bool=self.showMask
		elif propertyType==self.PROP_SHOW_MASKED:
			if self.showMasked is not None:
				io.u32=self.PROP_SHOW_MASKED
				io.bool=self.showMasked
		elif propertyType==self.PROP_OFFSETS:
			if self.xOffset is not None and self.yOffset is not None:
				io.u32=self.PROP_OFFSETS
				io.i32=self.xOffset
				io.i32=self.yOffset
		elif propertyType==self.PROP_COLOR:
			if self.color is not None and type(self.color[0])!=float and type(self.color[1])!=float and type(self.color[2])!=float:
				io.u32=self.PROP_COLOR
				io.byte=self.color[0]
				io.byte=self.color[1]
				io.byte=self.color[2]
		elif propertyType==self.PROP_COMPRESSION:
			if self.compression is not None:
				io.u32=self.PROP_COMPRESSION
				io.u32=self.compression
		elif propertyType==self.PROP_GUIDES:
			if self.guidelines is not None and self.guidelines:
				io.u32=self.PROP_GUIDES
				io.addBytes(self._guidelinesEncode_())
		elif propertyType==self.PROP_RESOLUTION:
			if self.horizontalResolution is not None and self.verticalResolution is not None:
				io.u32=self.PROP_RESOLUTION
				io.u32=self.horizontalResolution
				io.i32=self.verticalResolution
		elif propertyType==self.PROP_TATTOO:
			if self.uniqueId is not None:
				io.u32=int(self.uniqueId,16)
		elif propertyType==self.PROP_PARASITES:
			if self.parasites is not None and self.parasites:
				io.u32=self.PROP_PARASITES
				io.addBytes(self._parasitesEncode_())
		elif propertyType==self.PROP_UNIT:
			if self.units is not None:
				io.u32=self.PROP_UNIT
				io.u32=self.units
		elif propertyType==self.PROP_PATHS:
			if self.paths is not None and self.paths:
				io.u32=self.PROP_PATHS
				io.u32=len(self.paths)
				for path in self.paths:
					io.append(self._pathEncode_(path))
		elif propertyType==self.PROP_USER_UNIT:
			if self.userUnits is not None:
				io.u32=self.PROP_USER_UNIT
				io.addBytes(self._userUnitsEncode_())
		elif propertyType==self.PROP_VECTORS:
			if self.vectors is not None and self.vectors:
				io.u32=self.PROP_VECTORS
				io.addBytes(self._vectorsEncode_())
		elif propertyType==self.PROP_TEXT_LAYER_FLAGS:
			if self.textLayerFlags is not None:
				io.u32=self.PROP_TEXT_LAYER_FLAGS
				io.u32=self.textLayerFlags
		elif propertyType==self.PROP_OLD_SAMPLE_POINTS:
			pass
		elif propertyType==self.PROP_LOCK_CONTENT:
			if self.locked is not None and self.locked:
				io.u32=self.PROP_LOCK_CONTENT
				io.bool=self.locked
		elif propertyType==self.PROP_GROUP_ITEM:
			if self.isGroup is not None and self.isGroup:
				io.u32=self.PROP_GROUP_ITEM
		elif propertyType==self.PROP_ITEM_PATH:
			if self.itemPath is not None:
				io.u32=self.PROP_ITEM_PATH
				io.addBytes(self._itemPathEncode_())
		elif propertyType==self.PROP_GROUP_ITEM_FLAGS:
			if self.groupItemFlags is not None:
				io.u32=self.PROP_GROUP_ITEM_FLAGS
				io.u32=self.groupItemFlags
		elif propertyType==self.PROP_LOCK_POSITION:
			if self.positionLocked is not None and self.positionLocked:
				io.u32=self.PROP_LOCK_POSITION
				io.bool=self.positionLocked
		elif propertyType==self.PROP_FLOAT_OPACITY:
			if self.opacity is not None and type(self.opacity)==float:
				io.u32=self.PROP_FLOAT_OPACITY
				io.float32=self.opacity
		elif propertyType==self.PROP_COLOR_TAG:
			if self.colorTag is not None:
				io.u32=self.PROP_COLOR_TAG
				io.u32=self.colorTag
		elif propertyType==self.PROP_COMPOSITE_MODE:
			if self.compositeMode is not None:
				io.u32=self.PROP_COMPOSITE_MODE
				io.i32=self.compositeMode
		elif propertyType==self.PROP_COMPOSITE_SPACE:
			if self.compositeSpace is not None:
				io.u32=self.PROP_COMPOSITE_SPACE
				io.i32=self.compositeSpace
		elif propertyType==self.PROP_BLEND_SPACE:
			if self.blendSpace is not None:
				io.u32=self.PROP_BLEND_SPACE
				io.u32=self.blendSpace
		elif propertyType==self.PROP_FLOAT_COLOR:
			if self.color is not None and (type(self.color[0])==float or type(self.color[1])==float or type(self.color[2])==float):
				io.u32=self.PROP_FLOAT_COLOR
				io.float32=self.color[0]
				io.float32=self.color[1]
				io.float32=self.color[2]
		elif propertyType==self.PROP_SAMPLE_POINTS:
			if self.samplePoints is not None and self.samplePoints:
				io.u32=self.PROP_SAMPLE_POINTS
				self.addBytes(self._samplePointsEncode_())
		else:
			raise Exception('Unknown property id '+str(propertyType))
		return io.data

	def _propertiesDecode_(self,io):
		"""
		decode a list of properties
		"""
		while True:
			try:
				propertyType=io.u32
				dataLength=io.u32
			except struct.error: # end of data, so that's that.
				break
			if propertyType==0:
				break
			self._propertyDecode_(propertyType,io.getBytes(dataLength))
		return io.index
	def _propertiesEncode_(self):
		"""
		encode a list of properties
		"""
		io=IO()
		for propertyType in range(1,self.PROP_NUM_PROPS):
			moData=self._propertyEncode_(propertyType)
			if moData:
				io.addBytes(moData)
		return io.data

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
		
		
class GimpUserUnits(object):
	"""
	user-defined measurement units
	"""

	def __init__(self):
		self.factor=0
		self.numDigits=0
		self.id=''
		self.symbol=''
		self.abbrev=''
		self.sname=''
		self.pname=''

	def fromBytes(self,data,index=0):
		"""
		decode a byte buffer

		:param data: data buffer to decode
		:param index: index within the buffer to start at
		"""
		io=IO(data,index)
		self.factor=io.float32
		self.numDigits=io.u32
		self.id=io.sz754
		self.symbol=io.sz754
		self.abbrev=io.sz754
		self.sname=io.sz754
		self.pname=io.sz754
		return io.index
		
	def toBytes(self):
		"""
		convert this object to raw bytes
		"""
		io=IO()
		io.float32=self.factor
		io.u32=self.numDigits
		io.sz754=self.id
		io.sz754=self.symbol
		io.sz754=self.abbrev
		io.sz754=self.sname
		io.sz754=self.pname
		return io.data

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