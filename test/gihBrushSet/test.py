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
    """

    def setUp(self):
        self.dut=GimpGihBrushSet()
        
    def tearDown(self):
        pass
        
    def testBrushSet(self,filename):
        """
        :param filename: without extension
        """
        source='%s%s.gih'%(__HERE__,filename)
        dest='%sactual_%s.gih'%(__HERE__,filename)
        self.dut.load(source)
        # test string representation
        asStr=self.dut.__repr__()
        assert asStr
        # new check all the internal brushes
        for id,image in enumerate(self.dut.images):
            # test image saving (explicit)
            brushActual= '%sactualOutput_%s_%02d.png'%(__HERE__,filename,id+1)
            brushDesired='%sdesiredOutput_%s_%02d.png'%(__HERE__,filename,id+1)
            image.save(brushActual)
            # test for image match
            same=compareImage(image,brushDesired)
            assert same
            os.remove(brushActual)
        # test round-trip compatibility
        self.dut.save(dest)
        original=open(source,'rb').read()
        actual=open(dest,'rb').read()
        assert actual==original
        os.remove(dest)
        
    def testWilber(self):
        self.testBrushSet('Wilber')
        
    def testFeltpen(self):
        self.testBrushSet('feltpen')

        
def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testWilber"))
    testSuite.addTest(Test("testFeltpen"))
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
