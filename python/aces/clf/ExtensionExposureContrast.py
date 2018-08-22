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

import six

from aces.clf.ProcessNode import *

#
# Autodesk extensions
#

class ExposureContrast(ProcessNode):
    "A Common LUT Format ExposureContrast ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='linear'):
        "%s - Initialize the standard class variables" % 'ExposureContrast'
        ProcessNode.__init__(self, 'ExposureContrast', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = [[0.0, 1.0, 1.0]]
    # __init__

    def setExposureContrastPivot(self, exposure, contrast, pivot ):
        self._params[0] = [exposure, contrast, pivot]

    # Read / Write
    def write(self, tree):
        node = ProcessNode.write(self, tree)

        for param in self._params:
            ECParamsNode = etree.SubElement(node, 'ECParams')
            ECParamsNode.attrib['exposure'] = str(param[0])
            ECParamsNode.attrib['contrast'] = str(param[1])
            ECParamsNode.attrib['pivot'] = str(param[2])

        return node
    # write

    def readChild(self, element):
        if element.tag == 'ECParams':
            param = [0.0, 1.0, 1.0]
            for key, value in six.iteritems(element.attrib):
                if key == 'exposure':
                    param[0] = float(value)
                elif key == 'contrast':
                    param[1] = float(value)
                elif key == 'pivot':
                    param[2] = float(value)
            self._params[0] = param
        return None
    # readChild

    def process(self, values, stride=0, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        style = ''
        if 'style' in self._attributes: style = self._attributes['style']

        # Node parameters
        exposure = 0.0
        contrast = 1.0
        pivot = 1.0

        for param in self._params:
            exposure = param[0]
            contrast = param[1]
            pivot = param[2]

        '''
        print( "exposure      : %s" % exposure )
        print( "contrast      : %s" % contrast )
        print( "pivot         : %s" % pivot )
        '''

        # Handle processing of single values
        if stride == 0:
            stride = len(values)

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        for p in range(int(len(values)/stride)):
            value = values[p*stride:(p+1)*stride]
            outValue = values[p*stride:(p+1)*stride]

            if style == 'linear':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = pivot*pow(max(0.0,(pow(2.0,exposure)*outValue[i]/pivot)), contrast)

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'video':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = pow(pivot,1.0/1.83)*pow(max(0.0,(outValue[i]*pow(pow(2.0,exposure)/pivot),1.0/1.83)), contrast)

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'log':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    p = (0.6/2.046*math.log10(pivot/0.9) + 685.0/1023.0)
                    outValue[i] = (outValue[i] + exposure*0.6/2.046*math.log10(2.0) - p)*contrast + p

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(3, stride),stride):
                outValue[i] = values[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process

    def printInfoChild(self):
        #print( "ExposureContrast" )

        param = self._params[0]
        '''
        print( "\tExposure  : %s" % param[0] )
        print( "\tContrast  : %s" % param[1] )
        print( "\tPivot     : %s" % param[2] )
        '''

        values = {"exposure":param[0], "contrast":param[0], "pivot":param[2]}

        for key, value in six.iteritems(values):
            print( "%20s : %15s : %15s" % ("Value", key, value) )
    # printInfoChild
# ExposureContrast


