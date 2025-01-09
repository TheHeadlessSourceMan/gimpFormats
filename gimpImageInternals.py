#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Contains stuff around the internal image storage mechaanism
of gimp files.

Generally speaking, the user should not care about anything
in this file.
"""
import typing
import zlib
import PIL.Image
from gimpFormats.binaryIO import IO
from gimpFormats.gimpIOBase import GimpIOBase


class GimpChannel(GimpIOBase):
    """
    Represents a single channel or mask in a gimp image
    """

    def __init__(self,
        parent:GimpIOBase,
        name:str='',
        image:typing.Optional[PIL.Image.Image]=None):
        """ """
        GimpIOBase.__init__(self,parent)
        self.width:int=0
        self.height:int=0
        self.name:str=name
        self._data:typing.Union[None,bytes]=None
        self._imageHierarchy:typing.Union[GimpImageHierarchy,None]=None
        self._imageHierarchyPtr:typing.Optional[int]=None
        if image is not None:# this is last because image can reset values
            self.image=image

    def fromBytes(self,data:bytes,index:int=0)->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index)
        #print('Decoding channel at',index)
        self.width=io.u32
        self.height=io.u32
        self.name=io.sz754
        self._propertiesDecode_(io)
        self._imageHierarchyPtr=self._pointerDecode_(io)
        self._data=io.data
        return io.index

    def toBytes(self)->bytes:
        """
        encode this object to a byte buffer
        """
        io=IO()
        io.u32=self.width
        io.u32=self.height
        io.sz754=self.name
        io.addBytes(self._propertiesEncode_())
        ih=self._imageHierarchyPtr
        if ih is None:
            ih=0
        io.addBytes(self._pointerEncode_(ih))
        return io.data

    @property
    def image(self
        )->typing.Optional[PIL.Image.Image]:
        """
        get a final, compiled image
        """
        if self.imageHierarchy is None:
            return None
        return self.imageHierarchy.image
    @image.setter
    def image(self,image:PIL.Image.Image):
        """
        get a final, compiled image
        """
        self.width=image.width
        self.height=image.height
        if not self.name and isinstance(image,str):
            # try to use a filename as the name
            self.name=image.rsplit('\\',1)[-1].rsplit('/',1)[-1]
        self._imageHierarchy=GimpImageHierarchy(self,image)

    def _forceFullyLoaded(self)->None:
        """
        make sure everything is fully loaded from the file
        """
        # first, make sure the image is loaded so we can
        # get rid of the hierarchy nonsense
        _=self.image
        self._imageHierarchyPtr=None
        self._data=None

    @property
    def imageHierarchy(self
        )->typing.Optional['GimpImageHierarchy']:
        """
        Get the image hierarchy

        This is mainly used for decoding the image, so
        not much use to you.
        """
        if self._imageHierarchy is None \
            and self._imageHierarchyPtr is not None \
            and self._data is not None:
            #
            self._imageHierarchy=GimpImageHierarchy(self)
            self._imageHierarchy.fromBytes(self._data,self._imageHierarchyPtr)
        return self._imageHierarchy

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        ret.append('Name: '+str(self.name))
        ret.append('Size: '+str(self.width)+' x '+str(self.height))
        ret.append(GimpIOBase.__repr__(self,indent))
        return indent+(('\n'+indent).join(ret))


class GimpImageHierarchy(GimpIOBase):
    """
    Gets packed pixels from a gimp image

    NOTE: This was originally designed to be a hierarchy, like
        an image pyramid, through in practice they only use the
        top level of the pyramid (64x64) and ignore the rest.
    """

    def __init__(self,parent,image:'PIL.Image'=None):
        GimpIOBase.__init__(self,parent)
        self.width:int=0
        self.height:int=0
        self.bpp:int=0 # Number of bytes per pixel given
        self._levelPtrs:typing.List[int]=[]
        self._levels:typing.List[GimpImageLevel]=[]
        self._data:typing.Union[None,bytearray]=None
        if image is not None:# NOTE:can override earlier parameters
            self.image=image

    def fromBytes(self,data:typing.Union[bytes,bytearray],index:int=0)->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        if not data:
            #raise Exception('No data!')
            print("WARN: No image data!")
            return 0
        io=IO(data,index)
        #print('Decoding channel at',index)
        self.width=io.u32
        self.height=io.u32
        self.bpp=io.u32
        if self.bpp<1 or self.bpp>4:
            msg=['Unespected bytes-per-pixel for image data ({self.bpp}))'
                '(Probably means file corruption.)']
            raise Exception('\n'.join(msg))
        while True:
            ptr=self._pointerDecode_(io)
            if ptr==0:
                break
            self._levelPtrs.append(ptr)
        if self._levelPtrs: # remove "dummy" level pointers
            self._levelPtrs=[self._levelPtrs[0]]
        self._data=bytearray(data)
        return io.index

    def toBytes(self)->bytes:
        """
        encode this object to a byte buffer
        """
        dataIO=IO()
        io=IO()
        io.u32=self.width
        io.u32=self.height
        io.u32=self.bpp
        levels=self.levels
        if levels is not None:
            dataIndex=io.index+self._POINTER_SIZE_*(len(levels)+1)
            for level in levels:
                io.addBytes(self._pointerEncode_(dataIndex+io.index))
                dataIO.addBytes(level.toBytes())
        io.addBytes(self._pointerEncode_(0))
        io.addBytes(dataIO.data)
        return io.data

    @property
    def levels(self
        )->typing.List['GimpImageLevel']:
        """
        Get the levels within this hierarchy

        Presently hierarchy is not really used by gimp,
        so this returns an array of one item
        """
        if self._levels is None and self._data is not None:
            for ptr in self._levelPtrs:
                imageLevel=GimpImageLevel(self)
                imageLevel.fromBytes(self._data,ptr)
                self._levels=[imageLevel]
        return self._levels

    @property
    def image(self
        )->typing.Optional[PIL.Image.Image]:
        """
        get a final, compiled image
        """
        if not self.levels:
            return None
        return self.levels[0].image
    @image.setter
    def image(self,image:PIL.Image.Image):
        """
        set the image
        """
        self.width=image.width
        self.height=image.height
        if image.mode not in ['L','LA','RGB','RGBA']:
            raise NotImplementedError('Unsupported PIL image type')
        self.bpp=len(image.mode)
        self._levelPtrs=[]
        self._levels=[GimpImageLevel(self,image)]

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        ret.append('Size: '+str(self.width)+' x '+str(self.height))
        ret.append('Bytes Per Pixel: '+str(self.bpp))
        return indent+(('\n'+indent).join(ret))


class GimpImageLevel(GimpIOBase):
    """
    Gets packed pixels from a gimp image

    This represents a single level in an imageHierarchy
    """

    def __init__(self,
        parent:GimpIOBase,
        image:typing.Optional[PIL.Image.Image]=None):
        """ """
        GimpIOBase.__init__(self,parent)
        self.width:int=0
        self.height:int=0
        self._tiles:typing.List[PIL.Image.Image]=[] # tile PIL images
        self._image:typing.Optional[PIL.Image.Image]=None
        if image is not None:
            self.image=image

    def fromBytes(self,
        data:typing.Union[bytes,bytearray],
        index:int=0
        )->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index)
        #print('Decoding image level at',io.index)
        self.width=io.u32
        self.height=io.u32
        parent=self.parent
        if parent is None:
            parent=self
        if self.width!=parent.width or self.height!=parent.height:
            currentSize=f'({self.width},{self.height})'
            expectedSize=f'({parent.width},{parent.height})'
            msgA=[
                f'Image data size mismatch. {currentSize}!={expectedSize}',
                ' Usually this implies file corruption.']
            raise Exception('\n'.join(msgA))
        self._tiles=[]
        self._image=None
        for y in range(0,self.height,64):
            for x in range(0,self.width,64):
                ptr=self._pointerDecode_(io)
                size=(min(self.width-x,64),min(self.height-y,64))
                totalBytes=size[0]*size[1]*self.bpp
                if self.doc.compression==0: # none
                    data=io.data[ptr:ptr+totalBytes]
                elif self.doc.compression==1: # RLE
                    data=self._decodeRLE(io.data,size[0]*size[1],self.bpp,ptr)
                elif self.doc.compression==2: # zip
                    # guess how many bytes are needed
                    data=zlib.decompress(io.data[ptr:ptr+totalBytes+24])
                else:
                    msg=f'Unsupported compression mode: {self.doc.compression}'
                    raise Exception(msg)
                mode=self.mode
                if mode is None:
                    mode="L"
                subImage=PIL.Image.frombytes(
                    mode,size,bytes(data),decoder_name='raw')
                self._tiles.append(subImage)
        _=self._pointerDecode_(io) # list ends with nul character
        return io.index

    def toBytes(self)->bytes:
        """
        encode this object to a byte buffer
        """
        dataIO=IO()
        io=IO()
        io.u32=self.width
        io.u32=self.height
        tiles=self.tiles
        if tiles is not None:
            dataIndex=io.index+self._POINTER_SIZE_*(len(tiles)+1)
            for tile in tiles:
                io.addBytes(self._pointerEncode_(dataIndex+dataIO.index))
                data=tile.tobytes()
                if self.doc.compression==0: # none
                    pass
                elif self.doc.compression==1: # RLE
                    data=self._encodeRLE(data,self.bpp)
                elif self.doc.compression==2: # zip
                    data=zlib.compress(data)
                else:
                    msg=f'Unsupported compression mode: {self.doc.compression}'
                    raise Exception(msg)
                dataIO.addBytes(data)
        io.addBytes(self._pointerEncode_(0))
        io.addBytes(dataIO.data)
        return io.data

    def _decodeRLE(self,
        data:bytes,pixels:int,bpp:int,index:int=0
        )->bytes:
        """
        decode RLE encoded image data
        """
        ret:typing.List[typing.List[int]]=[[] for chan in range(bpp)]
        for chan in range(bpp):
            n=0
            while n<pixels:
                opcode=data[index]
                index+=1
                if 0<=opcode<=126: # a short run of identical bytes
                    val=data[index]
                    index+=1
                    for _ in range(opcode+1):
                        ret[chan].append(val)
                        n+=1
                elif opcode==127: # A long run of identical bytes
                    m=data[index]
                    index+=1
                    b=data[index]
                    index+=1
                    val=data[index]
                    index+=1
                    amt=m*256+b
                    for _ in range(amt):
                        ret[chan].append(val)
                        n+=1
                elif opcode==128: # A long run of different bytes
                    m=data[index]
                    index+=1
                    b=data[index]
                    index+=1
                    amt=m*256+b
                    for _ in range(amt):
                        val=data[index]
                        index+=1
                        ret[chan].append(val)
                        n+=1
                elif 129<=opcode<=255: # a short run of different bytes
                    amt=256-opcode
                    for _ in range(amt):
                        val=data[index]
                        index+=1
                        ret[chan].append(val)
                        n+=1
                else:
                    print('Unreachable branch',opcode)
                    raise Exception()
        # flatten/weave the individual channels into one strream
        flat=bytearray()
        for i in range(pixels):
            for chan in range(bpp):
                flat.append(ret[chan][i])
        return bytes(flat)

    def _encodeRLE(self,
        data:typing.Union[bytes,bytearray],
        bpp:int
        )->bytes:
        """
        encode image to RLE  image data
        """
        def countSame(
            data:typing.Union[bytes,bytearray],
            startIdx:int
            )->int:
            """
            count how many times bytes are identical
            """
            maxLen=len(data)
            idx=startIdx
            if idx>=maxLen:
                return 0
            c=data[idx]
            idx=startIdx+1
            while idx<maxLen and data[idx]==c:
                idx+=1
            return idx-startIdx
        def countDifferent(
            data:typing.Union[bytes,bytearray],
            startIdx:int=0
            )->int:
            """
            count how many times bytes are different
            """
            maxLen=len(data)
            idx=startIdx
            if idx>=maxLen:
                return 0
            c=data[idx]
            idx=startIdx+1
            while idx<maxLen and data[idx]!=c:
                idx+=1
                c=data[idx]
            return idx-startIdx
        def rleEncodeChan(
            data:typing.Union[bytes,bytearray]
            )->bytearray:
            """
            rle encode a single channel of data
            """
            ret=bytearray()
            idx=0
            while idx<len(data):
                nRepeats=countSame(data,0)
                if nRepeats==1: # different bytes
                    nDifferences=countDifferent(data,1)
                    if nDifferences<=127: # short run of different bytes
                        ret.append(129+nRepeats-1)
                        ret.append(data[idx])
                        idx+=nDifferences
                    else: # long run of different bytes
                        ret.append(128)
                        ret.append(int(nDifferences/256.0))
                        ret.append(nDifferences%256)
                        ret.append(data[idx])
                        idx+=nDifferences
                elif nRepeats<=127: # short run of same bytes
                    ret.append(nRepeats-1)
                    ret.append(data[idx])
                    idx+=nRepeats
                else: # long run of same bytes
                    ret.append(127)
                    ret.append(int(nRepeats/256.0))
                    ret.append(nRepeats%256)
                    ret.append(data[idx])
                    idx+=nRepeats
            return ret
        # if there is only one channel, encode and return it directly
        if bpp==1:
            return rleEncodeChan(data)
        # split into channels
        dataByChannel:typing.List[bytearray]=[]
        for chan in range(bpp):
            chanData=bytearray()
            for index in range(chan,bpp,len(data)):
                chanData.append(data[index])
            dataByChannel.append(chanData)
        # encode and join each channel
        ret=bytearray()
        for chanBytes in dataByChannel:
            ret.extend(rleEncodeChan(chanBytes))
        return bytes(ret)

    @property
    def bpp(self)->int:
        """
        get the number of bytes per pixel
        """
        if self.parent is None:
            return 1
        return self.parent.bpp
    @bpp.setter
    def bpp(self,bpp:int):
        if self.parent is not None:
            self.parent.bpp=bpp

    @property
    def mode(self)->typing.Optional[str]:
        """
        Get the color mode in PIL standard form
        """
        MODES=[None,'L','LA','RGB','RGBA']
        return MODES[self.bpp]

    @property
    def tiles(self
        )->typing.List[PIL.Image.Image]:
        """
        Get individual tiles for this image
        """
        if self._tiles is not None:
            return self._tiles
        if self.image is not None:
            return self._imgToTiles(self.image)
        return None

    def _imgToTiles(self,
        image:PIL.Image.Image
        )->typing.List[PIL.Image.Image]:
        """
        break an image into a series of tiles, each<=64x64
        """
        ret=[]
        for y in range(0,self.height,64):
            for x in range(0,self.width,64):
                bounds=(x,y,min(self.width-x,64),min(self.height-y,64))
                ret.append(image.crop(bounds))
        return ret

    @property
    def image(self
        )->typing.Optional[PIL.Image.Image]:
        """
        get a final, compiled image
        """
        if self._image is None:
            tiles=self.tiles
            if tiles is None:
                return None
            mode=self.mode
            if mode is None:
                mode='L'
            self._image=PIL.Image.new(mode,(self.width,self.height))
            tileNum=0
            for y in range(0,self.height,64):
                for x in range(0,self.width,64):
                    subImage=tiles[tileNum]
                    tileNum+=1
                    self._image.paste(subImage,(x,y))
            self._tiles=[] # TODO:do I want to keep the tiles for any reason??
        return self._image
    @image.setter
    def image(self,image:PIL.Image.Image):
        self._image=image
        self._tiles=[]
        self.width=image.width
        self.height=image.height

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        ret.append('Size: '+str(self.width)+' x '+str(self.height))
        return indent+(('\n'+indent).join(ret))
