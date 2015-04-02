import sys
import os

import xml.etree.ElementTree as etree

class Comment:
    "A Common LUT Format Comment element"

    def __init__(self, comment='', elementType='Comment'):
        "%s - Initialize the standard class variables" % 'Comment'
        self._comment = comment
        self._elementType = elementType
    # __init__

    # Read / Write
    def write(self, tree):
        element = etree.SubElement(tree, self._elementType)
        element.text = self._comment
        return element
    # write

    def read(self, element):
        self._comment = element.text
    # read

    def printInfo(self):
        print( "%20s : %15s" % (self._elementType, self._comment))
    # printInfo
# Comment

class Description(Comment):
    "A Common LUT Format Description element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'Description'
        Comment.__init__(self, comment, 'Description')
    # __init__
# Description

class InputDescriptor(Comment):
    "A Common LUT Format InputDescriptor element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'InputDescriptor'
        Comment.__init__(self, comment, 'InputDescriptor')
    # __init__
# InputDescriptor

class OutputDescriptor(Comment):
    "A Common LUT Format OutputDescriptor element"

    def __init__(self, comment=''):
        "%s - Initialize the standard class variables" % 'OutputDescriptor'
        Comment.__init__(self, comment, 'OutputDescriptor')
    # __init__
# OutputDescriptor


