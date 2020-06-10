#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the OLD gimp gpb brush format
"""
import struct
import PIL.Image
from gimpFormats.binaryIO import IO
from gimpFormats.gimpGbrBrush import GimpGbrBrush
from gimpFormats.gimpPatPattern import GimpPatPattern
from typing import Optional, Union, BinaryIO
    

class GimpGpbBrush:
    """
    Pure python implementation of the OLD gimp gpb brush format

    See:
        https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/vbr.txt
        
    Format:
        name: GimpGpbBrush
        description: Gimp brush (legacy)
        guid: {45129576-6728-4967-8888-6b9082862ca2}
        parentNames: Brush
        #mimeTypes: application/jpeg
        filenamePatterns: *.gpb
    """
    
    MAGIC_NUMBER=(0,'GIMP')

    def __init__(self,filename:Union[None,str,BinaryIO]=None):
        self.brush:GimpGbrBrush=GimpGbrBrush()
        self.pattern:GimpPatPattern=GimpPatPattern()
        self.filename:Union[str,None]=None
        if filename is not None:
            self.load(filename)

    def load(self,filename:Union[str,BinaryIO])->None:
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

    def _decode_(self,data,index=0):
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        index=self.brush._decode_(data,index)
        index=self.pattern._decode_(data,index)
        return index
        
    def toBytes(self):
        """
        encode this object to a byte array
        """
        io=IO()
        io.addBytes(self.brush.toBytes())
        io.addBytes(self.pattern.toBytes())
        return io.data

    def save(self,toFilename:Union[None,str,BinaryIO]=None,toExtension:Optional[str]=None):
        """
        save this gimp image to a file
        """
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.gpb'
            toFilename=self.filename
        elif hasattr(toFilename,'write'):
            self.filename=toFilename.name
        else:
            self.filename=toFilename
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
        ret.append(self.brush.__repr__(indent+'\t'))
        ret.append(self.pattern.__repr__(indent+'\t'))
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
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                g=GimGpbBrush(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGpbBrush.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
