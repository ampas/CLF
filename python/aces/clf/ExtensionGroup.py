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

from ProcessNode import *
from ProcessList import ProcessList

class Group(ProcessNode):
    "A Common LUT Format Group ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name=""):
        "%s - Initialize the standard class variables" % 'Group'
        ProcessNode.__init__(self, 'Group', inBitDepth, outBitDepth, id, name)
        self._processes = []

        # Remove in and out bit depth attributes
        # XXX Ignoring for now. Should be revisited when discussed by the project committee
        #del self._attributes['inBitDepth']
        #del self._attributes['outBitDepth']
    # __init__

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

    # Read / Write
    def write(self, tree, writeSelfContained=False):
        node = ProcessNode.write(self, tree)

        # Add ProcessNode elements
        for process in self._processes:
            # Choose whether to write Reference node or nodes referred to
            if isinstance(process, ProcessList.getClass("Reference")):
                process.setWriteReferencedNodes(writeSelfContained)
            process.write(node)

        return node
    # write

    def readChild(self, child):
        elementType = child.tag.replace('-', '')
        elementType = child.tag.replace('_', '')
        elementClass = ProcessList.getClass(elementType)
        #print( elementType, elementClass )

        if elementClass != None:
            element = elementClass()
            element.read(child)

            processNodeClass = ProcessList.getClass("ProcessNode")
            if issubclass(elementClass, processNodeClass):
                self.addProcess( element )
            else:
                self.addElement( element )
        else:
            print( "Group::read - Ignoring element : %s" % child.tag)

        return None
    # readChild

    def process(self, values, stride=0, verbose=False):
        result = values

        # Pass the value through each ProcessNode in the ProcessList
        for i in range(len(self._processes)):
            processNode = self._processes[i]
            #print( "processing : %s" % result )

            if processNode.getAttribute('bypass') == None:
                result = processNode.process(result, stride, verbose=verbose)
                if verbose:
                    print( "Group - %s (%s) - result value : %s" %
                        (processNode.getAttribute('name'), processNode.getNodeType(),
                            " ".join(map(lambda x: "%3.6f" % x, result)) ) )
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
                        result = RangeAdapter.process(result, stride, verbose=verbose)
                        if verbose:
                            print( "%s (%s) - result value : %s, result type : %s" %
                                (RangeAdapter.getAttribute('name'), RangeAdapter.getNodeType(),
                                    " ".join(map(lambda x: "%3.6f" % x, result)),
                                    type(result) ) )

        return result
    # process

    def printInfoChild(self):
        # Process Nodes
        print( "Process Nodes")
        for processNode in self._processes:
            processNode.printInfo()
            print( "" )
    # printInfoChild
# Group


