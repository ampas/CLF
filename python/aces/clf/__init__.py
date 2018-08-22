#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__ = 'Haarm-Pieter Duiker'
__copyright__ = 'Copyright (C) 2015 Academy of Motion Picture Arts and Sciences'
__maintainer__ = 'Academy of Motion Picture Arts and Sciences'
__email__ = 'acessupport@oscars.org'
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

# Feature set compatibility
from Common import setFeatureCompatibility, getFeatureCompatibility, featureSets

# General Types
from ProcessList import ProcessList
from Comment import Description, InputDescriptor, OutputDescriptor
from Info import Info
from ProcessNode import ProcessNode, bitDepths, bitDepthToNormalized, normalizedToBitDepth

# ProcessNodes
from Range import Range
from Matrix import Matrix
from ASCCDL import ASCCDL, ColorCorrection
from LUT1D import LUT1D, simpleSampledLUT, simpleSampledLUTHalfDomain
from LUT3D import LUT3D, simple3DLUT

# Autodesk-specific ProcessNodes
from ExtensionReference import Reference
from ExtensionExposureContrast import ExposureContrast
from ExtensionGamma import Gamma
from ExtensionLog import Log

# Duiker Research-specific ProcessNodes
from ExtensionGroup import Group

