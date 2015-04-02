from ProcessNode import *
from Array import Array

class Matrix(ProcessNode):
    "A Common LUT Format Matrix ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name=""):
        "%s - Initialize the standard class variables" % 'Matrix'
        ProcessNode.__init__(self, 'Matrix', inBitDepth, outBitDepth, id, name)
    # __init__

    def setMatrix(self, dimensions, values):
        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
        values = Array(dimensions, values, integers)
        self._array = values
        self.addElement( values )
    # setMatrix

    def readChild(self, element):
        child = None
        if element.tag == 'Array':
            child = Array()
            child.read(element)

            integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
            child.setValuesAreIntegers(integers)

            self._array = child
        return child
    # readChild

    def process(self, value, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        dimensions = self._array.getDimensions()
        matrix = self._array.getValues()

        '''
        print( "value       : %s" % value )
        print( "dimensions  : %s" % dimensions )
        print( "matrix      : %s" % matrix )
        '''

        # Actually process a value or two
        #outValue = value
        outValue = [0.0]*len(value)
        for i in range(len(value)):
            #outValue[i] = bitDepthToNormalized(value[i], inBitDepth)

            offset = i*dimensions[1]
            outValue[i] = matrix[0 + offset]*value[0] + matrix[1 + offset]*value[1] + matrix[2 + offset]*value[2]
            #print( "value : %d : %f = %f * %f + %f * %f + %f * %f" % (
            #    i, outValue[i], matrix[0 + offset], value[0], matrix[1 + offset], value[1], matrix[2 + offset], value[2]))
            if dimensions[1] == 4:
                outValue[i] += matrix[offset+3]

            #outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# Matrix


