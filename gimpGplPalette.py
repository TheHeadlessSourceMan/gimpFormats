#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gpl palette format
"""
import typing


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

    def __init__(self,
        filename:typing.Union[None,str,typing.BinaryIO]=None):
        """ """
        self.name:str=''
        self.columns:int=16
        self.colors:typing.List[typing.Tuple[int,int,int]]=[]
        self.colorNames:typing.List[typing.Optional[str]]=[]
        self.filename:typing.Optional[str]=None
        if filename is not None:
            self.load(filename)

    def load(self,
        filename:typing.Union[str,typing.BinaryIO]
        )->None:
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

    def _decode_(self,
        data:typing.Union[str,bytes,typing.List[str]],
        index:int=0
        )->None:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        if isinstance(data,bytes):
            data=data.decode('utf-8')
        if isinstance(data,str):
            data=[s.strip() for s in data.split('\n')]
        if index!=0:
            data=data[index:]
        if data[0]!="GIMP Palette":
            raise Exception('File format error.  Magic value mismatch.')
        self.name=data[1].split(':',1)[-1].lstrip()
        self.columns=int(data[2].split(':',1)[-1].lstrip())
        if data[3]!="#":
            raise Exception('File format error.  Separtor missing.')
        for line in data[4:]:
            lineArry=line.split(None,4)
            if len(lineArry)<3:
                continue
            self.colors.append(
                (int(lineArry[0]),int(lineArry[1]),int(lineArry[2])))
            if len(lineArry)>3:
                self.colorNames.append(' '.join(lineArry[3:]))
            else:
                self.colorNames.append(None)

    def toBytes(self)->bytes:
        """
        encode to a raw data stream
        """
        data=[]
        data.append("GIMP Palette")
        data.append(f'Name: {self.name}')
        data.append(f'Columns: {self.columns}')
        data.append("#")
        for i,color in enumerate(self.colors):
            colorName=self.colorNames[i]
            line=' '.join([str(c).rjust(3) for c in color])
            if colorName is not None:
                line=line+'\t'+colorName
            data.append(line)
        return ('\n'.join(data)+'\n').encode('utf-8')

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
                self.filename='untitled.gpl'
            toFilename=self.filename
        elif isinstance(toFilename,str):
            self.filename=toFilename
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
        ret.append('Columns: '+str(self.columns))
        ret.append('Colors:')
        for i,color in enumerate(self.colors):
            colorName=self.colorNames[i]
            line='(%d,%d,%d)'%(color[0],color[1],color[2])
            if colorName is not None:
                line=line+' '+colorName
        return indent+(('\n'+indent).join(ret))

    def __eq__(self,other:typing.Any)->bool:
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
                else:
                    print(f'ERR: unknown argument "{arg}"')
            else:
                g=GimpGplPalette(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGplPalette.py palette.gpl [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
