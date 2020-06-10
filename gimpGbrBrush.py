#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gbr brush format
"""
import struct
import PIL.Image
from gimpFormats.binaryIO import IO
from PIL.Image import Image
from typing import Optional, Tuple, BinaryIO, Union


class GimpGbrBrush:
    """
    Pure python implementation of the gimp gbr brush format

    See:
        https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/gbr.txt
    
    Format:
        name: GimpGbrBrush
        description: Gimp brush
        guid: {45129576-6728-4967-8888-6b9082862ca8}
        parentNames: Brush, Image
        #mimeTypes: application/jpeg
        filenamePatterns: *.gbr
    """
    
    MAGIC_NUMBER=(0,'GIMP')

    COLOR_MODES=[None,'L','LA','RGB','RGBA'] # only L or RGB allowed

    def __init__(self,filename: None=None) -> None:
        self.filename:Union[str,None]=None
        self.version:float=2
        self.width:int=0
        self.height:int=0
        self.bpp:int=1
        self.mode:int=self.COLOR_MODES[self.bpp]
        self.name:str=''
        self.rawImage:Union[Image,None]=None
        self.spacing:int=0
        if filename is not None:
            self.load(filename)

    def load(self,filename: Union[str,BinaryIO]) -> None:
        """
        load a gimp file

        :param filename: can be a file name or a file-like object
        """
        if hasattr(filename,'read'):
            self.filename=filename.name
            data=filename.read()
        else:
            self.filename=filename
            f=open(filename,'rb')
            data=f.read()
            f.close()
        self._decode_(data)

    def _decode_(self,data: bytes,index: int=0) -> int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        
        :return: the number of bytes read
        """
        io=IO(data,index)
        headerSize=io.u32
        self.version=io.u32
        if self.version!=2:
            raise Exception('ERR: unknown brush version %f at index %d'%(self.version,io.index))
        self.width=io.u32
        self.height=io.u32
        self.bpp=io.u32 # only allows grayscale or RGB
        self.mode=self.COLOR_MODES[self.bpp]
        magic=io.getBytes(4)
        if magic.decode('ascii')!='GIMP':
            raise Exception('"'+magic.decode('ascii')+'" '+str(index))
            raise Exception('File format error.  Magic value mismatch.')
        self.spacing=io.u32
        nameLen=headerSize-io.index
        self.name=io.getBytes(nameLen).decode('UTF-8')
        self.rawImage=io.getBytes(self.width*self.height*self.bpp)
        return io.index

    def toBytes(self) -> bytearray:
        """
        encode this object to byte array
        
        """
        io=IO()
        io.u32=28+len(self.name)
        io.u32=self.version
        io.u32=self.width
        io.u32=self.height
        io.u32=self.bpp
        io.addBytes('GIMP')
        io.u32=self.spacing
        io.addBytes(self.name)
        io.addBytes(self.rawImage)
        return io.data

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width,self.height)

    @property
    def image(self) -> Image:
        """
        get a final, compiled image
        """
        if self.rawImage is None:
            return None
        raw=bytes(self.rawImage)
        return PIL.Image.frombytes(self.mode,self.size,raw,decoder_name='raw')

    def save(self,toFilename: Optional[str]=None,toExtension: None=None) -> None:
        """
        save this gimp image to a file
        """
        asImage=False
        if toFilename is None:
            if self.filename is None:
                self.filename='Untitled.gbr'
            toFilename=self.filename
        else:
            self.filename=toFilename
        if toExtension is None:
            if toFilename is not None:
                toExtension=toFilename.rsplit('.',1)
                if len(toExtension)>1:
                    toExtension=toExtension[-1]
                else:
                    toExtension=None
        if toExtension is not None and toExtension!='gbr':
            asImage=True
        if asImage:
            self.image.save(toFilename)
        else:
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
        ret.append('Version: '+str(self.version))
        ret.append('Size: '+str(self.width)+' x '+str(self.height))
        ret.append('Spacing: '+str(self.spacing))
        ret.append('BPP: '+str(self.bpp))
        ret.append('Mode: '+str(self.mode))
        return ('\n'+indent).join(ret)


def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        g=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--dump':
                    print(g)
                elif arg[0]=='--show':
                    g.image.show()
                elif arg[0]=='--save':
                    g.image.save(arg[1])
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                g=GimpGbrBrush(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGbrBrush.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --show ................ show the brush image')
        print('   --save=out.jpg ........ save out the brush image')
        print('   --register ............ register this extension')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
