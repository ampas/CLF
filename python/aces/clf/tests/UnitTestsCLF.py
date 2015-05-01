#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

"""
The Academy / ASC Common LUT Format Sample Implementations are provided by the
Academy under the following terms and conditions:

Copyright © 2015 Academy of Motion Picture Arts and Sciences ("A.M.P.A.S.").
Portions contributed by others as indicated. All rights reserved.

A worldwide, royalty-free, non-exclusive right to copy, modify, create
derivatives, and use, in source and binary forms, is hereby granted, subject to
acceptance of this license. Performance of any of the aforementioned acts
indicates acceptance to be bound by the following terms and conditions:

* Copies of source code, in whole or in part, must retain the above copyright
notice, this list of conditions and the Disclaimer of Warranty.

* Use in binary form must retain the above copyright notice, this list of
conditions and the Disclaimer of Warranty in the documentation and/or other
materials provided with the distribution.

* Nothing in this license shall be deemed to grant any rights to trademarks,
copyrights, patents, trade secrets or any other intellectual property of
A.M.P.A.S. or any contributors, except as expressly stated herein.

* Neither the name "A.M.P.A.S." nor the name of any other contributors to this
software may be used to endorse or promote products derivative of or based on
this software without express prior written permission of A.M.P.A.S. or the
contributors, as appropriate.

This license shall be construed pursuant to the laws of the State of California,
and any disputes related thereto shall be subject to the jurisdiction of the
courts therein.

Disclaimer of Warranty: THIS SOFTWARE IS PROVIDED BY A.M.P.A.S. AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
NON-INFRINGEMENT ARE DISCLAIMED. IN NO EVENT SHALL A.M.P.A.S., OR ANY
CONTRIBUTORS OR DISTRIBUTORS, BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, RESITUTIONARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

WITHOUT LIMITING THE GENERALITY OF THE FOREGOING, THE ACADEMY SPECIFICALLY
DISCLAIMS ANY REPRESENTATIONS OR WARRANTIES WHATSOEVER RELATED TO PATENT OR
OTHER INTELLECTUAL PROPERTY RIGHTS IN THE ACES CONTAINER REFERENCE
IMPLEMENTATION, OR APPLICATIONS THEREOF, HELD BY PARTIES OTHER THAN A.M.P.A.S.,
WHETHER DISCLOSED OR UNDISCLOSED.
"""

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

import sys
import os
import unittest
import math
import tempfile

# Make sure we can import aces.clf
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from aces.clf import *

__author__ = 'Haarm-Pieter Duiker'
__copyright__ = 'Copyright (C) 2015 Academy of Motion Picture Arts and Sciences'
__maintainer__ = 'Academy of Motion Picture Arts and Sciences'
__email__ = 'acessupport@oscars.org'
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

        #
        # 'floatEncoding' options for Arrays
        #

        # Range node to bring the general range into float 0-1
        rpn10 = Range(bitDepths["UINT10"], bitDepths["FLOAT16"], "someId", "Transform3", style='noClamp')
        pl.addProcess(rpn10)

        #
        # All 'floatEncoding' options, with the Matrix ProcessNode
        #
        # Add a matrix node
        mpn10 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn10.setMatrix([3, 3, 3], 
            [2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.5],
            floatEncoding='integer16bit')
        pl.addProcess(mpn10)

        # Add another matrix node
        mpn11 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn11.setMatrix([3, 4, 3], 
            [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0],
            floatEncoding='integer32bit')
        pl.addProcess(mpn11)

        # Add another matrix node
        mpn12 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn12.setMatrix([3, 3, 3], 
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            floatEncoding='integer64bit')
        pl.addProcess(mpn12)

        # Add a matrix node
        mpn13 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn13.setMatrix([3, 3, 3], 
            [2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.5],
            floatEncoding='hex16bit')
        pl.addProcess(mpn13)

        # Add another matrix node
        mpn14 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn14.setMatrix([3, 4, 3], 
            [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0],
            floatEncoding='hex32bit')
        pl.addProcess(mpn14)

        # Add another matrix node
        mpn15 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn15.setMatrix([3, 3, 3], 
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            floatEncoding='hex64bit')
        pl.addProcess(mpn15)

        # Add another matrix node
        mpn16 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
        mpn16.setMatrix([3, 3, 3], 
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0])
        pl.addProcess(mpn16)

        #
        # All 'floatEncoding' options, with the LUT1D ProcessNode
        #
        l1d10 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d10.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='integer16bit')
        pl.addProcess(l1d10)

        l1d11 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d11.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='integer32bit')
        pl.addProcess(l1d11)

        l1d12 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d12.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='integer64bit')
        pl.addProcess(l1d12)

        l1d13 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d13.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='hex16bit')
        pl.addProcess(l1d13)

        l1d14 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d14.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='hex32bit')
        pl.addProcess(l1d14)

        l1d15 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d15.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0],
            floatEncoding='hex64bit')
        pl.addProcess(l1d15)

        l1d16 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1dId", "Transform")
        l1d16.setArray(1, 
            [0.0, 0.25, 0.5, 0.75, 1.0])
        pl.addProcess(l1d16)

        #
        # All 'floatEncoding' options, with the LUT3D ProcessNode
        #
        l3d10 = LUT3D("16f", "16f", "someId", "Transform")
        l3d10.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='integer16bit')
        pl.addProcess(l3d10)

        l3d11 = LUT3D("16f", "16f", "someId", "Transform")
        l3d11.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='integer32bit')
        pl.addProcess(l3d11)

        l3d12 = LUT3D("16f", "16f", "someId", "Transform")
        l3d12.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='integer64bit')
        pl.addProcess(l3d12)

        l3d13 = LUT3D("16f", "16f", "someId", "Transform")
        l3d13.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='hex16bit')
        pl.addProcess(l3d13)

        l3d14 = LUT3D("16f", "16f", "someId", "Transform")
        l3d14.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='hex32bit')
        pl.addProcess(l3d14)

        l3d15 = LUT3D("16f", "16f", "someId", "Transform")
        l3d15.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1],
            floatEncoding='hex64bit')
        pl.addProcess(l3d15)

        l3d16 = LUT3D("16f", "16f", "someId", "Transform")
        l3d16.setArray([2, 2, 2], 
            [0, 0, 0,  
            0, 0, 1,  
            0, 1, 0,  
            0, 1, 1,
            1, 0, 0,  
            1, 0, 1,  
            1, 1, 0,  
            1, 1, 1])
        pl.addProcess(l3d16)

        # Range node to bring the general range into back to int 0-1023
        rpn11 = Range(bitDepths["FLOAT16"], bitDepths["UINT10"], "someId", "Transform3", style='noClamp')
        pl.addProcess(rpn11)

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
