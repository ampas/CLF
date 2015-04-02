import xml.etree.ElementTree as etree

from Common import *

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
        element = etree.SubElement(tree, "%s:%s" % (nsprefix, self._transformType))
        #element = etree.SubElement(tree, self._transformType)

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
        self._transformType = normalize(element.tag)
        for key, value in element.attrib.iteritems():
            self._attributes[key] = value

        # Read child elements
        for child in element:
            elementType = child.tag

            if elementType == 'LinkTransform':
                self._linkTransformID = child.text
    # read

    def printInfo(self):
        print( "%20s" % self._transformType )

        for key, value in self._attributes.iteritems():
            print( "%20s : %15s, %15s" % ("Attribute", key, value))

        for child in self._children:
            child.printInfo()

        if self._linkTransformID != '':
            print( "%20s : %15s" % ("Link Transform", self._linkTransformID))
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

class RRTODTref(TransformReference):
    "An ACES Clip RRTODTref Transform Reference element"

    def __init__(self, name='', transformID='', status='', linkTransformID=''):
        "%s - Initialize the standard class variables" % 'RRTODTref'
        TransformReference.__init__(self, name, transformID, status, linkTransformID, 'RRTODTref')
    # __init__
# ODTref



