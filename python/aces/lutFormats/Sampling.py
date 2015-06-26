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

__author__ = 'Haarm-Pieter Duiker'
__copyright__ = 'Copyright (C) 2015 Academy of Motion Picture Arts and Sciences'
__maintainer__ = 'Academy of Motion Picture Arts and Sciences'
__email__ = 'acessupport@oscars.org'
__status__ = 'Production'

__major_version__ = '1'
__minor_version__ = '0'
__change_version__ = '0'
__version__ = '.'.join((__major_version__,
                        __minor_version__,
                        __change_version__))

import os
import math

import clf
from clf.Common import halfToUInt16, uint16ToHalf

# Generate an inverse 1D LUT by evaluating and resampling the original 1D LUT
# Inverse LUTs will have 2x the base LUT's number of entries. This may not be 
# enough to characterize the inverse function well.
def generateLUT1DInverseResampled(resolution, samples, minInputValue, maxInputValue):
    lutpns = []

    # Invert happens in 3 stages
    # 1. Range values down from the min and max output values to 0-1
    # 2. Generate the inverse LUT for these newly reranged values
    # 3. Range the value up to the range defined by minInputValue and maxInputValue
    # This is similar to how .CSP preluts are turned into ProcessNodes

    # Get the resolution of the prelut
    inputResolution = resolution[0]
    channels = resolution[1]

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
    minOutputValue = samples[0]
    for c in range(channels):
        minOutputValue = min(minOutputValue, samples[c])

    maxOutputValue = samples[-channels]
    for c in range(channels):
        maxOutputValue = max(maxOutputValue, samples[-channels+c])

    #print( inputResolution, minInputValue, maxInputValue, minOutputValue, maxOutputValue )

    # Create a Range node to normalize data from the range [minOut, maxOut]
    rangepn1 = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "inverse_1d_range_1", "inverse_1d_range_1")
    rangepn1.setMinInValue(minOutputValue)
    rangepn1.setMaxInValue(maxOutputValue)
    rangepn1.setMinOutValue(0.0)
    rangepn1.setMaxOutValue(1.0)

    lutpns.append(rangepn1)

    # Generate inverse 1d LUT by running values through the
    # - inverse normalization [0,1] back to [minOut, maxOut]
    # - the inverse of the original LUT
    inverseSamples = [0.0]*outputResolution*channels

    for inverseLutIndex in range(outputResolution):

        # Normalized LUT input
        inputValue = float(inverseLutIndex)/(outputResolution-1)

        # Invert the normalization
        rangedValue = inputValue*(maxOutputValue - minOutputValue) + minOutputValue

        inverseSample = [0.0]*channels

        # For each channel
        for channel in range(channels):
            # Find the location of the de-normalized value in the lut
            for lutIndex in range(inputResolution):
                sampleIndex = lutIndex*channels + channel
                if samples[sampleIndex] > rangedValue:
                    break

            # Get the interpolation value
            lutIndexLow = max(0, lutIndex-1)
            lutIndexHigh = min(inputResolution-1, lutIndex)
            sampleIndexLow = lutIndexLow*channels + channel
            sampleIndexHigh = lutIndexHigh*channels + channel

            if lutIndexLow == lutIndexHigh:
                lutInterp = 0.0
            else:
                lutInterp = (rangedValue - samples[sampleIndexLow])/(
                    samples[sampleIndexHigh] - samples[sampleIndexLow])

            # Find the output value
            outputInterpolated = (lutInterp + lutIndexLow)/(inputResolution-1)

            inverseSample[channel] = outputInterpolated

        inverseSamples[inverseLutIndex*channels:(inverseLutIndex+1)*channels] = inverseSample

    # Create a 1D LUT with generated sample values
    lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "inverse_1d_lut", "inverse_1d_lut")
    lutpn.setArray(channels, inverseSamples)

    lutpns.append(lutpn)

    # Create a Range node to expaand from [0,1] to [minIn, maxIn]
    rangepn2 = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "inverse_1d_range_2", "inverse_1d_range_2")
    rangepn2.setMinInValue(0.0)
    rangepn2.setMaxInValue(1.0)
    rangepn2.setMinOutValue(minInputValue)
    rangepn2.setMaxOutValue(maxInputValue)

    lutpns.append(rangepn2)

    return lutpns

