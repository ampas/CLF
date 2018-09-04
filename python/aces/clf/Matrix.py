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

import numpy as np

from ProcessNode import *
from Array import Array

class Matrix(ProcessNode):
    "A Common LUT Format Matrix ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name=""):
        "%s - Initialize the standard class variables" % 'Matrix'
        ProcessNode.__init__(self, 'Matrix', inBitDepth, outBitDepth, id, name)
    # __init__

    def setMatrix(self, dimensions, values, floatEncoding='string'):
        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
        values = Array(dimensions,
            values,
            integers,
            floatEncoding=floatEncoding)
        self._array = values
        self.addElement( values )
    # setMatrix

    def readChild(self, element):
        child = None
        if element.tag == 'Array':
            child = Array()
            child.read(element)

            integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
            child.setValuesAreIntegers(integers)

            self._array = child
        return child
    # readChild

    def process(self, values, stride=0, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        dimensions = self._array.getDimensions()
        matrix = self._array.getValues()

        '''
        print( "value       : %s" % value )
        print( "dimensions  : %s" % dimensions )
        print( "matrix      : %s" % matrix )
        '''

        # Handle processing of single values
        if stride == 0:
            stride = len(values)

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        # For each pixel
        for p in range(len(values)/stride):
            value = values[p*stride:(p+1)*stride]
            outValue = np.zeros(stride, dtype=np.float32)

            for i in range(min(dimensions[0], stride)):
                offset = i*dimensions[1]
                outValue[i] = 0
                for j in range(dimensions[0]):
                    outValue[i] += matrix[j + offset]*value[j]

                #print( "value : %d : %f = %f * %f + %f * %f + %f * %f" % (
                #    i, outValue[i], matrix[0 + offset], value[0], matrix[1 + offset], value[1], matrix[2 + offset], value[2]))
                if dimensions[1] == dimensions[0]+1:
                    outValue[i] += matrix[offset+dimensions[1]-1]

                #outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(dimensions[0], stride),stride):
                outValue[i] = value[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process
# Matrix


