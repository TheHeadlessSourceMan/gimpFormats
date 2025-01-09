#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Gimp color gradient
"""
import typing
from enum import Enum


RgbaColorTuple=typing.Union[
    typing.Tuple[int,int,int,int],
    typing.Tuple[float,float,float,float]]


BLEND_FUNCTIONS=Enum('BLEND_FUNCTIONS',start=0,names=(
    "linear","curved","sinusoidal","spherical (increasing)",
    "spherical (decreasing)","step"
    ))

COLOR_TYPES=Enum('COLOR_TYPES',start=0,names=(
    "RGB","HSV CCW","HSV CW"
    ))

ENDPOINT_COLOR_TYPES=Enum('ENDPOINT_COLOR_TYPES',start=0,names=(
    "fixed","foreground","foreground transparent",
    "background","background transparent"
    ))

class GradientSegment:
    """
    Single segment within a gradient
    """

    def __init__(self)->None:
        self.leftPosition:float=0
        self.middlePosition:float=0.5
        self.rightPosition:float=1.0
        self.leftColor:RgbaColorTuple=(0,0,0,0)
        self.rightColor:RgbaColorTuple=(255,255,255,0)
        self.blendFunc:typing.Optional[BLEND_FUNCTIONS]=None
        self.colorType:typing.Optional[COLOR_TYPES]=None
        self.leftColorType:typing.Optional[ENDPOINT_COLOR_TYPES]=None
        self.rightColorType:typing.Optional[ENDPOINT_COLOR_TYPES]=None

    def getColor(self,percent:float)->RgbaColorTuple:
        """
        given a decimal percent (1.0 = 100%) retrieve
        the appropriate color for this point in the gradient
        """
        raise NotImplementedError()

    def _decode_(self,
        data:typing.Union[str,typing.List[str]],
        index:int=0)->None:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        if isinstance(data,str):
            data=data.split(' ')
        if index!=0:
            data=data[index:]
        if len(data)<11 or len(data)>15:
            raise IndexError('Data table is unexpected size. '+str(len(data)))
        self.leftPosition=float(data[0])
        self.middlePosition=float(data[1])
        self.rightPosition=float(data[2])
        self.leftColor=(
            float(data[3]),float(data[4]),float(data[5]),float(data[6]))
        self.rightColor=(
            float(data[7]),float(data[8]),float(data[9]),float(data[10]))
        if len(data)>=12:
            self.blendFunc=BLEND_FUNCTIONS(int(data[11]))
            if len(data)>=13:
                self.colorType=COLOR_TYPES(int(data[12]))
                if len(data)>=14:
                    self.leftColorType=ENDPOINT_COLOR_TYPES(int(data[13]))
                    if len(data)>=15:
                        self.rightColorType=ENDPOINT_COLOR_TYPES(int(data[14]))

    def encode(self)->str:
        """
        encode this to a string
        """
        ret=[]
        ret.append("%06f"%self.leftPosition)
        ret.append("%06f"%self.middlePosition)
        ret.append("%06f"%self.rightPosition)
        for chan in self.leftColor:
            ret.append("%06f"%chan)
        for chan in self.rightColor:
            ret.append("%06f"%chan)
        if self.blendFunc is not None:
            ret.append(str(self.blendFunc))
            if self.colorType is not None:
                ret.append(str(self.blendFunc))
                if self.leftColorType is not None:
                    ret.append(str(self.blendFunc))
                    if self.rightColorType is not None:
                        ret.append(str(self.blendFunc))
        return ' '.join(ret)

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        ret.append(f'Left Position: {self.leftPosition}')
        ret.append(f'Middle Position: {self.middlePosition}')
        ret.append(f'Right Position: {self.rightPosition}')
        ret.append(f'Left Color: {self.leftColor}')
        ret.append(f'Right Color: {self.rightColor}')
        if self.blendFunc is None:
            s="None"
        else:
            s=self.blendFunc.name
        ret.append('Blend Function: '+s)
        if self.colorType is None:
            s="None"
        else:
            s=self.colorType.name
        ret.append('Color Type: '+s)
        if self.leftColorType is None:
            s="None"
        else:
            s=self.leftColorType.name
        ret.append('Left Color Type: '+s)
        if self.rightColorType is None:
            s="None"
        else:
            s=self.rightColorType.name
        ret.append('Right Color Type: '+s)
        return ('\n'+indent).join(ret)


class GimpGgrGradient:
    """
    Gimp golor gradient

    See:
        https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/ggr.txt

    Format:
        name: GimpGgrGradient
        description: Gimp color gradient file
        guid: {45129576-6728-4967-8888-6b9082862ca0}
        parentNames: ColorGradient
        #mimeTypes: application/jpeg
        filenamePatterns: *.ggr
    """

    MAGIC_NUMBER=(0,'GIMP Gradient')

    def __init__(self,filename:typing.Optional[str]=None)->None:
        self.filename:typing.Optional[str]=None
        self.segments:typing.List[GradientSegment]=[]
        self.name:str=''
        if filename is not None:
            self.load(filename)

    def load(self,
        filename:typing.Union[str,typing.BinaryIO]
        )->None:
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

    def _decode_(self,
        data:typing.Union[bytes,str,typing.List[str]],
        index:int=0)->None:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        if isinstance(data,bytes):
            if index!=0:
                data=data[index:]
            data=data.decode('utf-8')
        if isinstance(data,str):
            data=data[index:].split('\n')
        data=[l.strip() for l in data] # noqa: E741
        if data[0]!='GIMP Gradient':
            raise Exception('File format error.  Magic value mismatch.')
        self.name=data[1].split(':',1)[-1].strip()
        numSegments=int(data[2])
        for i in range(numSegments):
            gs=GradientSegment()
            gs._decode_(data[i+3]) # pylint: disable=protected-access
            self.segments.append(gs)

    def encode(self)->str:
        """
        encode this to a string
        """
        ret=['GIMP Gradient']
        ret.append('Name: '+self.name)
        ret.append(str(len(self.segments)))
        for segment in self.segments:
            ret.append(segment.encode())
        return ('\n'.join(ret)+'\n')

    def toBytes(self)->bytes:
        """
        encode this to bytes
        """
        return self.encode().encode('utf-8')

    def save(self,
        toFilename:typing.Union[None,str,typing.BinaryIO]=None,
        toExtension:typing.Optional[str]=None
        )->None:
        """
        save this gimp image to a file
        """
        if toExtension is not None and toExtension!='ggr':
            msg=f'Unable to convert to extension "{toExtension}"'
            raise Exception(msg)
        if toFilename is None:
            if self.filename is None:
                self.filename='Untitled.ggr'
            toFilename=self.filename
        elif not isinstance(toFilename,str):
            toFilename=toFilename.name
            self.filename=toFilename
        else:
            if toFilename.rsplit('.',1)[-1].lower()!='ggr':
                msg=f'Unable to convert to extension "{toExtension}"'
                raise Exception(msg)
            self.filename=toFilename
        if not hasattr(toFilename,'write'):
            f=open(toFilename,'wb')
        f.write(self.toBytes())

    def getColor(self,percent:float)->RgbaColorTuple:
        """
        given a decimal percent (1.0 = 100%) retrieve
        the appropriate color for this point in the gradient
        """
        raise NotImplementedError()

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        if self.filename is not None:
            ret.append('Filename: '+self.filename)
        ret.append('Name: '+str(self.name))
        for s in self.segments:
            ret.append(s.__repr__(indent+'\t'))
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
        g:typing.Optional[GimpGgrGradient]=None
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
                g=GimpGgrGradient(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGgrGradient.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
