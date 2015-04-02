import xml.etree.ElementTree as etree

from Common import *
from Comment import Comment, ContainerFormatVersion, ModificationTime, UUID

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
        element = etree.SubElement(tree, "%s:Info" % nsprefix)
        for child in self._children:
            child.write(element)
        return element
    # write

    def read(self, element):
        # Read child elements
        for child in element:
            elementType = child.tag
            #print( "Info child element type: %s" % elementType )

            if elementType == 'Application':
                self._children.append( Comment(child.text, 'Application', child.attrib) )
            if elementType == 'Comment':
                self._children.append( Comment(child.text, 'Comment') )
    # read

    def printInfo(self):
        print( "%20s" % "Info" )
        for child in self._children:
            child.printInfo()
    # printInfo
# Info


