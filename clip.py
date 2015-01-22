import sys
import os

import xml.etree.ElementTree as etree

from clf import *

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

class ClipMetadata:
    "An ACES Clip Metadata element"

    def __init__(self, clipPath=None):
        "%s - Initialize the standard class variables" % 'ACESmetadata'
        self._attributes = {}
        self._valueElements = {}
        self._elements = []

        self._prefix = "aces"
        self._nsuri = "http://www.oscars.org/aces/ref/acesmetadata"
        
        if clipPath!= None:
            self.readFile(clipPath)
    # __init__

    # Read / Write
    def write(self):
        #tree = etree.Element("%s:ACESmetadata" % self._prefix)
        tree = etree.Element("ACESmetadata")

        #tree.set("xmlns:%s" % self._prefix, self._nsuri)

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
            print( "attribute : %s, %s" % (key, value))
            self.setAttribute(key, value)

        # Read child elements
        for child in root:
            elementType = child.tag

            # Remove text used in xml names but not class names
            elementType = elementType.replace('-', '')
            elementType = elementType.replace('_', '')
            elementType = elementType.replace('aces:', '')

            elementClass = getClass(elementType)
            print( "element : %s, %s" % (elementType, elementClass) )

            if elementClass != None:
                element = elementClass()
                element.read(child)

                self.addElement( element )
            else:
                print( "ProcessList::read - Treating element %s as a raw value" % child.tag)
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
            print( "\tAttribute : %s, %s" % (key, value))

        # Raw value elements
        for key, value in self._valueElements.iteritems():
            print( "\tElement : %s, %s" % (key, value))

        # Elements
        for element in self._elements:
            element.printInfo()
    # printInfo
# ACESmetadata

class Comment:
    "An ACES Clip Comment element"

    def __init__(self, comment='', elementType='Comment', attributes={}):
        "%s - Initialize the standard class variables" % 'Comment'
        self._elementType = elementType
        self._comment = comment
        self._attributes = attributes
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.text = self._comment
        element.attrib = self._attributes
        return element
    # write

    def read(self, element):
        self._elementType = element.tag
        self._comment = element.text
        self._attributes = element.attrib
    # read

    def printInfo(self):
        print( "\t%s : %s, %s" % (self._elementType, self._comment, self._attributes))
    # printInfo
# Comment

class Info:
    "An ACES Clip Info element"

    def __init__(self, application='', appVersion='', comment=''):
        "%s - Initialize the standard class variables" % 'Info'
        self._children = []
        if appVersion != '':
            attributes = {}
            if appVersion != '':
                attributes['version'] = appVersion
            self._children.append( Comment(application, 'Application', attributes=attributes) )
        if comment != '':
            self._children.append( Comment(comment, 'Comment') )
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

            if elementType == 'Application':
                self._children.append( Comment(child.text, 'Application', child.attrib) )
            if elementType == 'Comment':
                self._children.append( Comment(child.text, 'Comment') )
    # read

    def printInfo(self):
        print( "\tInfo" )
        for child in self._children:
            child.printInfo()
    # printInfo
# Info

class ClipID:
    "An ACES Clip ClipID element"

    def __init__(self, clipName='', sourceMediaID='', clipDate='', note=''):
        "%s - Initialize the standard class variables" % 'ClipID'
        self._children = []
        if clipName != '':
            self._children.append( Comment(clipName, 'ClipName') )
        if clipDate != '':
            self._children.append( Comment(clipDate, 'ClipDate') )
        if sourceMediaID != '':
            self._children.append( Comment(sourceMediaID, 'Source_MediaID') )
        if note != '':
            self._children.append( Comment(note, 'Note') )
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, 'ClipID')
        for child in self._children:
            child.write(element)
        return element
    # write

    def read(self, element):
        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'ClipName':
                self._children.append( Comment(child.text, 'ClipName') )
            if elementType == 'ClipDate':
                self._children.append( Comment(child.text, 'ClipDate') )
            if elementType == 'Source_MediaID':
                self._children.append( Comment(child.text, 'Source_MediaID') )
            if elementType == 'Note':
                self._children.append( Comment(child.text, 'Note') )
    # read

    def printInfo(self):
        print( "\tInfo" )
        for child in self._children:
            child.printInfo()
    # printInfo
# ClipID

class Config:
    "An ACES Clip Config element"

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
        element = etree.SubElement(tree, 'Config')
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

                elementClass = getClass(elementType)

                if elementClass != None:
                    print( "element : %s, %s" % (elementType, elementClass) )
                    element = elementClass()
                    element.read(child)

                    self.addElement( element )
                else:
                    print( "ProcessList::read - Ignoring element %s" % child.tag)
    # read

    def printInfo(self):
        print( "\tConfig" )
        for child in self._children:
            child.printInfo()
    # printInfo
# Config

