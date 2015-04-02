import xml.etree.ElementTree as etree

from Common import *
from Comment import Comment, ContainerFormatVersion, ModificationTime, UUID

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
        element = etree.SubElement(tree, "%s:ClipID" % nsprefix)
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
        print( "%20s" % "ClipID" )
        for child in self._children:
            child.printInfo()
    # printInfo
# ClipID



