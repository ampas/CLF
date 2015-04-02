import sys
import os

from Comment import Comment

import xml.etree.ElementTree as etree

class Info:
    "A Common LUT Format Info element"

    def __init__(self, appRelease='', copyright=''):
        "%s - Initialize the standard class variables" % 'Info'
        self._children = []
        if appRelease != '':
            self._children.append( Comment(appRelease, 'AppRelease') )
        if copyright != '':
            self._children.append( Comment(copyright, 'Copyright') )
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

            if elementType == 'AppRelease':
                self._children.append( Comment(child.text, 'AppRelease') )
            if elementType == 'Copyright':
                self._children.append( Comment(child.text, 'Copyright') )

            # Autodesk-specific attribute
            if elementType == 'Release':
                self._children.append( Comment(child.text, 'Release') )
    # read

    def printInfo(self):
        print( "%20s" % "Info" )
        for child in self._children:
            child.printInfo()
    # printInfo
# Info


