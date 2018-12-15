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

import array
import math
import numpy as np
import os
import sys
import traceback
import timeit

import clf
import OpenImageIO as oiio

#
# Functions to handle packing and unpacking half-float values
#

# Unpacks half-float values from 32-bit float values returned
# if you specify type = oiio.HALF when calling read_image
def floatToHalfs(floatValue):
    halfs = np.frombuffer(np.getbuffer(np.float32(floatValue)), dtype=np.float16)
    return (halfs[0], halfs[1])

# Packs half-float values into a 32-bit float value that
# can be used when outputSpec.set_format( oiio.HALF ) is set
# with outputImage.write_image
def halfsToFloat(half1, half2):
    halfarray = np.array([half1, half2], dtype=np.float16)
    return np.frombuffer(np.getbuffer(np.float16(halfarray)), dtype=np.float32)[0]

# Create a numpy array of half-float pixels based on an array of
# 'floats' read from OpenImageIO.
# Each 4 byte 'float' is the binary equivalent of two packed 2-byte half-floats.
def oiioFloatPixelsToNPHalfArray(width, height, channels, oiioFloats):

    if oiio.VERSION < 10800:
        # Read float pixels into a numpy half-float pixel array
        npPixels = np.frombuffer(np.getbuffer(np.float32(oiioFloats)), dtype=np.float16)
    else:
        # Convert uint16 values into a numpy half-float pixel array
        npPixels = np.frombuffer(np.getbuffer(np.uint16(oiioFloats)), dtype=np.float16)

    return npPixels
# oiioFloatPixelsToNPHalfArray

# Create an array of 'floats' that OpenImageIO can use to write 
# to formats like OpenEXR that support half-float. Starting point
# is a numpy array of half-float pixels. 
# Each 4 byte 'float' is the binary equivalent of two packed 2-byte half-floats.
def npHalfArrayToOIIOFloatPixels(width, height, channels, npPixels):
    if oiio.VERSION < 10800:
        # Read half-float pixels into a numpy float pixel array
        oiioFloatsArray = np.frombuffer(np.getbuffer(np.float16(npPixels)), dtype=np.float32)
    else:
        # Read half-float pixels into a numpy float pixel array
        oiioFloatsArray = np.frombuffer(np.getbuffer(np.float16(npPixels)), dtype=np.uint16)

    return oiioFloatsArray
# npHalfArrayToOIIOFloatPixels

#
# Mappings between OIIO 'type' values and CLF bit depths
#
oiioBitDepthToCLFBitDepth = {
    oiio.UINT8  : clf.bitDepths["UINT8"],
    oiio.UINT16 : clf.bitDepths["UINT16"],
    oiio.HALF   : clf.bitDepths["FLOAT16"],
    oiio.FLOAT  : clf.bitDepths["FLOAT32"]
}

clfBitDepthToOIIOBitDepth = {
    clf.bitDepths["UINT8"]   : oiio.UINT8,
    clf.bitDepths["UINT10"]  : oiio.UINT16,
    clf.bitDepths["UINT12"]  : oiio.UINT16,
    clf.bitDepths["UINT16"]  : oiio.UINT16,
    clf.bitDepths["FLOAT16"] : oiio.HALF,
    clf.bitDepths["FLOAT32"] : oiio.FLOAT 
}