# Generate an inverse 1D LUT by evaluating all possible half-float values.
# All inverse LUTs will be 65536 entries, but you don't have to worry about resolution issues
def generateLUT1DInverseHalfDomain(resolution, samples, minInputValue, maxInputValue, rawHalfs=False):
    lutpns = []

    # Invert happens in 1 stages
    # 1. Generate the inverse LUT for each possible half-float value

    # Get the resolution of the prelut
    inputResolution = resolution[0]
    channels = resolution[1]

    # For this inversion approach, we will always use 64k entries
    outputResolution = 65536

    #print( inputResolution, minInputValue, maxInputValue, minOutputValue, maxOutputValue )

    # Generate inverse 1d LUT by running values through the
    # - the inverse of the original LUT
    inverseSamples = [0.0]*outputResolution*channels

    for inverseLutIndex in range(outputResolution):

        # LUT input
        inputValue = uint16ToHalf(inverseLutIndex)

        inverseSample = [0.0]*channels

        # For each channel
        for channel in range(channels):
            if math.isnan(inputValue):
                outputInterpolated = inputValue
            elif math.isinf(inputValue):
                outputInterpolated = inputValue
            else:
                # Find the location of the value in the lut
                for lutIndex in range(inputResolution):
                    sampleIndex = lutIndex*channels + channel
                    if samples[sampleIndex] > inputValue:
                        break

                # Get the interpolation value
                lutIndexLow = max(0, lutIndex-1)
                lutIndexHigh = min(inputResolution-1, lutIndex)
                sampleIndexLow = lutIndexLow*channels + channel
                sampleIndexHigh = lutIndexHigh*channels + channel

                if lutIndexLow == lutIndexHigh:
                    lutInterp = 0.0
                else:
                    lutInterp = (inputValue - samples[sampleIndexLow])/(
                        samples[sampleIndexHigh] - samples[sampleIndexLow])

                # Find the output value
                outputInterpolated = (lutInterp + lutIndexLow)/(inputResolution-1)

            #if rawHalfs:
            #    outputInterpolated = halfToUInt16(outputInterpolated)

            inverseSample[channel] = outputInterpolated

        inverseSamples[inverseLutIndex*channels:(inverseLutIndex+1)*channels] = inverseSample

    # Create a 1D LUT with generated sample values
    if rawHalfs:
        lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], 
            "inverse_1d_lut", "inverse_1d_lut", rawHalfs=rawHalfs, halfDomain=True)
    else:
        lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], 
            "inverse_1d_lut", "inverse_1d_lut", halfDomain=True)
    lutpn.setArray(channels, inverseSamples)

    lutpns.append(lutpn)

    return lutpns

# Generate an inverse 1D LUT using an IndexMap to hold the mapping directly.
def generateLUT1DInverseIndexMap(resolution, samples, minInputValue, maxInputValue):
    lutpns = []

    # Invert happens in 3 stages
    # 1. Create the index map that goes from LUT output values to index values
    # 2. Create a LUT that maps from index values to [0,1]
    # 3. Create a Range node to remap from [0,1] to [minInput,maxInput]

    # Get the resolution of the prelut
    inputResolution = resolution[0]
    channels = resolution[1]

    #print( inputResolution, minInputValue, maxInputValue )

    # Index Maps for the inverse LUT
    indexMaps = []
    for c in range(channels):
        indexMapInput = [0.0]*inputResolution
        for i in range(inputResolution):
            indexMapInput[i] = samples[i*channels + c]

        indexMapOutput = range(inputResolution)

        indexMaps.append([indexMapInput, indexMapOutput])

    # Sample values for the LUT - output is [0,1]
    inverseSamples = [0.0]*inputResolution*channels

    for i in range(inputResolution):
        v = float(i)/(inputResolution-1)
        for c in range(channels):
            inverseSamples[i*channels + c] = v

    # Create a 1D LUT with generated index map and sample values
    lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], 
        "inverse_1d_lut", "inverse_1d_lut")

    if channels == 3:
        lutpn.setIndexMaps(indexMaps[0], indexMaps[1], indexMaps[2])
    else:
        lutpn.setIndexMaps(indexMaps[0])

    lutpn.setArray(channels, inverseSamples)

    lutpns.append(lutpn)

    # Create a Range node to expaand from [0,1] to [minIn, maxIn]
    if minInputValue != 0.0 or maxInputValue != 1.0:
        rangepn2 = clf.Range(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "inverse_1d_range_1", "inverse_1d_range_1")
        rangepn2.setMinInValue(0.0)
        rangepn2.setMaxInValue(1.0)
        rangepn2.setMinOutValue(minInputValue)
        rangepn2.setMaxOutValue(maxInputValue)

        lutpns.append(rangepn2)

    return lutpns

