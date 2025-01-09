#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A specialized binary file base for Gimp files
"""
import typing
import struct
from gimpFormats.enums import (
    BLEND_MODES,COMPOSITE_MODES,COMPOSITE_SPACES,
    COMPRESSION_MODES, PROPS, TAG_COLORS, UNITS)
from gimpFormats.binaryIO import IO
from gimpFormats.gimpParasites import GimpParasite


class GimpIOBase:
    """
    A specialized binary file base for Gimp files
    """
    def __init__(self,parent:typing.Optional['GimpIOBase'])->None:
        self.parent:typing.Optional['GimpIOBase']=parent
        self.width:int=0
        self.height:int=0
        self.bpp:int=1
        self.parasites:typing.List[GimpParasite]=[]
        self.guidelines:typing.List[typing.Tuple[bool,int]]=[]
        self.itemPath:typing.List[str]=[]
        self.vectors:typing.List['GimpIOBase']=[]
        self.colorMap:typing.List[typing.Tuple[int,int,int]]=[]
        self.userUnits:typing.Optional[GimpUserUnits]=None
        self.samplePoints:typing.List[typing.Tuple[int,int]]=[]
        self.selected:bool=False
        self.isSelection:bool=False
        self.selectionAttachedTo:typing.Optional[str]=None
        self.blendMode:typing.Optional[BLEND_MODES]=None
        self.visible:typing.Optional[bool]=None
        self.isLinked:typing.Optional[bool]=None
        self.lockAlpha:typing.Optional[bool]=None
        self.applyMask:typing.Optional[bool]=None
        self.editingMask:typing.Optional[bool]=None
        self.showMask:typing.Optional[bool]=None
        self.showMasked:typing.Optional[bool]=None
        self.xOffset:typing.Optional[int]=None
        self.yOffset:typing.Optional[int]=None
        self.compression:typing.Optional[COMPRESSION_MODES]=None
        self.horizontalResolution:typing.Optional[int]=None
        self.verticalResolution:typing.Optional[int]=None
        self.uniqueId:typing.Optional[str]=None
        self.units:typing.Optional[UNITS]=None
        self.textLayerFlags:typing.Optional[int]=None
        self.locked:typing.Optional[bool]=None
        self.isGroup:typing.Optional[bool]=None
        self.groupItemFlags:int=0
        self.positionLocked:bool=False
        self.opacity:float=1.0
        self.colorTag:typing.Optional[TAG_COLORS]=None
        self.compositeMode:typing.Optional[COMPOSITE_MODES]=None
        self.compositeSpace:typing.Optional[COMPOSITE_SPACES]=None
        self.blendSpace:typing.Optional[int]=None
        self.color:typing.Optional[typing.Tuple[int,int,int]]=None
        self.vectorsVersion:typing.Optional[float]=0
        self.activeVectorIndex:typing.Optional[int]=0
        # TODO: I Think this next line was (badly) auto-generated or something
        #self.paths:typing.List[typing.List[float]]=[]
        self.paths:typing.List[str]=[]

    @property
    def _POINTER_SIZE_(self)->int:
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
    def _pointerDecode_(self,io:IO)->int:
        if self._POINTER_SIZE_==64:
            return io.u64
        return io.u32
    def _pointerEncode_(self,ptr,io=None)->bytearray:
        if not isinstance(ptr,int):
            raise Exception('pointer is wrong type = '+str(type(ptr)))
        if io is None:
            io=IO()
        if self._POINTER_SIZE_==64:
            io.u64=ptr
        else:
            io.u32=ptr
        return io.data

    @property
    def version(self)->float:
        """
        Get the version of this datatype
        """
        return self.doc.version

    @property
    def doc(self)->'GimpIOBase':
        """
        Get the main document object
        """
        item:GimpIOBase=self
        while item.parent is not None and item.parent!=item:
            item=item.parent
        return item
    @property
    def root(self)->'GimpIOBase':
        """
        Get the root of the file object tree
        (Which is the same as self.doc)
        """
        return self.doc

    @property
    def tattoo(self)->typing.Optional[str]:
        """
        This is the gimp nomenclature for the item's unique id
        """
        return self.uniqueId
    @tattoo.setter
    def tattoo(self,tattoo:typing.Optional[str]):
        """
        This is the gimp nomenclature for the item's unique id
        """
        self.uniqueId=tattoo

    def _parasitesDecode_(self,data:bytes)->int:
        """
        decode list of parasites
        """
        index=0
        while index<len(data):
            p=GimpParasite()
            index=p.fromBytes(data,index)
            self.parasites.append(p)
        return index

    def _parasitesEncode_(self)->bytes:
        """
        encode list of parasites
        """
        io=IO()
        for parasite in self.parasites:
            io.addBytes(parasite.toBytes())
        return io.data

    def _guidelinesDecode_(self,data:bytes)->None:
        """
        decode guidelines
        """
        index=0
        while index<len(data):
            position=struct.unpack('>I',data[index:index+4])[0]
            index+=4
            isVertical=data[index]==2
            index+=1
            self.guidelines.append((isVertical,position))

    def _guidelinesEncode_(self)->bytes:
        """
        encode guidelines
        """
        ret=bytearray()
        for isVertical,position in self.guidelines:
            ret.extend(struct.pack('>I',position))
            if isVertical:
                ret.append(2)
            else:
                ret.append(1)
        return bytes(ret)

    def _itemPathDecode_(self,data:bytes)->typing.Tuple[int,typing.List[str]]:
        """
        decode item path
        """
        index=0
        path:typing.List[str]=[]
        while index<len(data):
            p=struct.unpack('>I',data[index:index+4])[0]
            index+=4
            path.append(p)
        self.itemPath=path
        return index,path

    def _itemPathEncode_(self,
        itemPath:typing.Tuple[int,typing.Iterable[str]]
        )->bytes:
        """
        encode item path
        """
        ret=bytearray()
        _,segments=itemPath
        for segment in segments:
            ret.extend(struct.pack('>I',segment))
        return ret

    def _vectorsDecode_(self,data:bytes)->None:
        """
        decode vectors
        """
        import gimpFormats.gimpVectors
        index=0
        self.vectorsVersion=struct.unpack('>I',data[index:index+4])[0]
        index+=4
        self.activeVectorIndex=struct.unpack('>I',data[index:index+4])[0]
        index+=4
        numPaths=struct.unpack('>I',data[index:index+4])[0]
        index+=4
        for _ in range(numPaths):
            gv=gimpFormats.gimpVectors.GimpVector(self)
            index=gv.fromBytes(data,index)
            self.vectors.append(gv)

    def _vectorsEncode_(self)->bytes:
        """
        encode vectors
        """
        ret=bytearray()
        ret.extend(struct.pack('>I',self.vectorsVersion))
        ret.extend(struct.pack('>I',self.activeVectorIndex))
        ret.extend(struct.pack('>I',len(self.vectors)))
        for gv in self.vectors:
            ret.extend(gv.toBytes()) # type: ignore
        return bytes(ret)

    @property
    def activeVector(self)->typing.Optional['GimpIOBase']:
        """
        get the vector that is currently active
        """
        if self.activeVectorIndex is None:
            return None
        return self.vectors[self.activeVectorIndex]

    @property
    def expanded(self)->bool:
        """
        is the group layer expanded
        """
        return self.groupItemFlags&0x00000001>0
    @expanded.setter
    def expanded(self,expanded:bool):
        """
        is the group layer expanded
        """
        if expanded:
            self.groupItemFlags|=0x00000001
        else:
            self.groupItemFlags&=(~0x00000001)

    def _colormapDecode_(self,
        data:bytes,
        index:typing.Optional[int]=None
        )->None:
        """
        :param data: can be bytes or an IO object

        decode colormap/palette
        """
        ioObj=None
        if index is None:
            index=0
        if isinstance(data,IO):
            ioObj=data
            index=data.index
            data=data.data
        numColors=struct.unpack('>I',data[0:4])[0] # number of colors
        index+=4
        colors=[]
        n=0
        while index<len(data) and n<numColors:
            r=data[index]
            index+=1
            g=data[index]
            index+=1
            b=data[index]
            index+=1
            colors.append((r,g,b))
            n+=1
        self.colorMap=colors
        if ioObj is not None:
            ioObj.index=index

    def _colormapEncode_(self)->bytes:
        """
        encode colormap/palette to byte array
        """
        ret=bytearray(struct.pack('>I',len(self.colorMap)))
        for color in self.colorMap:
            ret.extend(color)
        return bytes(ret)

    def _userUnitsDecode_(self,data:bytes)->None:
        """
        decode a set of user-defined measurement units
        """
        u=GimpUserUnits()
        u.fromBytes(data)
        self.userUnits=u

    def _userUnitsEncode_(self)->bytes:
        """
        encode a set of user-defined measurement units
        """
        if self.userUnits is None:
            return bytes()
        return self.userUnits.toBytes()

    def _samplePointsDecode_(self,data:bytes)->None:
        """
        decode a series of points
        """
        index=0
        samplePoints=[]
        while index<len(data):
            x=struct.unpack('>I',data[index:index+4])[0]
            index+=4
            y=struct.unpack('>I',data[index:index+4])[0]
            index+=4
            samplePoints.append((x,y))
        self.samplePoints=samplePoints

    def _samplePointsEncode_(self)->bytes:
        """
        encode a series of points
        """
        ret=bytearray()
        for point in self.samplePoints:
            ret.extend(struct.pack('>I',point[0]))
            ret.extend(struct.pack('>I',point[1]))
        return bytes(ret)

    def _propertyDecode_(self,propertyType:PROPS,data:bytes)->int:
        """
        decode a single property
        """
        io=IO(data,boolSize=32)
        #print('DECODING PROPERTY',propertyType,len(data))
        if propertyType==PROPS.COLORMAP:
            self._colormapDecode_(data)
        elif propertyType==PROPS.ACTIVE_LAYER:
            self.selected=True
        elif propertyType==PROPS.ACTIVE_CHANNEL:
            self.selected=True
        elif propertyType==PROPS.SELECTION:
            self.isSelection=True
        elif propertyType==PROPS.FLOATING_SELECTION:
            self.selectionAttachedTo=io.u32
        elif propertyType==PROPS.OPACITY:
            self.opacity=io.u32
        elif propertyType==PROPS.MODE:
            self.blendMode=io.u32
        elif propertyType==PROPS.VISIBLE:
            self.visible=True
        elif propertyType==PROPS.LINKED:
            self.isLinked=io.bool
        elif propertyType==PROPS.LOCK_ALPHA:
            self.lockAlpha=io.bool
        elif propertyType==PROPS.APPLY_MASK:
            self.applyMask=io.bool
        elif propertyType==PROPS.EDIT_MASK:
            self.editingMask=io.bool
        elif propertyType==PROPS.SHOW_MASK:
            self.showMask=io.bool
        elif propertyType==PROPS.SHOW_MASKED:
            self.showMasked=io.bool
        elif propertyType==PROPS.OFFSETS:
            self.xOffset=io.i32
            self.yOffset=io.i32
        elif propertyType==PROPS.COLOR:
            r=io.byte
            g=io.byte
            b=io.byte
            self.color=(r,g,b)
        elif propertyType==PROPS.COMPRESSION:
            self.compression=io.byte
        elif propertyType==PROPS.GUIDES:
            self._guidelinesDecode_(data)
        elif propertyType==PROPS.RESOLUTION:
            self.horizontalResolution=io.float32
            self.verticalResolution=io.float32
        elif propertyType==PROPS.TATTOO:
            self.uniqueId=data.hex()
        elif propertyType==PROPS.PARASITES:
            self._parasitesDecode_(data)
        elif propertyType==PROPS.UNIT:
            self.units=io.u32
        elif propertyType==PROPS.PATHS:
            numPaths=io.u32
            for _ in range(numPaths):
                nRead,path=self._itemPathDecode_(data[io.index:])
                self.paths.extend(path)
                io.index+=nRead
        elif propertyType==PROPS.USER_UNIT:
            self._userUnitsDecode_(data)
        elif propertyType==PROPS.VECTORS:
            self._vectorsDecode_(data)
        elif propertyType==PROPS.TEXT_LAYER_FLAGS:
            self.textLayerFlags=int(data)
        elif propertyType==PROPS.OLD_SAMPLE_POINTS:
            raise Exception("ERR: old sample points structure not supported")
        elif propertyType==PROPS.LOCK_CONTENT:
            self.locked=io.bool
        elif propertyType==PROPS.GROUP_ITEM:
            self.isGroup=True
        elif propertyType==PROPS.ITEM_PATH:
            self._itemPathDecode_(data)
        elif propertyType==PROPS.GROUP_ITEM_FLAGS:
            self.groupItemFlags=io.u32
        elif propertyType==PROPS.LOCK_POSITION:
            self.positionLocked=io.bool
        elif propertyType==PROPS.FLOAT_OPACITY:
            self.opacity=io.float32
        elif propertyType==PROPS.COLOR_TAG:
            self.colorTag=io.u32
        elif propertyType==PROPS.COMPOSITE_MODE:
            self.compositeMode=io.i32
        elif propertyType==PROPS.COMPOSITE_SPACE:
            self.compositeSpace=io.i32
        elif propertyType==PROPS.BLEND_SPACE:
            self.blendSpace=io.u32
        elif propertyType==PROPS.FLOAT_COLOR:
            r=io.float32
            g=io.float32
            b=io.float32
            self.color=(r,g,b)
        elif propertyType==PROPS.SAMPLE_POINTS:
            self._samplePointsDecode_(data)
        else:
            raise Exception('Unknown property id '+str(propertyType))
        return io.index

    def isFloatColor(self,
        color:typing.Iterable[typing.Union[int,float]]
        )->bool:
        """
        check to see if any of the values of color is a float
        """
        for ch in color:
            if isinstance(ch,float):
                return True
        return False

    def _propertyEncode_(self,propertyType:int)->bytes:
        """
        encode a single property

        If the property is the same as the default, or not specified,
        returns empty array
        """
        io=IO(boolSize=32)
        if propertyType==PROPS.COLORMAP:
            if self.colorMap is not None and self.colorMap:
                io.u32=PROPS.COLORMAP
                io.addBytes(self._colormapEncode_())
        elif propertyType==PROPS.ACTIVE_LAYER:
            if self.selected is not None and self.selected:
                io.u32=PROPS.ACTIVE_LAYER
        elif propertyType==PROPS.ACTIVE_CHANNEL:
            if self.selected is not None and self.selected:
                io.u32=PROPS.ACTIVE_LAYER
        elif propertyType==PROPS.SELECTION:
            if self.isSelection is not None and self.isSelection:
                io.u32=PROPS.SELECTION
        elif propertyType==PROPS.FLOATING_SELECTION:
            if self.selectionAttachedTo is not None:
                io.u32=PROPS.FLOATING_SELECTION
                io.u32=self.selectionAttachedTo
        elif propertyType==PROPS.OPACITY:
            if self.opacity is not None and not isinstance(self.opacity,float):
                io.u32=PROPS.OPACITY
                io.u32=self.opacity
        elif propertyType==PROPS.MODE:
            if self.blendMode is not None:
                io.u32=PROPS.MODE
                io.u32=self.blendMode
        elif propertyType==PROPS.VISIBLE:
            if self.visible is not None and self.visible:
                io.u32=PROPS.VISIBLE
        elif propertyType==PROPS.LINKED:
            if self.isLinked is not None and self.isLinked:
                io.u32=PROPS.LINKED
                io.bool=self.isLinked
        elif propertyType==PROPS.LOCK_ALPHA:
            if self.lockAlpha is not None and self.lockAlpha:
                io.u32=PROPS.LOCK_ALPHA
                io.bool=self.lockAlpha
        elif propertyType==PROPS.APPLY_MASK:
            if self.applyMask is not None:
                io.u32=PROPS.APPLY_MASK
                io.bool=self.applyMask
        elif propertyType==PROPS.EDIT_MASK:
            if self.editingMask is not None and self.editingMask:
                io.u32=PROPS.EDIT_MASK
                io.bool=self.editingMask
        elif propertyType==PROPS.SHOW_MASK:
            if self.showMask is not None and self.showMask:
                io.u32=PROPS.SHOW_MASK
                io.bool=self.showMask
        elif propertyType==PROPS.SHOW_MASKED:
            if self.showMasked is not None:
                io.u32=PROPS.SHOW_MASKED
                io.bool=self.showMasked
        elif propertyType==PROPS.OFFSETS:
            if self.xOffset is not None and self.yOffset is not None:
                io.u32=PROPS.OFFSETS
                io.i32=self.xOffset
                io.i32=self.yOffset
        elif propertyType==PROPS.COLOR:
            if self.color is not None and not self.isFloatColor(self.color):
                io.u32=PROPS.COLOR
                io.byte=self.color[0]
                io.byte=self.color[1]
                io.byte=self.color[2]
        elif propertyType==PROPS.COMPRESSION:
            if self.compression is not None:
                io.u32=PROPS.COMPRESSION
                io.u32=self.compression
        elif propertyType==PROPS.GUIDES:
            if self.guidelines is not None and self.guidelines:
                io.u32=PROPS.GUIDES
                io.addBytes(self._guidelinesEncode_())
        elif propertyType==PROPS.RESOLUTION:
            if self.horizontalResolution is not None \
                and self.verticalResolution is not None:
                io.u32=PROPS.RESOLUTION
                io.u32=self.horizontalResolution
                io.i32=self.verticalResolution
        elif propertyType==PROPS.TATTOO:
            if self.uniqueId is not None:
                io.u32=int(self.uniqueId,16)
        elif propertyType==PROPS.PARASITES:
            if self.parasites is not None and self.parasites:
                io.u32=PROPS.PARASITES
                io.addBytes(self._parasitesEncode_())
        elif propertyType==PROPS.UNIT:
            if self.units is not None:
                io.u32=PROPS.UNIT
                io.u32=self.units
        elif propertyType==PROPS.PATHS:
            if self.paths is not None and self.paths:
                io.u32=PROPS.PATHS
                io.u32=len(self.paths)
                for path in self.paths:
                    io.addBytes(self._itemPathEncode_(path))
        elif propertyType==PROPS.USER_UNIT:
            if self.userUnits is not None:
                io.u32=PROPS.USER_UNIT
                io.addBytes(self._userUnitsEncode_())
        elif propertyType==PROPS.VECTORS:
            if self.vectors is not None and self.vectors:
                io.u32=PROPS.VECTORS
                io.addBytes(self._vectorsEncode_())
        elif propertyType==PROPS.TEXT_LAYER_FLAGS:
            if self.textLayerFlags is not None:
                io.u32=PROPS.TEXT_LAYER_FLAGS
                io.u32=self.textLayerFlags
        elif propertyType==PROPS.OLD_SAMPLE_POINTS:
            pass
        elif propertyType==PROPS.LOCK_CONTENT:
            if self.locked is not None and self.locked:
                io.u32=PROPS.LOCK_CONTENT
                io.bool=self.locked
        elif propertyType==PROPS.GROUP_ITEM:
            if self.isGroup is not None and self.isGroup:
                io.u32=PROPS.GROUP_ITEM
        elif propertyType==PROPS.ITEM_PATH:
            if self.itemPath is not None:
                io.u32=PROPS.ITEM_PATH
                io.addBytes(self._itemPathEncode_((0,self.itemPath)))
        elif propertyType==PROPS.GROUP_ITEM_FLAGS:
            if self.groupItemFlags is not None:
                io.u32=PROPS.GROUP_ITEM_FLAGS
                io.u32=self.groupItemFlags
        elif propertyType==PROPS.LOCK_POSITION:
            if self.positionLocked is not None and self.positionLocked:
                io.u32=PROPS.LOCK_POSITION
                io.bool=self.positionLocked
        elif propertyType==PROPS.FLOAT_OPACITY:
            if self.opacity is not None and isinstance(self.opacity,float):
                io.u32=PROPS.FLOAT_OPACITY
                io.float32=self.opacity
        elif propertyType==PROPS.COLOR_TAG:
            if self.colorTag is not None:
                io.u32=PROPS.COLOR_TAG
                io.u32=self.colorTag
        elif propertyType==PROPS.COMPOSITE_MODE:
            if self.compositeMode is not None:
                io.u32=PROPS.COMPOSITE_MODE
                io.i32=self.compositeMode
        elif propertyType==PROPS.COMPOSITE_SPACE:
            if self.compositeSpace is not None:
                io.u32=PROPS.COMPOSITE_SPACE
                io.i32=self.compositeSpace
        elif propertyType==PROPS.BLEND_SPACE:
            if self.blendSpace is not None:
                io.u32=PROPS.BLEND_SPACE
                io.u32=self.blendSpace
        elif propertyType==PROPS.FLOAT_COLOR:
            if self.color is not None and self.isFloatColor(self.color):
                io.u32=PROPS.FLOAT_COLOR
                io.float32=self.color[0]
                io.float32=self.color[1]
                io.float32=self.color[2]
        elif propertyType==PROPS.SAMPLE_POINTS:
            if self.samplePoints is not None and self.samplePoints:
                io.u32=PROPS.SAMPLE_POINTS
                io.addBytes(self._samplePointsEncode_())
        else:
            raise Exception('Unknown property id '+str(propertyType))
        return io.data

    def _propertiesDecode_(self,io:IO)->int:
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
    def _propertiesEncode_(self)->bytes:
        """
        encode a list of properties
        """
        io=IO()
        for propertyType in range(1,PROPS.NUM_PROPS.value):
            moData=self._propertyEncode_(propertyType)
            if moData:
                io.addBytes(moData)
        return io.data

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        if self.itemPath is not None:
            ret.append(f'Item Path: {self.itemPath}')
        if self.selected is not None:
            ret.append(f'Selected: {self.selected}')
        if self.isSelection is not None:
            ret.append(f'is Selection: {self.isSelection}')
        if self.selectionAttachedTo is not None:
            ret.append(f'Selection Attached To: {self.selectionAttachedTo}')
        if self.blendMode is not None:
            ret.append(f'Blend Mode: {self.blendMode.name}')
        if self.visible is not None:
            ret.append(f'Visible: {self.visible}')
        if self.isLinked is not None:
            ret.append(f'Linked: {self.isLinked}')
        if self.lockAlpha is not None:
            ret.append(f'Alpha Locked: {self.lockAlpha}')
        if self.applyMask is not None:
            ret.append(f'Apply Mask: {self.applyMask}')
        if self.editingMask is not None:
            ret.append(f'Editing Mask: {self.editingMask}')
        if self.showMask is not None:
            ret.append(f'Show Mask: {self.showMask}')
        if self.showMasked is not None:
            ret.append(f'Show Masked: {self.showMasked}')
        if self.xOffset is not None:
            ret.append(f'Offset: {self.xOffset} x {self.yOffset}')
        if self.compression is not None:
            compressionMode=self.compression.name
            ret.append(f'Compression: {compressionMode}')
        if self.horizontalResolution is not None:
            horizontalPpi=f'{self.horizontalResolution}ppi'
            verticalPpi=f'{self.verticalResolution}ppi'
            ret.append(f'Resolution: {horizontalPpi} x {verticalPpi}')
        if self.uniqueId is not None:
            ret.append(f'Unique ID (tattoo): {self.uniqueId}')
        if self.units is not None:
            ret.append(f'Units: {self.units.name}')
        if self.textLayerFlags is not None:
            ret.append(f'Text Layer Flags: {self.textLayerFlags}')
        if self.locked is not None:
            ret.append(f'Locked: {self.locked}')
        if self.isGroup is not None:
            ret.append(f'Is Group: {self.isGroup}')
        if self.groupItemFlags is not None:
            ret.append(f'Group Items Flag: {self.groupItemFlags}')
        if self.positionLocked is not None:
            ret.append(f'Position Locked: {self.positionLocked}')
        if self.opacity is not None:
            ret.append(f'Opacity: {self.opacity}')
        if self.colorTag is not None:
            ret.append(f'Tag Color: {self.colorTag.name}')
        if self.compositeMode is not None:
            # negative values are "Auto"
            val=self.compositeMode.name
            ret.append(f'Composite Mode: {val}')
        if self.compositeSpace is not None:
            # negative values are "Auto"
            val=self.compositeSpace.name
            ret.append(f'Composite Space: {val}')
        if self.blendSpace is not None:
            ret.append(f'Blend Space: {self.blendSpace}')
        if self.color is not None:
            ret.append('Color: (%s,%s,%s)'%
                (self.color[0],self.color[1],self.color[2]))
        if self.userUnits is not None:
            ret.append('User Units: ')
            ret.append(self.userUnits.__repr__(indent+'\t'))
        if self.parasites:
            ret.append('Parasites: ')
            for item in self.parasites:
                ret.append(item.__repr__(indent+'\t'))
        if self.guidelines:
            ret.append('Guidelines: ')
            for guideline in self.guidelines:
                if guideline[0]==0:
                    ret.append('Direction: horizontal')
                else:
                    ret.append('Direction: vertical')
                ret.append(f'location: {guideline[1]}')
        if self.samplePoints:
            ret.append('Sample Points: ')
            for x,y in self.samplePoints:
                ret.append(f'({x},{y})')
        if self.vectors:
            ret.append('Vectors: ')
            for vector in self.vectors:
                ret.append(vector.__repr__(indent+'\t'))
        if self.colorMap:
            ret.append('Color Map: ')
            for i,color in enumerate(self.colorMap):
                colorStr=','.join([str(c) for c in color])
                ret.append(f'{i}: ({colorStr})')
        return indent+(('\n'+indent).join(ret))


class GimpUserUnits:
    """
    user-defined measurement units
    """

    def __init__(self)->None:
        self.factor:int=0
        self.numDigits:int=0
        self.id:str=''
        self.symbol:str=''
        self.abbrev:str=''
        self.sname:str=''
        self.pname:str=''

    def fromBytes(self,data:bytes,index:int=0)->int:
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

    def toBytes(self)->bytes:
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

    def __repr__(self,indent:str='')->str:
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
