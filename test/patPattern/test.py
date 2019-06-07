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
		self.dut=GimpPatPattern()
		
	def tearDown(self):
		pass
		
	def test3dgreen(self):
		self.dut.load(__HERE__+'3dgreen.pat')
		# test image saving (implicit)
		self.dut.save(__HERE__+'actualOutput_3dgreen.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_3dgreen.png')
		assert same
		os.remove(__HERE__+'actualOutput_3dgreen.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_3dgreen.pat')
		original=open(__HERE__+'3dgreen.pat','rb').read()
		actual=open(__HERE__+'actualOutput_3dgreen.pat','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_3dgreen.pat')
		
	def testLeopard(self):
		self.dut.load(__HERE__+'leopard.pat')
		# test image saving (explicit)
		self.dut.image.save(__HERE__+'actualOutput_leopard.png')
		# test for image match
		same=compareImage(self.dut.image,__HERE__+'desiredOutput_leopard.png')
		assert same
		os.remove(__HERE__+'actualOutput_leopard.png')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_leopard.pat')
		original=open(__HERE__+'leopard.pat','rb').read()
		actual=open(__HERE__+'actualOutput_leopard.pat','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_leopard.pat')

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("test3dgreen"))
	testSuite.addTest(Test("testLeopard"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()