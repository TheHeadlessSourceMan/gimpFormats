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
		self.dut=GimpGplPalette()
		
	def tearDown(self):
		pass
		
	def testPlasma(self):
		self.dut.load(__HERE__+'Plasma.gpl')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_Plasma.gpl')
		original=open(__HERE__+'Plasma.gpl','rb').read()
		actual=open(__HERE__+'actualOutput_Plasma.gpl','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_Plasma.gpl')

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("testPlasma"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()