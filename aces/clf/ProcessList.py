import sys
import os

import xml.etree.ElementTree as etree

# General Types
from Comment import Description, InputDescriptor, OutputDescriptor
from Info import Info
from ProcessNode import ProcessNode

# ProcessNodes
from Range import Range
from Matrix import Matrix
from ASCCDL import ASCCDL, ColorCorrection
from LUT1D import LUT1D
from LUT3D import LUT3D

# Autodesk-specific ProcessNodes
from Reference import Reference
from ExposureContrast import ExposureContrast
from Gamma import Gamma
from Log import Log

# Duiker Research-specific ProcessNodes
from Group import Group

class ProcessList:
    "A Common LUT Format ProcessList element"

    @staticmethod
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
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, clfPath=None):
        "%s - Initialize the standard class variables" % 'ProcessList'
        self._attributes = {}
        self._valueElements = {}
        self._elements = []
        self._processes = []
        
        if clfPath != None:
            self.readFile(clfPath)
    # __init__

    # Read / Write
    def write(self, element=None, writeSelfContained=False):
        if element != None:
            tree = etree.SubElement(element, 'ProcessList')
        else:
            tree = etree.Element('ProcessList')

        # Add attributes        
        for key, value in self._attributes.iteritems():
            tree.set(key, "%s" % value)

        # Add raw value elements
        for key, value in self._valueElements.iteritems():
            valueElement = etree.SubElement(tree, key)
            valueElement.text = str(value)

        # Add elements
        for element in self._elements:
            element.write(tree)

        # Add ProcessNode elements
        for process in self._processes:
            # Choose whether to write Reference node or nodes referred to
            if isinstance(process, Reference):
                process.setWriteReferencedNodes(writeSelfContained)
            process.write(tree)
        
        document = etree.ElementTree(tree)

        return document
    # write

    def writeFile(self, clfPath, writeSelfContained=False):
        document = self.write(writeSelfContained=writeSelfContained)
        # Non pretty-saving to disk
        #document.write(scriptPath)
        
        # Pretty saving to to disk
        self.xmlPrettyWrite(document, clfPath)

        return document
    # writeFile

    def read(self, element):
        root = element

        # Store attributes
        for key, value in root.attrib.iteritems():
            self.setAttribute(key, value)

        # Read child elements
        for child in root:
            elementType = child.tag.replace('-', '')
            elementType = child.tag.replace('_', '')
            elementClass = self.getClass(elementType)
            #print( elementType, elementClass )

            if elementClass != None:
                element = elementClass()
                element.read(child)

                processNodeClass = self.getClass("ProcessNode")
                if issubclass(elementClass, processNodeClass):
                    self.addProcess( element )
                else:
                    self.addElement( element )
            else:
                print( "ProcessList::read - Ignoring element : %s" % child.tag)
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

    def setID(self, name):
        self.setAttribute('id', name)
    def getID(self):
        return self.getAttribute('id')

    def setInverseOf(self, name):
        self.setAttribute('inverseOf', name)
    def getInverseOf(self):
        return self.getAttribute('inverseOf')
  
    def setCompCLFversion(self, name):
        self.setAttribute('compCLFversion', name)
    def getCompCLFversion(self):
        return self.getAttribute('compCLFversion')

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

    # Processes
    def addProcess(self, process):
        self._processes.append(process)
    def getProcesses(self):
        return self._processes
    def getProcess(self, name):
        for processNode in self._processes:
            if processNode.getAttribute('name') == name:
                return processNode
        return None

    # Color processing
    def process(self, value, verbose=False):
        result = list(value)
        for processNode in self._processes:
            #print( "processing : %s" % result )
            if processNode.getAttribute('bypass') == None:
                result = processNode.process(result, verbose=verbose)
                if verbose:
                    print( "%s (%s) - result value : %s" % 
                        (processNode.getAttribute('name'), processNode.getNodeType(), 
                            " ".join(map(lambda x: "%3.6f" % x, result)) ) )
            else:
                if verbose:
                    print( "%s (%s) - bypassing" % 
                        (processNode.getAttribute('name'), processNode.getNodeType()))
        return result
    # process

    # Print information
    def printInfo(self):
        print( "ProcessList" )

        # Attributes        
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        # Raw value elements
        for key, value in self._valueElements.iteritems():
            print( "%20s : %15s : %15s" % ("Element", key, value))

        # Elements
        for element in self._elements:
            element.printInfo()

        print( "" )
        
        # Process Nodes
        print( "Process Nodes")
        for processNode in self._processes:
            processNode.printInfo()
            print( "" )

    # printInfo
# ProcessList

