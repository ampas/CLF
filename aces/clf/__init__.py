#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLF Implementation
==================

Usage
-----

Python
******

Command Line
************

Build
-----

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
from ProcessNode import ProcessNode, bitDepths

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

