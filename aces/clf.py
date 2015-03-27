import sys
import os
import math
import struct
import numpy as np

import xml.etree.ElementTree as etree

def xmlPrettyWrite(document, path):
    # Pretty saving to to disk
    documentString = etree.tostring(document.getroot(), encoding='UTF-8')
        
    from xml.dom import minidom
    prettyString = minidom.parseString(documentString).toprettyxml()
   
    fp = open(path, 'wb')
    fp.write(prettyString)
    fp.close()
#xmlPrettyWrite

# Resolve class based on name
def getClass( cls ):
    glb = globals()
    if cls in glb:
        return glb[cls]
    else:
        return None

class ProcessList:
    "A Common LUT Format ProcessList element"

    def __init__(self, clfPath=None):
        "%s - Initialize the standard class variables" % 'ProcessList'
        self._attributes = {}
        self._valueElements = {}
        self._elements = []
        self._processes = []
        
        if clfPath != None:
            self.readFile(clfPath)
    # __init__

    # Read / Write
    def write(self, element=None, writeSelfContained=False):
        if element != None:
            tree = etree.SubElement(element, 'ProcessList')
        else:
            tree = etree.Element('ProcessList')

        # Add attributes        
        for key, value in self._attributes.iteritems():
            tree.set(key, "%s" % value)

        # Add raw value elements
        for key, value in self._valueElements.iteritems():
            valueElement = etree.SubElement(tree, key)
            valueElement.text = str(value)

        # Add elements
        for element in self._elements:
            element.write(tree)

        # Add ProcessNode elements
        for process in self._processes:
            # Choose whether to write Reference node or nodes referred to
            if isinstance(process, Reference):
                process.setWriteReferencedNodes(writeSelfContained)
            process.write(tree)
        
        document = etree.ElementTree(tree)

        return document
    # write

    def writeFile(self, clfPath, writeSelfContained=False):
        document = self.write(writeSelfContained=writeSelfContained)
        # Non pretty-saving to disk
        #document.write(scriptPath)
        
        # Pretty saving to to disk
        xmlPrettyWrite(document, clfPath)

        return document
    # writeFile

    def read(self, element):
        root = element

        # Store attributes
        for key, value in root.attrib.iteritems():
            self.setAttribute(key, value)

        # Read child elements
        for child in root:
            elementType = child.tag.replace('-', '')
            elementType = child.tag.replace('_', '')
            elementClass = getClass(elementType)
            #print( elementType, elementClass )

            if elementClass != None:
                element = elementClass()
                element.read(child)

                processNodeClass = getClass("ProcessNode")
                if issubclass(elementClass, processNodeClass):
                    self.addProcess( element )
                else:
                    self.addElement( element )
            else:
                print( "ProcessList::read - Ignoring element : %s" % child.tag)
    # read

    def readFile(self, clfPath):
        tree = etree.parse(clfPath)
        root = tree.getroot()
        self.read(root)
    # readFile

    # Attributes
    def setAttribute(self, name, value):
        self._attributes[name] = value
    def getAttribute(self, name):
        if name in self._attributes:
            value = self._attributes[name]
        else:
            value = None
        return value

    def setName(self, name):
        self.setAttribute('name', name)
    def getName(self):
        return self.getAttribute('name')

    def setID(self, name):
        self.setAttribute('id', name)
    def getID(self):
        return self.getAttribute('id')

    def setInverseOf(self, name):
        self.setAttribute('inverseOf', name)
    def getInverseOf(self):
        return self.getAttribute('inverseOf')
  
    def setCompCLFversion(self, name):
        self.setAttribute('compCLFversion', name)
    def getCompCLFversion(self):
        return self.getAttribute('compCLFversion')

    # Elements
    def addElement(self, element):
        if element != None:
            self._elements.append(element)
    # XXX
    # To be implemented
    def getElement(self, name):
        return None

    # Value Elements
    def addValueElement(self, key, value):
        self._valueElements[key] = value
    def getValueElement(self, key):
        if key in self._valueElements:
            return self._valueElements[key]
        else:
            return None

    # Processes
    def addProcess(self, process):
        self._processes.append(process)
    def getProcesses(self):
        return self._processes
    def getProcess(self, name):
        for processNode in self._processes:
            if processNode.getAttribute('name') == name:
                return processNode
        return None

    # Color processing
    def process(self, value, verbose=False):
        result = list(value)
        for processNode in self._processes:
            #print( "processing : %s" % result )
            if processNode.getAttribute('bypass') == None:
                result = processNode.process(result)
                if verbose:
                    print( "%s (%s) - result value : %s" % 
                        (processNode.getAttribute('name'), processNode.getNodeType(), 
                            " ".join(map(lambda x: "%3.6f" % x, result)) ) )
            else:
                if verbose:
                    print( "%s (%s) - bypassing" % 
                        (processNode.getAttribute('name'), processNode.getNodeType()))
        return result
    # process

    # Print information
    def printInfo(self):
        print( "ProcessList" )

        # Attributes        
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        # Raw value elements
        for key, value in self._valueElements.iteritems():
            print( "%20s : %15s : %15s" % ("Element", key, value))

        # Elements
        for element in self._elements:
            element.printInfo()

        print( "" )
        
        # Process Nodes
        print( "Process Nodes")
        for processNode in self._processes:
            processNode.printInfo()
            print( "" )

    # printInfo
