#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Pure python implementation of the gimp file formats
"""
from gimpFormats.gimpXcfDocument import *
from gimpFormats.gimpGbrBrush import *
from gimpFormats.gimpGgrGradient import *
from gimpFormats.gimpGihBrushSet import *
from gimpFormats.gimpGpbBrush import *
from gimpFormats.gimpGtpToolPreset import *
from gimpFormats.gimpPatPattern import *
from gimpFormats.gimpVbrBrush import *


register=False


class GimpFormatPlugin:
    pass
    

# ========= automatically add format info for pyformatgenie =========
if register:
    try:
        # will run this every time this module is loaded
        import pyformatgenie
        pfg=pyformatgenie.PyFormatGenie()
        pfg.add(GimpFormatPlugin)
        # and the most important part...
        pfg.save()
    except ImportError as e:
        # pyformatgenie is not installed (yet?). Continue with whatever you came here for.
        pass


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
                elif arg[0]=='--showLayer':
                    if arg[1]=='*':
                        for n in range(len(g.layers)):
                            i=g.layers[n].image
                            if i is None:
                                print('No image for layer',n)
                            else:
                                print('showing layer',n)
                                i.show()
                    else:
                        i=g.layers[int(arg[1])].image
                        if i is None:
                            print('No image for layer',int(arg[1]))
                        else:
                            print('showing layer',arg[1])
                            i.show()
                elif arg[0]=='--saveLayer':
                    layer=arg[1].split(',',1)
                    if len(layer)>1:
                        filename=layer[1]
                    else:
                        filename='layer *.png'
                    layer=arg[1][0]
                    if layer=='*':
                        if filename.find('*')<0:
                            filename='.'.join(filename.split('.',1).insert(1,'*'))
                        for n in range(len(g.layers)):
                            i=g.layers[n].image
                            if i is None:
                                print('No image for layer',n)
                            else:
                                fn2=filename.replace('*',str(n))
                                print('saving layer',fn2)
                                i.save(fn2)
                    else:
                        i=g.layers[int(layer)].image
                        if i is None:
                            print('No image for layer',layer)
                        else:
                            i.save(filename.replace('*',layer))
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
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


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
