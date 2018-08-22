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

import aces.clf as clf
from aces.lutFormats import *
from aces.lutFormats.LutFormat import *

class LutFormatCSP(LutFormat):
    "A class that implements IO for the Rising Sun Research .csp LUT formats"

    # Descriptions, extensions and capabilities for this class
    formatType = "Cinespace"
    formats = [
        ["csp - 1D, 3D or 1D/3D LUT format",
         "csp",
         [IO_CAPABILITY_READ,
          IO_CAPABILITY_WRITE_1D,
          IO_CAPABILITY_WRITE_3D,
          IO_CAPABILITY_WRITE_1D3D1D]
         ]
        ]

    def __init__(self): 
        "%s - Initialize the standard class variables" % LutFormatCSP.formatType
        LutFormat.__init__(self)
    # __init__

    @classmethod
    def read(cls,
             lutPath, 
             inverse=False, 
             interpolation='linear',
             inversesUseIndexMaps=True, 
             inversesUseHalfDomain=True):
        return cls.readCSP(lutPath,
            inverse, 
            interpolation)

    @classmethod
    def write1D(cls,
                lutPath,
                samples,
                lutResolution1d,
                inputMin,
                inputMax):
        #print( "%s format write 1D - %s" % (LutFormatCSP.formatType, lutPath) )
        return LutFormatCSP.writeCSP1D(lutPath, 
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
        #print( "%s format write 3D - %s" % (LutFormatCSP.formatType, lutPath) )
        return LutFormatCSP.writeCSP3D(lutPath, 
                                       inputMin, 
                                       inputMax, 
                                       samples, 
                                       lutResolution3d)

    @classmethod
    def write1D3D1D(cls,
                    lutPath,
                    samples1dIn,
                    lutResolution1dIn,
                    inputMin,
                    inputMax,
                    samples3d,
                    lutResolution3d,
                    samples1dOut,
                    lutResolution1dOut,
                    outputMin,
                    outputMax):
        #print( "%s format write 1D 3D 1D - %s" % (LutFormatCSP.formatType, lutPath) )
        return LutFormatCSP.writeCSP1D3D(lutPath,
                                         samples1dIn,
                                         lutResolution1dIn,
                                         inputMin,
                                         inputMax,
                                         samples3d,
                                         lutResolution3d)

    @staticmethod
    def generateCLFPrelut(cspPreluts):
        '''
        A basic implementation of expanding the CSP preluts. This should be replaced with a proper
        cubic interpolation implementation.
        '''
        prelutpns = []

        # Get the individual preluts
        (prelutR, prelutG, prelutB) = cspPreluts

        # Get the resolution of the prelut
        inputResolution = max(len(prelutR[0]), len(prelutG[0]), len(prelutB[0]))

        # XXX
        # Given that we're resampling, we should probably increase the
        # resolution of the resampled lut relative to the source
        outputResolution = inputResolution

        # If the prelut only affects the range, skip this step
        if inputResolution > 2:
            outputResolution *= 2

        # Find the minimum and maximum input
        # XXX
        # We take the min and max of all three preluts because the Range node
        # only takes single value, not RGB triples. If the prelut ranges are 
        # very different, this could introduce some artifacting
        minInputValue = min(prelutR[0][0], prelutG[0][0], prelutB[0][0])
        maxInputValue = max(prelutR[0][-1], prelutG[0][-1], prelutB[0][-1])

        #print( inputResolution, minInputValue, maxInputValue )

        # Create a Range node to normalize data from that range [min, max]
        rangepn = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "prelut_range", "prelut_range")
        rangepn.setMinInValue(minInputValue)
        rangepn.setMaxInValue(maxInputValue)
        rangepn.setMinOutValue(0.0)
        rangepn.setMaxOutValue(1.0)

        prelutpns.append(rangepn)

        # If the prelut only affects the range, skip generating a lut to represent it
        if inputResolution > 2:
            # Generate 1d LUT by running values through the
            # - inverse normalization
            # - the cspprelut
            samples = [0.0]*outputResolution*3

            for i in range(outputResolution):
                # Normalized LUT input
                inputValue = float(i)/(outputResolution-1)

                # Invert the normalization
                rangedValue = inputValue*(maxInputValue - minInputValue) + minInputValue

                sample = [0.0, 0.0, 0.0]

                # For each channel
                for channel in range(len(cspPreluts)):
                    # Find the location of the de-normalized value in the prelut
                    for prelutIndex in range(inputResolution):
                        if cspPreluts[channel][0][prelutIndex] > rangedValue:
                            break

                    # Get the interpolation value
                    prelutIndexLow = max(0, prelutIndex-1)
                    prelutIndexHigh = min(inputResolution-1, prelutIndex)
                    prelutInterp = (rangedValue - cspPreluts[channel][0][prelutIndexLow])/(
                        cspPreluts[channel][0][prelutIndexHigh] - cspPreluts[channel][0][prelutIndexLow])

                    # Find the output value
                    outputInterpolationRange = (cspPreluts[channel][1][prelutIndexHigh] - cspPreluts[channel][1][prelutIndexLow])
                    outputInterpolated = prelutInterp*outputInterpolationRange + cspPreluts[channel][1][prelutIndexLow]

                    sample[channel] = outputInterpolated

                samples[i*3:(i+1)*3] = sample

            # Create a 1D LUT with generated sample values
            lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "prelut_lut1d", "prelut_lut1d")
            lutpn.setArray(len(cspPreluts), samples)

            prelutpns.append(lutpn)

        return prelutpns

    # XXX
    # Need to warn user about the lack of an inverse for 3D LUTs
    # Or implement one. That would be slow in Python (or C, or OpenCL) though
    @staticmethod
    def readCSP(lutPath, inverse=False, interpolation='linear'):
        with open(lutPath) as f:
            lines = f.read().splitlines()

        resolution = []
        samples = []
        prelut = []
        minInputValue = 0.0
        maxInputValue = 1.0

        tokens = lines[0].split()
        if tokens[0] == "CSPLUTV100":
            format = lines[1].split()[0]

            if format in ["1D", "3D"]:
                # Find the first line of metadata
                metaStart = 2
                while lines[metaStart].rstrip() != "BEGIN METADATA":
                    metaStart += 1
                metaStart += 1

                metadata = ""
                dataStart = metaStart
                for line in lines[metaStart:]:
                    dataStart += 1
                    if line.rstrip() == "END METADATA":
                        break
                    else:
                        metadata += (line.rstrip())
                        #print( "metadata line : %s" % line.rstrip() )

                #print( "metadata : %s" % metadata)
                dataStart += 1
                
                while lines[dataStart].rstrip() == '':
                    #print( "blank line")
                    dataStart += 1

                #print( "Prelut data starts on line : %d" % dataStart )

                #
                # Read Index Maps
                #

                # Red Index Map
                prelutRedResolution = int(lines[dataStart+0])
                prelutRedInput = list(map(float, lines[dataStart+1].split()))
                prelutRedOutput = list(map(float, lines[dataStart+2].split()))

                # Green Index Map
                prelutGreenResolution = int(lines[dataStart+3])
                prelutGreenInput = list(map(float, lines[dataStart+4].split()))
                prelutGreenOutput = list(map(float, lines[dataStart+5].split()))

                # Blue Index Map
                prelutBlueResolution = int(lines[dataStart+6])
                prelutBlueInput = list(map(float, lines[dataStart+7].split()))
                prelutBlueOutput = list(map(float, lines[dataStart+8].split()))

                prelut = [[prelutRedInput, prelutRedOutput],
                    [prelutGreenInput, prelutGreenOutput],
                    [prelutBlueInput, prelutBlueOutput]]

                #
                # Read LUT data
                #
                dataStart = dataStart+10

                while lines[dataStart].rstrip() == '':
                    #print( "blank line")
                    dataStart += 1

                resolution = list(map(int, lines[dataStart].split()))
                dataStart += 1

                #print( "lut data starts on line : %d" % dataStart )

                # 3D LUT data
                if format == "3D":
                    # CSP incremements LUT samples red, then green, then blue
                    # CLF incremements LUT samples blue, then green, then red 
                    # so we need to move samples around
                    samples = [0.0]*resolution[0]*resolution[1]*resolution[2]*3
                    cspIndex = 0
                    for line in lines[dataStart:]:
                        # Convert from sample number to LUT index, CSP-style
                        indexR = cspIndex%resolution[0]
                        indexG = (cspIndex//resolution[0])%resolution[1]
                        indexB = cspIndex//(resolution[0]*resolution[1])

                        # Convert from LUT index to sample number, CLF-style
                        clfIndex = (indexR*resolution[0] + indexG)*resolution[1] + indexB
                        clfIndex *= 3

                        # Convert from text to float
                        cspSamples = list(map(float, line.split()))

                        # Add to the sample values array
                        if len(cspSamples) == 3:
                            #print( "csp sample %d -> lut index : %d, %d, %d -> clf index : %d" % 
                            #    (cspIndex, indexR, indexG, indexB, clfIndex))
                            #print( "lut value : %3.6f %3.6f %3.6f" % (cspSamples[0], cspSamples[1], cspSamples[2]) )

                            samples[clfIndex:clfIndex+3] = cspSamples

                        cspIndex += 1

                # 1D LUT data
                elif format == "1D":
                    samples = [0.0]*resolution[0]*3

                    cspIndex = 0
                    for line in lines[dataStart:]:
                        clfIndex = cspIndex
                        clfIndex *= 3

                        # Convert from text to float
                        cspSamples = list(map(float, line.split()))

                        # Add to the sample values array
                        if len(cspSamples) == 3:
                            #print( "csp sample %d -> clf index : %d" % 
                            #    (cspIndex, clfIndex/3))
                            #print( "lut value : %3.6f %3.6f %3.6f" % (cspSamples[0], cspSamples[1], cspSamples[2]) )

                            samples[clfIndex:clfIndex+3] = cspSamples

                        cspIndex += 1

        #
        # Create ProcessNodes
        #
        lutpns = []

        if prelut != []:
            #print( "Generating prelut")
            prelutpns = LutFormatCSP.generateCLFPrelut(prelut)
            if prelutpns != []:
                for prelutpn in prelutpns:
                    lutpns.append(prelutpn)

        if format == "3D":
            lutpn = clf.LUT3D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut3d", "lut3d")
            lutpn.setArray(resolution, samples)
            lutpns.append(lutpn)
        elif format == "1D":
            lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut1d", "lut1d")
            lutpn.setArray(3, samples)
            lutpns.append(lutpn)

        return lutpns
    # readCSP

    @ staticmethod
    def writeCSP1D(filename, 
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
            fp.write('CSPLUTV100\n')
            fp.write('1D\n')
            fp.write('\n')
            fp.write('BEGIN METADATA\n')
            fp.write('END METADATA\n')

            fp.write('\n')

            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')
            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')
            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')

            fp.write('\n')

            fp.write('%d\n' % entries)
            if components == 1:
              for i in range(0, entries):
                  entry = ''
                  for j in range(3):
                      entry = '%s %3.6f' % (entry, data[i * channels])
                  fp.write('%s\n' % entry)
            else:
              for i in range(entries):
                  entry = ''
                  for j in range(components):
                      entry = '%s %3.6f' % (entry, data[i * channels + j])
                  fp.write('%s\n' % entry)
            fp.write('\n')

        return True
    # writeCSP1D

    @staticmethod
    def writeCSP3D(filename, 
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
            fp.write('CSPLUTV100\n')
            fp.write('3D\n')
            fp.write('\n')
            fp.write('BEGIN METADATA\n')
            fp.write('END METADATA\n')

            fp.write('\n')

            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')
            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')
            fp.write('2\n')
            fp.write('%f %f\n' % (from_min, from_max))
            fp.write('0.0 1.0\n')

            fp.write('\n')

            fp.write('%s\n' % ' '.join(map(str, resolution)) )
     
            # Note: CSP increments red fastest
            for b in range(resolution[0]):
                for g in range(resolution[1]):
                    for r in range(resolution[2]):
                        entry = " ".join(map(lambda x : "%3.6f" % x, data[r][g][b]))
                        fp.write('%s\n' % entry)
        return True
    # writeCSP3D

    @staticmethod
    def writeCSP1D3D(lutPath,
                     samples1dIn,
                     lutResolution1dIn,
                     inputMin,
                     inputMax,
                     samples3d,
                     lutResolution3d):

        #print( ' '.join(map(str, lutResolution3d)) )

        with open(lutPath, 'w') as fp:
            fp.write('CSPLUTV100\n')
            fp.write('3D\n')
            fp.write('\n')
            fp.write('BEGIN METADATA\n')
            fp.write('END METADATA\n')

            fp.write('\n')

            for c in range(3):
                fp.write('%d\n' % lutResolution1dIn)

                for s in range(lutResolution1dIn):
                    value = (float(s)/(lutResolution1dIn-1))*(
                        inputMax - inputMin) + inputMin
                    fp.write('%f ' % value)
                fp.write('\n')

                for s in range(lutResolution1dIn):
                    fp.write('%f ' % samples1dIn[s*3 + c])
                fp.write('\n')

            fp.write('\n')

            fp.write('%s\n' % ' '.join(map(str, lutResolution3d)) )
     
            # Note: CSP increments red fastest
            for b in range(lutResolution3d[0]):
                for g in range(lutResolution3d[1]):
                    for r in range(lutResolution3d[2]):
                        entry = " ".join(map(lambda x : "%3.6f" % x, samples3d[r][g][b]))
                        fp.write('%s\n' % entry)
        return True
    # writeCSP1D3D

# LutFormatCSP
