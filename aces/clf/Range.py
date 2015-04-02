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
                minOutValue != None and
                (inBitDepth not in [bitDepths['FLOAT16'], bitDepths['FLOAT32']]) ):
                outValue[i] = max(minOutValue, outValue[i] + minOutValue - minInValue)

            # Only maximum values
            elif( maxInValue != None and 
                maxOutValue != None and
                (inBitDepth not in [bitDepths['FLOAT16'], bitDepths['FLOAT32']]) ):
                outValue[i] = min( maxOutValue, outValue[i] + maxOutValue - maxInValue)

            # Convert to bit-depth specific range
            outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# Range