#
# Read an image
#
def readPixelArray(inputPath, 
    bitDepthOverride="auto"):
    print( "Loading image - path : %s" % inputPath)

    inputImage = oiio.ImageInput.open( inputPath )

    if inputImage:
        # get image specs
        inputImageSpec = inputImage.spec()
        type = inputImageSpec.format.basetype
        width = inputImageSpec.width
        height = inputImageSpec.height
        channels = inputImageSpec.nchannels
        channelnames = inputImageSpec.channelnames
        metadata = inputImageSpec.extra_attribs
        metanames = [attr.name for attr in metadata]

        bitShift = 0

        print( "Loading image - spects : %d x %d - %d channels, %s bit depth, %s" % (width, height, channels, type, channelnames))

        # Handle automatic bit-depth conversions
        if bitDepthOverride:
            if bitDepthOverride == "auto":
                bitDepth = oiioBitDepthToCLFBitDepth[type]

                # 10, 12 or 16 bit values should map to maximum values of
                # 1023, 4095 or 65535 respectively. The OIIO default is treat
                # them all as 16-bit / 65535. This corrects for that behavior.
                if 'oiio:BitsPerSample' in metanames:
                    oiioBitDepth = metadata[ metanames.index( "oiio:BitsPerSample" ) ].value

                    if type == oiio.UINT16:
                        bitShift = (16 - oiioBitDepth)
                        print( "Reading as 16-bit int, then shifting by %d bits" % bitShift )

                        if oiioBitDepth == 10:
                            bitDepth = clf.bitDepths["UINT10"]
                        elif oiioBitDepth == 12:
                            bitDepth = clf.bitDepths["UINT12"]
            else:
                type = clfBitDepthToOIIOBitDepth[bitDepthOverride]
                bitDepth = bitDepthOverride
        else:
            bitDepth = oiioBitDepthToCLFBitDepth[type]

        sourceData = inputImage.read_image(type)

        inputImage.close()

        # Reset integer bit-depth 
        if bitShift != 0:
            #print( "Shifting integer values" )
            for i in range(len(sourceData)):
                sourceData[i] = sourceData[i] >> bitShift

        # OIIO versions < 1.8 didn't return half-float values directly
        # so this will convert from the packed representation to half-floats
        if type == oiio.HALF:
            print( "Unpacking half-float values" )
            sourceData = oiioFloatPixelsToNPHalfArray(width, height, channels, sourceData)
    else:
        (sourceData, bitDepth, width, height, channels, metadata) = (None, clf.bitDepths["UINT10"], 0, 0, 0, None, None)

    return (sourceData, bitDepth, width, height, channels, metadata, channelnames)
# readPixelArray

#
# Write an image
#
def writePixelArray(outputPath, 
    pixels, 
    bitDepth, 
    width, 
    height, 
    channels, 
    metadata,
    channelnames,
    compression=None,
    compressionQuality=0):
    print( "Writing image - path : %s" % outputPath)

    bitShift = 0
    metanames = [attr.name for attr in metadata]

    # Automatic conversion from CLF bit depth to OIIO 'type'
    type = clfBitDepthToOIIOBitDepth[bitDepth]

    #
    # Convert the pixel values as necessary
    #  'pixels' is assumed to refer to a float array
    #

    # Convert float values to 8-bit unsigned integer
    if type == oiio.UINT8:
        pixels8 = np.zeros(width*height*channels, dtype=np.uint8)
        for i in range(len(pixels)):
            pixels8[i] = int(pixels[i])
        pixels = pixels8

    # Convert float values to 16-bit unsigned integer
    elif type == oiio.UINT16:
        # 10, 12 or 16 bit values map to maximum values of
        # 1023, 4095 or 65535 respectively. The OIIO default is treat
        # them all as 16-bit / 65535. This bit shift will move the 10 or
        # 12 bit values back to the 16 bit range that OIIO expects.
        bitShift = 0
        if bitDepth == clf.bitDepths["UINT10"]:
            bitShift = 6
        elif bitDepth == clf.bitDepths["UINT12"]:
            bitShift = 4

        pixels16 = np.zeros(width*height*channels, dtype=np.uint16)
        # Cast to 16 bit and reset integer bit-depth if necessary
        for i in range(len(pixels)):
            pixels16[i] = int(pixels[i]) << bitShift
        pixels = pixels16

    # OIIO doesn't store half-float values directly, so this will
    # convert from half-floats to the packed representation
    elif type == oiio.HALF:
        print( "Packing half-float values" )
        pixels = npHalfArrayToOIIOFloatPixels(width, height, channels, pixels)

    #
    # set image specs
    #
    outputSpec = oiio.ImageSpec()
    outputSpec.set_format( type )
    outputSpec.width = width
    outputSpec.height = height
    outputSpec.nchannels = channels
    outputSpec.channelnames = channelnames

    # Mapping between bit depth and 'oiio:BitsPerSample' metadata value
    bitDepthValue = {
        clf.bitDepths["UINT8"] : 8,
        clf.bitDepths["UINT10"] : 10,
        clf.bitDepths["UINT12"] : 12,
        clf.bitDepths["UINT16"] : 16
    }

    # Add the metadata tags
    for attr in metadata:
        #print( attr.name, attr.value, str(attr.type) )
        value = attr.value

        # Reset specific values. Ex. bits per sample
        if attr.name == "oiio:BitsPerSample":
            #print( "Resetting bits per sample. bit depth value : %s. Metadata value : %d" % (
            #    bitDepth, value) )
            value = bitDepthValue[bitDepth]

        outputSpec.attribute( attr.name, attr.type, value )

    # Ugly special case
    if type in [oiio.UINT8, oiio.UINT16] and not ("oiio:BitsPerSample" in metanames):
        #print( "Setting bits per sample. bit depth value : %s. Metadata value : %d" % (
        #    bitDepth, bitDepthValue[bitDepth]) )
        outputSpec.attribute("oiio:BitsPerSample", bitDepthValue[bitDepth])

    #
    # Set compression
    #
    if compression:
        outputSpec.attribute("compression", compression)
            
    if compressionQuality > 0:
        outputSpec.attribute("CompressionQuality", compressionQuality)        

    #
    # Create, write and close the image
    #
    outputImage = oiio.ImageOutput.create(outputPath)
    if not outputImage:
        print( "\nImage %s could not be created. Writing aborted.\n" % outputPath )
        return
    ok = outputImage.open (outputPath, outputSpec, oiio.Create)
    if not ok:
        print( "\nImage %s could not be opened. Writing aborted.\n" % outputPath )
        return
    try:
        ok = outputImage.write_image(outputSpec.format, pixels)
    except:
        print( "\nCaught exception." )
        print( '-'*60 )
        traceback.print_exc()
        print( '-'*60 )
        ok = False
    if not ok:
        print( "\nImage %s could not write. Writing failed.\n" % outputPath )
        return
    outputImage.close()
