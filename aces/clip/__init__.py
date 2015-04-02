#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Clip Metadata Implementation
============================

Usage
-----
The full specification for the Clip Metadata format is available here
https://github.com/ampas/aces-dev/tree/master/documents

Python
******
Example usage is included in tests/UnitTestsClip.py

Command Line
************

Build
-----

Mac OS X - Required packages
****************************

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
from ClipMetadata import ClipMetadata
from Comment import Comment, ContainerFormatVersion, ModificationTime, UUID
from Info import Info
from ClipID import ClipID
from Config import Config
from TransformList import InputTransformList, PreviewTransformList
from TransformReference import IDTref, LMTref, RRTref, ODTref, RRTODTref
from GradeRef import GradeRef
from TransformLibrary import TransformLibrary
