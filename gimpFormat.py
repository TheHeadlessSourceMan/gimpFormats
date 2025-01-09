#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp file formats
"""
import typing
from gimpFormats.gimpXcfDocument import GimpDocument


register=False


class GimpFormatPlugin:
    """
    A plugin to the gimp format
    """
    # TODO: implement this?


# ========= automatically add format info for pyformatgenie =========
if register:
    try:
        # will run this every time this module is loaded
        import pyformatgenie # type:ignore
        pfg=pyformatgenie.PyFormatGenie()
        pfg.add(GimpFormatPlugin)
        # and the most important part...
        pfg.save()
    except ImportError:
        # pyformatgenie is not installed (yet?). Continue with
        # whatever you came here for.
        pass


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        g:typing.Optional[GimpDocument]=None
        for arg in args:
            if arg.startswith('-'):
                kv=[a.strip() for a in arg.split('=',1)]
                if kv[0] in ('-h','--help'):
                    printhelp=True
                elif kv[0]=='--dump':
                    print(g)
                elif kv[0]=='--showLayer':
                    if g is None:
                        print('ERR: No image')
                        continue
                    if kv[1]=='*':
                        for n,layer in enumerate(g.layers):
                            i=layer.image
                            if i is None:
                                print('No image for layer',n)
                            else:
                                print('showing layer',n)
                                i.show()
                    else:
                        i=g.layers[int(kv[1])].image
                        if i is None:
                            print('No image for layer',int(kv[1]))
                        else:
                            print('showing layer',kv[1])
                            i.show()
                elif kv[0]=='--saveLayer':
                    if g is None:
                        print('ERR: No image')
                        continue
                    layerName=kv[1].split(',',1)
                    if len(layerName)>1:
                        filename=layerName[1]
                    else:
                        filename='layer *.png'
                    layerId=kv[1][0]
                    if layerId=='*':
                        if filename.find('*')<0:
                            fnParts=filename.split('.',1)
                            fnParts.insert(1,'*')
                            filename='.'.join(fnParts)
                        for n,layer in enumerate(g.layers):
                            i=layer.image
                            if i is None:
                                print('No image for layer',n)
                            else:
                                fn2=filename.replace('*',str(n))
                                print('saving layer',fn2)
                                i.save(fn2)
                    else:
                        i=g.layers[int(layerId)].image
                        if i is None:
                            print('No image for layer',layerId)
                        else:
                            i.save(filename.replace('*',layerId))
                else:
                    print(f'ERR: unknown argument "{arg}"')
            else:
                g=GimpDocument(arg)
    if printhelp:
        print('Usage:')
        print('  gimpFormat.py file.xcf [options]')
        print('Options:')
        print('   -h, --help ............ this help screen')
        print('   --dump ................ dump info about this file')
        print('   --showLayer=n ......... show layer(s) (use * for all)')
        print('   --saveLayer=n,out.jpg . save layer(s) out to file')
        print('   --register ............ register this extension')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
