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
		self.dut=GimpGihBrushSet()
		
	def tearDown(self):
		pass
		
	def testWilber(self):
		self.dut.load(__HERE__+'Wilber.gih')
		# test image saving (implicit)
		self.dut.save(__HERE__+'actualOutput_Wilber.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_Wilber.png')
		assert same
		os.remove(__HERE__+'actualOutput_Wilber.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_Wilber.gih')
		original=open(__HERE__+'Wilber.gih','rb').read()
		actual=open(__HERE__+'actualOutput_Wilber.gih','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_Wilber.gih')
		
	def testFeltpen(self):
		self.dut.load(__HERE__+'feltpen.gih')
		# test image saving (explicit)
		self.dut.image.save(__HERE__+'actualOutput_feltpen.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_feltpen.png')
		assert same
		os.remove(__HERE__+'actualOutput_feltpen.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_feltpen.gih')
		original=open(__HERE__+'feltpen.gih','rb').read()
		actual=open(__HERE__+'actualOutput_feltpen.gih','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_feltpen.gih')

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("testWilber"))
	testSuite.addTest(Test("testFeltpen"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()