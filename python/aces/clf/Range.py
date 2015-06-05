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

class Range(ProcessNode):
    "A Common LUT Format Range ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style=''):
        "%s - Initialize the standard class variables" % 'Range'
        ProcessNode.__init__(self, 'Range', inBitDepth, outBitDepth, id, name)
        if style != '':
            self._attributes['style'] = style
        self.valueElements = {}
    # __init__

    def setMinInValue(self, minInValue):
        self._valueElements['minInValue'] = minInValue
    def setMaxInValue(self, maxInValue):
        self._valueElements['maxInValue'] = maxInValue
    def setMinOutValue(self, minOutValue):
        self._valueElements['minOutValue'] = minOutValue
    def setMaxOutValue(self, maxOutValue):
        self._valueElements['maxOutValue'] = maxOutValue

    def readChild(self, element):
        if element.tag == 'minInValue':
            self._valueElements['minInValue'] = float(element.text)
        elif element.tag == 'maxInValue':
            self._valueElements['maxInValue'] = float(element.text)
        elif element.tag == 'minOutValue':
            self._valueElements['minOutValue'] = float(element.text)
        elif element.tag == 'maxOutValue':
            self._valueElements['maxOutValue'] = float(element.text)
        return None
    # readChild

    def process(self, value, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        clamp = True
        if 'style' in self._attributes: 
            clamp = (self._attributes['style'] == 'clamp')

        # Node parameters
        minInValue = None
        maxInValue = None
        minOutValue = None
        maxOutValue = None

        if 'minInValue' in self._valueElements: 
            minInValue = self._valueElements['minInValue'] / bitDepthSize(inBitDepth)
        if 'maxInValue' in self._valueElements: 
            maxInValue = self._valueElements['maxInValue'] / bitDepthSize(inBitDepth)
        if 'minOutValue' in self._valueElements: 
            minOutValue = self._valueElements['minOutValue'] / bitDepthSize(outBitDepth)
        if 'maxOutValue' in self._valueElements: 
            maxOutValue = self._valueElements['maxOutValue'] / bitDepthSize(outBitDepth)

        '''
        print( "min in value  : %s" % minInValue )
        print( "max in value  : %s" % maxInValue )
        print( "min out value : %s" % minOutValue )
        print( "max out value : %s" % maxOutValue )
        '''

        # Actually process a value or two
        outValue = value
        for i in range(len(value)):
            # Convert to normalized range
            outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

            # All values specified
            if( minInValue != None and 
                maxInValue != None and
                minOutValue != None and
                maxOutValue != None ):
                scale=(maxOutValue - minOutValue) / (maxInValue - minInValue)
                outValue[i] = outValue[i] * scale + minOutValue - minInValue*scale
                if clamp:
                    outValue[i] = min( maxOutValue, max( minOutValue, outValue[i] ) )

            # Only minimum values
            elif( minInValue != None and 
                minOutValue != None ):
                outValue[i] = outValue[i] + minOutValue - minInValue
                if clamp:
                    outValue[i] = max(minOutValue, outValue[i])

            # Only maximum values
            elif( maxInValue != None and 
                maxOutValue != None ):
                outValue[i] = outValue[i] + maxOutValue - maxInValue
                if clamp:
                    outValue[i] = min( maxOutValue, outValue[i])

            # Convert to bit-depth specific range
            outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# Range


