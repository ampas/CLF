import sys
import array

import numpy as np

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
    # Read half float pixels into a numpy pixel array
    npPixels = np.zeros(width*height*channels, dtype=np.float16)

    # OIIO packs two half-float into a single float value
    # They have to be split out and then stored in a new array
    for entry in range(len(oiioFloats)):
        (half1, half2) = floatToHalfs(oiioFloats[entry])
        npPixels[entry*2    ] = half1
        npPixels[entry*2 + 1] = half2

    return npPixels
# oiioFloatPixelsToNPHalfArray

# Create an array of 'floats' that OpenImageIO can use to write 
# to formats like OpenEXR that support half-float. Starting point
# is a numpy array of half-float pixels. 
# Each 4 byte 'float' is the binary equivalent of two packed 2-byte half-floats.
def npHalfArrayToOIIOFloatPixels(width, height, channels, npPixels):
    # Allocate array of floats. Divide by two as two half values will be
    # packes into each float value
    oiioFloats = [0.0]*(width*height*channels/2)

    # Step through the float array, grabbing the appropriate two half values
    # and bringing them together
    for entry in range(len(oiioFloats)):
        #print( "%d / %d" % (entry, len(npPixels)) )
        half1 = npPixels[entry*2    ]
        half2 = npPixels[entry*2 + 1]
        floatValue = halfsToFloat(half1, half2)
        oiioFloats[entry] = floatValue

    oiioFloatsArray = array.array('f', oiioFloats)
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

    # get image specs
    inputImageSpec = inputImage.spec()
    type = inputImageSpec.format.basetype
    width = inputImageSpec.width
    height = inputImageSpec.height
    channels = inputImageSpec.nchannels
    metadata = inputImageSpec.extra_attribs
    metanames = [attr.name for attr in metadata]

    bitShift = 0

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

    # OIIO doesn't return half-float values directly, so this will
    # convert from the packed representation to half-floats
    if type == oiio.HALF:
        print( "Unpacking half-float values" )
        sourceData = oiioFloatPixelsToNPHalfArray(width, height, channels, sourceData)

    return (sourceData, bitDepth, width, height, channels, metadata)
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
    metadata):
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
    # Create, write and close the image
    #
    outputImage = oiio.ImageOutput.create(outputPath)
    outputImage.open (outputPath, outputSpec, oiio.Create)
    outputImage.write_image(outputSpec.format, pixels)
    outputImage.close()
# writePixelArray

#
# Filter an image
#
def filterImageWithCLF(inputPath, 
    outputPath, 
    processList, 
    verbose=False,
    outBitDepth=None):

    #
    # Get the input image pixel array
    #
    pixels, inBitDepth, width, height, channels, metadata = readPixelArray(inputPath)
    #print( len(pixels), bitDepth, width, height, channels )

    # Determine outBitDepth
    if not outBitDepth or not (outBitDepth in clf.bitDepths.values()):
        outBitDepth = inBitDepth

    #
    # Create Range ProcessNodes to convert data to the correct bit depth
    # for input to the CLF and then for output to file
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
    processedPixels = array.array("f", "\0" * width * height * channels * 4)

    # Process
    print( "Filtering image" )
    for i in range(width):
        for j in range(height):
            index = (j*width + i)*channels
            #ovalue = list(pixels[index:index+3])
            ovalue = pixels[index:index+channels]

            pvalue = list(ovalue)
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
                print( "Processed %04d, %04d : %s -> %s" % (i, j, list(ovalue), pvalue))

            for c in range(channels):
                processedPixels[index + c] = pvalue[c]

    #
    # Write the processed pixel array to the output
    #
    writePixelArray(outputPath, processedPixels, outBitDepth, width, height, channels, metadata)
# filterImageWithCLF

#
# Get the options, load a CLF and filter an image
#
def main():
    import optparse

    p = optparse.OptionParser(description='Filter an image using the Common LUT Format',
                                prog='clfFilter',
                                version='clfFilter',
                                usage='%prog [options]')

    p.add_option('--input', '-i', default=None)
    p.add_option('--output', '-o', default=None)
    p.add_option('--clf', '-c', default=None)
    p.add_option('--verbose', '-v', action="store_true")
    p.add_option('--outputBitDepth', '', default=None)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfPath = options.clf
    inputPath = options.input
    outputPath = options.output
    verbose = options.verbose == True
    outputBitDepth = options.outputBitDepth

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    if verbose:
        print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    if not outputBitDepth in clf.bitDepths.values():
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
            outBitDepth=outputBitDepth)
# main

if __name__ == '__main__':
    main()
