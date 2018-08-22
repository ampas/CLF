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

import os
import clf

import Sampling
import LutFormat

class LutFormatSPI(LutFormat.LutFormat):
    "A class that implements IO for the Sony .spi1d, spi3d and .spimtx LUT formats"

    # Descriptions, extensions and capabilities for this class
    formatType = "SPI"
    formats = [
        ["spi1d - 1D LUT format",
         "spi1d",
         [LutFormat.IO_CAPABILITY_READ, LutFormat.IO_CAPABILITY_WRITE_1D]],
        ["spi3d - 3D LUT format",
         "spi3d",
         [LutFormat.IO_CAPABILITY_READ, LutFormat.IO_CAPABILITY_WRITE_3D]],
        ["spimtx - matrix format",
         "spimtx",
         []]
        ]

    def __init__(self):
        "%s - Initialize the standard class variables" % LutFormatSPI.formatType
        LutFormat.LutFormat.__init__(self)
    # __init__

    @classmethod
    def read(cls,
             lutPath,
             inverse=False,
             interpolation='linear',
             inversesUseIndexMaps=True,
             inversesUseHalfDomain=True):
        #print( "%s format read - %s" % (LutFormatSPI.formatType, lutPath) )
        extension = os.path.splitext(lutPath)[1][1:].strip().lower()

        if extension == 'spi1d':
            return LutFormatSPI.readSPI1D(lutPath,
                inverse,
                interpolation,
                inversesUseIndexMaps,
                inversesUseHalfDomain)
        elif extension == 'spi3d':
            return LutFormatSPI.readSPI3D(lutPath,
                inverse,
                interpolation)
        elif extension == 'spimtx':
            return LutFormatSPI.readSPIMTX(lutPath)

        return False

    @classmethod
    def write1D(cls,
                lutPath,
                samples,
                lutResolution1d,
                inputMin,
                inputMax):
        #print( "%s format write 1D - %s" % (LutFormatSPI.formatType, lutPath) )
        return LutFormatSPI.writeSPI1D(lutPath,
                                       inputMin,
                                       inputMax,
                                       samples,
                                       lutResolution1d,
                                       3,
                                       3)

    @classmethod
    def write3D(cls,
                lutPath,
                samples,
                lutResolution3d,
                inputMin,
                inputMax):
        #print( "%s format write 3D - %s" % (LutFormatSPI.formatType, lutPath) )
        return LutFormatSPI.writeSPI3D(lutPath,
                                       inputMin,
                                       inputMax,
                                       samples,
                                       lutResolution3d)

    @staticmethod
    def readSPI1D(lutPath,
                  inverse=False,
                  interpolation='linear',
                  inversesUseIndexMaps=True,
                  inversesUseHalfDomain=True):
        with open(lutPath) as f:
            lines = f.read().splitlines()

        #
        # Read LUT data
        #
        resolution = [0, 0]
        samples = []
        indexMap = []
        minInputValue = 0.0
        maxInputValue = 1.0

        for line in lines:
            #print( "line : %s" % line )
            tokens = line.split()

            if tokens[0] == "Version":
                version = int(tokens[1])
                if version != 1:
                    break
            elif tokens[0] == "From":
                minInputValue = float(tokens[1])
                maxInputValue = float(tokens[2])
            elif tokens[0] == "Length":
                resolution[0] = int(tokens[1])
            elif tokens[0] == "Components":
                resolution[1] = int(tokens[1])
            elif tokens[0] in ["{", "}"]:
                continue
            else:
                samples.extend(map(float, tokens))
            #else:
            #    print( "Skipping line : %s" % tokens )

        #
        # Create ProcessNodes
        #
        lutpns = []

        # Forward transform, pretty straightforward
        if not inverse:
            # Remap input range
            if minInputValue != 0.0 or maxInputValue != 1.0:
                rangepn = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "range", "range")
                rangepn.setMinInValue(minInputValue)
                rangepn.setMaxInValue(maxInputValue)
                rangepn.setMinOutValue(0.0)
                rangepn.setMaxOutValue(1.0)

                lutpns.append(rangepn)

            # LUT node
            lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut1d", "lut1d", interpolation=interpolation)
            lutpn.setArray(resolution[1], samples)

            lutpns.append(lutpn)

        # Inverse transform, LUT has to be resampled
        else:
            if inversesUseIndexMaps:
                print( "Generating inverse of 1D LUT using Index Maps")
                lutpnInverses = Sampling.generateLUT1DInverseIndexMap(resolution, samples, minInputValue, maxInputValue)
            elif inversesUseHalfDomain:
                print( "Generating full half-domain inverse of 1D LUT")
                lutpnInverses = Sampling.generateLUT1DInverseHalfDomain(resolution, samples, minInputValue, maxInputValue, rawHalfs=True)
            else:
                print( "Generating resampled inverse of 1D LUT")
                lutpnInverses = Sampling.generateLUT1DInverseResampled(resolution, samples, minInputValue, maxInputValue)
            lutpns.extend(lutpnInverses)

        return lutpns

    # XXX
    # Need to warn user about the lack of an inverse for 3D LUTs
    # Or implement one. That would be slow in Python (or C, or OpenCL) though
    @staticmethod
    def readSPI3D(lutPath, inverse=False, interpolation='linear'):
        with open(lutPath) as f:
            lines = f.read().splitlines()

        # Translate between different names for the same interpolation if necessary
        ocioToCLFInterpolation = {'linear':'trilinear'}
        if interpolation in ocioToCLFInterpolation:
            interpolation = ocioToCLFInterpolation[interpolation]

        resolution = [0, 0, 0]
        samples = []
        indexMap = []
        minInputValue = 0.0
        maxInputValue = 1.0

        tokens = lines[0].split()
        if tokens[0] == "SPILUT":
            version = float(tokens[1])
            if version == 1.0:
                tokens = map(int, lines[1].split())
                if tokens[0] == 3 or tokens[1] == 3:
                    tokens = map(int, lines[2].split())
                    resolution = tokens

                    # This assumes that the value are printed in order
                    # with blue incrementing fastest like the CLF specification
                    # This is generally true, but should be generalized at some
                    # point to take into account the indices printed as the
                    # first three values on each line
                    for line in lines[3:]:
                        tokens = map(float, line.split())
                        samples.extend(tokens[3:])

        #
        # Create ProcessNodes
        #
        lutpn = clf.LUT3D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut3d", "lut3d", interpolation=interpolation)
        lutpn.setArray(resolution, samples)

        return [lutpn]

    @staticmethod
    def readSPIMTX(lutPath):
        print( "%s format, readSPIMTX not implemented - %s" % (LutFormatSPI.formatType, lutPath) )
        return False

    @staticmethod
    def writeSPI1D(filename,
                   from_min,
                   from_max,
                   data,
                   entries,
                   channels,
                   components=3):
        """
        Object description.

        Credit to *Alex Fry* for the original single channel version of the spi1d
        writer.

        Parameters
        ----------
        parameter : type
            Parameter description.

        Returns
        -------
        type
             Return value description.
        """

        # May want to use fewer components than there are channels in the data
        # Most commonly used for single channel LUTs
        components = min(3, components, channels)

        with open(filename, 'w') as fp:
            fp.write('Version 1\n')
            fp.write('From %f %f\n' % (from_min, from_max))
            fp.write('Length %d\n' % entries)
            fp.write('Components %d\n' % components)
            fp.write('{\n')
            for i in range(0, entries):
                entry = ''
                for j in range(0, components):
                    entry = '%s %s' % (entry, data[i * channels + j])
                fp.write('        %s\n' % entry)
            fp.write('}\n')

        return True
    # writeSPI1D

    @staticmethod
    def writeSPI3D(filename,
                   from_min,
                   from_max,
                   data,
                   resolution):
        """
        Object description.

        Parameters
        ----------
        parameter : type
            Parameter description.

        Returns
        -------
        type
             Return value description.
        """

        #print( ' '.join(map(str, resolution)) )

        with open(filename, 'w') as fp:
            fp.write('SPILUT 1.0\n')
            fp.write('3 3\n')
            fp.write('%s\n' % ' '.join(map(str, resolution)) )

            for r in range(resolution[0]):
                for g in range(resolution[1]):
                    for b in range(resolution[2]):
                        entry  = " ".join(map(str,[r,g,b]))
                        entry += " "
                        entry += " ".join(map(str, data[r][g][b]))
                        fp.write('%s\n' % entry)

        return True
    # writeSPI3D

# LutFormatSPI
