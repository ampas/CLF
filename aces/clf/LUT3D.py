from ProcessNode import *
from Array import Array
from IndexMap import IndexMap

class LUT3D(ProcessNode):
    "A Common LUT Format LUT 3D ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        interpolation='trilinear'):
        "%s - Initialize the standard class variables" % 'LUT3D'
        ProcessNode.__init__(self, 'LUT3D', inBitDepth, outBitDepth, id, name)
        if interpolation != '':
            self._attributes['interpolation'] = interpolation

        self._array = None
        self._indexMaps = []
    # __init__

    def setIndexMaps(self, valuesR, valuesG = None, valuesB = None):
        indexMapR = IndexMap(len(valuesR[0]), valuesR)
        self._indexMaps.append( indexMapR ) 
        self.addElement( indexMapR )
        
        # Either one or three indexMaps
        if( valuesG != None and valuesB != None ):
            indexMapG = IndexMap(len(valuesG[0]), valuesG)
            self._indexMaps.append( indexMapG ) 
            self.addElement( indexMapG )

            indexMapB = IndexMap(len(valuesB[0]), valuesB)
            self._indexMaps.append( indexMapB ) 
            self.addElement( indexMapB )
    # setIndexMaps

    def setArray(self, dimension, values):
        dimensions = dimension
        dimensions.append(3)

        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))

        self._array = Array(dimensions, values, integers)
        self.addElement( self._array )
    # setArray

    def getLUTDimensions(self):
        return self._array.getDimensions()
    def getLUTValues(self):
        return self._array.getValues()

    def getIndexMapDimensions(self, channel):
        return self._indexMaps[channel].getDimensions()
    def getIndexMapValues(self, channel):
        return self._indexMaps[channel].getValues()

    def readChild(self, element):
        child = None
        if element.tag == 'Array':
            child = Array()
            child.read(element)

            integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
            child.setValuesAreIntegers(integers)

            self._array = child
        elif element.tag == 'IndexMap':
            child = IndexMap()
            child.read(element)
            self._indexMaps.append( child )
        return child
    # readChild

    def process(self, value, verbose=False):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        interpolation = ''
        if 'interpolation' in self._attributes: interpolation = self._attributes['interpolation']

        '''
        print( "interpolation  : %s" % interpolation )
        '''

        # Get LUT dimensions
        dimensions = self.getLUTDimensions()

        # Actually process a value or two
        outValue = value

        # Run each channel through the index map, or base normalization
        for i in range(min(3, len(value))):
            # Run through single Index Map then normalize
            if len(self._indexMaps) > 1:
                outValue[i] = self._indexMaps[i].process(outValue[i])
                outValue[i] /= float(dimensions[i]-1)

            # Run through per-channel Index Map then normalize
            elif len(self._indexMaps) > 0:
                outValue[i] = self._indexMaps[0].process(outValue[i])
                outValue[i] /= float(dimensions[i]-1)

            # Normalize from bit-depth
            else:
                # Convert input bit depth
                outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

        # Run color through LUT
        # trilinear interpolation
        if interpolation == 'trilinear':
            outValue = self._array.lookup3DTrilinear(outValue)

        # tetrahedral interpolation
        elif interpolation == 'tetrahedral':
            outValue = self._array.lookup3DTetrahedral(outValue)

        # Bit Depth conversion for output is ignored for LUTs
        # as LUT values are assumed to target a specific bit depth
        #for i in range(min(3, len(value))):
        #   outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# LUT3D

#
# 3D LUT example
#
def simple3DLUT(id, 
    transformId, 
    resolution, 
    f=lambda x, y, z: [x, y, z], 
    inBitDepth=bitDepths["FLOAT16"],
    outBitDepth=bitDepths["FLOAT16"]):

    l3d = LUT3D(inBitDepth, 
        outBitDepth, 
        id, 
        transformId)

    channels = 3
    lutValues = [0.0]*resolution[0]*resolution[1]*resolution[2]*channels

    # Should make the sampling work with integer values as well.
    # Current approach assumes normalized float values as input
    for x in range(resolution[0]):
        samplex = float(x)/(resolution[0]-1)

        for y in range(resolution[1]):
            sampley = float(y)/(resolution[1]-1)

            for z in range(resolution[2]):
                samplez = float(z)/(resolution[2]-1)

                # Red changes fastest
                lutValueIndex = (((x*resolution[0] +y)*resolution[1] + z))*channels

                fvalue = f(samplex, sampley, samplez)
                lutValues[lutValueIndex:lutValueIndex+channels] = fvalue

                #sample = [samplex, sampley, samplez]
                #print( "%d, %d, %d, %d: %s -> %s" % (x, y, z, lutValueIndex, sample, fvalue))

    l3d.setArray(resolution, lutValues)
    return l3d
