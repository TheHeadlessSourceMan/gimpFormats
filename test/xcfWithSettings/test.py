#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
from gimpFormats import *
from imageTools import *


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
class Test(unittest.TestCase):
    """
    Run unit test
    
    This tests a gimp file with selections and other active settings
    """

    def setUp(self):
        self.dut=GimpDocument()
        
    def tearDown(self):
        pass
        
    def testImage(self):
        self.dut.load(__HERE__+'with_settings.xcf')
        # test string representation
        asStr=self.dut.__repr__()
        assert asStr
        # test string representation
        asStr=self.dut.__repr__()
        assert asStr
        #TODO: selection should be the same as the layer's mask
        mask=self.dut.layers[1].mask
        for sel in self.dut.vectors:
            path=sel.svgPath
            print('\nSelection (%d) "%s" = %s'%(len(sel.strokes),sel.name,path))
        #self.dut.save(__HERE__+'actualOutput.png')
        #same=compareImage(self.dut.layers[0].image,__HERE__+'desiredOutput.png')
        #assert same

        
def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testImage"))
    return testSuite
        
        
def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    """
    Run all the test suites in the standard way.
    """
    unittest.main()


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
