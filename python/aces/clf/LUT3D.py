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

class LUT3D(ProcessNode):
    "A Common LUT Format LUT 3D ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        interpolation='trilinear'):
        "%s - Initialize the standard class variables" % 'LUT3D'
        ProcessNode.__init__(self, 'LUT3D', inBitDepth, outBitDepth, id, name)
        if interpolation != '':
            self._attributes['interpolation'] = interpolation

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

    def setArray(self, dimension, values):
        dimensions = dimension
        dimensions.append(3)

        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))

        self._array = Array(dimensions, values, integers)
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
        if element.tag == 'Array':
            child = Array()
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

    def process(self, value, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        interpolation = ''
        if 'interpolation' in self._attributes: interpolation = self._attributes['interpolation']

        '''
        print( "interpolation  : %s" % interpolation )
        '''

        # Get LUT dimensions
        dimensions = self.getLUTDimensions()

        # Actually process a value or two
        outValue = value

        # Run each channel through the index map, or base normalization
        for i in range(min(3, len(value))):
            # Run through single Index Map then normalize
            if len(self._indexMaps) > 1:
                outValue[i] = self._indexMaps[i].process(outValue[i])
                outValue[i] /= float(dimensions[i]-1)

            # Run through per-channel Index Map then normalize
            elif len(self._indexMaps) > 0:
                outValue[i] = self._indexMaps[0].process(outValue[i])
                outValue[i] /= float(dimensions[i]-1)

            # Normalize from bit-depth
            else:
                # Convert input bit depth
                outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

        # Run color through LUT
        # trilinear interpolation
        if interpolation == 'trilinear':
            outValue = self._array.lookup3DTrilinear(outValue)

        # tetrahedral interpolation
        elif interpolation == 'tetrahedral':
            outValue = self._array.lookup3DTetrahedral(outValue)

        # Bit Depth conversion for output is ignored for LUTs
        # as LUT values are assumed to target a specific bit depth
        #for i in range(min(3, len(value))):
        #   outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# LUT3D

#
# 3D LUT example
#
def simple3DLUT(id, 
    transformId, 
    resolution, 
    f=lambda x, y, z: [x, y, z], 
    inBitDepth=bitDepths["FLOAT16"],
    outBitDepth=bitDepths["FLOAT16"]):

    l3d = LUT3D(inBitDepth, 
        outBitDepth, 
        id, 
        transformId)

    channels = 3
    lutValues = [0.0]*resolution[0]*resolution[1]*resolution[2]*channels

    # Should make the sampling work with integer values as well.
    # Current approach assumes normalized float values as input
    for x in range(resolution[0]):
        samplex = float(x)/(resolution[0]-1)

        for y in range(resolution[1]):
            sampley = float(y)/(resolution[1]-1)

            for z in range(resolution[2]):
                samplez = float(z)/(resolution[2]-1)

                # Red changes fastest
                lutValueIndex = (((x*resolution[0] +y)*resolution[1] + z))*channels

                fvalue = f(samplex, sampley, samplez)
                lutValues[lutValueIndex:lutValueIndex+channels] = fvalue

                #sample = [samplex, sampley, samplez]
                #print( "%d, %d, %d, %d: %s -> %s" % (x, y, z, lutValueIndex, sample, fvalue))

    l3d.setArray(resolution, lutValues)
    return l3d
