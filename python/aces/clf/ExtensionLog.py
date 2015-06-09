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

from ProcessNode import *

#
# Autodesk extensions
#

class Log(ProcessNode):
    "A Common LUT Format Log ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='log10'):
        "%s - Initialize the standard class variables" % 'Log'
        ProcessNode.__init__(self, 'Log', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = []
    # __init__

    def setLogParams(self, gamma=0.6, refWhite=685, refBlack=95, highlight=1.0, shadow=0.0, channel=None ):
        self._params.append([gamma, refWhite, refBlack, highlight, shadow, channel])

    # Read / Write
    def write(self, tree):
        node = ProcessNode.write(self, tree)

        for param in self._params:
            LogParamsNode = etree.SubElement(node, 'LogParams')
            LogParamsNode.attrib['gamma'] = str(param[0])
            LogParamsNode.attrib['refWhite'] = str(param[1])
            LogParamsNode.attrib['refBlack'] = str(param[2])
            LogParamsNode.attrib['highlight'] = str(param[3])
            LogParamsNode.attrib['shadow'] = str(param[4])
            if param[5] != None:
                LogParamsNode.attrib['channel'] = param[5]

        return node
    # write

    def readChild(self, element):
        if element.tag == 'LogParams':
            param = [0.6, 685.0, 95.0, 1.0, 0.0, None]
            for key, value in element.attrib.iteritems():
                if key == 'gamma':
                    param[0] = float(value)
                elif key == 'refWhite':
                    param[1] = float(value)
                elif key == 'refBlack':
                    param[2] = float(value)
                elif key == 'highlight':
                    param[3] = float(value)
                elif key == 'shadow':
                    param[4] = float(value)
                elif key == 'channel':
                    param[5] = value
            self._params.append(param)
        return None
    # readChild

    def process(self, values, stride, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        style = ''
        if 'style' in self._attributes: style = self._attributes['style']

        # Node parameters
        gamma = [0.6, 0.6, 0.6]
        refWhite = [685.0, 685.0, 685.0]
        refBlack = [95.0, 95.0, 95.0]
        highlight = [1.0, 1.0, 1.0]
        shadow = [0.0, 0.0, 0.0]

        params = self._params
        channels = {'R':0, 'G':1, 'B':2}
        for param in self._params:
            if param[5] == None:
                gamma = [param[0], param[0], param[0]]
                refWhite = [param[1], param[1], param[1]]
                refBlack = [param[2], param[2], param[2]]
                highlight = [param[3], param[3], param[3]]
                shadow = [param[4], param[4], param[4]]
            else:
                channel = channels[param[5]]
                gamma[channel] = param[0]
                refWhite[channel] = param[1]
                refBlack[channel] = param[2]
                highlight[channel] = param[3]
                shadow[channel] = param[4]

        '''
        print( "gamma      : %s" % gamma )
        print( "ref white  : %s" % refWhite )
        print( "ref black  : %s" % refBlack )
        print( "highlight  : %s" % highlight )
        print( "shadow     : %s" % shadow )
        '''

        FLOAT_MIN = 1.1754943508222875 * pow(10,-38)

        # Handle processing of single values
        if stride == 0:
            stride = len(values)

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        for p in range(len(values)/stride):
            value = values[p*stride:(p+1)*stride]
            outValue = values[p*stride:(p+1)*stride]

            if style == 'log10':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = math.log10(max(outValue[i], FLOAT_MIN))
                    
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'log2':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = math.log10(max(outValue[i], FLOAT_MIN))/math.log10(2.0)
                    
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'antiLog10':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = pow(10.0, outValue[i])
                    
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'antiLog2':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    outValue[i] = pow(2.0, outValue[i])
                    
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'logToLin':
                for i in range(3):
                    linearRefBlack = pow(10.0, min(-0.00001, (refBlack[i]-refWhite[i])*0.002/gamma[i]))
                    gain = (highlight[i] - shadow[i])/(1.0 - linearRefBlack)

                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    relativeExposure = pow(10.0, (1023.0*outValue[i] - refWhite[i])*0.002/gamma[i])
                    outValue[i] = (relativeExposure - linearRefBlack)*gain + shadow[i]

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'linToLog':
                for i in range(3):
                    linearRefBlack = pow(10.0, min(-0.00001, (refBlack[i]-refWhite[i])*0.002/gamma[i]))
                    gain = (highlight[i] - shadow[i])/(1.0 - linearRefBlack)

                    outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

                    relativeExposure = linearRefBlack + (outValue[i] - shadow[i])/gain
                    outValue[i] = (refWhite[i] + math.log10(max(FLOAT_MIN, relativeExposure))*gamma[i]/0.002)/1023.0

                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(3, stride),stride):
                outValue[i] = value[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process

    def printInfoChild(self):
        #print( "Log" )
        gamma = [0.6, 0.6, 0.6]
        refWhite = [685.0, 685.0, 685.0]
        refBlack = [95.0, 95.0, 95.0]
        highlight = [1.0, 1.0, 1.0]
        shadow = [0.0, 0.0, 0.0]

        params = self._params
        channels = {'R':0, 'G':1, 'B':2}
        for param in self._params:
            if param[5] == None:
                gamma = [param[0], param[0], param[0]]
                refWhite = [param[1], param[1], param[1]]
                refBlack = [param[2], param[2], param[2]]
                highlight = [param[3], param[3], param[3]]
                shadow = [param[4], param[4], param[4]]
            else:
                channel = channels[param[5]]
                gamma[channel] = param[0]
                refWhite[channel] = param[1]
                refBlack[channel] = param[2]
                highlight[channel] = param[3]
                shadow[channel] = param[4]

        '''
        print( "\tGamma      : %s" % gamma )
        print( "\tRef white  : %s" % refWhite )
        print( "\tRef black  : %s" % refBlack )
        print( "\tHighlight  : %s" % highlight )
        print( "\tShadow     : %s" % shadow )
        '''

        values = {"gamma":gamma, "ref white":refWhite, "ref black":refBlack, "highlight":highlight, "shadow":shadow}

        for key, value in values.iteritems():
            print( "%20s : %15s : %15s" % ("Value", key, value) )
    # printInfoChild
# Log


