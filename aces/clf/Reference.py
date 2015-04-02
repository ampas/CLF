import ProcessList
from ProcessNode import *

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

    def process(self, value, verbose=False):
        outValue = value
        if verbose:
            print( "Reference processing - begin" )
        if self._processList != None:
            outValue = self._processList.process(outValue, verbose=verbose)
        if verbose:
            print( "Reference processing - end\n" )
        return outValue
    # process

    def printInfoChild(self):
        print( "%20s : %15s" % ("Resolved Path", self._resolvedPath) )
        if self._processList != None:
            self._processList.printInfo()
    # printInfoChild
# Reference



