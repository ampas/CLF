from ProcessNode import *

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
            for key, value in element.attrib.iteritems():
                if key == 'exposure':
                    param[0] = float(value)
                elif key == 'contrast':
                    param[1] = float(value)
                elif key == 'pivot':
                    param[2] = float(value)
            self._params[0] = param
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

        # Actually process a value or two
        outValue = value
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

        return outValue
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

        for key, value in values.iteritems():
            print( "%20s : %15s : %15s" % ("Value", key, value) )
    # printInfoChild
# ExposureContrast


