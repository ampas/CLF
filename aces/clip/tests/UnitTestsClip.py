#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines unit tests for *Clip*.

These tests aren't particularly meaningful, but 
they do exercise basic IO.

Usage
-----
Command line:
python aces/clip/tests/UnitTestsClip.py

Python
import aces.clip.tests.UnitTestsClip as testclip
testclip.unittests()

"""

from __future__ import division

import sys
import os
import unittest
import math
import tempfile

# Make sure we can import aces.clip
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from aces.clf import *
from aces.clip import *

__author__ = 'ACES Developers'
__copyright__ = 'Copyright (C) 2014 - 2015 - ACES Developers'
__license__ = ''
__maintainer__ = 'ACES Developers'
__email__ = 'aces@oscars.org'
__status__ = 'Production'

__all__ = ['TestClip']


class TestClip(unittest.TestCase):
    """
    Performs tests on *Clip Metadata*.
    """
    _tmpdir = ""
    _tmpclip = ""

    @classmethod
    def setUpClass(cls):
        """
        Initialises common tests attributes.
        """
        cls._tmpdir = tempfile.gettempdir()
        cls._tmpclip = os.path.join(cls._tmpdir, "test.xml")
        print( "Unit tests will use : %s" % cls._tmpclip )

    @classmethod
    def tearDownClass(cls):
        """
        Post tests actions.
        """
        print( "Cleaning up : %s" % cls._tmpclip )
        os.unlink(cls._tmpclip)

    def createExampleClip(self, clipPath):
        # Create
        clip = ClipMetadata()

        # Populate
        clip.setName('Example Clip Metadata')

        # Add ID data
        clip.addElement(ContainerFormatVersion(str(1.0)))
        #clip.addValueElement("UUID", "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
        clip.addElement(UUID("urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6"))
        clip.addElement(ModificationTime("2014-11-24T10:20:13-8:00"))

        # Add Info element
        clip.addElement(Info("testModule", "2015.0.01", "This is a comment"))

        # Add ClipID element
        clip.addElement(ClipID("A0001B0003FX", "A0001", "2014-11-20T12:24:13-8:00", "This is a note"))

        # Add Config element and sub-elements
        config = Config("1.0", "2014-11-29T23:55:13-8:00")

        itl = InputTransformList('inputTransformID')
        itl.addElement(IDTref("TransformName1", "id1", "applied", "IDT.something.v1.0"))

        gr = GradeRef("", "some_space_to_aces", "aces_to_some_space")
        cdl0 = ColorCorrection(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl0ID", "Transform40", "Fwd")
        cdl0.setSlope(0.05, 1.1, 0.9)
        cdl0.setPower(9.0, 0.8, 0.7)
        cdl0.setOffset(10.1, 0.01, 0.02)
        cdl0.setSaturation(0.05)
        gr.addElement(cdl0)

        itl.addElement(gr)
        config.addElement(itl)

        ptl = PreviewTransformList('previewTransformID')
        ptl.addElement(LMTref("TransformName3", "id3", "bypass", "LMT.something.v1.0"))
        ptl.addElement(RRTref("TransformName4", "id4", "bypass", "RRT.something.v1.0"))
        ptl.addElement(ODTref("TransformName5", "id5", "bypass", "ODT.something.v1.0"))
        ptl.addElement(RRTODTref("TransformName6", "id6", "bypass", "RRTODT.something.v1.0"))
        config.addElement(ptl)

        clip.addElement(config)

        # Add transform library
        tl = TransformLibrary()

        # Create an example CLF
        pl0 = ProcessList()

        # Add a ASC CDL Node
        cdl1 = ColorCorrection(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl1ID", "Transform4", "Fwd")
        cdl1.setSlope(0.95, 1.1, 0.9)
        cdl1.setPower(0.9, 0.8, 0.7)
        cdl1.setOffset(0.01, 0.01, 0.02)
        cdl1.setSaturation(0.95)

        pl0.addElement(cdl1)
        tl.addElement(pl0)

        # Create an example CLF
        pl1 = ProcessList()

        # Add a range node to CLF
        rpn0 = Range(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform0")
        rpn0.setMinInValue(0.0)
        rpn0.setMinOutValue(0.5)
        pl1.addProcess(rpn0)

        # Add CLF to transform library
        tl.addElement(pl1)

        # Create an example CLF
        #pl2 = ProcessList('examples/test.xml')
        #tl.addElement(pl2)

        clip.addElement(tl)

        # Write
        clip.writeFile(clipPath)

        return clip
    # createExampleClip

    #
    # Tests
    #
    def test1Create(self):
        """
        Performs tests on the *Clip* creation.
        """
        # Create Clip
        clip = self.createExampleClip(self._tmpclip)

        # Test
        self.assertIsInstance(clip, ClipMetadata)
    #testCreate

    def test2Read(self):
        """
        Performs tests on the *Clip* creation.
        """
        # Load Clip
        clip = ClipMetadata(self._tmpclip)

        # Test
        self.assertIsInstance(clip, ClipMetadata)

        # Print Clip information
        #clip.printInfo()
    #testRead

def unittests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClip)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    unittests()
    #unittest.main()
