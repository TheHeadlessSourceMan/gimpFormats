#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the OLD gimp gpb brush format
"""
import typing
from gimpFormats.binaryIO import IO
from gimpFormats.gimpGbrBrush import GimpGbrBrush
from gimpFormats.gimpPatPattern import GimpPatPattern


class GimpGpbBrush:
    """
    Pure python implementation of the OLD gimp gpb brush format

    See:
        https://developer.gimp.org/core/standards/gpb/

    Format:
        name: GimpGpbBrush
        description: Gimp brush (legacy)
        guid: {45129576-6728-4967-8888-6b9082862ca2}
        parentNames: Brush
        #mimeTypes: application/jpeg
        filenamePatterns: *.gpb
    """

    MAGIC_NUMBER:typing.Tuple[int,str]=(0,'GIMP')

    def __init__(self,
        filename:typing.Union[None,str,typing.BinaryIO]=None):
        """ """
        self.brush:GimpGbrBrush=GimpGbrBrush()
        self.pattern:GimpPatPattern=GimpPatPattern()
        self.filename:typing.Optional[str]=None
        if filename is not None:
            self.load(filename)

    def load(self,filename:typing.Union[str,typing.BinaryIO])->None:
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
        self._decode_(data)

    def _decode_(self,data:bytes,index:int=0)->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        index=self.brush._decode_(data,index) # pylint: disable=protected-access # noqa: E501
        index=self.pattern._decode_(data,index) # pylint: disable=protected-access # noqa: E501
        return index

    def toBytes(self)->bytes:
        """
        encode this object to a byte array
        """
        if self.brush is None:
            return bytes()
        io=IO()
        io.addBytes(self.brush.toBytes())
        io.addBytes(self.pattern.toBytes())
        return io.data

    def save(self,
        toFilename:typing.Union[None,str,typing.BinaryIO]=None,
        toExtension:typing.Optional[str]=None
        )->None:
        """
        save this gimp image to a file
        """
        f=None
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.gpb'
            toFilename=self.filename
        elif isinstance(toFilename,str):
            self.filename=toFilename
        else:
            f=toFilename
            toFilename=toFilename.name
            self.filename=toFilename
        if toExtension is None:
            toExtension=toFilename.rsplit('.',1)[-1]
        else:
            toFilename=toFilename.rsplit('.',1)[0]
            toFilename=f'{toFilename}.{toExtension}'
        if toExtension=='gpb':
            if f is None:
                f=open(toFilename,'wb')
            f.write(self.toBytes())
        elif toExtension=='vbr':
            # TODO: convert between brush types!
            raise NotImplementedError()
        else:
            # save as an image
            image=self.brush.image
            if image is None:
                image=self.pattern.image
            if image is not None:
                image.save(toFilename)

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        if self.filename is not None:
            ret.append('Filename: '+self.filename)
        ret.append(self.brush.__repr__(indent+'\t'))
        ret.append(self.pattern.__repr__(indent+'\t'))
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
        g=None
        for arg in args:
            if arg.startswith('-'):
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ['-h','--help']:
                    printhelp=True
                elif kv[0]=='--dump':
                    print(g)
                else:
                    print(f'ERR: unknown argument "{arg}"')
            else:
                g=GimpGpbBrush(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGpbBrush.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