# writePixelArray

from multiprocessing import Pool, Lock, cpu_count

#
# Filter a single row - one pixel at a time
#
# This version processes a single pixel at a time.
def filterRow_pixel(row, 
    width,
    height, 
    channels, 
    pixels, 
    InRange,
    processList,
    OutRange,
    processedPixels,
    verbose):

    if row%math.ceil((height-1)/100.0) == 0:
        print( "%3.1f - row %d / %d" % (row/(height-1.0)*100.0, row, height-1) )

    for i in range(width):
        index = (row*width + i)*channels
        ovalue = pixels[index:index+channels]

        pvalue = np.array(ovalue, dtype=np.float32)
        # Reset values if input image and CLF input bit depths don't match
        if InRange:
            pvalue = InRange.process(pvalue)

        # Process values
        #print( "Processing %04d, %04d : %s" % (i, j, ovalue))
        pvalue = processList.process(pvalue)

        # Reset values if output image and CLF output bit depths don't match
        if OutRange:
            pvalue = OutRange.process(pvalue)

        if verbose:
            print( "Processed %04d, %04d : %s -> %s" % (i, j, ovalue, pvalue))

        for c in range(channels):
            processedPixels[index + c] = pvalue[c]

    return True

#
# Filter a single row - as a group of pixels
#
# This version processes a row of pixels as a group, using the 'stride' parameter
# It it marginally faster than processing one pixel at a time.
def filterRow_stride(row, 
    width, 
    height,
    channels, 
    pixels, 
    InRange,
    processList,
    OutRange,
    processedPixels,
    verbose):

    if row%math.ceil((height-1)/100.0) == 0:
        print( "%3.1f - row %d / %d" % (row/(height-1.0)*100.0, row, height-1) )

    index = (row*width)*channels

    # Copy a single row
    ovalue = pixels[index:index+width*channels]
    pvalue = np.array(ovalue, dtype=np.float32)

    # Reset values if input image and CLF input bit depths don't match
    if InRange:
        pvalue = InRange.process(pvalue, stride=channels)

    # Process values
    #print( "Processing %04d, %04d : %s" % (i, j, ovalue))
    pvalue = processList.process(pvalue, stride=channels, verbose=verbose)

    # Reset values if output image and CLF output bit depths don't match
    if OutRange:
        pvalue = OutRange.process(pvalue, stride=channels)

    if verbose:
        print( "Processed %04d : %s -> %s" % (row, ovalue, pvalue))

    for c in range(width*channels):
        processedPixels[index + c] = pvalue[c]

    return True

