#!/usr/bin/env
# -*- coding: utf-8 -*-
from typing import Optional, Union, BinaryIO, List, Tuple

"""
Pure python implementation of the gimp gpl palette format
"""


class GimpGplPalette:
    """
    Pure python implementation of the gimp gpl palette format
        
    Format:
        name: GimpGplPalette
        description: Gimp color palette
        guid: {45129576-6728-4967-8888-6b9082862ca3}
        parentNames: [Color]
        #mimeTypes: application/jpeg
        filenamePatterns: *.gpl
    """
    
    MAGIC_NUMBER=(0,"GIMP Palette")

    def __init__(self,filename: Union[None,str,BinaryIO]=None) -> None:
        self.name:str=''
        self.columns:int=16
        self.colors:List[Tuple[int,int,int]]=[]
        self.colorNames:List[Union[str,None]]=[]
        self.filename:Union[str,None]=None
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
            f=open(filename,'r')
            data=f.read()
            f.close()
        self._decode_(data)

    def _decode_(self,data: Union[str,bytes],index: int=0) -> None:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        if isinstance(data,bytes):
            data=data.decode('utf-8')
        data=[s.strip() for s in data.split('\n')]
        if data[0]!="GIMP Palette":
            raise Exception('File format error.  Magic value mismatch.')
        self.name=data[1].split(':',1)[-1].lstrip()
        self.columns=int(data[2].split(':',1)[-1].lstrip())
        if data[3]!="#":
            raise Exception('File format error.  Separtor missing.')
        for line in data[4:]:
            line=line.split(None,4)
            if len(line)<3:
                continue
            self.colors.append((int(line[0]),int(line[1]),int(line[2])))
            if len(line)>3:
                self.colorNames.append(' '.join(line[3:]))
            else:
                self.colorNames.append(None)

    def toBytes(self) -> bytes:
        """
        encode to a raw data stream
        """
        data=[]
        data.append("GIMP Palette")
        data.append('Name: '+str(self.name))
        data.append('Columns: '+str(self.columns))
        data.append("#")
        for i,color in enumerate(self.colors):
            colorName=self.colorNames[i]
            line=str(color[0]).rjust(3)+' '+str(color[1]).rjust(3)+' '+str(color[2]).rjust(3)
            if colorName is not None:
                line=line+'\t'+colorName
            data.append(line)
        return ('\n'.join(data)+'\n').encode('utf-8')

    def save(self,toFilename: Union[None,str,BinaryIO]=None,toExtension: None=None) -> None:
        """
        save this gimp image to a file
        """
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.gpl'
            toFilename=self.filename
        elif hasattr(toFilename,'write'):
            self.filename=toFilename.name
        else:
            self.filename=toFilename
        if toExtension is None:
            if toFilename is not None:
                toExtension=toFilename.rsplit('.',1)
                if len(toExtension)>1:
                    toExtension=toExtension[-1]
                else:
                    toExtension=None
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
        ret.append('Columns: '+str(self.columns))
        ret.append('Colors:')
        for i,color in enumerate(self.colors):
            colorName=self.colorNames[i]
            line='(%d,%d,%d)'%color[0],color[1],color[2]
            if colorName is not None:
                line=line+' '+colorName
        return '\n'.join(ret)

    def __eq__(self,other):
        """
        perform a comparison
        """
        if other.name!=self.name:
            return False
        if other.columns!=self.columns:
            return False
        if len(self.colors)!=len(other.colors):
            return False
        for i,c in enumerate(self.colors):
            if c!=other.colors[i]:
                return False
            if self.colorNames[i]!=other.colorNames[i]:
                return False
        return True


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
                g=GimpVbrBrush(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGplPalette.py palette.gpl [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
