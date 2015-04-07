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

    def process(self, value, verbose=False):
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

        # Actually process a value or two
        outValue = value
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

        return outValue
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