# ProcessList

class Comment:
    "A Common LUT Format Comment element"

    def __init__(self, comment='', elementType='Comment'):
        "%s - Initialize the standard class variables" % 'Comment'
        self._comment = comment
        self._elementType = elementType
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.text = self._comment
        return element
    # write

    def read(self, element):
        self._comment = element.text
    # read

    def printInfo(self):
        print( "%20s : %15s" % (self._elementType, self._comment))
    # printInfo
# Comment

class Description(Comment):
    "A Common LUT Format Description element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'Description'
        Comment.__init__(self, comment, 'Description')
    # __init__
# Description

class InputDescriptor(Comment):
    "A Common LUT Format InputDescriptor element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'InputDescriptor'
        Comment.__init__(self, comment, 'InputDescriptor')
    # __init__
# InputDescriptor

class OutputDescriptor(Comment):
    "A Common LUT Format OutputDescriptor element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'OutputDescriptor'
        Comment.__init__(self, comment, 'OutputDescriptor')
    # __init__
# OutputDescriptor

class Info:
    "A Common LUT Format Info element"

    def __init__(self, appRelease='', copyright=''):
        "%s - Initialize the standard class variables" % 'Info'
        self._children = []
        if appRelease != '':
            self._children.append( Comment(appRelease, 'AppRelease') )
        if copyright != '':
            self._children.append( Comment(copyright, 'Copyright') )
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, 'Info')
        for child in self._children:
            child.write(element)
        return element
    # write

    def read(self, element):
        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'AppRelease':
                self._children.append( Comment(child.text, 'AppRelease') )
            if elementType == 'Copyright':
                self._children.append( Comment(child.text, 'Copyright') )

            # Autodesk-specific attribute
            if elementType == 'Release':
                self._children.append( Comment(child.text, 'Release') )
    # read

    def printInfo(self):
        print( "%20s" % "Info" )
        for child in self._children:
            child.printInfo()
    # printInfo
# Info

# Utility functions
def clamp(value, minValue=0.0, maxValue=1.0):
    return min( maxValue, max( minValue, value ) )
# clamp

def mix(value1, value2, mixAmount):
    outValue = [0] * len(value1)
    for i in range(len(value1)):
        outValue[i] = (1.0 - mixAmount)*value1[i] + mixAmount*value2[i]
    return outValue
# mix

# References for Bit-depth strings
bitDepths = {
    "UINT8"   : "8i", 
    "UINT10"  : "10i",
    "UINT12"  : "12i",
    "UINT16"  : "16i", 
    "FLOAT16" : "16f", 
    "FLOAT32" : "32f"
}

