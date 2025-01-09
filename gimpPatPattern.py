#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of a gimp pattern file
"""
import typing
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

    COLOR_MODES=(None,'L','LA','RGB','RGBA')

    def __init__(self,
        filename:typing.Union[None,str,typing.BinaryIO]=None):
        """ """
        self.filename:typing.Optional[str]=None
        self.version:float=1
        self.width:int=0
        self.height:int=0
        self.bpp:int=4
        self.mode:typing.Optional[str]=self.COLOR_MODES[self.bpp]
        self.name:str=''
        self._rawImage:typing.Optional[bytes]=None
        self._image:typing.Optional[PIL.Image.Image]=None
        if filename is not None:
            self.load(filename)

    def load(self,filename:typing.Union[str,typing.BinaryIO])->None:
        """
        load a gimp file

        :param filename: can be a file name or a file-like object
        """
        if isinstance(filename,str):
            self.filename=filename
            f=open(filename,'rb')
            data=f.read()
            f.close()
        else:
            self.filename=filename.name
            data=filename.read()
        self._decode_(data)

    def _decode_(self,data:bytes,index:int=0)->int:
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
        return io.index-index

    def toBytes(self)->bytes:
        """
        encode to a byte buffer
        """
        if self.image is None:
            return bytes()
        io=IO()
        io.u32=24+len(self.name)
        io.u32=self.version
        io.u32=self.width
        io.u32=self.height
        mode=self.image.mode
        if mode is None:
            mode='L'
        io.u32=len(mode)
        io.addBytes('GPAT')
        io.addBytes(self.name.encode('utf-8'))
        if self._rawImage is None:
            rawImage=self.image.tobytes(encoder_name='raw')
        else:
            rawImage=self._rawImage
        io.addBytes(rawImage)
        return io.data

    @property
    def size(self)->typing.Tuple[int,int]:
        """
        the size of the pattern
        """
        return (self.width,self.height)

    @property
    def image(self)->typing.Optional[PIL.Image.Image]:
        """
        get a final, compiled image
        """
        if self._image is None:
            if self._rawImage is None:
                return None
            raw=bytes(self._rawImage)
            mode=self.mode
            if mode is None:
                mode='L'
            self._image=PIL.Image.frombytes(
                mode,self.size,raw,decoder_name='raw')
        return self._image
    @image.setter
    def image(self,image:PIL.Image.Image):
        self._image=image
        self._rawImage=None

    def save(self,
        toFilename:typing.Optional[str]=None,
        toExtension:typing.Optional[str]=None
        )->None:
        """
        save this gimp image to a file
        """
        asImage=False
        f=None
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.pat'
            toFilename=self.filename
        elif isinstance(toFilename,str):
            self.filename=str(toFilename)
        else:
            f=toFilename
            toFilename=toFilename.name
            self.filename=toFilename
        if toExtension is None:
            if toFilename is not None:
                ext=toFilename.rsplit('.',1)
                if len(ext)>1:
                    toExtension=ext[-1]
                else:
                    toExtension=None
        if toExtension is not None and toExtension!='pat':
            asImage=True
        if asImage:
            if self.image is not None:
                self.image.save(toFilename)
        else:
            if f is None:
                f=open(toFilename,'wb')
            f.write(self.toBytes())

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
        ret.append('BPP: '+str(self.bpp))
        ret.append('Mode: '+str(self.mode))
        return '\n'.join(ret)


def cmdline(args:typing.Iterable[str])->int:
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
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ('-h','--help'):
                    printhelp=True
                elif kv[0]=='--dump':
                    print(g)
                elif kv[0]=='--show':
                    if g is None:
                        print('ERR: No pattern to show')
                    else:
                        g.image.show()
                elif kv[0]=='--save':
                    if g is None:
                        print('ERR: No pattern to save')
                    else:
                        g.image.save(kv[1])
                else:
                    print(f'ERR: unknown argument "{arg}"')
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
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
