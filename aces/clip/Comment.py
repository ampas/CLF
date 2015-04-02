import xml.etree.ElementTree as etree

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
        print( "%20s : %15s" % (self._elementType, self._comment))
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

    # printInfo
# Comment

class ContainerFormatVersion(Comment):
    "An ACES Clip ContainerFormatVersion element"

    def __init__(self, value=''):
        "%s - Initialize the standard class variables" % 'ContainerFormatVersion'
        Comment.__init__(self, value, 'ContainerFormatVersion')
    # __init__
# ContainerFormatVersion

class ModificationTime(Comment):
    "An ACES Clip ContainerFormatVersion element"

    def __init__(self, value=''):
        "%s - Initialize the standard class variables" % 'ModificationTime'
        Comment.__init__(self, value, 'ModificationTime')
    # __init__
# ModificationTime

class UUID(Comment):
    "An ACES Clip UUID element"

    def __init__(self, type=''):
        "%s - Initialize the standard class variables" % 'UUID'
        Comment.__init__(self, '', 'UUID', {"type":type})
    # __init__
# UUID



