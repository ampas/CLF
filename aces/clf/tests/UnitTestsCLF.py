#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines unit tests for *CLF*.

These tests aren't particularly meaningful, but 
they do exercise basic IO and color processing.

Usage
-----
Command line:
python aces/clf/tests/UnitTestsCLF.py

Python
import aces.clf.tests.UnitTestsCLF as testclf
testclf.unittests()

"""

from __future__ import division

import sys
import os
import unittest
import math
import tempfile

# Make sure we can import aces.clf
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from aces.clf import *

__author__ = 'ACES Developers'
__copyright__ = 'Copyright (C) 2014 - 2015 - ACES Developers'
__license__ = ''
__maintainer__ = 'ACES Developers'
__email__ = 'aces@oscars.org'
__status__ = 'Production'

__all__ = ['TestCLF']


class TestCLF(unittest.TestCase):
    """
    Performs tests on *CLF*.
    """
    _tmpdir = ""
    _tmpclf = ""

    @classmethod
    def setUpClass(cls):
        """
        Initialises common tests attributes.
        """
        cls._tmpdir = tempfile.gettempdir()
        cls._tmpclf = os.path.join(cls._tmpdir, "test.clf")
        print( "Unit tests will use : %s" % cls._tmpclf )

    @classmethod
    def tearDownClass(cls):
        """
        Post tests actions.
        """
        print( "Cleaning up : %s" % cls._tmpclf )
        os.unlink(cls._tmpclf)

    def createCLF(self, clfPath):
        pl = ProcessList()

        # Populate
        pl.setID('Type.name.version')
        pl.setInverseOf('Type.Inverse.name.version')
        pl.setCompCLFversion(1.2)
        pl.setName('Example transform')
        #pl.setAttribute('Extra', 'value')

        # Add optional sub-elements
        ds1 = Description("A description string")
        pl.addElement(ds1)

        ds2 = Description("A second description string")
        pl.addElement(ds2)

        is1 = InputDescriptor("A description of the expected input")
        pl.addElement(is1)

        os2 = OutputDescriptor("A description of the intended input")
        pl.addElement(os2)

        info = Info("Version 0.01", "Copyright AMPAS 2015")
        pl.addElement(info)

        # Add sub-elements that are just key-value pairs
        #pl.addValueElement("Key1", 5.0)
        #pl.addValueElement("Description", "Yet another description")

        # Add a generic process node
        #pn1 = ProcessNode("TestProcessNode", "10i", "16f", "someId", "Transform1")
        #pl.addProcess(pn1)

        # Add a matrix node
        mpn1 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform1")
        mpn1.setMatrix([3, 3, 3], [2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.5])
        pl.addProcess(mpn1)

        # Add another matrix node
        mpn2 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn2.setMatrix([3, 4, 3], [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0])
        pl.addProcess(mpn2)

        # Add a range node
        rpn1 = Range(bitDepths["FLOAT16"], bitDepths["UINT12"], "someId", "Transform3", style='noClamp')
        rpn1.setMinInValue(0.0)
        #rpn1.setMaxInValue(1.0)
        rpn1.setMinOutValue(0.0)
        #rpn1.setMaxOutValue(890)
        pl.addProcess(rpn1)

        # Add a ASC CDL Node
        cdl1 = ASCCDL(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl1ID", "Transform4", "Fwd")
        cdl1.setSlope(1.0, 1.1, 0.9)
        cdl1.setPower(0.9, 0.8, 0.7)
        cdl1.setOffset(0.01, 0.01, 0.02)
        cdl1.setSaturation(0.95)

        # Add optional sub-elements
        ds2 = Description("A description string for the ASC CDL node")
        cdl1.addElement(ds2)

        # Set bypass attribute
        cdl1.setAttribute("bypass", True)
        pl.addProcess(cdl1)

        # Add a 1D lut node
        l1d1 = LUT1D(bitDepths["UINT12"], bitDepths["UINT10"], "someId", "Transform5")
        l1d1.setArray(3, [
            0, 0, 0, 
            1023, 1023, 1023])
        pl.addProcess(l1d1)

        # Add another 1D lut node
        l1d2 = LUT1D(bitDepths["UINT10"], bitDepths["UINT10"], "someId", "Transform6")
        l1d2.setArray(1, [0, 512, 1023])
        l1d2.setIndexMaps([[0, 256, 1023], [0, 1, 2]])
        pl.addProcess(l1d2)

        # Add another 1D lut node
        l3d1 = LUT3D("10i", "10i", "someId", "Transform7")
        #indexMapR = [[0, 128, 1023], [0, 1, 2]]
        indexMapG = [[0, 768], [0, 1]]
        #indexMapB = [[0, 64, 512, 1023], [0, 64, 128, 1023]]
        #l3d1.setIndexMaps(indexMapR, indexMapG, indexMapB)
        l3d1.setIndexMaps(indexMapG)
        l3d1.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1023,  
            0, 1023, 0,  
            0, 1023, 1023,
            1023, 0, 0,  
            1023, 0, 1023,  
            1023, 1023, 0,  
            1023, 1023, 1023])
        pl.addProcess(l3d1)

        # Add a range node
        rpn2 = Range(bitDepths["UINT10"], bitDepths["FLOAT16"], "someId", "Transform7", style='clamp')
        pl.addProcess(rpn2)

        #
        # Autodesk-specific extensions
        #

        # Add a Gamma Node
        gamma1 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma1ID", "Transform8", "basicFwd")
        gamma1.setGamma(2.2, 0.1, "R")
        gamma1.setDynamicParam("LOOK_SWITCH")
        pl.addProcess(gamma1)

        # Add a Gamma Node
        gamma2 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma2ID", "Transform9", "basicRev")
        gamma2.setGamma(2.2, 0.1, "B")
        pl.addProcess(gamma2)

        # Add a Gamma Node
        gamma3 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma3ID", "Transform10", "basicFwd")
        gamma3.setGamma(2.2, 0.1)
        pl.addProcess(gamma3)

        # Add a Gamma Node
        gamma4 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma4ID", "Transform11", "moncurveFwd")
        gamma4.setGamma(2.6, 0.05)
        pl.addProcess(gamma4)

        # Add a Gamma Node
        gamma5 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma5ID", "Transform12", "moncurveRev")
        gamma5.setGamma(2.6, 0.05)
        pl.addProcess(gamma5)

        # Add a ExposureContrast Node
        ecp1 = ExposureContrast(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ecp1ID", "Transform13", "linear")
        ecp1.setExposureContrastPivot(1.0, 1.2, 1.0)
        pl.addProcess(ecp1)

        # Add a ExposureContrast Node
        ecp2 = ExposureContrast(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ecp2ID", "Transform14", "linear")
        ecp2.setExposureContrastPivot(-1.0, 0.5, 1.0)
        pl.addProcess(ecp2)

        # Add a Log Node
        log1 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log1ID", "Transform15", "antiLog2")
        pl.addProcess(log1)

        # Add a Log Node
        log2 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log2ID", "Transform16", "log2")
        pl.addProcess(log2)

        # Add a Log Node
        log3 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log3ID", "Transform17", "antiLog10")
        pl.addProcess(log3)

        # Add a Log Node
        log4 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log4ID", "Transform18", "log10")
        pl.addProcess(log4)

        # Add a Log Node
        log5 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log5ID", "Transform19", "logToLin")
        log5.setLogParams(0.45, 444.0, 0.0, 0.18, 0.0)
        pl.addProcess(log5)

        # Add a Log Node
        log6 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log6ID", "Transform20", "linToLog")
        log6.setLogParams(0.45, 444.0, 0.0, 0.18, 0.0)
        pl.addProcess(log6)

        # Add a range node
        #rpn4 = Range(bitDepths["UINT10"], bitDepths["FLOAT16"], "someId", "Transform0b")
        #pl.addProcess(rpn4)

        #
        # Reference example
        #
        #referencePathBase = '/work/client/academy/ocio/configGeneration/examples'
        #referencePath = 'test.xml'

        #ref1 = Reference(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ref1ID", "Transform21", 
        #    referencePath, referencePathBase)
        #pl.addProcess(ref1)

        #
        # More advanced LUT usage
        #

        # Add a 1D lut node that uses the 'rawHalfs' flag
        # The half float values are converted to 16 bit integer values when written to disk. 
        # The values converted back to half-float on read.
        # The 16 bit integer value '0' maps to the half-float value 0.0
        # The 16 bit integer values '11878' maps to the half-float value 0.1
        # The 16 bit integer values '15360' maps to the half-float value 1.0
        # Interpolation between LUT values happens with the half-float values
        l1d3 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1d3Id", "Transform5b", rawHalfs=True)
        l1d3.setArray(1, [0.0, 0.1, 1.0])
        l1d3.setDynamicParam("LOOK_SWITCH")
        pl.addProcess(l1d3)

        # Add a 1D lut node that uses the 'halfDomain' flag
        # Half-float values are used as the index into the LUT
        l1d4 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1d4Id", "Transform5c", rawHalfs=True, halfDomain=True)
        # Creating the identity LUT
        l1d4.setArray(1, map(Array.uint16ToHalf, range(65536)))
        pl.addProcess(l1d4)


        #
        # Functions that could be sampled into a 1D LUT
        #

        # Example function 1
        f1 = lambda x: x*x

        # Example function 2
        def f2(x):
            #print( x )
            if math.isnan(x) or math.isinf(x):
                return x
            elif x < 0.0:
                return 0.0
            else:
                return x ** 0.5

        # Example function 3
        def lift(x, l):
            return x + l
        f3 = lambda x: lift(x, 0.05)

        l1dS1 = simpleSampledLUT("anID", "aTransformID", 1, 11, f3)
        pl.addProcess(l1dS1)

        l1dS2 = simpleSampledLUTHalfDomain("anID", "aTransformID", 1, f2, rawHalfs=False)
        pl.addProcess(l1dS2)

        #
        # Functions that could be sampled into a 3D LUT
        #
        f3D1 = lambda x, y, z: [x*x, y**0.5, z*2]

        def simplesat(r, g, b, sat):
            l = 0.3*r + 0.59*g + 0.11*b
            rO = r*sat + (1-sat)*l
            gO = g*sat + (1-sat)*l
            bO = b*sat + (1-sat)*l
            return [rO, gO, bO]

        f3D2 = lambda x, y, z: simplesat(x, y, z, 0.25)

        l3dS1 = simple3DLUT("anID", "saturationMod", [4, 4, 4], f3D2)
        pl.addProcess(l3dS1)

        #
        # Duiker Research-specific extensions 
        #

        #
        # Group example
        #
        group1 = Group(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ref1ID", "Transform22")

        # Add a Gamma Node
        ggamma4 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gammaG1ID", "TransformG1", "moncurveFwd")
        ggamma4.setGamma(0.454545, 0.001)
        group1.addProcess(ggamma4)

        # Add a range node
        grpn1 = Range(bitDepths["FLOAT16"], bitDepths["UINT10"], "someId", "TransformG2", style='noClamp')
        grpn1.setMinInValue(0.0)
        grpn1.setMinOutValue(0.0)
        group1.addProcess(grpn1)

        # Add a description
        gds1 = Description("A description string for the group")
        group1.addElement(gds1)

        pl.addProcess(group1)

        # Write
        pl.writeFile(clfPath)

        return pl        
    #createCLF

    def processExample(self, processList, value):
        rangePL = ProcessList()

        # Add a range node
        rpn0 = Range(value[3], bitDepths["FLOAT16"], "someId", "Transform0")
        rangePL.addProcess(rpn0)

        processedValue = map(float,value[:3])
        print( "Input Value  : %s" % processedValue)

        # Normalize values
        processedValue = rangePL.process(processedValue, verbose=True)    

        # Run through processList
        processedValue = processList.process(processedValue, verbose=True)

        return processedValue
    # processExample

    #
    # Tests
    #
    def test1Create(self):
        """
        Performs tests on the *CLF* creation.
        """
        # Create CLF
        pl = self.createCLF(self._tmpclf)

        # Test
        self.assertIsInstance(pl, ProcessList)
    #testCreate

    def test2Read(self):
        """
        Performs tests on the *CLF* creation.
        """
        # Load CLF
        pl = ProcessList(self._tmpclf)

        # Test
        self.assertIsInstance(pl, ProcessList)

        # Print CLF information
        #pl.printInfo()
    #testRead

    def test3Process(self):
        """
        Performs tests on the *CLF* creation.
        """
        # Load CLF
        pl = ProcessList(self._tmpclf)
        self.assertTrue(pl != None)

        # Process value
        processValue = "0.5 0 1.0 32f".split()
        processedValue = self.processExample(pl, processValue)

        # Test
        self.assertTrue(processedValue != [0.0, 0.0, 0.0])
    #testProcess

def unittests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCLF)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    unittests()
    #unittest.main()
