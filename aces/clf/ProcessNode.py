import sys
import os

import xml.etree.ElementTree as etree

# General Types
from Comment import Description
from Common import *

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

class ProcessNode:
    "A Common LUT Format ProcessNode element"

    def __init__(self, nodeType, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", bypass=False):
        "%s - Initialize the standard class variables" % nodeType
        self._nodeType = nodeType
        self._elements = []
        self._valueElements = {}
        self._dynamicParams = []

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

        # Add dynamic parameters
        for dparam in self._dynamicParams:
            DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
            DynamicParameterNode.attrib['param'] = dparam

        # Add elements
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
            # Convert text to booleans where appropriate
            if value in ["True", "False"]:
                value = (value == "True")
            self.setAttribute(key, value)

        # Read child elements
        for child in element:
            childType = child.tag
            #print( elementType )

            # Read Description elements 
            if childType == 'Description':
                description = Description()
                description.read(child)
                self.addElement( description )

            # Read DynamicParameter elements
            elif childType == 'DynamicParameter':
                for key, value in child.attrib.iteritems():
                    if key == 'param':
                        self._dynamicParams.append(value)

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

        # Print dynamic parameter elements
        for dparam in self._dynamicParams:
            print( "%20s : %15s" % ("Dynamic Parameter", dparam) )

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

    # Dynamic Parameters
    def setDynamicParam(self, name):
        self._dynamicParams.append(name)
    def getDynamicParam(self, name):
        return (name in self._dynamicParams)

    # Node values
    def getNodeType(self):
        return self._nodeType

    # Color processing
    def process(self, value, verbose=False):
        if verbose:
            print( "ProcessNode::process - processing bypassed")
        return value

    # Setters and getters
    def setInBitDepth(self, name):
        self.setAttribute('inBitDepth', name)
    def getInBitDepth(self):
        return self.getAttribute('inBitDepth')

    def setOutBitDepth(self, name):
        self.setAttribute('outBitDepth', name)
    def getOutBitDepth(self):
        return self.getAttribute('outBitDepth')
# ProcessNode