#
# Filter a single row - parallel
#
# This version takes a row of pixels and returns a filtered row of pixels.
# It is designed to be used with the Pool map_async call.
def filterRow_parallel(row, 
    width, 
    height,
    channels, 
    pixels, 
    InRange,
    processList,
    OutRange,
    processedPixels,
    verbose):

    #t0 = timeit.default_timer()
    if verbose:
        print( "process %d - row %d" % (os.getpid(), row) )

    if row%math.ceil((height-1)/100.0) == 0:
        print( "%3.1f - row %d / %d" % (row/(height-1.0)*100.0, row, height-1) )

    # Copy a single row
    ovalue = pixels

    pvalue = np.array(ovalue, dtype=np.float32)
    # Reset values if input image and CLF input bit depths don't match
    if InRange:
        pvalue = InRange.process(pvalue, stride=channels)

    # Process values
    #print( "Processing %04d, %04d : %s" % (i, j, ovalue))
    pvalue = processList.process(pvalue, stride=channels)

    # Reset values if output image and CLF output bit depths don't match
    if OutRange:
        pvalue = OutRange.process(pvalue, stride=channels)

    #t1 = timeit.default_timer()
    #elapsed = t1 - t0
    
    #if verbose:
    #    print( "Filtering row %d took %s seconds" % (row, elapsed) )

    return pvalue

# filterRow_parallel_splitargs splits the single argument 'args' into mulitple arguments
# this is needed because map() can only be used for functions
# that take a single argument (see http://stackoverflow.com/q/5442910/1461210)
def filterRow_parallel_splitargs(args):
    try:
        return filterRow_parallel(*args)
    except:
        #print( "\nprocess %d - exception caught\n" % os.getpid() )
        pass

#
# Filter an image
#
def filterImageWithCLF(inputPath, 
    outputPath, 
    processList, 
    verbose=False,
    outBitDepth=None,
    multithreaded=cpu_count(),
    compression=None,
    compressionQuality=0):

    #
    # Get the input image pixel array
    #
    t0 = timeit.default_timer()

    pixels, inBitDepth, width, height, channels, metadata, channelnames = readPixelArray(inputPath)
    if pixels == None:
        print( "\nImage %s could not be opened. Filtering aborted.\n" % inputPath )
        return
    #print( len(pixels), bitDepth, width, height, channels )

    t1 = timeit.default_timer()
    elapsed = t1 - t0
    print( "Reading took %s seconds" % elapsed )

    # Determine outBitDepth
    if not outBitDepth or not (outBitDepth in clf.bitDepths.values()):
        outBitDepth = inBitDepth

    #
    # Create two Range ProcessNodes to convert data
    # 1: from the bitdepth of the input image to the bit depth of the CLF start
    # 2: from the bitdepth of the CLF output to the bit depth of the output image
    #
    processListInBitDepth = processList.getInBitDepth()
    processListOutBitDepth = processList.getOutBitDepth()

    InRange = None
    if processListInBitDepth != inBitDepth:
        InRange = clf.Range(inBitDepth, processListInBitDepth)

    OutRange = None
    if processListOutBitDepth != outBitDepth:
        OutRange = clf.Range(processListOutBitDepth, outBitDepth)

    #
    # Filter image
    #

    # Float buffer for the processed pixels
    # Values will be converted to other bit depths when writing to disk
    processedPixels = np.zeros(width * height * channels, dtype=np.float32)

    # Process
    t0 = timeit.default_timer()

    # Multi-threaded execution
    if multithreaded > 1:
        print( "Filtering image - multithreaded (%d threads)" % multithreaded )
        try:
            pool = Pool(processes=multithreaded)

            # Each process filters a single row and returns the results
            # Feels a little clunky, but it gets us the speed of multithreading
            # and we're probably not worried about the memory hit since we're
            # only processing one image at a time.

            #print ( "Creating map_async pool ")
            result = pool.map_async(filterRow_parallel_splitargs,
                [(x, 
                    width, 
                    height,
                    channels, 
                    pixels[x*width*channels:x*width*channels+width*channels], 
                    InRange,
                    processList,
                    OutRange,
                    processedPixels,
                    verbose) for x in range(height)],
                chunksize=1)

            try:
                parallelProcessedPixels = result.get(0xFFFF)
            except KeyboardInterrupt:
                print( "\nProcess received Ctrl-C. Exiting.\n" )
                return
            except:
                print( "\nCaught exception. Exiting." )
                print( '-'*60 )
                traceback.print_exc()
                print( '-'*60 )
                return

            # The filtered rows have to be copied back to the 'processedPixels' block
            # when everything finishes up
            for i in range(height):
                for j in range(width*channels):
                    processedPixels[i*width*channels + j] = parallelProcessedPixels[i][j]
        except:
            print( "Error in multithreaded processing. Exiting." )
            print( '-'*60 )
            traceback.print_exc()
            print( '-'*60 )
            return

    # Single-threaded execution
    else:
        print( "Filtering image - single threaded" )

        #for j in range(height):
        j = 5
        if True:
            # Using filterRow_stride instead of filterRow_pixel
            # Processing a full row is ~10% faster than processing individual pixels
            filterRow_stride(j,
                width, height, channels, pixels, 
                InRange, processList, OutRange,
                processedPixels,
                verbose)

    t1 = timeit.default_timer()
    elapsed = t1 - t0
    print( "Filtering took %s seconds" % elapsed )

    #
    # Write the processed pixel array to the output
    #
    t0 = timeit.default_timer()

    writePixelArray(outputPath, processedPixels, outBitDepth, width, height, channels, metadata,
        channelnames, compression, compressionQuality)

    t1 = timeit.default_timer()
    elapsed = t1 - t0
    print( "Writing took %s seconds" % elapsed )

