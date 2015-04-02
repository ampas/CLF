import math

import xml.etree.ElementTree as etree

class IndexMap:
    "A Common LUT Format IndexMap element"

    def __init__(self, dimension=[], values=[], elementType='IndexMap'):
        "%s - Initialize the standard class variables" % elementType
        self._dimension = dimension
        self._values = values
        self._elementType = elementType
    # __init__

    def setDimension(self, dimension):
        self._dimension = dimension
    def getDimension(self):
        return self._dimension

    def setValues(self, values):
        self._values = values
    def getValues(self):
        return self._values

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.set('dim', str(self._dimension))
        # XXX
        # Make this pretty at some point
        element.text = " ".join(map(lambda a, b: "%s@%s" % (float(a),int(b)), self._values[0], self._values[1]))

        return element
    # write

    def read(self, element):
        # Store attributes
        for key, value in element.attrib.iteritems():
            if key == 'dim':
                self._dimension = int(value)

        self._values = []
        self._values.append( map(lambda p: float(p.split('@')[0]), element.text.split()) )
        self._values.append( map(lambda p: float(p.split('@')[1]), element.text.split()) )
    # read

    # Process values
    def process(self, value, verbose=False):
        inputValues = self._values[0]
        outputValues = self._values[1]

        if value <= inputValues[0]:
            result = outputValues[0]
        elif value >= inputValues[-1]:
            result = outputValues[-1]
        else:
            for i in range(len(inputValues)):
                if value <= inputValues[i+1]:
                    inputLow = inputValues[i]
                    inputHigh = inputValues[i+1]
                    interp = (value - inputLow)/(inputHigh - inputLow)
                    outputLow = outputValues[i]
                    outputHigh = outputValues[i+1]
                    result = interp*(outputHigh - outputLow) + outputLow
                    break
        return result
    # process

    def printInfo(self):
        print( "\tIndexMap" )
        print( "\t\tmap : %s" % " ".join(map(lambda a, b: "%s,%s" % (a,b), self._values[0], self._values[1])) )
    # printInfo
# IndexMap

