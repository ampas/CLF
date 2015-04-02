import sys
import os

import xml.etree.ElementTree as etree

# Make sure we can import aces.clip
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from aces.clf import *

from Common import *
from Comment import Comment, ContainerFormatVersion, ModificationTime, UUID
from Info import Info
from ClipID import ClipID
from Config import Config
from TransformLibrary import TransformLibrary

def xmlPrettyWrite(document, path):
    # Pretty saving to to disk
    documentString = etree.tostring(document.getroot(), encoding='UTF-8')

    try:
        from xml.dom import minidom
        prettyString = minidom.parseString(documentString).toprettyxml()
    except:
        print( "Pretty printing failed - writing non-pretty string")
        prettyString = documentString
   
    fp = open(path, 'wb')
    fp.write(prettyString)
    fp.close()
#xmlPrettyWrite

class ClipMetadata:
    "An ACES Clip Metadata element"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, clipPath=None):
        "%s - Initialize the standard class variables" % 'ACESmetadata'
        self._attributes = {}
        self._valueElements = {}
        self._elements = []

        
        if clipPath!= None:
            self.readFile(clipPath)
    # __init__

    # Read / Write
    def write(self):
        tree = etree.Element("%s:ACESmetadata" % nsprefix)
        #tree = etree.Element("ACESmetadata")

        tree.set("xmlns:%s" % nsprefix, nsuri)

        # Add attributes        
        for key, value in self._attributes.iteritems():
            tree.set(key, "%s" % value)

        # Add elements
        for key, value in self._valueElements.iteritems():
            valueElement = etree.SubElement(tree, key)
            valueElement.text = str(value)

        # Add elements
        for element in self._elements:
            element.write(tree)
        
        document = etree.ElementTree(tree)

        return document
    # write

    def writeFile(self, clfPath):
        document = self.write()
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
            #print( "attribute : %s, %s" % (key, value))
            self.setAttribute(key, value)

        # Read child elements
        for child in root:
            elementType = child.tag

            # Remove text used in xml names but not class names
            elementType = elementType.replace('-', '')
            elementType = elementType.replace('_', '')
            elementType = elementType.replace('aces:', '')
            elementType = normalize(elementType)

            elementClass = self.getClass(elementType)
            #print( "element : %s, %s" % (elementType, elementClass) )

            if elementClass != None:
                element = elementClass()
                element.read(child)

                self.addElement( element )
            else:
                print( "ClipMetadata::read - Treating unsupported element, %s, as a raw value" % child.tag)
                self.addValueElement(child.tag, child.text)
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

    # Print information
    def printInfo(self):
        print( "ACESmetadata" )

        # Attributes        
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        # Raw value elements
        for key, value in self._valueElements.iteritems():
            print( "%20s : %15s : %15s" % ("Element", key, value))

        print( "" )

        # Elements
        for element in self._elements:
            element.printInfo()
            print( "" )
    # printInfo
# ClipMetadata



