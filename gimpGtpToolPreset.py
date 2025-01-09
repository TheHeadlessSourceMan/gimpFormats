#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp gtp tool preset format
"""
import typing


class ParenFileValue:
    """
    A parentheses-based file format
    (possibly "scheme" language?)
    """

    def __init__(self)->None:
        self.name:typing.Optional[str]=None
        self.values:typing.List[typing.Union[str,float,bool]]=[]

    def _addValue(self,bufArray:typing.List[str])->None:
        if self.name is None: # first value is the name
            self.name=bufArray[0]
        if bufArray:
            bufStr=''.join(bufArray)
            if bufStr in ('yes','no'): # boolean
                self.values.append(bufStr=='yes')
            elif bufStr[0].isdigit() or bufStr[0] in ('-','.'):
                if bufStr[0]=='.':
                    bufStr='0'+bufStr
                self.values.append(float(bufStr))
            elif bufStr[0]=='"':
                self.values.append(bufStr[1:-1])
            else:
                msg=f'Unknown value "{bufArray}" while setting "{self.name}"'
                raise Exception(msg)

    def __repr__(self,indent:str='')->str:
        """
        Get a textual representation of this object
        """
        ret=[]
        ret.append('Value Type: '+str(self.name))
        for v in self.values:
            if isinstance(v,ParenFileValue):
                ret.append(v.__repr__(indent+'\t'))
            else:
                ret.append(str(v))
        return ('\n'+indent).join(ret)


def parenFileDecode(
    data:typing.Union[str,bytes],
    index:int=0
    )->typing.Tuple[int,typing.Iterable[ParenFileValue]]:
    """
    Decode a parentheses-based file format
    (possibly "scheme" language?)
    """
    values=[]
    if isinstance(data,bytes):
        data=data.decode('utf-8')
    maxIndex=len(data)
    def pDec(data,index=0):
        """
        helper routine to parse a single value
        """
        pval=ParenFileValue()
        ws=[' ','\t','\r','\n']
        if index==0:
            while index<maxIndex:
                c=data[index]
                index+=1
                if c=='(':
                    break
        building=[]
        while index<maxIndex:
            while index<maxIndex: # skip any whitespace
                c=data[index]
                if c!=' ':
                    break
                index+=1
            while c not in ws and c!=')':
                if index>=maxIndex:
                    break
                building.append(c)
                c=data[index]
                index+=1
            pval.name=''.join(building)
            building=[]
            while index<maxIndex: # for each value
                pval._addValue(building) # pylint: disable=protected-access
                building=[]
                while index<maxIndex: # skip any whitespace
                    c=data[index]
                    if c not in ws:
                        break
                    index+=1
                if c==')': # finished
                    pval._addValue(building) # pylint: disable=protected-access
                    return index+1,pval
                if c=='(': # child value
                    index,v=pDec(data,index+1)
                    pval.values.append(v)
                elif c=='"': # parse a whole string
                    building.append(c)
                    while True:
                        index+=1
                        if index>=maxIndex:
                            break
                        c=data[index]
                        building.append(c)
                        if c=='"':
                            break
                    pval._addValue(building) # pylint: disable=protected-access
                    building=[]
                    index+=1
                else:
                    building.append(c)
                    index+=1
        return index,pval
    while index<maxIndex:
        index,pval=pDec(data,index)
        values.append(pval)
    return index,values


def parenFileEncode(values:typing.List[ParenFileValue])->str:
    """
    encode a values tree to a buffer
    """
    ret=[]
    ret.append('# GIMP tool preset file')
    ret.append('')
    for val in values:
        if val.name is not None:
            ret.append(str(val))
    ret.append('')
    ret.append('# end of GIMP tool preset file')
    ret.append('')
    return '\n'.join(ret)


class GimpGtpToolPreset:
    """
    Pure python implementation of the gimp gtp tool preset format

    Format:
        name: GimpGtpToolPreset
        description: Gimp tool preset
        guid: {45129576-6728-4967-8888-6b9082862ca4}
        #parentNames:
        #mimeTypes: application/jpeg
        filenamePatterns: *.gtp
    """

    def __init__(self,
        filename:typing.Union[None,str,typing.BinaryIO]=None):
        """ """
        self.values:typing.List[ParenFileValue]=[]
        self.filename:typing.Optional[str]=None
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

    def _decode_(self,data:typing.Union[str,bytes],index:int=0)->int:
        """
        decode a byte buffer

        :param data: data buffer to decode
        :param index: index within the buffer to start at
        """
        index,values=parenFileDecode(data,index)
        self.values=list(values)
        return index

    def toBytes(self)->bytes:
        """
        encode to bytes
        """
        return parenFileEncode(self.values).encode('utf-8')

    def save(self,
        toFilename:typing.Union[str,None,typing.BinaryIO]=None,
        toExtension:typing.Optional[str]=None
        )->None:
        """
        save this gimp tool preset to a file
        """
        f=None
        if toFilename is None:
            if self.filename is None:
                self.filename='untitled.gtp'
            toFilename=self.filename
        elif isinstance(toFilename,str):
            self.filename=toFilename
        else:
            f=toFilename
            toFilename=f.name
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
        for v in self.values:
            ret.append(v.__repr__(indent+'\t'))
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
                else:
                    print(f'ERR:unknown argument "{arg}"')
            else:
                g=GimpGtpToolPreset(arg)
    if printhelp:
        print('Usage:')
        print('  gimpGtpToolPreset.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --register ............ register this extension')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
