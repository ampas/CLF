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
import six

import xml.etree.ElementTree as etree

from aces.clf.Common import *
from aces.clf.Array import Array

class IndexMap:
    "A Common LUT Format IndexMap element"

    def __init__(self, dimension=[], values=[], elementType='IndexMap', useCachedProcess=True):
        "%s - Initialize the standard class variables" % elementType
        self._dimension = dimension
        self._values = values
        self._elementType = elementType
        self._useCachedProcess = useCachedProcess
        self._processCached = None

        if self._useCachedProcess and self._values != [] and self._dimension != []:
            self._createCachedProcess()
    # __init__

    def setDimension(self, dimension):
        self._dimension = dimension
    def getDimension(self):
        return self._dimension

    def setValues(self, values):
        self._values = values
        if self._useCachedProcess and self._values != [] and self._dimension != []:
            self._createCachedEval()
    def getValues(self):
        return self._values

    def setuseCachedProcess(self, useCachedProcess):
        self._useCachedProcess = useCachedProcess
    def getUseCachedProcessue(self):
        return self._useCachedProcess

    # evaluation and caching
    def _processRaw(self, value, verbose=False):
        inputValues = self._values[0]
        outputValues = self._values[1]

        # NaNs
        if np.isnan(value):
            result = value
        # Infs
        elif np.isinf(value):
            result = value

        # Normal numbers

        # Below the input range
        elif value <= inputValues[0]:
            result = outputValues[0]

        # Above the input range
        elif value >= inputValues[-1]:
            result = outputValues[-1]

        # Within the input range
        else:
            for i in range(len(inputValues)):
                if value <= inputValues[i+1]:
                    inputLow = inputValues[i]
                    inputHigh = inputValues[i+1]
                    interp = (value - inputLow)/(inputHigh - inputLow)
                    outputLow = outputValues[i]
                    outputHigh = outputValues[i+1]
                    result = interp*(outputHigh - outputLow) + outputLow
                    break
        return result
    # process

    # _createCachedEval
    def _createCachedProcess(self):
        channels = 1
        resolution = 65536
        cacheValues = [0.0]*resolution

        for i in range(resolution):
            # Figure out which half value corresponds to the specific 16 bit integer value
            sample = uint16ToHalf(i)

            # Apply the function to the sample value
            # Should take the channel as input, or process an RGB triple
            fvalue = self._processRaw(sample)

            # Store the values
            for c in range(channels):
                cacheIndex = i*channels + c
                cacheValues[cacheIndex] = fvalue
                #print( "%d, %d, %d: %f -> %f" % (i, c, lutValueIndex, sample, fvalue))

        dimensions = [len(cacheValues), channels]
        self._processCached = Array(dimensions, cacheValues)
    # _createCachedEval

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.set('dim', str(self._dimension))
        # XXX
        # Make this pretty at some point
        element.text = " ".join(list(map(lambda a, b: "%s@%s" % (float(a),int(b)), self._values[0], self._values[1])))

        return element
    # write

    def read(self, element):
        # Store attributes
        for key, value in six.iteritems(element.attrib):
            if key == 'dim':
                self._dimension = int(value)

        self._values = []
        self._values.append( list(map(lambda p: float(p.split('@')[0]), element.text.split())) )
        self._values.append( list(map(lambda p: float(p.split('@')[1]), element.text.split())) )
    # read

    # Process values
    def process(self, value, verbose=False):
        # Pull results from cache
        if self._useCachedProcess:
            if self._processCached == None:
                self._createCachedProcess()
            result = self._processCached.lookup1DHalfDomainInterpolated(value, 0)
        # Evaluate with base IndexMap values 
        else:
            result = self._processRaw(value, verbose)
        return result
    # process

    def printInfo(self):
        print( "%20s" % "IndexMap" )
        length = len(self._values[0])

        print( "%20s : %s" % ("Length", length ) )
        #print( "\t\tvalues     : %s" % self._values )
        print( "%20s" % "Values" )

        if length < 15:
            print( "\t\tmap : %s" % " ".join(map(lambda a, b: "%s,%s" % (a,b), self._values[0], self._values[1])) )
        else:
            pairs = list(map(lambda a, b: "%6.9f, %6.9f" % (a,b), self._values[0], self._values[1]))
            for n in (range(3)):
                print( " "*30 + pairs[n] )

            print( " "*30 + "    ...    " )

            for n in (range(length-3,length)):
                print( " "*30 + pairs[n] )

    # printInfo
# IndexMap

