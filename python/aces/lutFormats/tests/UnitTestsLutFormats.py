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
#aces1OCIOConfirDir = "/work/client/academy/ocio/hpd/OpenColorIO-Configs/aces_1.0.0"
aces1OCIOConfirDir = "/path/to/OpenColorIO-Configs/aces_1.0.0"

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



