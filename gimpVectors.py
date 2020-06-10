#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Stuff related to vectors/paths within a gimp document
"""
from typing import List
from gimpFormats.gimpIOBase import GimpIOBase
from gimpFormats.binaryIO import IO
from gimpFormats.gimpParasites import GimpParasite


class GimpVector(GimpIOBase):
    """
    A gimp brush stroke vector
    """

    def __init__(self,parent):
        GimpIOBase.__init__(self,parent)
        self.name:str=''
        self.uniqueId:int=0
        self.visible:bool=True
        self.linked:bool=False
        self.parasites:List[GimpParasite]=[]
        self.strokes:List[GimpStroke]=[]

    @property
    def svgPath(self)->str:
        """
        this vector converted to an svg path string
        """
        svg=[]
        for stroke in self.strokes:
            svg.append(stroke.svgPath)
        print('STROKES=%d %s'%(len(self.strokes),svg))
        return ' '.join(svg)
    @svgPath.setter
    def svgPath(self,svgPath:str):
        raise NotImplementedError()

    def fromBytes(self,data,index=0):
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index,boolSize=32)
        print(io.data[0:50])
        self.name=io.sz754
        self.uniqueId=io.u32
        self.visible=io.bool
        self.linked=io.bool
        numParasites=io.u32
        numStrokes=io.u32
        raise Exception('Parasites=%d Strokes=%d'%(numParasites,numStrokes))
        for _ in range(numParasites):
            p=GimpParasite()
            io.index=p.fromBytes(io.data,io.index)
            self.parasites.append(p)
        for _ in range(numStrokes):
            gs=GimpStroke(self)
            io.index=gs.fromBytes(io.data,io.index)
            self.strokes.append(p)
        return io.index

    def toBytes(self):
        """
        encode to binary data
        """
        io=IO(boolSize=32)
        io.sz754=self.name
        io.u32=self.uniqueId
        io.bool=self.visible
        io.bool=self.linked
        io.u32=len(self.parasites)
        io.u32=len(self.strokes)
        for p in self.parasites:
            io.addBytes(p.toBytes())
        for gs in self.strokes:
            io.addBytes(gs.toBytes())
        return io.data

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
        self.strokeType:int=1 # one of self.STROKE_TYPES
        self.closedShape:bool=True
        self.points:List[GimpPoint]=[]
        self.numFloatsPerPoint:int=1
        self.numPoints:int=0

    @property
    def svgPath(self)->str:
        """
        this vector converted to an svg path string
        """
        svg=[]
        for point in self.points:
            if not svg:
                # initial move
                svg.append('M%d %d'%(point.x,point.y))
            elif self.strokeType==0:
                # line
                svg.append('L%d %d'%(point.x,point.y))
            elif self.strokeType==1:
                # bezier
                if point.pointType==0:
                    # anchor point
                    svg.append('%d %d Q'%(point.x,point.y))
                else:
                    # control point
                    svg.append('%d %d,'%(point.x,point.y))
                    svg.append(point)
            else:
                raise Exception('Unknown stroke type')
            svg.append(stroke.svgPath)
        if self.closedShape:
            svg.append('Z')
        return ' '.join(svg)

    def fromBytes(self,data:bytes,index:int=0):
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index,boolSize=32)
        self.strokeType=io.u32
        self.closedShape=io.bool
        self.numFloatsPerPoint=io.u32
        self.numPoints=io.u32
        for _ in range(self.numPoints):
            gp=GimpPoint(self)
            io.index=gp.fromBytes(io.data,io.index,self.numFloatsPerPoint)
            self.points.append(gp)
        return io.index

    def toBytes(self):
        """
        encode to binary data
        """
        io=IO(boolSize=32)
        io.u32=self.strokeType
        io.bool=self.closedShape
        io.u32=self.numFloatsPerPoint
        io.u32=self.numPoints
        for gp in self.points:
            io.addBytes(gp.toBytes())
        return io.data

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
        self.x:int=0
        self.y:int=0
        self.pressure:float=1.0
        self.xTilt:float=0.5
        self.yTilt:float=0.5
        self.wheel:float=0.5
        self.pointType:int=0

    def fromBytes(self,data,index=0,numFloatsPerPoint=0):
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        :param numFloatsPerPoint: required so we know
            how many different brush dynamic measurements are
            inside each point
        """
        io=IO(data,index,boolSize=32)
        self.pressure=1.0
        self.xTilt=0.5
        self.yTilt=0.5
        self.wheel=0.5
        self.pointType=io.u32
        if numFloatsPerPoint<1:
            numFloatsPerPoint=(len(io.data)-io.index)/4
        self.x=io.float
        self.y=io.float
        if numFloatsPerPoint>2:
            self.pressure=io.float
            if numFloatsPerPoint>3:
                self.xTilt=io.float
                if numFloatsPerPoint>4:
                    self.yTilt=io.float
                    if numFloatsPerPoint>5:
                        self.wheel=io.float
        return io.index

    def toBytes(self):
        """
        encode to binary data
        """
        io=IO(boolSize=32)
        io.u32=self.pointType
        io.float=self.x
        io.float=self.y
        if self.pressure is not None:
            io.float=self.pressure
            if self.xTilt is not None:
                io.float=self.xTilt
                if self.yTilt is not None:
                    io.float=self.yTilt
                    if self.wheel is not None:
                        io.float=self.wheel
        return io.data

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