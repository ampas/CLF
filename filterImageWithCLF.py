import sys
import array

import clf
import OpenImageIO as oiio

def readPixelArray(inputPath):
    inputImage = oiio.ImageInput.open( inputPath )

    # get image specs
    inputImageSpec = inputImage.spec()
    type = inputImageSpec.format.basetype
    width = inputImageSpec.width
    height = inputImageSpec.height
    channels = inputImageSpec.nchannels

    sourceData = inputImage.read_image(type)

    inputImage.close()

    return(sourceData, type, width, height, channels)

def writePixelArray(outputPath, pixels, type, width, height, channels):
    # set image specs
    outputSpec = oiio.ImageSpec()
    outputSpec.set_format( oiio.FLOAT )
    outputSpec.width = width
    outputSpec.height = height
    outputSpec.nchannels = channels

    outputImage = oiio.ImageOutput.create(outputPath)
    outputImage.open (outputPath, outputSpec, oiio.Create)

    outputImage.write_image(outputSpec.format, pixels)
    outputImage.close()

def filterImageWithCLF(inputPath, outputPath, clf, normalize=False):
    print( "filterImageWithCLF" )

    # Get the input image pixel array
    print( "Grabbing data from %s" % inputPath)
    pixels, type, width, height, channels = readPixelArray(inputPath)
    print( type, width, height, type, channels )

    # Buffer for the processed pixels
    processedPixels = array.array("f", "\0" * width * height * channels * 4)

    # Process
    for i in range(width):
        for j in range(height):
            index = (j*width + i)*channels
            ovalue = list(pixels[index:index+3])

            if normalize:
                # Normalize integer data
                # OIIO treats 10 or 12 bit data as 16 bits, for our purposes
                if type == oiio.BASETYPE.UINT16:
                    ovalue = map(lambda x: x/float(pow(2,16)-1), ovalue)

            pvalue = clf.process(ovalue, verbose=False)
            print( "Processed %04d, %04d : %s -> %s" % (i, j, ovalue, pvalue))

            processedPixels[index + 0] = pvalue[0]
            processedPixels[index + 1] = pvalue[1]
            processedPixels[index + 2] = pvalue[2]

    # Write the processed pixel array to the output
    writePixelArray(outputPath, processedPixels, type, width, height, channels)

def loadCLF(clfPath):
    # Open the Common LUT Format file
    pl = clf.ProcessList(clfPath)
    print( pl.getName() )
    return pl

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

    p = optparse.OptionParser(description='Filter an image using the Common LUT Format',
                                prog='clfFilter',
                                version='clfFilter',
                                usage='%prog [options]')

    p.add_option('--input', '-i', default=None)
    p.add_option('--output', '-o', default=None)
    p.add_option('--clf', '-c', default=None)
    p.add_option('--ex1', action="store_true")
    p.add_option('--dontNormalize', '-d', action="store_true")

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfPath = options.clf
    inputPath = options.input
    outputPath = options.output
    ex1 = options.ex1
    normalize = not options.dontNormalize

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
    clf = None
    if clfPath != None:
        clf = loadCLF(clfPath)
    elif ex1 != None:
        clf = createCLFExample1()

    if clf != None and outputPath != None and inputPath != None:
        filterImageWithCLF(inputPath, outputPath, clf, normalize)

# main

if __name__ == '__main__':
    main()
