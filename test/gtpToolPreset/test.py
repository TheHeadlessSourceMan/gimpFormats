#!/usr/bin/env
# -*- coding:utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
#from imageTools import compareImage
from gimpFormats import GimpGtpToolPreset


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
class Test(unittest.TestCase):
    """
    Run unit test
    """

    def setUp(self):
        self.dut=GimpGtpToolPreset()

    def tearDown(self):
        pass

    def testSmudgeRough(self):
        """
        Test against the smudge rough tool preset
        """
        self.dut.load(__HERE__+'Smudge-Rough.gtp')
        # test string representation
        asStr=repr(self.dut)()
        assert asStr
        # test round-trip compatibility
        self.dut.save(__HERE__+'actualOutput_Smudge-Rough.gtp')
        original=open(__HERE__+'Smudge-Rough.gtp','rb').read()
        actual=open(__HERE__+'actualOutput_Smudge-Rough.gtp','rb').read()
        assert actual==original
        os.remove(__HERE__+'actualOutput_Smudge-Rough.gtp')


def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testSmudgeRough"))
    return testSuite


def cmdline(args):
    """
    Run the command line

    :param args:command line arguments (WITHOUT the filename)

    Run all the test suites in the standard way.
    """
    _=args
    unittest.main()


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