def sample1D(processList,
             lutResolution1d,
             inputMin,
             inputMax):
    #print( "sample1D" )

    # Sample all values in 1D range
    samples = [0.0]*lutResolution1d*3
    for lutIndex in range(lutResolution1d):

        sampleValue = float(lutIndex)/(lutResolution1d-1)*(
            inputMax - inputMin) + inputMin
        lutValue = processList.process([sampleValue]*3)

        samples[lutIndex*3:(lutIndex+1)*3] = lutValue

    return samples
# sample1D

def sample3D(processList,
             lutResolution3d,
             inputMin,
             inputMax):
    #print( "sample3D" )

    # Sample all values in 3D range
    samples = [[[[0.0,0.0,0.0] for i in xrange(lutResolution3d[0])] for i in xrange(lutResolution3d[1])] for i in xrange(lutResolution3d[2])]

    for r in range(lutResolution3d[0]):
        for g in range(lutResolution3d[1]):
            for b in range(lutResolution3d[2]):

                sampleValueR = float(r)/(lutResolution3d[0]-1)*(
                    inputMax - inputMin) + inputMin
                sampleValueG = float(g)/(lutResolution3d[1]-1)*(
                    inputMax - inputMin) + inputMin
                sampleValueB = float(b)/(lutResolution3d[2]-1)*(
                    inputMax - inputMin) + inputMin
                sampleValue = [sampleValueR, sampleValueG, sampleValueB]
                lutValue = processList.process(sampleValue)

                #print( "%d, %d, %d : %3.3f, %3.3f, %3.3f -> %3.3f, %3.3f, %3.3f" % (
                #    r, g, b,
                #    sampleValueR, sampleValueG, sampleValueB,
                #    lutValue[0], lutValue[1], lutValue[2]))

                samples[r][g][b] = lutValue

    return samples
# sample3D

def createShaper(shaperType,
                 shaperMin,
                 shaperMax):
    # 
    # Create the forward and inverse input shaper ProcessLists
    #
    shaperPL = clf.ProcessList()
    shaperPLInverse = clf.ProcessList()

    # Log shaper
    if shaperType == 'log2':
        #print( "log shaper - %f, %f" % (shaperMin, shaperMax))

        # Forward ProcessNodes
        logPn = clf.Log(style='log2')
        shaperPL.addProcess(logPn)

        rangePn = clf.Range()
        rangePn.setMinInValue(shaperMin)
        rangePn.setMaxInValue(shaperMax)
        rangePn.setMinOutValue(0.0)
        rangePn.setMaxOutValue(1.0)
        shaperPL.addProcess(rangePn)

        # Input min and max
        inputMin = pow(2, shaperMin)
        inputMax = pow(2, shaperMax)

        # Inverse ProcessNodes
        rangePn2 = clf.Range()
        rangePn2.setMinInValue(0.0)
        rangePn2.setMaxInValue(1.0)
        rangePn2.setMinOutValue(shaperMin)
        rangePn2.setMaxOutValue(shaperMax)
        shaperPLInverse.addProcess(rangePn2)

        logPn2 = clf.Log(style='antiLog2')
        shaperPLInverse.addProcess(logPn2)

    # Linear shaper
    elif shaperType == 'linear':
        #print( "linear shaper - %f, %f" % (shaperMin, shaperMax))

        # Forward ProcessNodes
        rangePn = clf.Range()
        rangePn.setMinInValue(shaperMin)
        rangePn.setMaxInValue(shaperMax)
        rangePn.setMinOutValue(0.0)
        rangePn.setMaxOutValue(1.0)
        shaperPL.addProcess(rangePn)

        # Input min and max
        inputMin = shaperMin
        inputMax = shaperMax

        # Inverse ProcessNodes
        rangePn2 = clf.Range()
        rangePn2.setMinInValue(0.0)
        rangePn2.setMaxInValue(1.0)
        rangePn2.setMinOutValue(shaperMin)
        rangePn2.setMaxOutValue(shaperMax)
        shaperPLInverse.addProcess(rangePn2)


    # No shaper
    else:
        inputMin = 0.0
        inputMax = 1.0

    return (shaperPL, shaperPLInverse, inputMin, inputMax)
