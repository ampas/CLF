#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLF LUT Reading and Writing
===========================

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

# Needed to make sure that clf is in the sys.path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

'''
Having the explicit imports here feels off, but also necessary...
'''

# General Types
from Registry import Registry
from Common import *

# LUT formats
from LutSPI import LutFormatSPI
from LutCSP import LutFormatCSP
from LutCLF import LutFormatCLF
from LutCTL import LutFormatCTL


