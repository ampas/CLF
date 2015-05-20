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
import LutFormat

class LutFormatCTL(LutFormat.LutFormat):
    "A class that implements IO for the Academy's Color Transform Language"

    # Descriptions, extensions and capabilities for this class
    formatType = "Color Transform Language"
    formats = [
        ["ctl - 1D, 3D or 1D/3D LUT format",
         "ctl",
         [LutFormat.IO_CAPABILITY_WRITE_1D,
          LutFormat.IO_CAPABILITY_WRITE_3D]
         ]
        ]

    def __init__(self): 
        "%s - Initialize the standard class variables" % LutFormatCTL.formatType
        LutFormat.LutFormat.__init__(self)
    # __init__

    @classmethod
    def read(cls,
             lutPath, 
             inverse=False, 
             interpolation='linear',
             inversesUseIndexMaps=True, 
             inversesUseHalfDomain=True):
        return cls.readCTL(lutPath,
            inverse, 
            interpolation)

    @classmethod
    def write1D(cls,
                lutPath,
                samples,
                lutResolution1d,
                inputMin,
                inputMax):
        #print( "%s format write 1D - %s" % (LutFormatCTL.formatType, lutPath) )
        return LutFormatCTL.writeCTL1D(lutPath, 
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
        #print( "%s format write 3D - %s" % (LutFormatCTL.formatType, lutPath) )
        return LutFormatCTL.writeCTL3D(lutPath, 
                                       inputMin, 
                                       inputMax, 
                                       samples, 
                                       lutResolution3d)

    @ staticmethod
    def writeCTL1D(filename, 
                   from_min, 
                   from_max, 
                   data, 
                   entries, 
                   channels, 
                   components=3):
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

        # May want to use fewer components than there are channels in the data
        # Most commonly used for single channel LUTs
        components = min(3, components, channels)

        with open(filename, 'w') as fp:
            fp.write('// %d x %d 1D LUT generated by "convertCLFtoLUT"\n' % (
              entries, components))
            fp.write('\n')
            fp.write('const float min1d = %3.9f;\n' % from_min)
            fp.write('const float max1d = %3.9f;\n' % from_max)
            fp.write('\n')

            # Write LUT
            if components == 1:
              fp.write('const float lut[] = {\n')
              for i in range(0, entries):
                  fp.write('%s' % data[i * channels])
                  if i != (entries-1):
                    fp.write(',')
                  fp.write('\n')
              fp.write('};\n')
              fp.write('\n')
            else:
              for j in range(components):
                fp.write('const float lut%d[] = {\n' % j)
                for i in range(0, entries):
                    fp.write('%s' % data[i * channels])
                    if i != (entries-1):
                      fp.write(',')
                    fp.write('\n')
                fp.write('};\n')
                fp.write('\n')

            fp.write('void main\n')
            fp.write('(\n')
            fp.write('  input varying float rIn,\n')
            fp.write('  input varying float gIn,\n')
            fp.write('  input varying float bIn,\n')
            fp.write('  input varying float aIn,\n')
            fp.write('  output varying float rOut,\n')
            fp.write('  output varying float gOut,\n')
            fp.write('  output varying float bOut,\n')
            fp.write('  output varying float aOut\n')
            fp.write(')\n')
            fp.write('{\n')
            fp.write('  float r = rIn;\n')
            fp.write('  float g = gIn;\n')
            fp.write('  float b = bIn;\n')
            fp.write('\n')
            fp.write('  // Apply LUT\n')
            if components == 1:
              fp.write('  r = lookup1D(lut, min1d, max1d, r);\n')
              fp.write('  g = lookup1D(lut, min1d, max1d, g);\n')
              fp.write('  b = lookup1D(lut, min1d, max1d, b);\n')
            elif components == 3:
              fp.write('  r = lookup1D(lut0, min1d, max1d, r);\n')
              fp.write('  g = lookup1D(lut1, min1d, max1d, g);\n')
              fp.write('  b = lookup1D(lut2, min1d, max1d, b);\n')          
            fp.write('\n')
            fp.write('  rOut = r;\n')
            fp.write('  gOut = g;\n')
            fp.write('  bOut = b;\n')
            fp.write('  aOut = aIn;\n')
            fp.write('}\n')

        return True
    # writeCTL1D

    @staticmethod
    def writeCTL3D(filename, 
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

        with open(filename, 'w') as fp:
            fp.write('// %d x %d x %d 3D LUT generated by "convertCLFtoLUT"\n' % (
              resolution[0], resolution[1], resolution[2]))
            fp.write('\n')
            fp.write('const float min3d[3] = {%3.9f, %3.9f, %3.9f};\n' % (
                from_min, from_min, from_min))
            fp.write('const float max3d[3] = {%3.9f, %3.9f, %3.9f};\n' % (
                from_max, from_max, from_max))
            fp.write('\n')

            # Write LUT
            fp.write('const float cube[%d][%d][%d][3] = \n' % (
                resolution[0], resolution[1], resolution[2]))

            fp.write('{\n')
            for r in range(resolution[0]):
                fp.write('\t{\n')
                for g in range(resolution[1]):
                    fp.write('\t\t{ ')
                    for b in range(resolution[2]):
                        fp.write('{')
                        entry = ", ".join(map(lambda x : "%3.6f" % x, data[r][g][b]))
                        fp.write('%s' % entry)
                        fp.write('}')
                        if b != resolution[2]-1:
                            fp.write(',\n\t\t  ')
                        else:
                            fp.write('\n ')
                    fp.write('}')
                    if g != resolution[1]-1:
                        fp.write(',\n')
                    else:
                        fp.write('\n')
                fp.write('\t}')
                if r != resolution[0]-1:
                    fp.write(', ')
                else:
                    fp.write('\n')
            fp.write('};\n')
            fp.write('\n')

            fp.write('void main\n')
            fp.write('(\n')
            fp.write('  input varying float rIn,\n')
            fp.write('  input varying float gIn,\n')
            fp.write('  input varying float bIn,\n')
            fp.write('  input varying float aIn,\n')
            fp.write('  output varying float rOut,\n')
            fp.write('  output varying float gOut,\n')
            fp.write('  output varying float bOut,\n')
            fp.write('  output varying float aOut\n')
            fp.write(')\n')
            fp.write('{\n')
            fp.write('  float r = rIn;\n')
            fp.write('  float g = gIn;\n')
            fp.write('  float b = bIn;\n')
            fp.write('\n')
            fp.write('  // Apply LUT\n')
            fp.write('  lookup3D_f(cube, min3d, max3d, r, g, b, r, g, b);\n')
            fp.write('\n')
            fp.write('  rOut = r;\n')
            fp.write('  gOut = g;\n')
            fp.write('  bOut = b;\n')
            fp.write('  aOut = aIn;\n')
            fp.write('}\n')

        return True
    # writeCTL3D

# LutFormatCTL
