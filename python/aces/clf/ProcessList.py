#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The Academy / ASC Common LUT Format Sample Implementations are provided by the
Academy under the following terms and conditions:

Copyright © 2015 Academy of Motion Picture Arts and Sciences ("A.M.P.A.S.").
Portions contributed by others as indicated. All rights reserved.

A worldwide, royalty-free, non-exclusive right to copy, modify, create
derivatives, and use, in source and binary forms, is hereby granted, subject to
acceptance of this license. Performance of any of the aforementioned acts
indicates acceptance to be bound by the following terms and conditions:

* Copies of source code, in whole or in part, must retain the above copyright
notice, this list of conditions and the Disclaimer of Warranty.

* Use in binary form must retain the above copyright notice, this list of
conditions and the Disclaimer of Warranty in the documentation and/or other
materials provided with the distribution.

* Nothing in this license shall be deemed to grant any rights to trademarks,
copyrights, patents, trade secrets or any other intellectual property of
A.M.P.A.S. or any contributors, except as expressly stated herein.

* Neither the name "A.M.P.A.S." nor the name of any other contributors to this
software may be used to endorse or promote products derivative of or based on
this software without express prior written permission of A.M.P.A.S. or the
contributors, as appropriate.

This license shall be construed pursuant to the laws of the State of California,
and any disputes related thereto shall be subject to the jurisdiction of the
courts therein.

Disclaimer of Warranty: THIS SOFTWARE IS PROVIDED BY A.M.P.A.S. AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
NON-INFRINGEMENT ARE DISCLAIMED. IN NO EVENT SHALL A.M.P.A.S., OR ANY
CONTRIBUTORS OR DISTRIBUTORS, BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, RESITUTIONARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

