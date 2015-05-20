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

'''
Simple tests of the lutFormats module
Should be turned into a proper set of unit tests.
'''

import os
import sys
# Make sure we can import lutFormats
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import lutFormats

tmpDir = "/tmp"
aces1OCIOConfirDir = "/work/client/academy/ocio/hpd/OpenColorIO-Configs/aces_1.0.0"
#aces1OCIOConfirDir = "/path/to/OpenColorIO-Configs/aces_1.0.0"

spiPath = "%s/luts/ACEScc_to_linear.spi1d" % aces1OCIOConfirDir
cspPath = "%s/baked/maya/sRGB (D60 sim.) for ACEScg Maya.csp" % aces1OCIOConfirDir

spipl = lutFormats.Registry.read( spiPath )
csppl = lutFormats.Registry.read( cspPath )

newSpiPath = "%s/ACEScc_to_linear_new.spi1d" % tmpDir
lutFormats.Registry.write(spipl, newSpiPath)

newSpi3dPath = "%s/srgb_new.spi3d" % tmpDir
lutFormats.Registry.write(csppl, newSpi3dPath, lutDataFormat="3D")

newCspPath = "%s/srgb_new_3d.csp" % tmpDir
lutFormats.Registry.write(csppl, newCspPath, lutDataFormat="3D")

newCsp1DPath = "%s/srgb_new_1d.csp" % tmpDir
lutFormats.Registry.write(csppl, newCsp1DPath)

newCsp1D3DPath = "%s/srgb_new_1d3d.csp" % tmpDir
lutFormats.Registry.write(csppl, newCsp1D3DPath, lutDataFormat="1D_3D_1D")

newClf1D3DPath = "%s/srgb_new_1d3d.clf" % tmpDir
lutFormats.Registry.write(csppl, newClf1D3DPath, lutDataFormat="1D_3D_1D")

newCtl1DPath = "%s/srgb_new_1d.ctl" % tmpDir
lutFormats.Registry.write(csppl, newCtl1DPath)

newCtl1D3DPath = "%s/srgb_new_3d.ctl" % tmpDir
lutFormats.Registry.write(csppl, newCtl1D3DPath, lutDataFormat="3D")