class TransformList:
    "An ACES Clip Transform List element"

    def __init__(self, linkTransformID='', listType='TransformList'):
        "%s - Initialize the standard class variables" % 'TransformList'
        self._listType = listType
        self._linkTransformID = ''
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
        element = etree.SubElement(tree, self._listType)
        for key, value in self._attributes.iteritems():
            element.attrib[key] = value

        for child in self._children:
            child.write(element)

        if self._linkTransformID != '':
            linkTransform = etree.SubElement(element, 'LinkTransform')
            linkTransform.text = self._linkTransformID

        return element
    # write

    def read(self, element):
        self._listType = element.tag

        for key, value in element.attrib.iteritems():
            self._attributes[key] = value

        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'LinkTransform':
                self._linkTransformID = child.text
            else:
                # Remove text used in xml names but not class names
                elementType = elementType.replace('-', '')
                elementType = elementType.replace('_', '')
                elementType = elementType.replace('aces:', '')

                elementClass = getClass(elementType)

                if elementClass != None:
                    print( "element : %s, %s" % (elementType, elementClass) )
                    element = elementClass()
                    element.read(child)

                    self.addElement( element )
                else:
                    print( "TransformList::read - Ignoring element %s" % child.tag)
    # read

    def printInfo(self):
        print( "\t%s" % self._listType )

        for key, value in self._attributes.iteritems():
            print( "\t\tAttribute : %s, %s" % (key, value))

        for child in self._children:
            child.printInfo()

        if self._linkTransformID != '':
            print( "\t\tLink Transform : %s" % self._linkTransformID )
    # printInfo
# TransformList

class InputTransformList(TransformList):
    "An ACES Clip Input Transform List element"

    def __init__(self, linkTransformID=''):
        "%s - Initialize the standard class variables" % 'InputTransformList'
        TransformList.__init__(self, linkTransformID, 'InputTransformList')
    # __init__
# InputTransformList

class PreviewTransformList(TransformList):
    "An ACES Clip Input Transform List element"

    def __init__(self, linkTransformID=''):
        "%s - Initialize the standard class variables" % 'PreviewTransformList'
        TransformList.__init__(self, linkTransformID, 'PreviewTransformList')
    # __init__
# PreviewTransformList

class TransformReference:
    "An ACES Clip Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID='', transformType='TransformReference'):
        "%s - Initialize the standard class variables" % 'TransformReference'
        self._transformType = transformType
        self._attributes = {}
        self._children = []
        self._linkTransformID = ''

        if name != '':
            self._attributes['name'] = name
        if transformID != '':
            self._attributes['transformID'] = transformID
        if status != '':
            self._attributes['status'] = status
        if linkTransformID != '':
            self._linkTransformID = linkTransformID
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._transformType)
        for key, value in self._attributes.iteritems():
            element.attrib[key] = value

        for child in self._children:
            child.write(element)

        if self._linkTransformID != '':
            linkTransform = etree.SubElement(element, 'LinkTransform')
            linkTransform.text = self._linkTransformID

        return element
    # write

    def read(self, element):
        self._transformType = element.tag
        for key, value in element.attrib.iteritems():
            self._attributes[key] = value

        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'LinkTransform':
                self._linkTransformID = child.text
    # read

    def printInfo(self):
        print( "\t%s" % self._transformType )

        for key, value in self._attributes.iteritems():
            print( "\t\tAttribute : %s, %s" % (key, value))

        for child in self._children:
            child.printInfo()

        if self._linkTransformID != '':
            print( "\t\tLink Transform : %s" % self._linkTransformID )
    # printInfo
# TransformReference

class IDTref(TransformReference):
    "An ACES Clip IDTref Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'IDTref'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'IDTref')
    # __init__
# IDTref

class LMTref(TransformReference):
    "An ACES Clip LMTref Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'LMTref'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'LMTref')
    # __init__
# LMTref

class RRTref(TransformReference):
    "An ACES Clip RRTref Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'RRTref'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'RRTref')
    # __init__
# RRTref

class ODTref(TransformReference):
    "An ACES Clip ODTref Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'ODTref'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'ODTref')
    # __init__
# ODTref

class GradeRef(TransformReference):
    "An ACES Clip GradeRef Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'GradeRef'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'GradeRef')
    # __init__
# GradeRef

class GradeRef:
    "An ACES Clip GradeRef Transform Referenceelement"

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

        if self._convertFromWorkingSpace != '':
            convertFromWorkingSpace = etree.SubElement(element, 'Convert_from_WorkSpace')
            convertFromWorkingSpace.attrib['name'] = self._convertFromWorkingSpace

        for child in self._children:
            child.write(element)

        if self._convertToWorkingSpace != '':
            convertToWorkingSpace = etree.SubElement(element, 'Convert_to_WorkSpace')
            convertToWorkingSpace.attrib['name'] = self._convertToWorkingSpace

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

                elementClass = getClass(elementType)

                if elementClass != None:
                    print( "element : %s, %s" % (elementType, elementClass) )
                    element = elementClass()
                    element.read(child)

                    self.addElement( element )
                else:
                    print( "GradeRef::read - Ignoring element %s" % child.tag)
    # read

    def printInfo(self):
        print( "\tGradeRef" )

        for key, value in self._attributes.iteritems():
            print( "\t\tAttribute : %s, %s" % (key, value))

        if self._convertToWorkingSpace != '':
            print( "\t\tConvert From Working Space : %s" % self._convertToWorkingSpace )

        for child in self._children:
            child.printInfo()

        if self._convertFromWorkingSpace != '':
            print( "\t\tConvert From Working Space : %s" % self._convertFromWorkingSpace )
    # printInfo
