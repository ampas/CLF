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

from aces.clf.ProcessList import ProcessList
from aces.clf.ProcessNode import *

#
# Autodesk extensions
#

# Ignores the 'alias' attribute for now
def resolvePath(path, basePath, alias):
    fullPath = None
    if 'path' != '':
        if 'basePath' != '':
            fullPath = os.path.join(basePath, path)
            #print( fullPath )
        else:
            fullPath = path
    return fullPath
# resolvePath

class Reference(ProcessNode):
    "A Common LUT Format Reference ProcessNode element"

    def __init__(self, inBitDepth=bitDepths["FLOAT16"], outBitDepth=bitDepths["FLOAT16"], id="", name="",
        path='', basePath='', alias='', writeReferencedNodes=False):
        "%s - Initialize the standard class variables" % 'Reference'
        ProcessNode.__init__(self, 'Reference', inBitDepth, outBitDepth, id, name)
        if alias != '':
            self._attributes['alias'] = alias
        if path != '':
            self._attributes['path'] = path
        if basePath != '':
            self._attributes['basePath'] = basePath

        self._writeReferencedNodes = writeReferencedNodes

        self.setPaths(path, basePath, alias)
    # __init__

    def setPaths(self, path='', basePath='', alias=''):
        self._resolvedPath = resolvePath(path, basePath, alias)
        if self._resolvedPath != None and os.path.exists(self._resolvedPath):
            self._processList = ProcessList.ProcessList(self._resolvedPath)
        else:
            self._processList = None
    # setPaths

    def setWriteReferencedNodes(self, writeReferencedNodes):
        self._writeReferencedNodes = writeReferencedNodes
    def getWriteReferencedNodes(self):
        return self._writeReferencedNodes

    # Read / Write
    def write(self, tree):
        if self._writeReferencedNodes:
            processes = self._processList.getProcesses()
            for process in processes:
                process.write(tree)
            return tree
        else:
            node = ProcessNode.write(self, tree)
            return node
    # write

    def readInitialize(self):
        alias = ''
        path = ''
        basePath = ''

        if 'alias' in self._attributes:
            alias = self._attributes['alias']
        if 'path' in self._attributes:
            path = self._attributes['path']
        if 'basePath' in self._attributes:
            basePath = self._attributes['basePath']

        self.setPaths(path, basePath, alias)
        return None
    # readInitialize

    def process(self, values, stride=0, verbose=False):
        if verbose:
            print( "Reference processing - begin" )
        if self._processList != None:
            outValues = self._processList.process(values, stride, verbose=verbose)
        else:
            outValues = values
        if verbose:
            print( "Reference processing - end\n" )
        return outValues
    # process

    def printInfoChild(self):
        print( "%20s : %15s" % ("Resolved Path", self._resolvedPath) )
        if self._processList != None:
            self._processList.printInfo()
    # printInfoChild
# Reference



