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

import math
import numpy as np
try:
    from scipy.interpolate import interp1d, LinearNDInterpolator
    sciPyEnabled = True
    raise ImportError('A very specific bad thing happened')
except ImportError, e:
    #print( "Scipy import failed" )
    sciPyEnabled = False

import xml.etree.ElementTree as etree

from Common import *

class Array:
    "A Common LUT Format Array element"

    def __init__(self, 
        dimensions=[], 
        values=[], 
        integers=False, 
        rawHalfs=False,
        floatEncoding='string',
        elementType='Array'):
        "%s - Initialize the standard class variables" % elementType
        self._dimensions = dimensions
        self._values = values
        self._valuesAreIntegers=integers
        self._rawHalfs = rawHalfs
        self._floatEncoding = floatEncoding
        self._elementType = elementType

        self._interp1ds = None
        self._interp3d = None

        # Create the interpolators that we'll use later
        if self._values != [] and self._dimensions != []:
            if len(self._dimensions) == 2:
                self.create1dInterpolators()
            elif len(self._dimensions) == 4:
                self.create3dInterpolator()
    # __init__

    def setDimensions(self, dimensions):
        self._dimensions = dimensions
    def getDimensions(self):
        return self._dimensions

    def setValues(self, values):
        self._values = values

        if self._values != [] and self._dimensions != []:
            if len(self._dimensions) == 2:
                self.create1dInterpolators()
            elif len(self._dimensions) == 4:
                self.create3dInterpolator()

    def getValues(self):
        return self._values

    def setValuesAreIntegers(self, integers):
        self._valuesAreIntegers = integers
    def getValuesAreIntegers(self):
        return self._valuesAreIntegers

    def setRawHalfs(self, rawHalfs):
        self._rawHalfs = rawHalfs
    def getRawHalfs(self):
        return self._rawHalfs

    def setFloatEncoding(self, floatEncoding):
        self._floatEncoding = floatEncoding
    def getFloatEncoding(self):
        return self._floatEncoding

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.set('dim', " ".join(map(str, self._dimensions)))
        
        # Slightly prettier printing
        element.text = "\n"

        # Use the last value for 1D or 3D LUTs
        if len(self._dimensions) in [2, 4]:
            columns = self._dimensions[-1]

        # Use the second dimension for Matrices
        else:
            columns = self._dimensions[1]

        integers = self._valuesAreIntegers

        for n in range(len(self._values)/columns):
            sample = self._values[n*columns:(n+1)*columns]

            # Integer values
            if integers:
                sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))

            # Float Values
            # Floats encoded using bitwise equivalent hex or integer values
            if self._rawHalfs or self._floatEncoding != 'string':
                # Encoding options: 
                # integer16bit, integer32bit, integer64bit, hex16bit, hex32bit, hex64bit
                if self._floatEncoding in ['integer16bit', 'integer32bit', 'integer64bit', 
                    'hex16bit', 'hex32bit', 'hex64bit']:
                    element.set('floatEncoding', self._floatEncoding)

                if self._rawHalfs or self._floatEncoding == 'integer16bit':
                    sample = map(halfToUInt16, sample)
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                elif self._floatEncoding == 'integer32bit':
                    sample = map(float32ToUInt32, sample)
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                elif self._floatEncoding == 'integer64bit':
                    sample = map(doubleToUInt64, sample)
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))

                elif self._floatEncoding == 'hex16bit':
                    sample = map(halfToHex, sample)
                    sampleText = " ".join(map(lambda x: "%15s" % str(x), sample))
                elif self._floatEncoding == 'hex32bit':
                    sample = map(float32ToHex, sample)
                    sampleText = " ".join(map(lambda x: "%15s" % str(x), sample))
                elif self._floatEncoding == 'hex64bit':
                    sample = map(doubleToHex, sample)
                    sampleText = " ".join(map(lambda x: "%16s" % str(x), sample))

                # An unknown encoding. Will be ignored.
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))

            # Floats printed as strings
            else:
                sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
            element.text += sampleText + "\n"

        # Hack
        # Will correct formatting for CLFs. Not Clip though...
        element.text += "\t\t"

        return element
    # write

    def read(self, element):
        # Store attributes
        for key, value in element.attrib.iteritems():
            if key == 'dim':
                self._dimensions = map(int, value.split())
            elif key == 'floatEncoding':
                self._floatEncoding = value

        dtype = np.float32
        if self._rawHalfs or self._floatEncoding == 'integer16bit':
            cast = lambda x: float(uint16ToHalf(x))
            dtype = np.float16
        elif self._floatEncoding == 'integer32bit':
            cast = uint32ToFloat32
            dtype = np.float32
        elif self._floatEncoding == 'integer64bit':
            cast = uint64ToDouble
            dtype = np.float64
        elif self._floatEncoding == 'hex16bit':
            cast = hexToHalf
            dtype = np.float16
        elif self._floatEncoding == 'hex32bit':
            cast = hexToFloat32
            dtype = np.float32
        elif self._floatEncoding == 'hex64bit':
            cast = hexToDouble
            dtype = np.float64
        else:
            cast = float
            dtype = np.float32

        textValues = element.text.split()
        numValues = np.zeros(len(textValues), dtype=dtype)
        for i in range(len(textValues)):
            numValues[i] = cast(textValues[i])

        self.setValues(numValues)
    # read

    def printInfo(self):
        print( "%20s" % "Array" )
        print( "%20s : %s" % ("Dimensions", self._dimensions) )
        #print( "\t\tvalues     : %s" % self._values )
        print( "%20s" % "Values" )

        # Use the last value for 1D or 3D LUTs
        if len(self._dimensions) in [2, 4]:
            columns = self._dimensions[-1]

        # Use the second dimension for Matrices
        else:
            columns = self._dimensions[1]

        rows = len(self._values)/columns
        if rows > 10:
            for n in (range(3)):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )

            print( " "*30 + " "*(columns/2*16) + "    ...    " )

            for n in (range(rows-3,rows)):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )
        else:
            for n in range(rows):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )
    # printInfo

    #
    # Interpolators
    #
    def create1dInterpolators(self):
        dimensions = self._dimensions

        #print( "Creating 1D interpolator" )

        self._interp1ds = []

        if sciPyEnabled:
            if dimensions[0] >= 4 and dimensions[0] < 65536:
                for channel in range(dimensions[1]):
                    indices = np.arange(0, dimensions[0])
                    output = np.zeros(dimensions[0], dtype=np.float32)
                    for i in range(len(output)):
                        output[i] = self.lookup1D(i, channel)

                    #print( indices )
                    #print( output )

                    # Create a cubic interpolator using the indices and array values
                    cubicInterpolator = interp1d(indices, output, 
                        kind='cubic', bounds_error=False, fill_value=0.0)

                    self._interp1ds.append(cubicInterpolator)

    def create3dInterpolator(self):
        values = self._values
        dimensions = self._dimensions

        self._interp3d = None

        if sciPyEnabled:
            # Create index array
            indices = [[0.0,0.0,0.0]]*dimensions[0]*dimensions[1]*dimensions[2]

            # Create output value array
            output = [[0.0,0.0,0.0]]*dimensions[0]*dimensions[1]*dimensions[2]

            i = 0
            for z in range(dimensions[2]):
                for y in range(dimensions[1]):
                    for x in range(dimensions[0]):
                        index1 = (x*dimensions[0]*dimensions[1] + y*dimensions[1] + z)*3 
                        indices[i] = [float(x), float(y), float(z)]
                        output[i] = values[index1:index1+3]
                        i += 1

            # Create tetrahedral interpolator
            tetrahedralInterpolator = LinearNDInterpolator(indices, output)

            self._interp3d = tetrahedralInterpolator

    #
    # Lookup values
    #

    # 1D exact
    def lookup1D(self, index, channel):
        values = self._values
        dimensions = self._dimensions

        if dimensions[1] == 3:
            channel = max(0, min(2, channel))
            if index < 0:
                result = values[0 + channel]
            elif index >= dimensions[0]:
                result = values[(dimensions[0]-1)*dimensions[1] + channel]
            else:
                result = values[index*dimensions[1] + channel]
        else:
            if index < 0:
                result = values[0]
            elif index >= dimensions[0]:
                result = values[dimensions[0]-1]
            else:
                result = values[index]
        return result
    # lookup1D

    # 1D Half-Domain lookup - nearest match
    def lookup1DHalfDomainNearest(self, position, channel):
        values = self._values
        dimensions = self._dimensions

        # Input half-float values are treated as 16 bit unsigned integers
        # Those integers are the index into the LUT
        if not interpolate:
            index = halfToUInt16(position)
            value = self.lookup1D(index, channel)
            result = value

        return result

    # 1D Half-Domain lookup - interpolated lookup
    def lookup1DHalfDomainInterpolated(self, position, channel):
        values = self._values
        dimensions = self._dimensions

        # In this case, the input values are treated as float32
        # The nearest float16 value are found and then 
        # used to as two entries in the LUT

        # 16 bit half floats uses code values as follows
        # We have to account for each case
        # 0 to 31743 = positive values 0.0 to 65504.0
        # 31744 = Inf
        # 31745 to 32767 = NaN
        # 32768 to 64511 = negative values 0.0 to -65504.0
        # 64512 = -Inf
        # 64513 to 65535 = NaN

        # Cast float32 to float16
        floatValue = position
        halfValue1 = np.float16(floatValue)

        # NaNs
        if np.isnan(halfValue1):
            #print( "lookup1DHalfDomain - NaN" )
            index = 31745
            value = self.lookup1D(index, channel)
            result = value

        # Infs
        elif np.isinf(halfValue1):
            # -Inf
            if position < 0:
                #print( "lookup1DHalfDomain - -Inf" )
                index = 64512
                value = self.lookup1D(index, channel)
                result = value
            # Inf
            else:
                #print( "lookup1DHalfDomain - +Inf" )
                index = 31744
                value = self.lookup1D(index, channel)
                result = value

        # Positive and negative numbers:
        else:
            floatDifference = floatValue - halfValue1

            offset = 1
            indexMin = 0
            indexMax = 31743
            if floatValue < 0.0:
                offset = -1
                indexMin = 32768
                indexMax = 64511

            # Cast could put half value above or below the original float value
            if floatDifference >= 0.0:
                halfValue2 = uint16ToHalf(max(indexMin, min(indexMax, halfToUInt16(halfValue1)+offset)))
                halfRange = (halfValue2 - halfValue1)
                if halfRange != 0.0:
                    ratio = floatDifference/halfRange
                else:
                    ratio = 0.0
            else:
                halfValue2 = uint16ToHalf(max(indexMin, min(indexMax, halfToUInt16(halfValue1)-offset)))
                halfRange = (halfValue2 - halfValue1)
                if halfRange != 0.0:
                    import warnings
                    #np.seterr(all='warn')
                    #try:
                    ratio = floatDifference/halfRange
                    #except RuntimeWarning:
                    #    print( "warning : floatDifference %f, halfRange %f" % (floatDifference, halfRange) )
                else:
                    ratio = 0.0

            # Convert half values to integers
            index1 = halfToUInt16(halfValue1)
            index2 = halfToUInt16(halfValue2)

            # Lookup values in LUT using integer indices
            value1 = self.lookup1D(index1, channel)
            value2 = self.lookup1D(index2, channel)

            # Interpolate
            result = (1-ratio)*value1 + ratio*value2

            '''
            print( "lookup1DHalfDomain - normal numbers" )
            print( "lookup1DHalfDomain - position        : %6.9f" % position )
            print( "lookup1DHalfDomain - float value     : %6.9f" % floatValue )
            print( "lookup1DHalfDomain - index 1         : %d" % index1 )
            print( "lookup1DHalfDomain - index 2         : %d" % index2 )
            print( "lookup1DHalfDomain - half value 1    : %6.9f" % halfValue1 )
            print( "lookup1DHalfDomain - half value 2    : %6.9f" % halfValue2 )
            print( "lookup1DHalfDomain - floatDifference : %6.9f" % floatDifference )
            print( "lookup1DHalfDomain - ratio           : %6.9f" % ratio )
            print( "lookup1DHalfDomain - value 1         : %6.9f" % value1 )
            print( "lookup1DHalfDomain - value 2         : %6.9f" % value2 )
            print( "lookup1DHalfDomain - result          : %6.9f" % result )
            '''                           

        return result
    # lookup1DHalfDomainInterpolated

    # 1D Half-Domain lookup
    def lookup1DHalfDomain(self, position, channel, interpolate=True):
        values = self._values
        dimensions = self._dimensions

        # Input half-float values are treated as 16 bit unsigned integers
        # Those integers are the index into the LUT
        if not interpolate:
            result = self.lookup1DHalfDomainNearest(position, channel)

        # In this case, the input values are treated as float32
        # The nearest float16 value are found and then 
        # used to as two entries in the LUT
        else:
            result = self.lookup1DHalfDomainInterpolated(position, channel)

        return result

    # 1D linearly interpolation lookup
    def lookup1DLinear(self, position, channel):
        values = self._values
        dimensions = self._dimensions

        index = position*(dimensions[0]-1)
        indexLow  = int(math.floor(index))
        indexHigh = int(math.ceil(index))
        interp = index - indexLow

        value1 = self.lookup1D(indexLow, channel)
        value2 = self.lookup1D(indexHigh, channel)

        result = (1-interp)*value1 + interp*value2

        return result
    # lookup1DLinear

    # 1D cubic interpolation lookup
    def lookup1DCubic(self, position, channel, useSciPy=False):
        dimensions = self._dimensions

        if dimensions[0] < 4 or not useSciPy or not sciPyEnabled:
            return lookup1DLinear(position, channel)

        index = position*(dimensions[0]-1)

        # Handle out of bounds positions
        if index < 0:
            result = self.lookup1D(0, channel)
        elif index >= dimensions[0]:
            result = self.lookup1D(dimensions[0]-1, channel)

        # Use cubic interpolation
        else:
            if not self._interp1ds:
                self.create1dInterpolators()

            lutChannel = min(dimensions[1], channel)
            result = self._interp1ds[lutChannel](index)

        return result

    def lookup3D(self, index3):
        values = self._values
        dimensions = self._dimensions

        # Corner cases
        index3 = map(lambda a, b: max(0, min(a, b-1)), index3, dimensions)

        index1 = (index3[0]*dimensions[0]*dimensions[1] + index3[1]*dimensions[1] + index3[2])*3 

        #result = [values[index1], values[index1+1], values[index1+2]]
        result = values[index1:index1+3]

        #print( "%d, %d, %d -> %d, %s" % (index3[0], index3[1], index3[2], index1, result))
        return result
    # lookup3D

    def lookup3DTrilinear(self, position):
        dimensions = self._dimensions

        #print( position )
        #print( dimensions )
        #print( len(self._values) )

        enclosingCubeColors = [0.0, 0.0, 0.0] * 8

        # clamp because we only use values between 0 and 1
        position = map(clamp, position)

        # index values interpolation factor for RGB
        indexRf = (position[0] * (dimensions[0]-1))
        interpR, indexR = math.modf(indexRf)
        indexR = int(indexR)

        indexGf = (position[1] * (dimensions[1]-1))
        interpG, indexG = math.modf(indexGf)
        indexG = int(indexG)

        indexBf = (position[2] * (dimensions[2]-1))
        interpB, indexB = math.modf(indexBf)
        indexB = int(indexB)

        #print( "index : %d, %d, %d" % (indexR, indexG, indexB))

        # Sample the 8 points around the current sample position
        enclosingCubeColors[0] = self.lookup3D([indexR    , indexG    , indexB    ])
        enclosingCubeColors[1] = self.lookup3D([indexR    , indexG    , indexB + 1])
        enclosingCubeColors[2] = self.lookup3D([indexR    , indexG + 1, indexB    ])
        enclosingCubeColors[3] = self.lookup3D([indexR    , indexG + 1, indexB + 1])
        enclosingCubeColors[4] = self.lookup3D([indexR + 1, indexG    , indexB    ])
        enclosingCubeColors[5] = self.lookup3D([indexR + 1, indexG    , indexB + 1])
        enclosingCubeColors[6] = self.lookup3D([indexR + 1, indexG + 1, indexB    ])
        enclosingCubeColors[7] = self.lookup3D([indexR + 1, indexG + 1, indexB + 1])

        # Interpolate along the 4 lines in B
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[1], interpB);
        enclosingCubeColors[2] = mix(enclosingCubeColors[2], enclosingCubeColors[3], interpB);
        enclosingCubeColors[4] = mix(enclosingCubeColors[4], enclosingCubeColors[5], interpB);
        enclosingCubeColors[6] = mix(enclosingCubeColors[6], enclosingCubeColors[7], interpB);
    
        # Interpolate along the 2 lines in G
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[2], interpG);
        enclosingCubeColors[4] = mix(enclosingCubeColors[4], enclosingCubeColors[6], interpG);

        # Interpolate along the 1 line in R
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[4], interpR);

        return enclosingCubeColors[0];
    # lookup3DTrilinear

    def lookup3DTetrahedral(self, position, useSciPy=False):
        # Fallback, and the default for now
        if not useSciPy or not sciPyEnabled:
            return self.lookup3DTrilinear(position)
        else:
            if not self._interp3d:
                self.create3dInterpolator()

            dimensions = self._dimensions

            # clamp because we only use values between 0 and 1
            position = map(clamp, position)

            # index values interpolation factor for RGB
            indexRf = (position[0] * (dimensions[0]-1))
            indexGf = (position[1] * (dimensions[1]-1))
            indexBf = (position[2] * (dimensions[2]-1))

            interpolated = self._interp3d(indexRf, indexGf, indexBf)

            return interpolated
# Array