# GradeRef


class TransformLibrary:
    "An ACES Clip TransformLibrary element"

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
        element = etree.SubElement(tree, 'TransformLibrary')
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

            elementClass = getClass(elementType)

            if elementClass != None:
                print( "element : %s, %s" % (elementType, elementClass) )
                element = elementClass()
                element.read(child)

                self.addElement(element)
            else:
                print( "TransformLibrary::read - Ignoring element %s" % child.tag)
    # read

    def printInfo(self):
        print( "\tTransformLibrary" )
        for child in self._children:
            child.printInfo()
    # printInfo
# TransformLibrary

#
# Tests
#
def createExampleClip(clipPath):
    # Create
    clip = ClipMetadata()

    # Populate
    clip.setName('Example Clip Metadata')

    # Add ID data
    clip.addValueElement("ContainerFormatVersion", str(1.0))
    clip.addValueElement("UUID", "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
    clip.addValueElement("ModificationTime", "2014-11-24T10:20:13-8:00")

    # Add Info element
    clip.addElement(Info("testModule", "2015.0.01", "This is a comment"))

    # Add ClipID element
    clip.addElement(ClipID("A0001B0003FX", "A0001", "2014-11-20T12:24:13-8:00", "This is a note"))

    # Add Config element and sub-elements
    config = Config("1.0", "2014-11-29T23:55:13-8:00")

    itl = InputTransformList('inputTransformID')
    itl.addElement(IDTref("TransformName1", "id1", "applied", "IDT.something.v1.0"))

    gr = GradeRef('', "aces_to_some_space", "some_space_to_aces")
    cdl0 = ColorCorrection(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl0ID", "Transform40", "Fwd")
    cdl0.setSlope(0.05, 1.1, 0.9)
    cdl0.setPower(9.0, 0.8, 0.7)
    cdl0.setOffset(10.1, 0.01, 0.02)
    cdl0.setSaturation(0.05)
    gr.addElement(cdl0)

    itl.addElement(gr)
    config.addElement(itl)

    ptl = PreviewTransformList('inputTransformID')
    ptl.addElement(LMTref("TransformName3", "id3", "bypass", "LMT.something.v1.0"))
    ptl.addElement(RRTref("TransformName4", "id4", "bypass", "RRT.something.v1.0"))
    ptl.addElement(ODTref("TransformName5", "id5", "bypass", "ODT.something.v1.0"))
    config.addElement(ptl)

    clip.addElement(config)

    # Add transform library
    tl = TransformLibrary()

    # Create an example CLF
    pl0 = ProcessList()

    # Add a ASC CDL Node
    cdl1 = ColorCorrection(bitDepths["UINT12"], bitDepths["FLOAT16"], "cdl1ID", "Transform4", "Fwd")
    cdl1.setSlope(0.95, 1.1, 0.9)
    cdl1.setPower(0.9, 0.8, 0.7)
    cdl1.setOffset(0.01, 0.01, 0.02)
    cdl1.setSaturation(0.95)

    pl0.addElement(cdl1)
    tl.addElement(pl0)

    # Create an example CLF
    pl1 = ProcessList()

    # Add a range node to CLF
    rpn0 = Range(bitDepths["FLOAT16"], bitDepths["FLOAT16"], "someId", "Transform0")
    pl1.addProcess(rpn0)

    # Add CLF to transform library
    tl.addElement(pl1)

    # Create an example CLF
    pl2 = ProcessList('examples/test.xml')
    tl.addElement(pl2)

    clip.addElement(tl)

    # Write
    clip.writeFile(clipPath)

    return clip
# createExampleClip

def copyExampleClip(clip1Path, clip2Path):
    # Create
    clip = ClipMetadata(clip1Path)

    clip.printInfo()

    clip.writeFile(clip2Path)

    return clip
# copyExampleClip

'''
Example usage
python ./clip.py -w clip.xml --write2 clip2.xml
'''

def main():
    import optparse

    p = optparse.OptionParser(description='A Clip Metadata implementation',
                                prog='clip',
                                version='0.01',
                                usage='%prog [options]')

    p.add_option('--write', '-w', default=None)
    p.add_option('--write2', '', default=None)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clip1WritePath = options.write
    clip2WritePath = options.write2

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
    if clip1WritePath != None:
        # Write an example LUT
        clip = createExampleClip(clip1WritePath)

        # Read the LUT back in, then write it out again
        # Verifies that read and write are symmetric
        if clip2WritePath != None:
            clip = copyExampleClip(clip1WritePath, clip2WritePath)
# main

if __name__ == '__main__':
    main()


