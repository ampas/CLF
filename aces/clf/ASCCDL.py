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

    def process(self, value, verbose=False):
        # Pass through if there aren't at least three channels
        if len(value) < 3:
            return value

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

        # Support CLF spec and Autodesk CTF style keywords
        outValue = value
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

        return outValue
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


