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

    def process(self, value, verbose=False):
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

        # Actually process a value or two
        outValue = value
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

        return outValue
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


