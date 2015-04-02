import math

import xml.etree.ElementTree as etree

from Common import *

class Array:
    "A Common LUT Format Array element"

    def __init__(self, 
        dimensions=[], 
        values=[], 
        integers=False, 
        rawHalfs=False,
        elementType='Array'):
        "%s - Initialize the standard class variables" % elementType
        self._dimensions = dimensions
        self._values = values
        self._valuesAreIntegers=integers
        self._rawHalfs = rawHalfs
        self._elementType = elementType
    # __init__

    def setDimensions(self, dimensions):
        self._dimensions = dimensions
    def getDimensions(self):
        return self._dimensions

    def setValues(self, values):
        self._values = values
    def getValues(self):
        return self._values

    def setValuesAreIntegers(self, integers):
        self._valuesAreIntegers = integers
    def getValuesAreIntegers(self):
        return self._valuesAreIntegers

    def setRawHalfs(self, rawHalfs):
        self._rawHalfs = rawHalfs
    def getRawHalfs(self):
        return self._rawHalfs

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.set('dim', " ".join(map(str, self._dimensions)))
        
        # Slightly prettier printing
        element.text = "\n"

        # Use the last value for 1D or 3D LUTs
        if len(self._dimensions) in [2, 4]:
            columns = self._dimensions[-1]

        # Use the second dimension for Matrices
        else:
            columns = self._dimensions[1]

        integers = self._valuesAreIntegers or self._rawHalfs

        for n in range(len(self._values)/columns):
            sample = self._values[n*columns:(n+1)*columns]

            if self._rawHalfs:
                sample = map(halfToUInt16, sample)

            if integers:
                sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
            else:
                sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
            element.text += sampleText + "\n"

        # Hack
        # Will correct formatting for CLFs. Not Clip though...
        element.text += "\t\t"

        return element
    # write

    def read(self, element):
        # Store attributes
        for key, value in element.attrib.iteritems():
            if key == 'dim':
                self._dimensions = map(int, value.split())

        if self._rawHalfs:
            cast = lambda x: float(uint16ToHalf(x))
        else:
            cast = float
        self._values = map(cast, element.text.split())
    # read

    def printInfo(self):
        print( "%20s" % "Array" )
        print( "%20s : %s" % ("Dimensions", self._dimensions) )
        #print( "\t\tvalues     : %s" % self._values )
        print( "%20s" % "Values" )

        # Use the last value for 1D or 3D LUTs
        if len(self._dimensions) in [2, 4]:
            columns = self._dimensions[-1]

        # Use the second dimension for Matrices
        else:
            columns = self._dimensions[1]

        rows = len(self._values)/columns
        if rows > 10:
            for n in (range(3)):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )

            print( " "*30 + " "*(columns/2*16) + "    ...    " )

            for n in (range(rows-3,rows)):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )
        else:
            for n in range(rows):
                sample = self._values[n*columns:(n+1)*columns]
                if self._valuesAreIntegers:
                    sampleText = " ".join(map(lambda x: "%15s" % str(int(x)), sample))
                else:
                    sampleText = " ".join(map(lambda x: "%15s" % ("%6.9f" % float(x)), sample))
                print( " "*30 + sampleText )
    # printInfo

    #
    # Lookup values
    #

    # 1D exact
    def lookup1D(self, index, channel):
        values = self._values
        dimensions = self._dimensions

        if dimensions[1] == 3:
            if index < 0:
                result = values[0 + channel]
            elif index >= dimensions[0]:
                result = values[(dimensions[0]-1)*dimensions[1] + channel]
            else:
                result = values[index*dimensions[1] + channel]
        else:
            if index < 0:
                result = values[0]
            elif index >= dimensions[0]:
                result = values[dimensions[0]-1]
            else:
                result = values[index]
        return result
    # lookup1D

    # 1D linear
    def lookup1DLinear(self, position, channel, halfDomain=False):
        values = self._values
        dimensions = self._dimensions

        # Input half-float values are treated as 16 bit unsigned integers
        # Those integers are the index into the LUT
        if halfDomain:
            index = halfToUInt16(position)
            value = self.lookup1D(index, channel)
            result = value

        # Normal lookup and interpolation
        else:
            index = position*(dimensions[0]-1)
            indexLow  = int(math.floor(index))
            indexHigh = int(math.ceil(index))
            interp = index - indexLow

            value1 = self.lookup1D(indexLow, channel)
            value2 = self.lookup1D(indexHigh, channel)

            result = (1-interp)*value1 + interp*value2
        return result
    # lookup1DLinear

    # XXX
    # To be implemented
    def lookup1DCubic(self, position, channel, halfDomain=False):
        return self.lookup1DLinear(position, channel, halfDomain=False)

    def lookup3D(self, index3):
        values = self._values
        dimensions = self._dimensions

        # Corner cases
        index3 = map(lambda a, b: max(0, min(a, b-1)), index3, dimensions)

        index1 = (index3[0]*dimensions[0]*dimensions[1] + index3[1]*dimensions[1] + index3[2])*3 

        result = [values[index1], values[index1+1], values[index1+2]]

        #print( "%d, %d, %d -> %d, %s" % (index3[0], index3[1], index3[2], index1, result))
        return result
    # lookup3D

    def lookup3DTrilinear(self, position):
        dimensions = self._dimensions

        #print( position )
        #print( dimensions )
        #print( len(self._values) )

        enclosingCubeColors = [0.0, 0.0, 0.0] * 8

        # clamp because we only use values between 0 and 1
        position = map(clamp, position)

        # index values interpolation factor for RGB
        indexRf = (position[0] * (dimensions[0]-1))
        interpR, indexR = math.modf(indexRf)
        indexR = int(indexR)

        indexGf = (position[1] * (dimensions[1]-1))
        interpG, indexG = math.modf(indexGf)
        indexG = int(indexG)

        indexBf = (position[2] * (dimensions[2]-1))
        interpB, indexB = math.modf(indexBf)
        indexB = int(indexB)

        #print( "index : %d, %d, %d" % (indexR, indexG, indexB))

        # Sample the 8 points around the current sample position
        enclosingCubeColors[0] = self.lookup3D([indexR    , indexG    , indexB    ])
        enclosingCubeColors[1] = self.lookup3D([indexR    , indexG    , indexB + 1])
        enclosingCubeColors[2] = self.lookup3D([indexR    , indexG + 1, indexB    ])
        enclosingCubeColors[3] = self.lookup3D([indexR    , indexG + 1, indexB + 1])
        enclosingCubeColors[4] = self.lookup3D([indexR + 1, indexG    , indexB    ])
        enclosingCubeColors[5] = self.lookup3D([indexR + 1, indexG    , indexB + 1])
        enclosingCubeColors[6] = self.lookup3D([indexR + 1, indexG + 1, indexB    ])
        enclosingCubeColors[7] = self.lookup3D([indexR + 1, indexG + 1, indexB + 1])

        # Interpolate along the 4 lines in B
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[1], interpB);
        enclosingCubeColors[2] = mix(enclosingCubeColors[2], enclosingCubeColors[3], interpB);
        enclosingCubeColors[4] = mix(enclosingCubeColors[4], enclosingCubeColors[5], interpB);
        enclosingCubeColors[6] = mix(enclosingCubeColors[6], enclosingCubeColors[7], interpB);
    
        # Interpolate along the 2 lines in G
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[2], interpG);
        enclosingCubeColors[4] = mix(enclosingCubeColors[4], enclosingCubeColors[6], interpG);

        # Interpolate along the 1 line in R
        enclosingCubeColors[0] = mix(enclosingCubeColors[0], enclosingCubeColors[4], interpR);

        return enclosingCubeColors[0];
    # lookup3DTrilinear

    # XXX
    # To be implemented
    def lookup3DTetrahedral(self, position):
        return self.lookup3DTrilinear(position)
# Array


