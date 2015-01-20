#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to convert from different LUT formats to CLF
"""

import array
import os
import sys

import clf

LUTFORMAT_UNKNOWN = 'Unknown'
LUTFORMAT_1D = '1D'
LUTFORMAT_3D = '3D'

def readSPI1D(lutPath):
    with open(lutPath) as f:
        lines = f.read().splitlines()

    #
    # Read LUT data
    #
    dataFormat = LUTFORMAT_1D
    resolution = [0, 0]
    samples = []
    indexMap = []
    minInputValue = 0.0
    maxInputValue = 1.0

    for line in lines:
        #print( "line : %s" % line )
        tokens = line.split()

        if tokens[0] == "Version":
            version = int(tokens[1])
            if version != 1:
                break
        elif tokens[0] == "From":
            minInputValue = float(tokens[1])
            maxInputValue = float(tokens[2])
        elif tokens[0] == "Length":
            resolution[0] = int(tokens[1])
        elif tokens[0] == "Components":
            resolution[1] = int(tokens[1])
        elif len(tokens) == 3:
            samples.extend(map(float, tokens))
        #else:
        #    print( "Skipping line : %s" % tokens )

    #
    # Create ProcessNodes
    #

    # Remap input range
    if minInputValue != 0.0 or maxInputValue != 1.0:
        rangepn = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "range", "range")
        rangepn.setMinInValue(minInputValue)
        rangepn.setMaxInValue(maxInputValue)
        rangepn.setMinOutValue(0.0)
        rangepn.setMaxOutValue(1.0)

        lutpns.append(rangepn)

    # LUT node
    lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut1d", "lut1d")
    lutpn.setArray(resolution[1], samples)

    lutpns.append(lutpn)

    #return (dataFormat, resolution, samples, indexMap, minInputValue, maxInputValue)
    return lutpns

def readSPI3D(lutPath):
    with open(lutPath) as f:
        lines = f.read().splitlines()

    dataFormat = LUTFORMAT_3D
    resolution = [0, 0, 0]
    samples = []
    indexMap = []
    minInputValue = 0.0
    maxInputValue = 1.0

    tokens = lines[0].split()
    if tokens[0] == "SPILUT":
        version = float(tokens[1])
        if version == 1.0:
            tokens = map(int, lines[1].split())
            if tokens[0] == 3 or tokens[1] == 3:
                tokens = map(int, lines[2].split())
                resolution = tokens

                # This assumes that the value are printed in order
                # with blue incrementing fastest like the CLF specification
                # This is generally true, but should be generalized at some
                # point to take into account the indices printed as the 
                # first three values on each line
                for line in lines[3:]:
                    tokens = map(float, line.split())
                    samples.extend(tokens[3:]) 

    #
    # Create ProcessNodes
    #
    lutpn = clf.LUT3D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut3d", "lut3d")
    lutpn.setArray(resolution, samples)

    #return (dataFormat, resolution, samples, indexMap, minInputValue, maxInputValue)
    return [lutpn]

def generateCLFPrelut(cspPreluts):
    prelutpns = []

    # Get the individual preluts
    (prelutR, prelutG, prelutB) = cspPreluts

    # Get the resolution of the prelut
    inputResolution = max(len(prelutR[0]), len(prelutG[0]), len(prelutB[0]))

    # XXX
    # Given that we're resampling, we should probably increase the
    # resolution of the resampled lut relative to the source
    outputResolution = inputResolution
    outputResolution *= 2

    # Find the minimum and maximum input
    # XXX
    # We take the min and max of all three preluts because the Range node
    # only takes single value, not RGB triples. If the prelut ranges are 
    # very different, this could introduce some artifacting
    minInputValue = min(prelutR[0][0], prelutG[0][0], prelutB[0][0])
    maxInputValue = max(prelutR[0][-1], prelutG[0][-1], prelutB[0][-1])

    print( inputResolution, minInputValue, maxInputValue )

    # Create a Range node to normalize data from that range [min, max]
    rangepn = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "prelut_range", "prelut_range")
    rangepn.setMinInValue(minInputValue)
    rangepn.setMaxInValue(maxInputValue)
    rangepn.setMinOutValue(0.0)
    rangepn.setMaxOutValue(1.0)

    prelutpns.append(rangepn)

    # Generate 1d LUT by running values through the
    # - inverse normalization
    # - the cspprelut
    samples = [0.0]*outputResolution*3

    for i in range(outputResolution):
        # Normalized LUT input
        inputValue = float(i)/(outputResolution-1)

        # Invert the normalization
        rangedValue = inputValue*(maxInputValue - minInputValue) + minInputValue

        sample = [0.0, 0.0, 0.0]

        # For each channel
        for channel in range(len(cspPreluts)):
            # Find the location of the de-normalized value in the prelut
            for prelutIndex in range(inputResolution):
                if cspPreluts[channel][0][prelutIndex] > rangedValue:
                    break

            # Get the interpolation value
            prelutIndexLow = max(0, prelutIndex-1)
            prelutIndexHigh = min(inputResolution-1, prelutIndex)
            prelutInterp = (rangedValue - cspPreluts[channel][0][prelutIndexLow])/(
                cspPreluts[channel][0][prelutIndexHigh] - cspPreluts[channel][0][prelutIndexLow])

            # Find the output value
            outputInterpolationRange = (cspPreluts[channel][1][prelutIndexHigh] - cspPreluts[channel][1][prelutIndexLow])
            outputInterpolated = prelutInterp*outputInterpolationRange + cspPreluts[channel][1][prelutIndexLow]

            sample[channel] = outputInterpolated

        samples[i*3:(i+1)*3] = sample

    # Create a 1D LUT with generated sample values
    lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "prelut_lut1d", "prelut_lut1d")
    lutpn.setArray(len(cspPreluts), samples)

    prelutpns.append(lutpn)

    return prelutpns

def readCSP(lutPath):
    with open(lutPath) as f:
        lines = f.read().splitlines()

    dataFormat = LUTFORMAT_UNKNOWN
    resolution = []
    samples = []
    prelut = []
    minInputValue = 0.0
    maxInputValue = 1.0

    tokens = lines[0].split()
    if tokens[0] == "CSPLUTV100":
        format = lines[1].split()[0]
        if format == "3D":
            dataFormat = LUTFORMAT_3D

            metadata = ""
            dataStart = 2
            if lines[2].rstrip() == "BEGIN METADATA":
                for line in lines[3:]:
                    dataStart += 1
                    if line.rstrip() == "END METADATA":
                        break
                    else:
                        metadata += (line.rstrip())

                #print( "metadata : %s" % metadata)
                dataStart += 2
                
                #print( "Data starts on line : %d" % dataStart )

                # Red Index Map
                prelutRedResolution = int(lines[dataStart+0])
                prelutRedInput = map(float, lines[dataStart+1].split())
                prelutRedOutput = map(float, lines[dataStart+2].split())

                # Green Index Map
                prelutGreenResolution = int(lines[dataStart+3])
                prelutGreenInput = map(float, lines[dataStart+4].split())
                prelutGreenOutput = map(float, lines[dataStart+5].split())

                # Blue Index Map
                prelutBlueResolution = int(lines[dataStart+6])
                prelutBlueInput = map(float, lines[dataStart+7].split())
                prelutBlueOutput = map(float, lines[dataStart+8].split())

                prelut = [[prelutRedInput, prelutRedOutput],
                    [prelutGreenInput, prelutGreenOutput],
                    [prelutBlueInput, prelutBlueOutput]]

                resolution = map(int, lines[dataStart+10].split())

                # CSP incremements LUT samples red, then green, then blue
                # CLF incremements LUT samples blue, then green, then red 
                # so we need to move samples around
                samples = [0.0]*resolution[0]*resolution[1]*resolution[2]*3
                cspIndex = 0
                for line in lines[dataStart+11:]:
                    # Convert from sample number to LUT index, CSP-style
                    indexR = cspIndex%resolution[0]
                    indexG = (cspIndex/resolution[0])%resolution[1]
                    indexB = cspIndex/(resolution[0]*resolution[1])

                    # Convert from LUT index to sample number, CLF-style
                    clfIndex = (indexR*resolution[0] + indexG)*resolution[1] + indexB
                    clfIndex *= 3

                    # Convert from text to float
                    cspSamples = map(float, line.split())

                    # Add to the sample values array
                    if len(cspSamples) == 3:
                        #print( "csp sample %d -> lut index : %d, %d, %d -> clf index : %d" % 
                        #    (cspIndex, indexR, indexG, indexB, clfIndex))
                        #print( "lut value : %3.6f %3.6f %3.6f" % (cspSamples[0], cspSamples[1], cspSamples[2]) )

                        samples[clfIndex:clfIndex+3] = cspSamples

                    cspIndex += 1

    #
    # Create ProcessNodes
    #
    lutpns = []

    if prelut != []:
        print( "Generating prelut")
        prelutpns = generateCLFPrelut(prelut)
        if prelutpns != []:
            for prelutpn in prelutpns:
                lutpns.append(prelutpn)

    lutpn = clf.LUT3D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut3d", "lut3d")
    lutpn.setArray(resolution, samples)
    lutpns.append(lutpn)

    #return (dataFormat, resolution, samples, indexMap, minInputValue, maxInputValue)
    return lutpns

def getLUTFileFormat(lutPath):
    fileFormat = os.path.split(lutPath)[1].split('.')[-1]
    return fileFormat

def readLUT(lutPath):
    dataFormat = LUTFORMAT_UNKNOWN
    resolution = [0, 0]
    samples = []
    indexMap = []
    minInputValue = 0.0
    maxInputValue = 1.0
    lutpns = []

    # Read LUTs here
    print( "Reading LUT : %s" % lutPath )

    fileFormat = getLUTFileFormat(lutPath)

    if fileFormat == "spi1d":
        print( "Reading Sony 1D LUT")
        #(dataFormat, resolution, samples, indexMap, minInputValue, maxInputValue) = readSPI1D(lutPath)
        lutpns = readSPI1D(lutPath)

    elif fileFormat == "spi3d":
        print( "Reading Sony 3D LUT")
        lutpns = readSPI3D(lutPath)

    elif fileFormat == "csp":
        print( "Reading CSP 1D shaper + 3D LUT")
        lutpns = readCSP(lutPath)

    else:
        print( "Unknown LUT format : %s" % fileFormat)

    return lutpns

def invertLUT1D(lut1DProcessNode):

    return lut1DProcessNode

def convertLUTtoCLF(lutPath, clfPath):
    # Load the LUT and convert to a CLF ProcessNode
    lutpns = readLUT(lutPath)

    # Create a CLF ProcessList and populate contents
    if lutpns != []:
        pl = clf.ProcessList()

        # Populate
        pl.setID('Converted lut')
        pl.setCompCLFversion(1.0)
        pl.setName('Converted lut')

        for lutpn in lutpns:
            pl.addProcess(lutpn)

        # Write CLF to disk
        pl.writeFile(clfPath)        

def createCLFExample1():
    pl = clf.ProcessList()

    # Populate
    pl.setID('Type.name.version')
    pl.setInverseOf('Type.Inverse.name.version')
    pl.setCompCLFversion(1.2)
    pl.setName('Example transform')
    pl.setAttribute('Extra', 'value')

    # Add another matrix node
    mpn1 = clf.MatrixProcessNode(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "someId", "Transform2")
    mpn1.setMatrix([3, 4, 3], [0.5, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.1, 0.0, 0.0, 2.0, 0.0])
    #mpn1.setMatrix([3, 4, 3], [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    pl.addProcess(mpn1)

    return pl

def main():
    import optparse

    p = optparse.OptionParser(description='Convert a LUT to the Common LUT Format',
                                prog='clfconvert',
                                version='0.01',
                                usage='%prog [options]')

    p.add_option('--input', '-i', default=None)
    p.add_option('--output', '-o', default=None)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    inputPath = options.input
    outputPath = options.output

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    #
    # Run 
    #
    if outputPath != None and inputPath != None:
        convertLUTtoCLF(inputPath, outputPath)

# main

if __name__ == '__main__':
    main()
