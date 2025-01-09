#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Gimp Image Pipe Format

The gih format is use to store a series of brushes, and some extra info
for how to use them.
"""
import typing
from collections import OrderedDict
from PIL.Image import Image
from gimpFormats.binaryIO import IO
from gimpFormats.gimpGbrBrush import GimpGbrBrush

class GimpGihBrushSet:
    """
    Gimp Image Pipe Format

    The gih format is use to store a series of brushes, and some extra info
    for how to use them.

    See:
        https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/gih.txt

    Format:
        name: GimpGihBrushSet
        description: Gimp brush set
        guid: {45129576-6728-4967-8888-6b9082862ca1}
        parentNames: [Brush]
        #mimeTypes: application/jpeg
        filenamePatterns: *.gih
    """

    def __init__(self,
        filename:typing.Union[None,str,typing.BinaryIO]=None
        )->None:
        """ """
        self.filename:typing.Optional[str]=None
        self.name:str=''
        self.params:OrderedDict=OrderedDict()
        self.brushes:typing.List[GimpGbrBrush]=[]
        if filename is not None:
            self.load(filename)

    @property
    def images(self)->typing.Iterable[Image]:
        """
        The brush images
        """
        ret=[]
        for brush in self.brushes:
            if brush.image is not None:
                ret.append(brush.image)
        return ret

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

    def _decode_(self,data:bytes,index:int=0)->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        io=IO(data,index)
        self.name=io.textLine
        secondLine=io.textLine.split(' ')
        self.params=OrderedDict()
        numBrushes=int(secondLine[0])
        # everything that's left in line 2
        # is a gimp-image-pipe-parameters parasite
        for i in range(1,len(secondLine)):
            param=secondLine[i].split(':',1)
            self.params[param[0].strip()]=param[1].strip()
        self.brushes=[]
        for _ in range(numBrushes):
            b=GimpGbrBrush()
            # NOTE: expects GimpGbrBrush._decode_ to be the num bytes read
            #  I don't know whether this is right, wrong, or sideways,
            #  but there you have it
            io.index+=b._decode_(io.data,io.index) # pylint: disable=protected-access # noqa: E501
            self.brushes.append(b)
        return io.index

    def toBytes(self)->bytes:
        """
        encode this object to a byte array
        """
        io=IO()
        io.textLine=self.name
        # add the second line of data
        secondLineA=[str(len(self.brushes))]
        for k,v in self.params.items():
            secondLineA.append(k+':'+str(v))
        secondLine=' '.join(secondLineA)
        io.textLine=secondLine
        # add the brushes
        for brush in self.brushes:
            #TODO: currently broken.  This results in header insterted twice
            # for some reason!
            io.addBytes(brush.toBytes())
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
                self.filename='untitled.gih'
            toFilename=self.filename
        elif isinstance(toFilename,str):
            self.filename=toFilename
        else:
            f=toFilename
            toFilename=toFilename.name
            self.filename=toFilename
        if toExtension is None:
            toExtension=self.filename.rsplit('.',1)[-1]
        if toExtension=='gih':
            if f is None:
                f=open(toFilename,'wb')
            f.write(self.toBytes())
        elif toExtension=='gbr':
            # export the brush set as a series of brush files
            baseFilename=toFilename.rsplit('.',1)[0]
            for i,brush in enumerate(self.brushes):
                modFilename=f'{baseFilename}_{i}.{toExtension}'
                brush.save(modFilename)
        else:
            # export the brush set as a series of image files
            baseFilename=toFilename.rsplit('.',1)[0]
            for i,brush in enumerate(self.brushes):
                modFilename=f'{baseFilename}_{i}.{toExtension}'
                brush.save(modFilename,toExtension)

    def __repr__(self,indent=''):
        """
        Get a textual representation of this object
        """
        ret=[]
        if self.filename is not None:
            ret.append('Filename: '+self.filename)
        ret.append('Name: '+str(self.name))
        for k,v in list(self.params.items()):
            ret.append(k+': '+str(v))
        for i,brush in enumerate(self.brushes):
            ret.append('Brush '+str(i))
            ret.append(brush.__repr__(indent+'\t'))
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
                    if arg[1]=='*':
                        for brush in g.brushes:
                            brush.image.show()
                    else:
                        g.brushes[int(arg[1])].image.show()
                elif arg[0]=='--save':
                    index,filename=arg[1].split(',',1)
                    if filename.find('*')<0:
                        filename='*.'.join(filename.split('.',1))
                    if index=='*':
                        for i,brush in enumerate(g.brushes):
                            fn2=filename.replace('*',str(i))
                            brush.image.save(fn2)
                    else:
                        fn2=filename.replace('*',i)
                        g.brushes[int(index)].image.save(fn2)
                else:
                    print(f'ERR: unknown argument "{arg}"')
            else:
                g=GimpGihBrushSet(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGihBrushSet.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --show=n .............. show the brush image(s) n=* for all')
        print('   --save=n,out.jpg ...... save out the brush image(s)')
        print('   --register ............ register this extension')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
