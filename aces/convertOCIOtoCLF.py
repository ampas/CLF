#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to convert from OCIO config transforms formats to CLF
"""

import array
import os
import sys

import PyOpenColorIO as OCIO

import clf
import convertLUTtoCLF

def convertMatrixToProcessNode(matrix, offset, direction):
    # Get resolution
    if len(matrix) == 16:
        resolution = [4, 4, 3]
    elif len(matrix) == 12:
        resolution = [3, 4, 3]
    elif len(matrix) == 9:
        resolution = [3, 3, 3]
    else:
        print( "Matrix resolution with %d entries unsupported" % len(matrix) )

    if direction == 'forward':
        # Check to see if this is really a 3x3 matrix hidden inside a 4x4
        if( len(matrix) == 16 and 
            ( matrix[ 3] == 0.0 and matrix[ 7] == 0.0 and matrix[11 == 0.0] and
                matrix[12] == 0.0 and matrix[13] == 0.0 and matrix[14 == 0.0] and matrix[15 == 1.0]) ):

            # Add offset into matrix if possible
            if( offset[0] != 0.0 or offset[1] != 0.0 or offset[2] != 0.0 ):
                resolution = [3, 4, 3]
                matrix[3] = offset[0]
                matrix[7] = offset[1]
                matrix[11] = offset[2]
                # CLF ignores the alpha offset

            # Or just copy into a smaller matrix
            else:
                matrix33 = [0.0]*9
                matrix33[0:3] = matrix[0:3]
                matrix33[3:6] = matrix[4:7]
                matrix33[6:9] = matrix[8:11]

                resolution = [3, 3, 3]
                matrix = matrix33

        mpn1 = clf.Matrix(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "matrix1", "matrix1")
        mpn1.setMatrix(resolution, matrix)
    else:
        print( "Matrix inverse not currently supported")
        return None

    return mpn1

def convertLogToProcessNode(base, direction):
    log = None
    if base == 10:
        if direction == 'forward':
            log = clf.Log(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "log", "log", "log10")
        else:
            log = clf.Log(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "log", "log", "antiLog10")
    elif base == 2:
        if direction == 'forward':
            log = clf.Log(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "log", "log", "log2")
        else:
            log = clf.Log(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "log", "log", "antiLog2")
    else:
        print( "Log base %s not supported" % (base))
    
    return log

def convertTransformsToProcessNodes( ocioTransform, 
                                     lutSearchPath=None,
                                     inversesUseIndexMaps=True, 
                                     inversesUseHalfDomain=True ):
    pns = []

    #print( ocioTransform )

    if isinstance(ocioTransform, OCIO.GroupTransform):
        print( "Group Transform" )
        children = ocioTransform.getTransforms()
        for childTransform in children:
            childpns = convertTransformsToProcessNodes(childTransform, 
                lutSearchPath, inversesUseIndexMaps, inversesUseHalfDomain)
            pns.extend( childpns )

    elif isinstance(ocioTransform, OCIO.FileTransform):
        lutPath = ocioTransform.getSrc()
        interpolation = ocioTransform.getInterpolation()
        direction = ocioTransform.getDirection()
        print( "File Transform : %s, %s, %s" % (lutPath, interpolation, direction) )

        if lutSearchPath != None:
            lutPath = os.path.join( lutSearchPath, lutPath )

        lutpns = convertLUTtoCLF.convertLUTToProcessNode(lutPath, direction, interpolation, 
            useIndexMaps=inversesUseIndexMaps, inversesUseHalfDomain=inversesUseHalfDomain)
        #print( "Created %d CLF process nodes" % len(lutpns) )
        pns.extend( lutpns )

    elif isinstance(ocioTransform, OCIO.MatrixTransform):
        matrix = ocioTransform.getMatrix()
        offset = ocioTransform.getOffset()
        direction = ocioTransform.getDirection()
        print( "Matrix Transform : %s, %s, %s" % (matrix, offset, direction) )
        matrixpn = convertMatrixToProcessNode(matrix, offset, direction)
        if matrixpn != None:
            pns.append(matrixpn)

    elif isinstance(ocioTransform, OCIO.LogTransform):
        base = ocioTransform.getBase()
        direction = ocioTransform.getDirection()
        print( "Log Transform : %s, %s" % (base, direction) )
        logpn = convertLogToProcessNode(base, direction)
        if logpn != None:
            pns.append(logpn)

    else:
        if ocioTransform:
            print( "Unsupported OCIO transform type : %s" % ocioTransform )

    return pns

def convertOCIOtoCLF(configPath, 
                     sourceColorSpaceNames, 
                     destColorSpaceNames, 
                     clfPath,
                     inversesUseIndexMaps, 
                     inversesUseHalfDomain):
    # Load the config
    config = OCIO.Config.CreateFromFile(configPath)

    configBasePath = os.path.split( configPath )[0]
    configLUTPath = os.path.join( configBasePath, config.getSearchPath() )

    description  = "CLF converted from OCIO config.\n"
    description += "Config Path : %s\n" % configPath

    #print( configLUTPath )

    # List that process nodes will be appended to
    lutpns = []

    # Generate the source color space to reference color space transforms
    for sourceColorSpaceName in sourceColorSpaceNames:
        # Get the OCIO transforms
        sourceColorSpace = config.getColorSpace(sourceColorSpaceName)
        sourceTransform = sourceColorSpace.getTransform( OCIO.Constants.COLORSPACE_DIR_TO_REFERENCE )

        # Convert to CLF ProcessNodes
        pns = convertTransformsToProcessNodes( sourceTransform, lutSearchPath=configLUTPath, 
            inversesUseIndexMaps=inversesUseIndexMaps, inversesUseHalfDomain=inversesUseHalfDomain )

        # Rename and add a description to each ProcessNode
        specificDescription = "Convert %s to reference" % sourceColorSpaceName

        count = 0
        for pn in pns:
            ds2 = clf.Description(specificDescription)
            pn.addElement(ds2)

            name = "%s to reference - node %d" % (sourceColorSpaceName, count)
            pn.setAttribute("name", name)
            count += 1

        # Append to the overall CLF ProcessNode list
        lutpns.extend( pns )

        # Extend the overall description
        description += "Source color space : %s\n" % sourceColorSpaceName

    # Generate the reference color space to destination color space transforms
    for destColorSpaceName in destColorSpaceNames:
        # Get the OCIO transforms
        destColorSpace = config.getColorSpace(destColorSpaceName)
        destTransform = destColorSpace.getTransform( OCIO.Constants.COLORSPACE_DIR_FROM_REFERENCE )

        # Convert to CLF ProcessNodes
        pns = convertTransformsToProcessNodes( destTransform, lutSearchPath=configLUTPath, 
            inversesUseIndexMaps=inversesUseIndexMaps, inversesUseHalfDomain=inversesUseHalfDomain )

        # Rename and add a description to each ProcessNode
        specificDescription = "Convert reference to %s" % destColorSpaceName

        count = 0
        for pn in pns:
            ds2 = clf.Description(specificDescription)
            pn.addElement(ds2)

            name = "reference to %s - node %d" % (destColorSpaceName, count)
            pn.setAttribute("name", name)
            count += 1

        # Append to the overall CLF ProcessNode list
        lutpns.extend( pns )

        # Extend the overall description
        description += "Destination color space name : %s\n" % destColorSpaceName

    # Create a CLF ProcessList and populate contents
    if lutpns != []:
        print( "Creating ProcessList")
        pl = clf.ProcessList()

        # Populate
        pl.setID('Converted lut')
        pl.setCompCLFversion(1.0)
        pl.setName('Converted lut')

        ds1 = clf.Description(description)
        pl.addElement(ds1)

        for lutpn in lutpns:
            pl.addProcess(lutpn)

        # Write CLF to disk
        print( "Writing CLF : %s" % clfPath)
        pl.writeFile(clfPath)
    else:
        print( "No ProcessNodes created for this transform. Skipping writing CLF." )        

def main():
    import optparse

    p = optparse.OptionParser(description='Convert an OCIO color space transform to the Common LUT Format',
                                prog='convertOCIOToCLF',
                                version='0.01',
                                usage='%prog [options]')

    p.add_option('--config', '-c', default=None)
    p.add_option('--source', '-s', type='string', action='append', default=[])
    p.add_option('--destination', '-d', type='string', action='append', default=[])
    p.add_option('--output', '-o', default=None)
    p.add_option('--inversesUseHalfDomain', '', action='store_true', default=False)
    p.add_option('--inversesUseIndexMaps', '', action='store_true', default=False)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    configPath = options.config
    sourceColorSpaces = options.source
    destColorSpaces = options.destination
    outputPath = options.output
    inversesUseHalfDomain = options.inversesUseHalfDomain
    inversesUseIndexMaps = options.inversesUseIndexMaps

    
    print( "config    : %s" % configPath )
    print( "output    : %s" % outputPath )
    print( "source    : %s" % sourceColorSpaces )
    print( "dest      : %s" % destColorSpaces )
    print( "half dom. : %s" % inversesUseHalfDomain )
    print( "index map : %s" % inversesUseIndexMaps )
    

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    #print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    #
    # Run 
    #
    if( configPath != None and outputPath != None 
        and (sourceColorSpaces != [] or destColorSpaces != [] ) ):
        convertOCIOtoCLF(configPath, sourceColorSpaces, 
            destColorSpaces, outputPath, inversesUseIndexMaps, inversesUseHalfDomain)

# main

if __name__ == '__main__':
    main()
