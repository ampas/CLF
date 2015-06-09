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

#
# Autodesk extensions
#

class Gamma(ProcessNode):
    "A Common LUT Format Gamma ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='basicFwd'):
        "%s - Initialize the standard class variables" % 'Gamma'
        ProcessNode.__init__(self, 'Gamma', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = []
    # __init__

    def setGamma(self, gamma, offset=0.0, channel=None ):
        self._params.append([gamma, offset, channel])

    # Read / Write
    def write(self, tree):
        node = ProcessNode.write(self, tree)

        for param in self._params:
            GammaParamNode = etree.SubElement(node, 'GammaParams')
            GammaParamNode.attrib['gamma'] = str(param[0])
            if param[1] != 0.0:
                GammaParamNode.attrib['offset'] = str(param[1])
            if param[2] != None:
                GammaParamNode.attrib['channel'] = param[2]

        return node
    # write

    def readChild(self, element):
        if element.tag == 'GammaParams':
            param = [0.0, 0.0, None]
            for key, value in element.attrib.iteritems():
                if key == 'gamma':
                    param[0] = float(value)
                elif key == 'offset':
                    param[1] = float(value)
                elif key == 'channel':
                    param[2] = value
            self._params.append(param)
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
        gamma = [1.0, 1.0, 1.0]
        offset = [0.0, 0.0, 0.0]

        params = self._params
        channels = {'R':0, 'G':1, 'B':2}
        for param in self._params:
            if param[2] == None:
                gamma = [param[0], param[0], param[0]]
                offset = [param[1], param[1], param[1]]
            else:
                channel = channels[param[2]]
                gamma[channel] = param[0]
                offset[channel] = param[1]

        '''
        print( "gamma      : %s" % gamma )
        print( "offset     : %s" % offset )
        '''

        # Handle processing of single values
        if stride == 0:
            stride = len(values)

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        for p in range(len(values)/stride):
            value = values[p*stride:(p+1)*stride]
            outValue = values[p*stride:(p+1)*stride]

            if style == 'basicFwd':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)
                    outValue[i] = pow(max(0.0, outValue[i]), gamma[i])
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'basicRev':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)
                    outValue[i] = pow(max(0.0, outValue[i]), 1/gamma[i])
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'moncurveFwd':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    pivot = (offset[i]/(gamma[i]-1))
                    if( outValue[i] <= pivot ):
                        outValue[i] = (gamma[i]-1.0)/offset[i]*pow(gamma[i]*offset[i]/((gamma[i]-1.0)*(offset[i]+1.0)), gamma[i])*outValue[i]
                    else:
                        outValue[i] = pow(max(0.0, (outValue[i] + offset[i])/(offset[i] + 1.0)), gamma[i])

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'moncurveRev':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    pivot = pow( gamma[i]*offset[i]/((gamma[i]-1.0)*(offset[i]+1.0)) , gamma[i])
                    if( outValue[i] <= (offset[i]/(gamma[i]-1)) ):
                        outValue[i] = pow((gamma[i]-1.0)/offset[i], gamma[i]-1.0)*pow((1.0 + offset[i])/gamma[i], gamma[i])*outValue[i]
                    else:
                        outValue[i] = pow(max(0.0, outValue[i]), 1.0/gamma[i])*(1.0 + offset[i]) - offset[i]

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(3, stride),stride):
                outValue[i] = value[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process

    def printInfoChild(self):
        #print( "Gamma" )
        gamma = [1.0, 1.0, 1.0]
        offset = [0.0, 0.0, 0.0]

        params = self._params
        channels = {'R':0, 'G':1, 'B':2}
        for param in self._params:
            if param[2] == None:
                gamma = [param[0], param[0], param[0]]
                offset = [param[1], param[1], param[1]]
            else:
                channel = channels[param[2]]
                gamma[channel] = param[0]
                offset[channel] = param[1]

        values = {"gamma":gamma, "offset":offset}

        for key, value in values.iteritems():
            print( "%20s : %15s : %15s" % ("Value", key, value) )
    # printInfoChild
# Gamma


