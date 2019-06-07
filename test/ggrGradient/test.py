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
		self.dut=GimpGgrGradient()
		
	def tearDown(self):
		pass
		
	def colorArray(self,numPoints):
		colors=[]
		i=0.0
		inc=1.0/numPoints
		while i<1.0:
			colors.append(self.dut.getColor(i))
			i+=inc
		return colors
		
	def saveColors(self,f,colorArray):
		f.write('r, g, b, a\n'.encode('utf-8'))
		for c in colorArray:
			line=[]
			for chan in c:
				line.append(str(c))
			line=', ',join(line)+'\n'
			f.write(line.encode('utf-8'))
		
	def testColdSteel(self):
		self.dut.load(__HERE__+'Cold_Steel_2.ggr')
		# test round-trip compatibility
		self.dut.save(__HERE__+'actualOutput_Cold_Steel_2.ggr')
		original=open(__HERE__+'Cold_Steel_2.ggr','rb').read()
		actual=open(__HERE__+'actualOutput_Cold_Steel_2.ggr','rb').read()
		assert actual==original
		os.remove(__HERE__+'actualOutput_Cold_Steel_2.ggr')
		# TODO: test calculated colors
		#colors=self.colorArray(512)
		#actual=open(__HERE__+'actualOutput_Cold_Steel_2.csv','wb')
		#saveColors(actual,colors)

		
def testSuite():
	"""
	Combine unit tests into an entire suite
	"""
	testSuite = unittest.TestSuite()
	testSuite.addTest(Test("testColdSteel"))
	return testSuite
		
		
if __name__ == '__main__':
	"""
	Run all the test suites in the standard way.
	"""
	unittest.main()