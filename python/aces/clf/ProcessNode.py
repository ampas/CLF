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

import sys
import os

import xml.etree.ElementTree as etree

# General Types
from Comment import Description
from Common import *
import Errors

from ProcessList import ProcessListChildMeta

# References for Bit-depth strings
bitDepths = {
    "UINT8"   : "8i",
    "UINT10"  : "10i",
    "UINT12"  : "12i",
    "UINT16"  : "16i",
    "FLOAT16" : "16f",
    "FLOAT32" : "32f"
}

def bitDepthToNormalized(value, bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = value/(pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = value/(pow(2, 10)-1.0)
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = value/(pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = value/(pow(2, 16)-1.0)
    else:
        outValue = value
    return outValue
# bitDepthToNormalized

def normalizedToBitDepth(value, bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = value*(pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = value*(pow(2, 10)-1.0)
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = value*(pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = value*(pow(2, 16)-1.0)
    else:
        outValue = value
    return outValue
# normalizedtoBitDepth

def bitDepthSize(bitDepth):
    # Convert to normalized representation
    if( bitDepth == bitDepths["UINT8"] ):
        outValue = (pow(2, 8)-1.0)
    elif( bitDepth == bitDepths["UINT10"] ):
        outValue = (pow(2, 10)-1.0)
    elif( bitDepth == bitDepths["UINT12"] ):
        outValue = (pow(2, 12)-1.0)
    elif( bitDepth == bitDepths["UINT16"] ):
        outValue = (pow(2, 16)-1.0)
    else:
        outValue = 1.0
    return outValue
# bitDepthSize

def bitDepthIsInteger(bitDepth):
    return bitDepth in [bitDepths["UINT8"], bitDepths["UINT10"], bitDepths["UINT12"], bitDepths["UINT16"]]

def bitDepthIsFloatingPoint(bitDepth):
    return not bitDepth in [bitDepths["UINT8"], bitDepths["UINT10"], bitDepths["UINT12"], bitDepths["UINT16"]]

#
# ProcessNode
#
class ProcessNode():
    "A Common LUT Format ProcessNode element"

    # Ensures that this class and children can be written to disk and read back later
    __metaclass__ = ProcessListChildMeta

    def __init__(self, nodeType, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="", bypass=False):
        "%s - Initialize the standard class variables" % nodeType
        self._nodeType = nodeType
        self._elements = []
        self._valueElements = {}
        self._dynamicParams = []

        self._attributes = {}
        self._attributes['inBitDepth'] = inBitDepth
        self._attributes['outBitDepth'] = outBitDepth
        self._attributes['id'] = id
        self._attributes['name'] = name
        if bypass:
            self._attributes['bypass'] = bypass
    # __init__

    # Read / Write
    def write(self, tree):
        node = etree.SubElement(tree, self._nodeType)

        # Add attributes
        for key, value in self._attributes.iteritems():
            node.set(key, "%s" % value)

        # Add raw value elements
        for key, value in self._valueElements.iteritems():
            valueElement = etree.SubElement(node, key)
            valueElement.text = str(value)

        # Add dynamic parameters
        for dparam in self._dynamicParams:
            DynamicParameterNode = etree.SubElement(node, 'DynamicParameter')
            DynamicParameterNode.attrib['param'] = dparam

        # Add elements
        for element in self._elements:
            element.write(node)

        return node
    # write

    # Used when a subclass needs to handle the interpretation of a child elment
    def readChild(self, element):
        print( "ProcessNode::readChild - child element of type %s will be skipped" % element.tag)
        return None

    # Used when a subclass needs to do something after reading has completed
    def readInitialize(self):
        return None

    def read(self, element, strict=False):
        #print( "%s - ProcessNode::read" % element.tag)
        # Store attributes
        for key, value in element.attrib.iteritems():
            # Convert text to booleans where appropriate
            if value in ["True", "False"]:
                value = (value == "True")
            self.setAttribute(key, value)

        # Read child elements
        for child in element:
            childType = child.tag
            #print( elementType )

            # Read Description elements
            if childType == 'Description':
                description = Description()
                description.read(child)
                self.addElement( description )

            # Read DynamicParameter elements
            elif childType == 'DynamicParameter':
                if getFeatureCompatibility() & featureSets["Autodesk"]:
                    for key, value in child.attrib.iteritems():
                        if key == 'param':
                            self._dynamicParams.append(value)
                else:
                    msg = "Unsupported feature : DynamicParameter element"
                    if strict:
                        raise Errors.UnsupportedExtensionError(msg)
                    else:
                        print( "ProcessNode::read - %s" % msg )

            # Otherwise, allow the subclasses to read elements
            else:
                #print( "%s - ProcessNode::read child - %s" % (element.tag, child.tag))
                childElement = self.readChild(child)
                if childElement != None:
                    self.addElement( childElement )

        # Initialize data structures after reading all attributes and child elements
        self.readInitialize()
    # read

    def printInfo(self):
        print( "ProcessNode type : %s" % self._nodeType)

        # Attributes
        for key, value in self._attributes.iteritems():
            print( "%20s : %15s : %15s" % ("Attribute", key, value))

        # Print raw value elements
        for key, value in self._valueElements.iteritems():
            print( "%20s : %15s : %15s" % ("Element", key, value))

        # Print dynamic parameter elements
        for dparam in self._dynamicParams:
            print( "%20s : %15s" % ("Dynamic Parameter", dparam) )

        # Print elements
        for element in self._elements:
            element.printInfo()

        self.printInfoChild()

        print( "" )
    # printInfo

    def printInfoChild(self):
        return
    # printInfoChild

    # Attributes
    def setAttribute(self, name, value):
        self._attributes[name] = value
    def getAttribute(self, name):
        if name in self._attributes:
            value = self._attributes[name]
        else:
            value = None
        return value

    # Elements
    def addElement(self, element):
        self._elements.append(element)
    # XXX
    # To be implemented
    def getElement(self):
        return None

    # Value Elements
    def addValueElement(self, key, value):
        self._valueElements[key] = value
    def getValueElement(self, key):
        if key in self._valueElements:
            return self._valueElements[key]
        else:
            return None

    # Dynamic Parameters
    def setDynamicParam(self, name):
        self._dynamicParams.append(name)
    def getDynamicParam(self, name):
        return (name in self._dynamicParams)

    # Node values
    def getNodeType(self):
        return self._nodeType

    # Color processing
    def process(self, values, stride=0, verbose=False):
        if verbose:
            print( "ProcessNode::process - no op")
        return value

    # Setters and getters
    def setInBitDepth(self, name):
        self.setAttribute('inBitDepth', name)
    def getInBitDepth(self):
        return self.getAttribute('inBitDepth')

    def setOutBitDepth(self, name):
        self.setAttribute('outBitDepth', name)
    def getOutBitDepth(self):
        return self.getAttribute('outBitDepth')
# ProcessNode