# createShaper

def sample1D3D1D(processList,
                 lutResolution1d3d1d,
                 shaperIn,
                 shaperOut):
    #print( "sample1D3D1D" )

    (lutResolution1dIn, lutResolution3d, lutResolution1dOut) = lutResolution1d3d1d
    (shaperInType, shaperInMin, shaperInMax) = shaperIn
    (shaperOutType, shaperOutMin, shaperOutMax) = shaperOut

    #
    # Create the input and output shaper processLists
    #
    (shaperInPL, shaperInPLInverse, inputMin, inputMax) = createShaper(shaperInType, shaperInMin, shaperInMax)
    (shaperOutPL, shaperOutPLInverse, outputMin, outputMax) = createShaper(shaperOutType, shaperOutMin, shaperOutMax)

    #
    # Create the input shaper samples
    #
    if shaperInType != None:
        #print( "sampleAndWrite1D3D1D - create input shaper" )

        samples1dIn = [0.0]*lutResolution1dIn*3
        for lutIndex in range(lutResolution1dIn):
            sampleValue = float(lutIndex)/(lutResolution1dIn-1)*(
                inputMax - inputMin) + inputMin

            lutValue = shaperInPL.process([sampleValue]*3)

            #print( "%3.3f -> %3.3f" % (sampleValue, lutValue[0]))

            samples1dIn[lutIndex*3:(lutIndex+1)*3] = lutValue
    else:
        samples1dIn = None

    #
    # Sample all values in 3D range
    # - Use the inverse sampler at the head of the sampling process
    #
    #print( "sampleAndWrite1D3D1D - create 3D LUT" )

    samples3d = [[[[0.0,0.0,0.0] for i in xrange(lutResolution3d[0])] for i in xrange(lutResolution3d[1])] for i in xrange(lutResolution3d[2])]

    for r in range(lutResolution3d[0]):
        for g in range(lutResolution3d[1]):
            for b in range(lutResolution3d[2]):

                sampleValueR = float(r)/(lutResolution3d[0]-1)
                sampleValueG = float(g)/(lutResolution3d[1]-1)
                sampleValueB = float(b)/(lutResolution3d[2]-1)
                sampleValue = [sampleValueR, sampleValueG, sampleValueB]

                if shaperInType != None:
                    shaperInInverseValue = shaperInPLInverse.process(sampleValue)
                else:
                    shaperInInverseValue = sampleValue

                processedValue = processList.process(shaperInInverseValue)

                if shaperOutType != None:
                    shaperOutValue = shaperOutPL.process(processedValue)
                else:
                    shaperOutValue = processedValue

                lutValue = shaperOutValue

                #print( "%d, %d, %d : %3.3f, %3.3f, %3.3f -> %3.3f, %3.3f, %3.3f" % (
                #    r, g, b,
                #    sampleValueR, sampleValueG, sampleValueB,
                #    lutValue[0], lutValue[1], lutValue[2]))

                samples3d[r][g][b] = lutValue

    #
    # Create the output shaper samples
    #
    if shaperOutType != None:
        #print( "sampleAndWrite1D3D1D - create output shaper" )

        samples1dOut = [0.0]*lutResolution1dOut*3
        for lutIndex in range(lutResolution1dOut):
            sampleValue = float(lutIndex)/(lutResolution1dOut-1)

            lutValue = shaperInPLInverse.process([sampleValue]*3)

            samples1dOut[lutIndex*3:(lutIndex+1)*3] = lutValue
    else:
        samples1dOut = None

    return (samples1dIn,
            inputMin, inputMax,
            samples3d,
            samples1dOut,
            outputMin, outputMax)
# sample1D3D1D

