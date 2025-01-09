#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gbr brush format
"""
import typing
import PIL.Image
from gimpFormats.binaryIO import IO


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

    MAGIC_NUMBER:typing.Tuple[int,str]=(0,'GIMP')

    COLOR_MODES:typing.List[typing.Optional[str]]=\
        [None,'L','LA','RGB','RGBA'] # only L or RGB allowed

    def __init__(self,
        filename:typing.Optional[str]=None):
        """ """
        self.filename:typing.Optional[str]=None
        self.version:float=2
        self.width:int=0
        self.height:int=0
        self.bpp:int=1
        self.mode:typing.Optional[str]=self.COLOR_MODES[self.bpp]
        self.name:str=''
        self.rawImageBytes:typing.Optional[bytes]=None
        self.spacing:int=0
        if filename is not None:
            self.load(filename)

    def load(self,
        filename:typing.Union[str,typing.BinaryIO]
        )->int:
        """
        load a gimp file

        :param filename: can be a file name or a file-like object
        """
        if not isinstance(filename,str):
            self.filename=filename.name
            data=filename.read()
        else:
            self.filename=filename
            f=open(filename,'rb')
            data=f.read()
            f.close()
        return self._decode_(data)

    def _decode_(self,data:bytes,index:int=0)->int:
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
            msg=f'ERR:unknown brush version {self.version} at index {io.index}'
            raise Exception(msg)
        self.width=io.u32
        self.height=io.u32
        self.bpp=io.u32 # only allows grayscale or RGB
        self.mode=self.COLOR_MODES[self.bpp]
        magic=io.getBytes(4)
        if magic.decode('ascii')!='GIMP':
            magicName=magic.decode('ascii')
            msg='File format error.  Magic value mismatch'
            msg=f'{msg}:"{magicName}" {index}'
            raise ImportError(msg)
        self.spacing=io.u32
        nameLen=headerSize-io.index
        self.name=io.getBytes(nameLen).decode('UTF-8')
        self.rawImageBytes=io.getBytes(self.width*self.height*self.bpp)
        return io.index

    def toBytes(self)->bytes:
        """
        encode this object to raw bytes
        """
        if self.rawImageBytes is None:
            return bytes()
        io=IO()
        io.u32=28+len(self.name)
        io.u32=self.version
        io.u32=self.width
        io.u32=self.height
        io.u32=self.bpp
        io.addBytes('GIMP')
        io.u32=self.spacing
        io.addBytes(self.name)
        io.addBytes(self.rawImageBytes)
        return io.data

    @property
    def size(self)->typing.Tuple[int,int]:
        """
        Size of the brush
        """
        return (self.width,self.height)

    @property
    def image(self)->typing.Optional[PIL.Image.Image]:
        """
        get a final, compiled image
        """
        if self.rawImageBytes is None:
            return None
        if self.mode is None:
            self.mode='L'
        raw=bytes(self.rawImageBytes)
        return PIL.Image.frombytes(self.mode,self.size,raw,decoder_name='raw')

    def show(self):
        """
        show the brush image using the system image viewer
        """
        if self.image is None:
            raise IndexError('No image data to save')
        self.image.show(title=self.name)

    def save(self,
        toFilename:typing.Optional[str]=None,
        toExtension:typing.Optional[str]=None
        )->None:
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
        if toFilename is None:
            toFilename='untitled.png'
        if toExtension is None:
            if toFilename is not None:
                toExtensionPath=toFilename.rsplit('.',1)
                if len(toExtensionPath)>1:
                    toExtension=toExtensionPath[-1]
                else:
                    toExtension=None
        if toExtension is not None and toExtension!='gbr':
            asImage=True
        if asImage:
            if self.image is None:
                raise IndexError('No image data to save')
            self.image.save(toFilename)
        else:
            if not hasattr(toFilename,'write'):
                f=open(toFilename,'wb')
            data=self.toBytes()
            if data is None:
                raise IndexError('No image data to save')
            f.write(data)

    def __repr__(self,indent:str='')->str:
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


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        g:typing.Optional[GimpGbrBrush]=None
        for arg in args:
            if arg.startswith('-'):
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ['-h','--help']:
                    printhelp=True
                elif kv[0]=='--dump':
                    print(g)
                elif kv[0]=='--show':
                    if g is None:
                        print('ERR: no image to show')
                    else:
                        g.show()
                elif kv[0]=='--save':
                    if g is None:
                        print('ERR: no image to save')
                    else:
                        g.save(kv[1])
                else:
                    print(f'ERR: unknown argument "{arg}"')
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
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
