import xml.etree.ElementTree as etree

from Common import *
from Comment import Comment, ContainerFormatVersion, ModificationTime, UUID
from TransformList import InputTransformList, PreviewTransformList

class Config:
    "An ACES Clip Config element"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, acesRelease='', timeStamp=''):
        "%s - Initialize the standard class variables" % 'Config'
        self._children = []
        if acesRelease != '':
            self._children.append( Comment(acesRelease, 'ACESrelease_Version') )
        if timeStamp != '':
            self._children.append( Comment(timeStamp, 'Timestamp') )
    # __init__

    # Elements
    def addElement(self, element):
        if element != None:
            self._children.append(element)
    # XXX
    # To be implemented
    def getElement(self, name):
        return None

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, "%s:Config" % nsprefix)
        for child in self._children:
            child.write(element)
        return element
    # write

    def read(self, element):
        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'ACESrelease_Version':
                self._children.append( Comment(child.text, 'ACESrelease_Version') )
            elif elementType == 'Timestamp':
                self._children.append( Comment(child.text, 'Timestamp') )
            else:
                # Remove text used in xml names but not class names
                elementType = elementType.replace('-', '')
                elementType = elementType.replace('_', '')
                elementType = elementType.replace('aces:', '')
                elementType = normalize(elementType)

                elementClass = self.getClass(elementType)

                if elementClass != None:
                    #print( "element : %s, %s" % (elementType, elementClass) )
                    element = elementClass()
                    element.read(child)

                    self.addElement( element )
                else:
                    print( "Config::read - Ignoring unsupport element, %s" % child.tag)
    # read

    def printInfo(self):
        print( "%20s" % "Config" )
        for child in self._children:
            child.printInfo()
            print( "" )
    # printInfo
# Config


