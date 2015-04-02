import xml.etree.ElementTree as etree

from Common import *
from aces.clf import *

class TransformLibrary:
    "An ACES Clip TransformLibrary element"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self):
        "%s - Initialize the standard class variables" % 'TransformLibrary'
        self._children = []
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
        element = etree.SubElement(tree, "%s:%s" % (nsprefix, 'TransformLibrary'))
        #element = etree.SubElement(tree,'TransformLibrary')
        for child in self._children:
            child.write(element)
        return element
    # write

    def read(self, element):
        # Read child elements
        for child in element:
            elementType = child.tag

            # Remove text used in xml names but not class names
            elementType = elementType.replace('-', '')
            elementType = elementType.replace('_', '')
            elementType = elementType.replace('aces:', '')

            elementClass = self.getClass(elementType)

            if elementClass != None:
                #print( "element : %s, %s" % (elementType, elementClass) )
                element = elementClass()
                element.read(child)

                self.addElement(element)
            else:
                print( "TransformLibrary::read - Ignoring unsupported element %s" % child.tag)
    # read

    def printInfo(self):
        print( "%20s" % "TransformLibrary" )
        for child in self._children:
            child.printInfo()
    # printInfo
# TransformLibrary