# filterImageWithCLF

#
# Get the options, load a CLF and filter an image
#
def main():
    import optparse

    usage  = "%prog [options]\n"
    usage += "\n"
    usage += "compression options:\n"
    usage += " exr format compression options  : none, rle, zip, zips(default), piz, pxr24, b44, b44a, dwaa, or dwab\n"
    usage += "   dwaa and dwab compression support depends on the version of OpenImageIO that you're using."
    usage += " tiff format compression options : none, lzw, zip(default), packbits\n"
    usage += " tga format compression options  : none, rle\n"
    usage += " sgi format compression options  : none, rle\n"
    usage += "\n"
    usage += "compression quality options:\n"
    usage += " jpg format compression quality options  : 0 to 100\n"


    p = optparse.OptionParser(description='Filter an image using the Common LUT Format',
                                prog='clfFilter',
                                version='clfFilter',
                                usage=usage)

    p.add_option('--input', '-i', default=None)
    p.add_option('--output', '-o', default=None)
    p.add_option('--clf', '-c', default=None)
    p.add_option('--verbose', '-v', action="store_true")
    p.add_option('--outputBitDepth', '', default=None)
    p.add_option('--multithreaded', '-m', type='int', default=cpu_count())
    p.add_option("--compression")
    p.add_option("--quality", type="int", dest="quality", default = -1)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfPath = options.clf
    inputPath = options.input
    outputPath = options.output
    verbose = options.verbose == True
    outputBitDepth = options.outputBitDepth
    multithreaded = options.multithreaded
    multithreaded = min(cpu_count(), max(1, multithreaded))
    compression = options.compression
    compressionQuality = options.quality

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    if verbose:
        print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    if outputBitDepth and not (outputBitDepth in clf.bitDepths.values()):
        print( "Output bit depth %s is not a valid CLF bit depth. It will be ignored." % outputBitDepth)
        print( "Valid values are %s." % ", ".join(clf.bitDepths.values()) )
        outputBitDepth = None
        return

    #
    # Load a CLF
    #
    processList = None
    if clfPath != None:
        processList = clf.ProcessList(clfPath)
        print( "Loaded CLF - title: %s, path: %s" % (processList.getName(), clfPath) )

    #
    # Filter an image
    #
    if processList != None and outputPath != None and inputPath != None:
        filterImageWithCLF(inputPath, 
            outputPath, 
            processList, 
            verbose,
            outBitDepth=outputBitDepth,
            multithreaded=multithreaded,
            compression=compression,
            compressionQuality=compressionQuality)
# main

if __name__ == '__main__':
    main()
