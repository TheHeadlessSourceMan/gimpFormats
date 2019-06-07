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
from smartimage.imgTools import *


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep
class Test(unittest.TestCase):
	"""
	Run unit test
	"""

	def setUp(self):
		self.dut=GimpVbrBrush()
		
	def tearDown(self):
		pass
		
	def testDiagonalStar(self):
		self.dut.load(__HERE__+'Diagonal-Star-17.vbr')
		# test image saving (explicit)
		#self.dut.image.save(__HERE__+'actualOutput_Diagonal-Star-17.png')
		# test for image match
		#same=compareImage(self.dut.image,__HERE__+'desiredOutput_Diagonal-Star-17.png')
		#assert same
		#os.remove(__HERE__+'actualOutput_Diagonal-Star-17.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_Diagonal-Star-17.vbr')
		original=GimpVbrBrush(__HERE__+'Diagonal-Star-17.vbr')#open(__HERE__+'Diagonal-Star-17.vbr','rb').read()
		actual=self.dut#open(__HERE__+'actualOutput_Diagonal-Star-17.vbr','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_Diagonal-Star-17.vbr')

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("testDiagonalStar"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()