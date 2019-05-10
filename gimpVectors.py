#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Stuff related to vectors/paths within a gimp document
"""
from gimpIoBase import GimpIOBase


class GimpVector(GimpIOBase):
	"""
	A gimp brush stroke vector
	"""

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.name=''
		self.uniqueId=0
		self.visible=True
		self.linked=False
		self.parasites=[]
		self.strokes=[]

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		self.name=self._sz754_()
		self.uniqueId=self._u32_()
		self.visible=self._u32_()==1
		self.linked=self._u32_()==1
		numParasites=self._u32_()
		numStrokes=self._u32_()
		for _ in range(numParasites):
			p=GimpParasite()
			self._idx=p._decode_(self._data,self._idx)
			self.parasites.append(p)
		for _ in range(numStrokes):
			gs=GimpStroke(self)
			self._idx=gs._decode_(self._data,self._idx)
			self.strokes.append(p)
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Name: '+str(self.name))
		ret.append('Unique ID (tattoo): '+str(self.uniqueId))
		ret.append('Visible: '+str(self.visible))
		ret.append('Linked: '+str(self.linked))
		if self.parasites:
			ret.append('Parasites: ')
			for item in self.parasites:
				ret.append(item.__repr__(indent+'\t'))
		if self.strokes:
			ret.append('Strokes: ')
			for item in self.strokes:
				ret.append(item.__repr__(indent+'\t'))
		return indent+(('\n'+indent).join(ret))


class GimpStroke(GimpIOBase):
	"""
	A single stroke within a vector
	"""

	STROKE_TYPES=['None','Bezier']

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.strokeType=1 # one of self.STROKE_TYPES
		self.closedShape=True
		self.points=[]

	def _decode_(self,data,idx=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		"""
		GimpIOBase._decode_(self,data,idx)
		self.strokeType=self._u32_()
		self.closedShape=self._u32_()==1
		numFloatsPerPoint=self._u32_()
		numPoints=self._u32_()
		for _ in range(numPoints):
			gp=GimpPoint(self)
			self._idx=gp._decode_(self._data,self._idx,numFloatsPerPoint)
			self.points.append(gp)
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Stroke Type: '+self.STROKE_TYPES[self.strokeType])
		ret.append('Closed: '+str(self.closedShape))
		ret.append('Points: ')
		for point in self.points:
			ret.append(point.__repr__(indent+'\t'))
		return indent+(('\n'+indent).join(ret))


class GimpPoint(GimpIOBase):
	"""
	A single point within a stroke
	"""

	POINT_TYPES=['Anchor','Bezier control point']

	def __init__(self,parent):
		GimpIOBase.__init__(self,parent)
		self.x=0
		self.y=0
		self.pressure=1.0
		self.xTilt=0.5
		self.yTilt=0.5
		self.wheel=0.5
		self.pointType=0

	def _decode_(self,data,idx=0,numFloatsPerPoint=0):
		"""
		decode a byte buffer as a gimp file

		:param data: data buffer to decode
		:param idx: index within the buffer to start at
		:param numFloatsPerPoint: required so we know
			how many different brush dynamic measurements are
			inside each point
		"""
		self.pressure=1.0
		self.xTilt=0.5
		self.yTilt=0.5
		self.wheel=0.5
		GimpIOBase._decode_(self,data,idx)
		self.pointType=self._u32_()
		if numFloatsPerPoint<1:
			numFloatsPerPoint=(len(data)-self._idx)/4
		self.x=self._float_()
		self.y=self._float_()
		if numFloatsPerPoint>2:
			self.pressure=self._float_()
			if numFloatsPerPoint>3:
				self.xTilt=self._float_()
				if numFloatsPerPoint>4:
					self.yTilt=self._float_()
					if numFloatsPerPoint>5:
						self.wheel=self._float_()
		return self._idx

	def __repr__(self,indent=''):
		"""
		Get a textual representation of this object
		"""
		ret=[]
		ret.append('Location: ('+str(self.x)+','+str(self.y)+')')
		ret.append('Pressure: '+str(self.pressure))
		ret.append('Location: ('+str(self.xTilt)+','+str(self.yTilt)+')')
		ret.append('Wheel: '+str(self.wheel))
		return indent+(('\n'+indent).join(ret))