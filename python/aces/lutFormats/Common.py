#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import os
import math

import clf

# LUT IO capabilities
IO_CAPABILITY_READ = "read"
IO_CAPABILITY_WRITE_1D = "write1D"
IO_CAPABILITY_WRITE_3D = "write3D"
IO_CAPABILITY_WRITE_1D3D1D = "write1D3D1D"

# Constants used for specifying LUT writing method
LUTDATAFORMAT_1D = '1D'
LUTDATAFORMAT_3D = '3D'
LUTDATAFORMAT_1D_3D_1D = '1D_3D_1D'


