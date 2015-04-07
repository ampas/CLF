#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLF Implementation
==================

Usage
-----
Common LUT Format files contain a single ProcessList with an arbitrary 
number of ProcessNodes.

The full specification for the format is available here
https://github.com/ampas/aces-dev/tree/master/documents

Python
******
More extensive examples are included in tests/UnitTestsCLF.py

import clf

# Create a ProcessList
pl = clf.ProcessList()

# Set a name
pl.setName('Example transform')

# Add a Matrix ProcessNode
mpn1 = clf.Matrix(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "someId", "Transform2")
mpn1.setMatrix([3, 4, 3], [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0])
pl.addProcess(mpn1)

# Write the CLF to disk
pl.writeFile("/some/path/test.clf")

# Process a color with the ProcessList
processValue = [0.5, 0, 1.0]
processedValue = pl.process(processedValue, verbose=True)

Command Line
************

Mac OS X - Required packages
****************************

OpenImageIO
___________

$ brew tap homebrew/science

Optional Dependencies
_____________________

$ brew install -vd libRaw
$ brew install -vd OpenCV
$ brew install -vd openimageio --with-python
"""

__author__ = 'ACES Developers'
__copyright__ = 'Copyright (C) 2014 - 2015 - ACES Developers'
__license__ = ''
__maintainer__ = 'ACES Developers'
__email__ = 'aces@oscars.org'
__status__ = 'Production'

__major_version__ = '1'
__minor_version__ = '0'
__change_version__ = '0'
__version__ = '.'.join((__major_version__,
                        __minor_version__,
                        __change_version__))

'''
Having the explicit imports here feels off, but also necessary...
'''

# General Types
from ProcessList import ProcessList
from Comment import Description, InputDescriptor, OutputDescriptor
from Info import Info
from ProcessNode import ProcessNode, bitDepths, bitDepthToNormalized, normalizedToBitDepth

#
# These ProcessNode imports should also be used in the ProcessList
# and Group Nodes
#

# ProcessNodes
from Range import Range
from Matrix import Matrix
from ASCCDL import ASCCDL, ColorCorrection
from LUT1D import LUT1D, simpleSampledLUT, simpleSampledLUTHalfDomain
from LUT3D import LUT3D, simple3DLUT

# Autodesk-specific ProcessNodes
from Reference import Reference
from ExposureContrast import ExposureContrast
from Gamma import Gamma
from Log import Log

# Duiker Research-specific ProcessNodes
from Group import Group

