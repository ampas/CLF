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

from ProcessNode import *
from Array import Array
from IndexMap import IndexMap
from Common import uint16ToHalf, halfToUInt16

class LUT1D(ProcessNode):
    "A Common LUT Format LUT 1D ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        interpolation='linear', rawHalfs='', halfDomain=''):
        "%s - Initialize the standard class variables" % 'LUT1D'
        ProcessNode.__init__(self, 'LUT1D', inBitDepth, outBitDepth, id, name)
        if interpolation != '':
            self._attributes['interpolation'] = interpolation
        if rawHalfs != '':
            self._attributes['rawHalfs'] = rawHalfs
        if halfDomain != '':
            self._attributes['halfDomain'] = halfDomain


        self._array = None
        self._indexMaps = []
    # __init__

    def setIndexMaps(self, valuesR, valuesG = None, valuesB = None):
        indexMapR = IndexMap(len(valuesR[0]), valuesR)
        self._indexMaps.append( indexMapR ) 
        self.addElement( indexMapR )
        
        # Either one or three indexMaps
        if( valuesG != None and valuesB != None ):
            indexMapG = IndexMap(len(valuesG[0]), valuesG)
            self._indexMaps.append( indexMapG ) 
            self.addElement( indexMapG )

            indexMapB = IndexMap(len(valuesB[0]), valuesB)
            self._indexMaps.append( indexMapB ) 
            self.addElement( indexMapB )
    # setIndexMaps

    def setArray(self, dimension, values, floatEncoding='string'):
        dimensions = [len(values)/dimension, dimension]

        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
        rawHalfs = not (self.getAttribute('rawHalfs') in [None, False])

        self._array = Array(dimensions, 
            values, 
            rawHalfs=rawHalfs, 
            integers=integers,
            floatEncoding=floatEncoding)
        self.addElement( self._array )
    # setArray

    def getLUTDimensions(self):
        return self._array.getDimensions()
    def getLUTValues(self):
        return self._array.getValues()

    def getIndexMapDimensions(self, channel):
        return self._indexMaps[channel].getDimensions()
    def getIndexMapValues(self, channel):
        return self._indexMaps[channel].getValues()

    def readChild(self, element):
        child = None
        elementType = self.getElementType(element.tag)
        if elementType == 'Array':
            rawHalfs = not (self.getAttribute('rawHalfs') in [None, False])

            child = Array(rawHalfs=rawHalfs)
            child.read(element)

            integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
            child.setValuesAreIntegers(integers)

            self._array = child
        elif element.tag == 'IndexMap':
            child = IndexMap()
            child.read(element)
            self._indexMaps.append( child )
        return child
    # readChild

    def process(self, values, stride=0, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        interpolation = ''
        if 'interpolation' in self._attributes: interpolation = self._attributes['interpolation']

        rawHalfs = not (self.getAttribute('rawHalfs') in [None, False])
        halfDomain = not (self.getAttribute('halfDomain') in [None, False])
        
        '''
        print( "interpolation  : %s" % interpolation )
        print( "raw halfs      : %s" % rawHalfs )
        print( "halfs domain   : %s" % halfDomain )
        '''

        # Get LUT dimensions
        dimensions = self.getLUTDimensions()

        # Handle processing of single values
        if stride == 0:
            stride = len(values)

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        for p in range(len(values)/stride):
            value = values[p*stride:(p+1)*stride]
            outValue = values[p*stride:(p+1)*stride]

            for i in range(min(3, stride)):
                # Run through single Index Map then normalize
                if len(self._indexMaps) > 1:
                    outValue[i] = self._indexMaps[i].process(outValue[i])
                    outValue[i] /= float(dimensions[0]-1)

                # Run through per-channel Index Map then normalize
                elif len(self._indexMaps) > 0:
                    outValue[i] = self._indexMaps[0].process(outValue[i])
                    outValue[i] /= float(dimensions[0]-1)

                # Normalize from bit-depth
                else:
                    # Convert input bit depth
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                # Run through LUT
                # Use Cubic interpolation
                if interpolation == 'cubic':
                    outValue[i] = self._array.lookup1DCubic(outValue[i], i)

                # Use halfDomain lookup and interpolation
                elif halfDomain:
                    outValue[i] = self._array.lookup1DHalfDomain(outValue[i], i, interpolate=True)

                # Linear interpolation is the default
                #elif interpolation == 'linear':
                else:
                    outValue[i] = self._array.lookup1DLinear(outValue[i], i)


                # Bit Depth conversion for output is ignored for LUTs
                # as LUT values are assumed to target a specific bit depth
                #outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(3, stride),stride):
                outValue[i] = value[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process
# LUT1D

#
# Create a 1D lut based on sampling a function
#
def simpleSampledLUT(id, 
    transformId, 
    channels, 
    resolution, 
    f=lambda x: x, 
    inBitDepth=bitDepths["FLOAT16"],
    outBitDepth=bitDepths["FLOAT16"]):

    l1d = LUT1D(inBitDepth, 
        outBitDepth, 
        id, 
        transformId)

    lutValues = [0.0]*resolution*channels

    for i in range(resolution):
        sample = float(i)/(resolution-1)
        for c in range(channels):
            lutValueIndex = i*channels + c
            lutValues[lutValueIndex] = f(sample)
            #print( "%d, %d, %d: %f -> %f" % (i, c, lutValueIndex, sample, f(sample)))

    l1d.setArray(channels, lutValues)
    return l1d

#
# Create a 1D lut based on sampling a function, for all possible half-float values
#
def simpleSampledLUTHalfDomain(id, 
    transformId, 
    channels, 
    f=lambda x: x, 
    rawHalfs=False, 
    inBitDepth=bitDepths["FLOAT16"],
    outBitDepth=bitDepths["FLOAT16"]):

    l1dH = LUT1D(inBitDepth, 
        outBitDepth, 
        id, 
        transformId,
        halfDomain=True,
        rawHalfs=rawHalfs)

    resolution = 65536
    lutValues = [0.0]*resolution*channels

    for i in range(resolution):
        # Figure out which half value corresponds to the specific 16 bit integer value
        sample = uint16ToHalf(i)

        # Apply the function to the sample value
        # Should take the channel as input, or process an RGB triple
        fvalue = f(sample)

        # Store the values
        for c in range(channels):
            lutValueIndex = i*channels + c
            lutValues[lutValueIndex] = fvalue
            #print( "%d, %d, %d: %f -> %f" % (i, c, lutValueIndex, sample, fvalue))

    l1dH.setArray(channels, lutValues)

    return l1dH

