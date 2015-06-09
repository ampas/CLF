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

import xml.etree.ElementTree as etree

from ProcessNode import *

class ASCCDL(ProcessNode):
    "A Common LUT Format ASC_CDL ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style="Fwd", classLabel="ASC_CDL"):
        "%s - Initialize the standard class variables" % classLabel
        ProcessNode.__init__(self, classLabel, inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._values = {}
    # __init__

    def setSlope(self, r, g, b):
        self._values['slope'] = [r, g, b]
    def setOffset(self, r, g, b):
        self._values['offset'] = [r, g, b]
    def setPower(self, r, g, b):
        self._values['power'] = [r, g, b]
    def setSaturation(self, s):
        self._values['saturation'] = s

    # Read / Write
    def write(self, tree):
        node = ProcessNode.write(self, tree)

        SOPNode = etree.SubElement(node, 'SOPNode')
        if 'slope' in self._values:
            Slope = etree.SubElement(SOPNode, 'Slope')
            Slope.text = " ".join(map(str, self._values['slope']))
        if 'offset' in self._values:
            Offset = etree.SubElement(SOPNode, 'Offset')
            Offset.text = " ".join(map(str, self._values['offset']))
        if 'power' in self._values:
            Power = etree.SubElement(SOPNode, 'Power')
            Power.text = " ".join(map(str, self._values['power']))

        SatNode = etree.SubElement(node, 'SatNode')
        if 'saturation' in self._values:
            Saturation = etree.SubElement(SatNode, 'Saturation')
            Saturation.text = str(self._values['saturation'])

        return node
    # write

    def readChild(self, element):
        if element.tag == 'SOPNode':
            for child in element:
                childType = child.tag
                if childType == 'Slope':
                    self._values['slope'] = map(float, child.text.split())
                elif childType == 'Offset':
                    self._values['offset'] = map(float, child.text.split())
                elif childType == 'Power':
                    self._values['power'] = map(float, child.text.split())
        elif element.tag == 'SatNode':
            for child in element:
                childType = child.tag
                if childType == 'Saturation':
                    self._values['saturation'] = float(child.text)
        return None
    # readChild

    def process(self, values, stride=0, verbose=False):
        # Handle processing of single values
        if stride == 0:
            stride = len(value)

        # Pass through if there aren't at least three channels
        if stride < 3:
            return values

        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        style = ''
        if 'style' in self._attributes: style = self._attributes['style']

        # Node parameters
        slope = [1.0, 1.0, 1.0]
        offset = [0.0, 0.0, 0.0]
        power = [1.0, 1.0, 1.0]
        saturation = 1.0

        if 'slope' in self._values: 
            slope = self._values['slope']
        if 'offset' in self._values: 
            offset = self._values['offset']
        if 'power' in self._values: 
            power = self._values['power']
        if 'saturation' in self._values: 
            saturation = self._values['saturation']

        '''
        print( "slope      : %s" % slope )
        print( "offset     : %s" % offset )
        print( "power      : %s" % power )
        print( "saturation : %s" % saturation )
        '''

        # Initialize the output value
        outValues = np.zeros(len(values), dtype=np.float32)

        # Support CLF spec and Autodesk CTF style keywords
        for p in range(len(values)/stride):
            value = value[p*stride:(p+1)*stride]
            outValue = values[p*stride:(p+1)*stride]

            if style == 'Fwd' or style == 'v1.2_Fwd':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(value[i], inBitDepth)
                    outValue[i] = pow( clamp( outValue[i] * slope[i] + offset[i] ), power[i])

                luma = 0.2126 * outValue[0] + 0.7152 * outValue[1] + 0.0722 * outValue[2] 
                for i in range(3):
                    outValue[i] = clamp( luma + saturation * (outValue[i] - luma) )
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'FwdNoClamp' or style == 'noClampFwd':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(value[i], inBitDepth)
                    tmp = outValue[i] * slope[i] + offset[i]
                    if tmp < 0:
                        outValue[i] = tmp
                    else:
                        outValue[i] = pow(tmp, power[i])

                luma = 0.2126 * outValue[0] + 0.7152 * outValue[1] + 0.0722 * outValue[2] 
                for i in range(3):
                    outValue[i] = luma + saturation * (outValue[i] - luma)
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'Rev' or style == 'v1.2_Rev':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(value[i], inBitDepth)
                    outValue[i] = clamp( outValue[i] )

                luma = 0.2126 * outValue[0] + 0.7152 * outValue[1] + 0.0722 * outValue[2] 
                print( luma )

                for i in range(3):
                    outSat = luma + (1.0/saturation) * (outValue[i] - luma)
                    outValue[i] = ( pow( clamp(outSat), 1.0/power[i] ) - offset[i] ) / slope[i]
                    outValue[i] = clamp( outValue[i] )
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            elif style == 'RevNoClamp' or style == 'noClampRev':
                for i in range(3):
                    outValue[i] = bitDepthToNormalized(value[i], inBitDepth)

                luma = 0.2126 * outValue[0] + 0.7152 * outValue[1] + 0.0722 * outValue[2] 

                for i in range(3):
                    outSat = luma + (1.0/saturation) * (outValue[i] - luma)
                    if outSat < 0:
                        outValue[i] = ( clamp(outSat) - offset[i] ) / slope[i]
                    else:
                        outValue[i] = ( pow( clamp(outSat), 1.0/power[i] ) - offset[i] ) / slope[i]
                    outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)

            # Copy the extra channels
            for i in range(min(3, stride),stride):
                outValue[i] = value[i]

            # Copy to the output array
            outValues[p*stride:(p+1)*stride] = outValue

        return outValues
    # process

    def printInfoChild(self):
        #print( "ASC_CDL" )
        for key, value in self._values.iteritems():
            print( "%20s : %15s : %15s" % ("Value", key, value) )
        '''
        if 'slope' in self._values: 
            print( "\tSlope  : %s" % self._values['slope'] )
        if 'offset' in self._values: 
            print( "\tOffset : %s" % self._values['offset'] )
        if 'power' in self._values: 
            print( "\tPower  : %s" % self._values['power'] )
        if 'saturation' in self._values: 
            print( "\tSaturation : %s" % self._values['saturation'] )
        '''
    # printInfoChild
# ASCCDL

class ColorCorrection(ASCCDL):
    "A Common LUT Format ColorCorrection ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style="Fwd", classLabel="ColorCorrection"):
        "%s - Initialize the standard class variables" % 'ColorCorrection'
        ASCCDL.__init__(self, inBitDepth, outBitDepth, id, name, style, "ColorCorrection")

        # Remove the attributes that aren't part of the official CDL structure
        self._attributes.pop("inBitDepth")
        self._attributes.pop("outBitDepth")
        self._attributes.pop("style")
        self._attributes.pop("name")
    # __init__
# ColorCorrection