WITHOUT LIMITING THE GENERALITY OF THE FOREGOING, THE ACADEMY SPECIFICALLY
DISCLAIMS ANY REPRESENTATIONS OR WARRANTIES WHATSOEVER RELATED TO PATENT OR
OTHER INTELLECTUAL PROPERTY RIGHTS IN THE ACES CONTAINER REFERENCE
IMPLEMENTATION, OR APPLICATIONS THEREOF, HELD BY PARTIES OTHER THAN A.M.P.A.S.,
WHETHER DISCLOSED OR UNDISCLOSED.
"""

import os
import gzip
import numpy as np
import sys
import xml.etree.ElementTree as etree

from Common import getFeatureCompatibility, featureSets
import Errors

class ProcessList:
    "A Common LUT Format ProcessList element"

    @staticmethod
    def xmlPrettify(document, path):
        # Pretty saving to to disk
        documentString = etree.tostring(document.getroot(), encoding='UTF-8')
            
        from xml.dom import minidom
        prettyString = minidom.parseString(documentString).toprettyxml()
       
        return prettyString
    #xmlPrettify

    # ProcessNode registry
    serializableClasses = {}

    @staticmethod
    def registerClass(name, cls):
        #print( "ProcessList register : %s, %s" % (name, cls))
        ProcessList.serializableClasses[name] = cls

    # Resolve class based on name
    @staticmethod
    def getClass(cls):
        glb = ProcessList.serializableClasses
        if cls in glb:
            return glb[cls]
        else:
            return None

    def __init__(self, clfPath=None, strict=False):
        "%s - Initialize the standard class variables" % 'ProcessList'
        self._attributes = {}
        self._valueElements = {}
        self._elements = []
        self._processes = []
        
        if clfPath != None:
            self.readFile(clfPath, strict)
    # __init__

    def __iter__(self):
        return iter(self._processes)
    # __iter__

    def __getitem__(self, key): 
        return self._processes[key]
    # __getitem__

    def __len__(self):
        return len(self._processes)
    # __len__

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
            if isinstance(process, self.getClass("Reference")):
                process.setWriteReferencedNodes(writeSelfContained)
            process.write(tree)
        
        document = etree.ElementTree(tree)

        return document
    # write

    def writeFile(self, clfPath, writeSelfContained=False, writeGzip=False):
        document = self.write(writeSelfContained=writeSelfContained)

        # Writing Gzipped XML data
        if writeGzip:
            if getFeatureCompatibility() & featureSets["Duiker Research"]:
                prettyString = self.xmlPrettify(document, clfPath)
                f = gzip.open(clfPath, 'wb')
                f.write(prettyString)
                f.close()
            else:
                msg = "Unsupported feature : write gzipped file"
                #print( "ProcessList::writeFile - %s" % msg )
                raise Errors.UnsupportedExtensionError(msg)

        # Writing XML text
        else:
            # Non pretty-saving to disk
            #document.write(scriptPath)
            
            # Pretty saving to to disk
            prettyString = self.xmlPrettify(document, clfPath)
            fp = open(clfPath, 'wb')
            fp.write(prettyString)
            fp.close()

        return True
    # writeFile

    def getElementType(self, tag):
        # ..find('}') allows us to strip out namespaces
        elementType = tag[tag.find('}')+1:]
        elementType = elementType.replace('-', '')
        elementType = elementType.replace('_', '')
        return elementType
    # getElementType

    def read(self, element, strict=False):
        root = element

        # Store attributes
        for key, value in root.attrib.iteritems():
            self.setAttribute(key, value)

        # Read child elements
        for child in root:
            # Find the Python class associated with this XML element tag
            elementType = self.getElementType(child.tag)
            elementClass = self.getClass(elementType)
            #print( child.tag, elementType, elementClass )

            if elementClass != None:
                # Instantiate the class and read XML data
                element = elementClass()

                # Add ProcessNodes to the ProcessList data structures
                processNodeClass = self.getClass("ProcessNode")
                if issubclass(elementClass, processNodeClass):
                    element.read(child, strict=strict)

                    # Check that a given ProcessNode class is compatible with 
                    # the current feature set
                    if ( (elementType in ["ExposureContrast", "Gamma", "Log", "Reference"] and
                        not (getFeatureCompatibility() & featureSets["Autodesk"])) or
                        (elementType in ["Group"] and
                            not (getFeatureCompatibility() & featureSets["Duiker Research"])) ):
                        msg = "Unsupported feature : ProcessNode type %s" % elementType
                        if strict:
                            raise Errors.UnsupportedExtensionError(msg)
                        else:
                            print( "ProcessList::read - %s" % msg )

                    self.addProcess( element )

                # Add elements to the ProcessList data structures
                else:
                    element.read(child)
                    self.addElement( element )
            else:
                msg = "Ignoring element : %s" % child.tag
                if strict:
                    raise Errors.UnknownProcessNodeError(msg)
                else:
                    print( "ProcessList::read - %s" % msg )
    # read

    def readFile(self, clfPath, strict=False):
        # Support for reading gzipped xml data
        if getFeatureCompatibility() & featureSets["Duiker Research"]:
            # Try to read as gzipped XML file
            try:
                f = gzip.open(clfPath, 'rb')
                tree = etree.parse(f)
                root = tree.getroot()
                self.read(root, strict)
                f.close()

            # Read as normal XML otherwise
            except:
                tree = etree.parse(clfPath)
                root = tree.getroot()
                self.read(root, strict)

        # Read as XML otherwise
        else:
            tree = etree.parse(clfPath)
            root = tree.getroot()
            self.read(root, strict)
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

    # Setters and getters
    def setInBitDepth(self, name):
        if len(self._processes) > 0:
            self._processes[0].setAttribute('inBitDepth', name)
    def getInBitDepth(self):
        if len(self._processes) > 0:
            return self._processes[0].getAttribute('inBitDepth')
        else:
            return None

    def setOutBitDepth(self, name):
        if len(self._processes) > 0:
            self._processes[-1].setAttribute('outBitDepth', name)
    def getOutBitDepth(self):
        if len(self._processes) > 0:
            return self._processes[-1].getAttribute('outBitDepth')
        else:
            return None

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
    def process(self, values, stride=0, verbose=False):
        # Cast all values to float32 for processing
        result = np.array(values, np.float32)

        if verbose:
            print( "Processing %d values. Stride size: %d" % (len(values), stride) )

        # Pass the value through each ProcessNode in the ProcessList
        for i in range(len(self._processes)):
            processNode = self._processes[i]
            #print( "processing : %s" % result )

            # Process the current value using the ProcessNode
            if (processNode.getAttribute('bypass') == None or
                not(getFeatureCompatibility() & featureSets["Autodesk"]) ):
                result = processNode.process(result, stride, verbose=verbose)
                if verbose:
                    print( "%s (%s) - result value : %s, result type : %s" % 
                        (processNode.getAttribute('name'), processNode.getNodeType(), 
                            " ".join(map(lambda x: "%3.6f" % x, result)),
                            type(result) ) )

                    if (processNode.getAttribute('bypass') != None and
                        not(getFeatureCompatibility() & featureSets["Autodesk"])):
                        print( "%s (%s) - bypass ignored based on feature compatibility setting." % 
                            (processNode.getAttribute('name'), processNode.getNodeType()) )

            # Bypass this ProcessNode
            else:
                if verbose:
                    print( "%s (%s) - bypassing" % 
                        (processNode.getAttribute('name'), processNode.getNodeType()))

                # Handle bit-depth mismatches
                if i > 0 and i < (len(self._processes)-1):
                    RangeClass = ProcessList.serializableClasses['Range']
                    inBitDepth = self._processes[i-1].getOutBitDepth()
                    outBitDepth = self._processes[i+1].getInBitDepth()

                    if inBitDepth != outBitDepth:
                        if verbose:
                            print( "%s (%s) - Adding a Range node to adapt bit depth %s to bit depth %s" % (
                                processNode.getAttribute('name'), processNode.getNodeType(), inBitDepth, outBitDepth))

                        RangeAdapter = RangeClass(inBitDepth, outBitDepth, "adapter", "adapter", style='noClamp')
                        result = RangeAdapter.process(result, verbose=verbose)
                        if verbose:
                            print( "%s (%s) - result value : %s, result type : %s" % 
                                (RangeAdapter.getAttribute('name'), RangeAdapter.getNodeType(), 
                                    " ".join(map(lambda x: "%3.6f" % x, result)),
                                    type(result) ) )

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

#
# Metaclass for nodes that will register with ProcessList
#
class ProcessListChildMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        ProcessList.registerClass(name, cls)
        return cls
# ProcessNodeMeta

