import xml.etree.ElementTree as etree

from Common import *
from aces.clf.ASCCDL import ColorCorrection

class GradeRef:
    "An ACES Clip GradeRef Transform Referenceelement"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, status='', convertFromWorkingSpace='', convertToWorkingSpace=''):
        "%s - Initialize the standard class variables" % 'GradeRef'
        self._linkTransformID = ''
        self._children = []
        self._attributes = {}

        if status != '':
            self._attributes['status'] = status
        if convertToWorkingSpace != '':
            self._convertToWorkingSpace = convertToWorkingSpace
        if convertFromWorkingSpace != '':
            self._convertFromWorkingSpace = convertFromWorkingSpace
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
        element = etree.SubElement(tree, "GradeRef")
        for key, value in self._attributes.iteritems():
            element.attrib[key] = value

        if self._convertToWorkingSpace != '':
            convertToWorkingSpace = etree.SubElement(element, 'Convert_to_WorkSpace')
            convertToWorkingSpace.attrib['name'] = self._convertToWorkingSpace

        for child in self._children:
            child.write(element)

        if self._convertFromWorkingSpace != '':
            convertFromWorkingSpace = etree.SubElement(element, 'Convert_from_WorkSpace')
            convertFromWorkingSpace.attrib['name'] = self._convertFromWorkingSpace

        return element
    # write

    def read(self, element):
        for key, value in element.attrib.iteritems():
            self._attributes[key] = value

        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'Convert_to_WorkSpace':
                self._convertToWorkingSpace = child.attrib['name']
            elif elementType == 'Convert_from_WorkSpace':
                self._convertFromWorkingSpace = child.attrib['name']
            else:
                # Remove text used in xml names but not class names
                elementType = elementType.replace('-', '')
                elementType = elementType.replace('_', '')
                elementType = elementType.replace('aces:', '')

                elementClass = self.getClass(elementType)

                if elementClass != None:
                    #print( "element : %s, %s" % (elementType, elementClass) )
                    element = elementClass()
                    element.read(child)

                    self.addElement( element )
                else:
                    print( "GradeRef::read - Ignoring unsupported element %s" % child.tag)
    # read

    def printInfo(self):
        print( "%20s" % "GradeRef" )

        for key, value in self._attributes.iteritems():
            print( "%20s : %s, %s" % ("Attribute", key, value))

        if self._convertToWorkingSpace != '':
            print( "%20s : %s" % ("Convert To Working", self._convertToWorkingSpace) )
            print( "" )

            for child in self._children:
                child.printInfo()
                print( "" )

        if self._convertFromWorkingSpace != '':
            print( "%20s : %s" % ("Convert From Working", self._convertFromWorkingSpace) )
    # printInfo
# GradeRef