def bitDepthToNormalized(value, bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = value/(pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = value/(pow(2, 10)-1.0)        
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = value/(pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = value/(pow(2, 16)-1.0)
    else:
        outValue = value
    return outValue
# bitDepthToNormalized

def normalizedToBitDepth(value, bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = clamp(value)*(pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = clamp(value)*(pow(2, 10)-1.0)        
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = clamp(value)*(pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = clamp(value)*(pow(2, 16)-1.0)
    else:
        outValue = value
    return outValue
# normalizedtoBitDepth

def bitDepthSize(bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = (pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = (pow(2, 10)-1.0)        
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = (pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = (pow(2, 16)-1.0)
    else:
        outValue = 1.0
    return outValue
# bitDepthSize

def bitDepthIsInteger(bitDepth):
    return bitDepth in [bitDepths["UINT8"], bitDepths["UINT10"], bitDepths["UINT12"], bitDepths["UINT16"]]

def bitDepthIsFloatingPoint(bitDepth):
    return not bitDepth in [bitDepths["UINT8"], bitDepths["UINT10"], bitDepths["UINT12"], bitDepths["UINT16"]]

# Utilities for bit-wise conversion between half-float and 16 bit-integer representations
def uint16ToHalf(uint16value):
    return np.frombuffer(np.getbuffer(np.uint16(uint16value)), dtype=np.float16)[0]

def halfToUInt16(halfValue):
    return np.frombuffer(np.getbuffer(np.float16(halfValue)), dtype=np.uint16)[0]

def sampleHalfFloatDomain(f, rawHalfs=False, index=None, channels=1):
    if index:
        sample = [uint16ToHalf(index)]*channels
        half = f(sample)
        if rawHalfs:
            for c in range(channels):
                half[c] = halfToUInt16(half[c])
        return half
    else:
        halfs = [0.0]*samples*65536
        for index in range(65536):
            sample = [uint16ToHalf(index)]*channels
            halfs[index*channels:(index+1)*channels] = f(sample)
            if rawHalfs:
                for c in range(channels):
                    halfs[index + c] = halfToUInt16(halfs[index + c])
        return halfs

class ProcessNode:
    "A Common LUT Format ProcessNode element"

    def __init__(self, nodeType, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", bypass=False):
        "%s - Initialize the standard class variables" % nodeType
        self._nodeType = nodeType
        self._elements = []
        self._valueElements = {}

        self._attributes = {}
        self._attributes['inBitDepth'] = inBitDepth
        self._attributes['outBitDepth'] = outBitDepth
        self._attributes['id'] = id
        self._attributes['name'] = name
        if bypass:
            self._attributes['bypass'] = bypass
    # __init__

    # Read / Write
    def write(self, tree):
        node = etree.SubElement(tree, self._nodeType)

        # Add attributes        
        for key, value in self._attributes.iteritems():
            node.set(key, "%s" % value)

        # Add raw value elements
        for key, value in self._valueElements.iteritems():
            valueElement = etree.SubElement(node, key)
            valueElement.text = str(value)

        # Add  elements
        for element in self._elements:
            element.write(node)

        return node
    # write

    # Used when a subclass needs to handle the interpretation of a child elment
    def readChild(self, element):
        print( "ProcessNode::readChild - child element of type %s will be skipped" % element.tag)
        return None

    # Used when a subclass needs to do something after reading has completed
    def readInitialize(self):
        return None

    def read(self, element):
        #print( "%s - ProcessNode::read" % element.tag)
        # Store attributes
        for key, value in element.attrib.iteritems():
            self.setAttribute(key, value)

        # Read child elements
        for child in element:
            elementType = child.tag
            #print( elementType )

            # Read generic elements 
            if elementType == 'Description':
                description = Description()
                description.read(child)
                self.addElement( description )

            # Otherwise, allow the subclasses to read elements
            else:
                #print( "%s - ProcessNode::read child - %s" % (element.tag, child.tag))
                childElement = self.readChild(child)
                if childElement != None:
                    self.addElement( childElement )

        # Initialize data structures after reading all attributes and child elements
        self.readInitialize()
    # read

    def printInfo(self):
        print( "ProcessNode type : %s" % self._nodeType)

        # Attributes        
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        # Print raw value elements
        for key, value in self._valueElements.iteritems():
            print( "%20s : %15s : %15s" % ("Element", key, value))

        # Print elements
        for element in self._elements:
            element.printInfo()
        
        self.printInfoChild()

        print( "" )
    # printInfo

    def printInfoChild(self):
        return
    # printInfoChild

    # Attributes
    def setAttribute(self, name, value):
        self._attributes[name] = value
    def getAttribute(self, name):
        if name in self._attributes:
            value = self._attributes[name]
        else:
            value = None
        return value

    # Elements
    def addElement(self, element):
        self._elements.append(element)
    # XXX
    # To be implemented
    def getElement(self):
        return None

    # Value Elements
    def addValueElement(self, key, value):
        self._valueElements[key] = value
    def getValueElement(self, key):
        if key in self._valueElements:
            return self._valueElements[key]
        else:
            return None

    # Node values
    def getNodeType(self):
        return self._nodeType

    # Color processing
    def process(self, value):
        print( "ProcessNode::process - processing bypassed")
        return value
# ProcessNode

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

        # Input half-float values are treated to 16 bit unsigned integers
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
    def process(self, value):
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

    def process(self, value):
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

    def process(self, value):
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

    def process(self, value):
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

class LUT1D(ProcessNode):
    "A Common LUT Format LUT 1D ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        interpolation='linear', rawHalfs='', halfDomain=''):
        "%s - Initialize the standard class variables" % 'LUT1D'
        ProcessNode.__init__(self, 'LUT1D', inBitDepth, outBitDepth, id, name)
        if interpolation != '':
            self._attributes['interpolation'] = interpolation
        if rawHalfs != '':
            self._attributes['rawHalfs'] = rawHalfs
        if halfDomain != '':
            self._attributes['halfDomain'] = halfDomain

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
        dimensions = [len(values)/dimension, dimension]

        integers = bitDepthIsInteger(self.getAttribute('outBitDepth'))
        rawHalfs = (self.getAttribute('rawHalfs') != None)

        self._array = Array(dimensions, values, rawHalfs=rawHalfs, integers=integers)
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
            rawHalfs = (self.getAttribute('rawHalfs') != None)

            child = Array(rawHalfs=rawHalfs)
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

    def process(self, value):
        # Base attributes
        inBitDepth = self._attributes['inBitDepth']
        outBitDepth = self._attributes['outBitDepth']

        # Node attributes
        interpolation = ''
        if 'interpolation' in self._attributes: interpolation = self._attributes['interpolation']

        rawHalfs = (self.getAttribute('rawHalfs') != None)
        halfDomain = (self.getAttribute('halfDomain') != None)
        
        '''
        print( "interpolation  : %s" % interpolation )
        print( "raw halfs      : %s" % rawHalfs )
        print( "halfs domain   : %s" % halfDomain )
        '''

        # Get LUT dimensions
        dimensions = self.getLUTDimensions()

        # Actually process a value or two
        outValue = value
        for i in range(min(3, len(value))):
            # Run through single Index Map then normalize
            if len(self._indexMaps) > 1:
                outValue[i] = self._indexMaps[i].process(outValue[i])
                outValue[i] /= float(dimensions[0]-1)

            # Run through per-channel Index Map then normalize
            elif len(self._indexMaps) > 0:
                outValue[i] = self._indexMaps[0].process(outValue[i])
                outValue[i] /= float(dimensions[0]-1)

            # Normalize from bit-depth
            else:
                # Convert input bit depth
                outValue[i] = bitDepthToNormalized(outValue[i], inBitDepth)

            # Run through LUT
            if interpolation == 'linear':
                outValue[i] = self._array.lookup1DLinear(outValue[i], i, halfDomain)

            # Bit Depth conversion for output is ignored for LUTs
            # as LUT values are assumed to target a specific bit depth
            #outValue[i] = normalizedToBitDepth(outValue[i], outBitDepth)
        return outValue
    # process
# LUT1D

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

    def process(self, value):
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
# Autodesk extensions
#
class Gamma(ProcessNode):
    "A Common LUT Format Gamma ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='Fwd'):
        "%s - Initialize the standard class variables" % 'Gamma'
        ProcessNode.__init__(self, 'Gamma', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = []
        self._dynamicParams = []
    # __init__

    def setGamma(self, gamma, offset=0.0, channel=None ):
        self._params.append([gamma, offset, channel])

    def setDynamicParam(self, name):
        self._dynamicParams.append(name)

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

        for dparam in self._dynamicParams:
            DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
            DynamicParameterNode.attrib['param'] = dparam

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
        elif element.tag == 'DynamicParameter':
            for key, value in element.attrib.iteritems():
                if key == 'param':
                    self._dynamicParams.append(value)
        return None
    # readChild

    def process(self, value):
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

        for dparam in self._dynamicParams:
            print( "%20s : %15s" % ("Dynamic Parameter", dparam) )
    # printInfoChild
# Gamma

class ExposureContrast(ProcessNode):
    "A Common LUT Format ExposureContrast ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='Fwd'):
        "%s - Initialize the standard class variables" % 'ExposureContrast'
        ProcessNode.__init__(self, 'ExposureContrast', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = [[0.0, 1.0, 1.0]]
        self._dynamicParams = []
    # __init__

    def setExposureContrastPivot(self, exposure, contrast, pivot ):
        self._params[0] = [exposure, contrast, pivot]

    def setDynamicParam(self, name):
        self._dynamicParams.append(name)

    # Read / Write
    def write(self, tree):
        node = ProcessNode.write(self, tree)

        for param in self._params:
            ECParamsNode = etree.SubElement(node, 'ECParams')
            ECParamsNode.attrib['exposure'] = str(param[0])
            ECParamsNode.attrib['contrast'] = str(param[1])
            ECParamsNode.attrib['pivot'] = str(param[2])

        for dparam in self._dynamicParams:
            DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
            DynamicParameterNode.attrib['param'] = dparam

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
        elif element.tag == 'DynamicParameter':
            for key, value in element.attrib.iteritems():
                if key == 'param':
                    self._dynamicParams.append(value)
        return None
    # readChild

    def process(self, value):
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

        for dparam in self._dynamicParams:
            print( "\tDynamic Parameter : %s" % dparam )
    # printInfoChild
# ExposureContrast

class Log(ProcessNode):
    "A Common LUT Format Log ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", 
        style='Fwd'):
        "%s - Initialize the standard class variables" % 'Log'
        ProcessNode.__init__(self, 'Log', inBitDepth, outBitDepth, id, name)
        self._attributes['style'] = style
        self._params = []
        self._dynamicParams = []
    # __init__

    def setLogParams(self, gamma=0.6, refWhite=685, refBlack=95, highlight=1.0, shadow=0.0, channel=None ):
        self._params.append([gamma, refWhite, refBlack, highlight, shadow, channel])

    def setDynamicParam(self, name):
        self._dynamicParams.append(name)

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

        for dparam in self._dynamicParams:
            DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
            DynamicParameterNode.attrib['param'] = dparam

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
        elif element.tag == 'DynamicParameter':
            for key, value in element.attrib.iteritems():
                if key == 'param':
                    self._dynamicParams.append(value)
        return None
    # readChild

    def process(self, value):
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

        for dparam in self._dynamicParams:
            print( "%20s : %15s" % ("Dynamic Parameter", dparam) )
    # printInfoChild
# Log

# Ignores the 'alias' attribute for now
def resolvePath(path, basePath, alias):
    fullPath = None
    if 'path' != '':
        if 'basePath' != '':
            fullPath = os.path.join(basePath, path)
            #print( fullPath )
        else:
            fullPath = path
    return fullPath
# resolvePath

class Reference(ProcessNode):
    "A Common LUT Format Reference ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="",
        path='', basePath='', alias='', writeReferencedNodes=False):
        "%s - Initialize the standard class variables" % 'Reference'
        ProcessNode.__init__(self, 'Reference', inBitDepth, outBitDepth, id, name)
        if alias != '':
            self._attributes['alias'] = alias
        if path != '':
            self._attributes['path'] = path
        if basePath != '':
            self._attributes['basePath'] = basePath

        self._dynamicParams = []
        self._writeReferencedNodes = writeReferencedNodes

        self.setPaths(path, basePath, alias)
    # __init__

    def setPaths(self, path='', basePath='', alias=''):
        self._resolvedPath = resolvePath(path, basePath, alias)
        if self._resolvedPath != None and os.path.exists(self._resolvedPath):
            self._processList = ProcessList(self._resolvedPath)
        else:
            self._processList = None
    # setPaths

    def setWriteReferencedNodes(self, writeReferencedNodes):
        self._writeReferencedNodes = writeReferencedNodes
    def getWriteReferencedNodes(self):
        return self._writeReferencedNodes

    def setDynamicParam(self, name):
        self._dynamicParams.append(name)

    # Read / Write
    def write(self, tree):
        if self._writeReferencedNodes:
            processes = self._processList.getProcesses()
            for process in processes:
                process.write(tree)
            return tree
        else:
            node = ProcessNode.write(self, tree)

            for dparam in self._dynamicParams:
                DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
                DynamicParameterNode.attrib['param'] = dparam

            return node
    # write

    def readChild(self, element):
        if element.tag == 'DynamicParameter':
            for key, value in element.attrib.iteritems():
                if key == 'param':
                    self._dynamicParams.append(value)
        return None
    # readChild

    def readInitialize(self):
        alias = ''
        path = ''
        basePath = ''

        if 'alias' in self._attributes:
            alias = self._attributes['alias']
        if 'path' in self._attributes:
            path = self._attributes['path']
        if 'basePath' in self._attributes:
            basePath = self._attributes['basePath']

        self.setPaths(path, basePath, alias)
        return None
    # readInitialize

    def process(self, value):
        outValue = value
        print( "Reference processing - begin" )
        if self._processList != None:
            outValue = self._processList.process(outValue, verbose=True)
        print( "Reference processing - end\n" )
        return outValue
    # process

    def printInfoChild(self):
        print( "%20s : %15s" % ("Resolved Path", self._resolvedPath) )
        if self._processList != None:
            self._processList.printInfo()

        for dparam in self._dynamicParams:
            print( "%20s : %15s" % ("Dynamic Parameter", dparam) )
    # printInfoChild
# Reference

#
# Tests
#
def createExampleCLF(clfPath):
    # Create
    pl = ProcessList()

    # Populate
    pl.setID('Type.name.version')
    pl.setInverseOf('Type.Inverse.name.version')
    pl.setCompCLFversion(1.2)
    pl.setName('Example transform')
    pl.setAttribute('Extra', 'value')

    # Add optional sub-elements
    ds1 = Description("A description string")
    pl.addElement(ds1)

    ds2 = Description("A second description string")
    pl.addElement(ds2)

    is1 = InputDescriptor("A description of the expected input")
    pl.addElement(is1)

    os2 = OutputDescriptor("A description of the intended input")
    pl.addElement(os2)

    info = Info("Version 0.01", "Copyright AMPAS 2015")
    pl.addElement(info)

    # Add sub-elements that are just key-value pairs
    #pl.addValueElement("Key1", 5.0)
    #pl.addValueElement("Description", "Yet another description")

    # Add a generic process node
    #pn1 = ProcessNode("TestProcessNode", "10i", "16f", "someId", "Transform1")
    #pl.addProcess(pn1)

    # Add a matrix node
    mpn1 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform1")
    mpn1.setMatrix([3, 3, 3], [2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.5])
    pl.addProcess(mpn1)

    # Add another matrix node
    mpn2 = Matrix(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform2")
    mpn2.setMatrix([3, 4, 3], [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0])
    pl.addProcess(mpn2)

    # Add a range node
    rpn1 = Range(bitDepths["FLOAT16"], bitDepths["UINT12"], "someId", "Transform3", style='noClamp')
    rpn1.setMinInValue(0.0)
    #rpn1.setMaxInValue(1.0)
    rpn1.setMinOutValue(0.0)
    #rpn1.setMaxOutValue(890)
    pl.addProcess(rpn1)

    # Add a ASC CDL Node
    cdl1 = ASCCDL(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl1ID", "Transform4", "Fwd")
    cdl1.setSlope(1.0, 1.1, 0.9)
    cdl1.setPower(0.9, 0.8, 0.7)
    cdl1.setOffset(0.01, 0.01, 0.02)
    cdl1.setSaturation(0.95)

    # Add optional sub-elements
    ds2 = Description("A description string for the ASC CDL node")
    cdl1.addElement(ds2)

    # Set bypass attribute
    cdl1.setAttribute("bypass", True)
    pl.addProcess(cdl1)

    # Add a 1D lut node
    l1d1 = LUT1D(bitDepths["FLOAT16"], bitDepths["UINT10"], "someId", "Transform5")
    l1d1.setArray(3, [
        0, 0, 0, 
        1023, 1023, 1023])
    pl.addProcess(l1d1)

    # Add another 1D lut node
    l1d2 = LUT1D(bitDepths["UINT10"], bitDepths["UINT10"], "someId", "Transform6")
    l1d2.setArray(1, [0, 512, 1023])
    l1d2.setIndexMaps([[0, 256, 1023], [0, 1, 2]])
    pl.addProcess(l1d2)

    # Add another 1D lut node
    l3d1 = LUT3D("10i", "10i", "someId", "Transform7")
    #indexMapR = [[0, 128, 1023], [0, 1, 2]]
    indexMapG = [[0, 768], [0, 1]]
    #indexMapB = [[0, 64, 512, 1023], [0, 64, 128, 1023]]
    #l3d1.setIndexMaps(indexMapR, indexMapG, indexMapB)
    l3d1.setIndexMaps(indexMapG)
    l3d1.setArray([2, 2, 2], 
        [0, 0, 0,  
        0, 0, 1023,  
        0, 1023, 0,  
        0, 1023, 1023,
        1023, 0, 0,  
        1023, 0, 1023,  
        1023, 1023, 0,  
        1023, 1023, 1023])
    pl.addProcess(l3d1)

    # Add a range node
    rpn2 = Range(bitDepths["UINT10"], bitDepths["FLOAT16"], "someId", "Transform7", style='clamp')
    pl.addProcess(rpn2)

    #
    # Autodesk-specific extensions
    #

    # Add a Gamma Node
    gamma1 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma1ID", "Transform8", "basicFwd")
    gamma1.setGamma(2.2, 0.1, "R")
    gamma1.setDynamicParam("LOOK_SWITCH")
    pl.addProcess(gamma1)

    # Add a Gamma Node
    gamma2 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma2ID", "Transform9", "basicRev")
    gamma2.setGamma(2.2, 0.1, "B")
    pl.addProcess(gamma2)

    # Add a Gamma Node
    gamma3 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma3ID", "Transform10", "basicFwd")
    gamma3.setGamma(2.2, 0.1)
    pl.addProcess(gamma3)

    # Add a Gamma Node
    gamma4 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma4ID", "Transform11", "moncurveFwd")
    gamma4.setGamma(2.6, 0.05)
    pl.addProcess(gamma4)

    # Add a Gamma Node
    gamma5 = Gamma(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "gamma5ID", "Transform12", "moncurveRev")
    gamma5.setGamma(2.6, 0.05)
    pl.addProcess(gamma5)

    # Add a ExposureContrast Node
    ecp1 = ExposureContrast(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ecp1ID", "Transform13", "linear")
    ecp1.setExposureContrastPivot(1.0, 1.2, 1.0)
    pl.addProcess(ecp1)

    # Add a ExposureContrast Node
    ecp2 = ExposureContrast(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ecp2ID", "Transform14", "linear")
    ecp2.setExposureContrastPivot(-1.0, 0.5, 1.0)
    pl.addProcess(ecp2)

    # Add a Log Node
    log1 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log1ID", "Transform15", "antiLog2")
    pl.addProcess(log1)

    # Add a Log Node
    log2 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log2ID", "Transform16", "log2")
    pl.addProcess(log2)

    # Add a Log Node
    log3 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log3ID", "Transform17", "antiLog10")
    pl.addProcess(log3)

    # Add a Log Node
    log4 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log4ID", "Transform18", "log10")
    pl.addProcess(log4)

    # Add a Log Node
    log5 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log5ID", "Transform19", "logToLin")
    log5.setLogParams(0.45, 444.0, 0.0, 0.18, 0.0)
    pl.addProcess(log5)

    # Add a Log Node
    log6 = Log(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "log6ID", "Transform20", "linToLog")
    log6.setLogParams(0.45, 444.0, 0.0, 0.18, 0.0)
    pl.addProcess(log6)

    # Add a range node
    rpn4 = Range(bitDepths["UINT10"], bitDepths["FLOAT16"], "someId", "Transform0b")
    pl.addProcess(rpn4)

    # Add a 1D lut node that uses the 'rawHalfs' flag
    # The half float values are converted to 16 bit integer values when written to disk. 
    # The values converted back to half-float on read.
    # The 16 bit integer value '0' maps to the half-float value 0.0
    # The 16 bit integer values '11878' maps to the half-float value 0.1
    # The 16 bit integer values '15360' maps to the half-float value 1.0
    # Interpolation between LUT values happens with the half-float values
    l1d3 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1d3Id", "Transform5b", rawHalfs=True)
    l1d3.setArray(1, [0.0, 0.1, 1.0])
    pl.addProcess(l1d3)

    # Add a 1D lut node that uses the 'halfDomain' flag
    # Half-float values are used as the index into the LUT
    l1d4 = LUT1D(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "l1d4Id", "Transform5c", rawHalfs=True, halfDomain=True)
    # Creating the identity LUT
    l1d4.setArray(1, map(uint16ToHalf, range(65536)))
    pl.addProcess(l1d4)

    #
    # Reference example
    #
    #referencePathBase = '/work/client/academy/ocio/configGeneration/examples'
    #referencePath = 'test.xml'

    #ref1 = Reference(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "ref1ID", "Transform21", 
    #    referencePath, referencePathBase)
    #pl.addProcess(ref1)

    # Write
    pl.writeFile(clfPath)

    return pl
# createExampleCLF

def copyExampleCLF(clf1Path, clf2Path):
    # Create
    pl = ProcessList(clf1Path)

    #pl.printInfo()

    pl.writeFile(clf2Path, writeSelfContained=True)

    return pl
# copyExampleCLF

def processExample(processList, value):
    rangePL = ProcessList()

    # Add a range node
    rpn0 = Range(value[3], bitDepths["FLOAT16"], "someId", "Transform0")
    rangePL.addProcess(rpn0)

    processedValue = map(float,value[:3])
    print( "Input Value  : %s" % processedValue)

    # Normalize values
    processedValue = rangePL.process(processedValue, verbose=True)    

    # Run through processList
    processedValue = processList.process(processedValue, verbose=True)

    return processedValue
# processExample

'''
Example usage
python ./clf.py -w test.clf --write2 test2.clf --process "0.5 0 1.0 32f"
'''

def main():
    import optparse

    p = optparse.OptionParser(description='An Common LUT Format implementation',
                                prog='clf',
                                version='clf',
                                usage='%prog [options]')

    p.add_option('--write', '-w', default=None)
    p.add_option('--write2', '', default=None)
    p.add_option('--process', '-p', default=None)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfWritePath = options.write
    clf2WritePath = options.write2
    processValue = options.process.split()

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    #print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    #
    # Run diagnostics
    #
    if clfWritePath != None:
        # Write an example LUT
        processList = createExampleCLF(clfWritePath)

        # Read the LUT back in, then write it out again
        # Verifies that read and write are symmetric
        if clf2WritePath != None:
            processList = copyExampleCLF(clfWritePath, clf2WritePath)

        # Process a value with the copy of the LUT
        # Verifies that ProcessNodes do something reasonable
        if processValue != None:
            processExample(processList, processValue)

# main

if __name__ == '__main__':
    main()


