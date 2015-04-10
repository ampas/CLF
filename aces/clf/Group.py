from ProcessNode import *

#
# These ProcessNode imports should also be used in the ProcessList
# and Group Nodes
#

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

#
# Duiker Research extensions
#

class Group(ProcessNode):
    "A Common LUT Format Group ProcessNode element"

    # Resolve class based on name
    @staticmethod
    def getClass( cls ):
        glb = globals()
        if cls in glb:
            return glb[cls]
        else:
            return None

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
            if isinstance(process, Reference):
                process.setWriteReferencedNodes(writeSelfContained)
            process.write(node)
        
        return node
    # write

    def readChild(self, child):
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
            print( "Group::read - Ignoring element : %s" % child.tag)

        return None
    # readChild

    def process(self, value, verbose=False):
        result = value
        for processNode in self._processes:
            #print( "processing : %s" % result )
            if processNode.getAttribute('bypass') == None:
                result = processNode.process(result, verbose=verbose)
                if verbose:
                    print( "Group - %s (%s) - result value : %s" % 
                        (processNode.getAttribute('name'), processNode.getNodeType(), 
                            " ".join(map(lambda x: "%3.6f" % x, result)) ) )
            else:
                if verbose:
                    print( "%s (%s) - bypassing" % 
                        (processNode.getAttribute('name'), processNode.getNodeType()))
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


