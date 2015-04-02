import xml.etree.ElementTree as etree

from Common import *
from TransformReference import IDTref, LMTref, RRTref, ODTref, RRTODTref
from GradeRef import GradeRef

class TransformList:
    "An ACES Clip Transform List element"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, 
                 linkTransformID='', 
                 listType='TransformList', 
                 linkTransformListName='LinkTransform'):
        "%s - Initialize the standard class variables" % 'TransformList'
        self._listType = listType
        self._linkTransformID = ''
        self._linkTransformListName = linkTransformListName
        self._children = []
        self._attributes = {}

        if linkTransformID != '':
            self._linkTransformID = linkTransformID
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
        element = etree.SubElement(tree, "%s:%s" % (nsprefix, self._listType) )
        #element = etree.SubElement(tree, self._listType )

        for key, value in self._attributes.iteritems():
            element.attrib[key] = value

        for child in self._children:
            child.write(element)

        if self._linkTransformID != '':
            linkTransform = etree.SubElement(element, self._linkTransformListName)
            linkTransform.text = self._linkTransformID

        return element
    # write

    def read(self, element):
        self._listType = normalize(element.tag)

        for key, value in element.attrib.iteritems():
            self._attributes[key] = value

        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == self._linkTransformListName:
                self._linkTransformID = child.text
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
                    print( "TransformList::read - Ignoring unsupported element %s" % child.tag)
    # read

    def printInfo(self):
        print( "%20s" % self._listType )

        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        for child in self._children:
            child.printInfo()
            print( "" )

        if self._linkTransformID != '':
            print( "%20s : %15s" % (self._linkTransformListName, self._linkTransformID) )
    # printInfo
# TransformList

class InputTransformList(TransformList):
    "An ACES Clip Input Transform List element"

    def __init__(self, linkTransformID=''):
        "%s - Initialize the standard class variables" % 'InputTransformList'
        TransformList.__init__(self, linkTransformID, 'InputTransformList', 'LinkInputTransformList')
    # __init__
# InputTransformList

class PreviewTransformList(TransformList):
    "An ACES Clip Input Transform List element"

    def __init__(self, linkTransformID=''):
        "%s - Initialize the standard class variables" % 'PreviewTransformList'
        TransformList.__init__(self, linkTransformID, 'PreviewTransformList', 'LinkPreviewTransformList')
    # __init__
# PreviewTransformList



