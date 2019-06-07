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
		self.dut=GimpGbrBrush()
		
	def tearDown(self):
		pass
		
	def testPepper(self):
		self.dut.load(__HERE__+'pepper.gbr')
		# test image saving (implicit)
		self.dut.save(__HERE__+'actualOutput_pepper.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_pepper.png')
		assert same
		os.remove(__HERE__+'actualOutput_pepper.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_pepper.gbr')
		original=open(__HERE__+'pepper.gbr','rb').read()
		actual=open(__HERE__+'actualOutput_pepper.gbr','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_pepper.gbr')
		
	def testDunes(self):
		self.dut.load(__HERE__+'dunes.gbr')
		# test image saving (explicit)
		self.dut.image.save(__HERE__+'actualOutput_dunes.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_dunes.png')
		assert same
		os.remove(__HERE__+'actualOutput_dunes.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_dunes.gbr')
		original=open(__HERE__+'dunes.gbr','rb').read()
		actual=open(__HERE__+'actualOutput_dunes.gbr','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_dunes.gbr')

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("testDunes"))
	testSuite.addTest(Test("testPepper"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()