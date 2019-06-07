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
		self.dut=GimpGtpToolPreset()
		
	def tearDown(self):
		pass
		
	def testSmudgeRough(self):
		self.dut.load(__HERE__+'Smudge-Rough.gtp')
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
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()