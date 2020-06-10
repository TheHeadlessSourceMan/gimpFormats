#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of a gimp pattern file
"""
from typing import Optional, Tuple, BinaryIO, Union
import PIL.Image
from gimpFormats.binaryIO import IO


class GimpPatPattern:
    """
    Pure python implementation of a gimp pattern file

    See:
        https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/pat.txt

    Format:
        name: GimpPatPattern
        description: Gimp pattern
        guid: {45129576-6728-4967-8888-6b9082862ca5}
        parentNames: Image
        #mimeTypes: application/jpeg
        filenamePatterns: *.pat
    """

    MAGIC_NUMBER=(0,'GPAT')

    COLOR_MODES=[None,'L','LA','RGB','RGBA']

    def __init__(self,filename: Union[None,str,BinaryIO]=None) -> None:
        self.filename:Union[str,None]=None
        self.version:float=1
        self.width:int=0
        self.height:int=0
        self.bpp:int=4
        self.mode:Union[None,str]=self.COLOR_MODES[self.bpp]
        self.name:str=''
        self._rawImage:Union[None,bytes]=None
        self._image:Union[None,'PIL.Image']=None
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

    def _decode_(self,data: bytes,index: int=0) -> None:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index)
        headerSize=io.u32
        self.version=io.u32
        self.width=io.u32
        self.height=io.u32
        self.bpp=io.u32
        self.mode=self.COLOR_MODES[self.bpp]
        magic=io.getBytes(4)
        if magic.decode('ascii')!='GPAT':
            raise Exception('File format error.  Magic value mismatch.')
        nameLen=headerSize-io.index
        self.name=io.getBytes(nameLen).decode('UTF-8')
        self._rawImage=io.getBytes(self.width*self.height*self.bpp)
        self._image=None

    def toBytes(self) -> bytearray:
        """
        encode to a byte buffer
        """
        io=IO()
        io.u32=24+len(self.name)
        io.u32=self.version
        io.u32=self.width
        io.u32=self.height
        io.u32=len(self.image.mode)
        io.addBytes('GPAT')
        io.addBytes(self.name.encode('utf-8'))
        if self._rawImage is None:
            rawImage=self.image.tobytes(encoder_name='raw')
        else:
            rawImage=self._rawImage
        io.addBytes(rawImage)
        return io.data

    @property
    def size(self) -> Tuple[int, int]:
        """
        the size of the pattern
        """
        return (self.width,self.height)

    @property
    def image(self):
        """
        get a final, compiled image
        """
        if self._image is None:
            if self._rawImage is None:
                return None
            raw=bytes(self._rawImage)
            self._image=PIL.Image.frombytes(self.mode,self.size,raw,decoder_name='raw')
        return self._image
    @image.setter
    def image(self,image):
        self._image=image
        self._rawImage=None

    def save(self,toFilename: Optional[str]=None,toExtension: None=None) -> None:
        """
        save this gimp image to a file
        """
        asImage=False
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.pat'
            toFilename=self.filename
        elif hasattr(toFilename,'write'):
            self.filename=toFilename.name
        else:
            self.filename=str(toFilename)
        if toExtension is None:
            if toFilename is not None:
                toExtension=toFilename.rsplit('.',1)
                if len(toExtension)>1:
                    toExtension=toExtension[-1]
                else:
                    toExtension=None
        if toExtension is not None and toExtension!='pat':
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
        ret.append('BPP: '+str(self.bpp))
        ret.append('Mode: '+str(self.mode))
        return '\n'.join(ret)


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
                g=GimpPatPattern(arg)
    if printhelp:
        print('Usage:')
        print('  gimpPatPattern.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --show ................ show the pattern image')
        print('   --save=out.jpg ........ save out the pattern image')
        print('   --register ............ register this extension')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
