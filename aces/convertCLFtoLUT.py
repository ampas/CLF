#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to convert from CLF to different LUT formats
"""

import array
import math
import os
import sys

import clf

LUTDATAFORMAT_UNKNOWN = 'Unknown'
LUTDATAFORMAT_1D = '1D'
LUTDATAFORMAT_3D = '3D'
LUTDATAFORMAT_1D_3D_1D = '1D_3D_1D'

def write_SPI_1d(filename, 
                 from_min, 
                 from_max, 
                 data, 
                 entries, 
                 channels, 
                 components=3):
    """
    Object description.

    Credit to *Alex Fry* for the original single channel version of the spi1d
    writer.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    # May want to use fewer components than there are channels in the data
    # Most commonly used for single channel LUTs
    components = min(3, components, channels)

    with open(filename, 'w') as fp:
        fp.write('Version 1\n')
        fp.write('From %f %f\n' % (from_min, from_max))
        fp.write('Length %d\n' % entries)
        fp.write('Components %d\n' % components)
        fp.write('{\n')
        for i in range(0, entries):
            entry = ''
            for j in range(0, components):
                entry = '%s %s' % (entry, data[i * channels + j])
            fp.write('        %s\n' % entry)
        fp.write('}\n')

def write_SPI_3d(filename, 
                 from_min, 
                 from_max, 
                 data, 
                 resolution):
    """
    Object description.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    print( ' '.join(map(str, resolution)) )

    with open(filename, 'w') as fp:
        fp.write('SPILUT 1.0\n')
        fp.write('3 3\n')
        fp.write('%s\n' % ' '.join(map(str, resolution)) )
 
        for r in range(resolution[0]):
            for g in range(resolution[1]):
                for b in range(resolution[2]):
                    entry  = " ".join(map(str,[r,g,b]))
                    entry += " "
                    entry += " ".join(map(str, data[r][g][b]))
                    fp.write('%s\n' % entry)

def write_CSP_1d(filename, 
                 from_min, 
                 from_max, 
                 data, 
                 entries, 
                 channels, 
                 components=3):
    """
    Object description.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    # May want to use fewer components than there are channels in the data
    # Most commonly used for single channel LUTs
    components = min(3, components, channels)

    with open(filename, 'w') as fp:
        fp.write('CSPLUTV100\n')
        fp.write('1D\n')
        fp.write('\n')
        fp.write('BEGIN METADATA\n')
        fp.write('END METADATA\n')

        fp.write('\n')

        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')
        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')
        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')

        fp.write('\n')

        fp.write('%d\n' % entries)
        if components == 1:
          for i in range(0, entries):
              entry = ''
              for j in range(3):
                  entry = '%s %3.6f' % (entry, data[i * channels])
              fp.write('%s\n' % entry)
        else:
          for i in range(entries):
              entry = ''
              for j in range(components):
                  entry = '%s %3.6f' % (entry, data[i * channels + j])
              fp.write('%s\n' % entry)
        fp.write('\n')

def write_CSP_3d(filename, 
                 from_min, 
                 from_max, 
                 data, 
                 resolution):
    """
    Object description.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    print( ' '.join(map(str, resolution)) )

    with open(filename, 'w') as fp:
        fp.write('CSPLUTV100\n')
        fp.write('3D\n')
        fp.write('\n')
        fp.write('BEGIN METADATA\n')
        fp.write('END METADATA\n')

        fp.write('\n')

        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')
        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')
        fp.write('2\n')
        fp.write('%f %f\n' % (from_min, from_max))
        fp.write('0.0 1.0\n')

        fp.write('\n')

        fp.write('%s\n' % ' '.join(map(str, resolution)) )
 
        # Note: CSP increments red fastest
        for b in range(resolution[0]):
            for g in range(resolution[1]):
                for r in range(resolution[2]):
                    entry = " ".join(map(lambda x : "%3.6f" % x, data[r][g][b]))
                    fp.write('%s\n' % entry)


def write_1d(filename, 
             from_min, 
             from_max, 
             data, 
             data_entries, 
             data_channels, 
             lut_components=3,
             format='spi1d'):
    """
    Object description.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    ocioFormatsToExtensions = {'cinespace' : 'csp',
                               'flame'     : '3dl',
                               'icc'       : 'icc',
                               'houdini'   : 'lut',
                               'lustre'    : '3dl'}

    if format in ocioFormatsToExtensions:
        if ocioFormatsToExtensions[format] == 'csp':
            write_CSP_1d(filename,
                         from_min,
                         from_max,
                         data,
                         data_entries,
                         data_channels,
                         lut_components)
    else:
        write_SPI_1d(filename,
                     from_min,
                     from_max,
                     data,
                     data_entries,
                     data_channels,
                     lut_components)

def write_3d(filename, 
             from_min, 
             from_max, 
             data, 
             data_resolution, 
             format='spi1d'):
    """
    Object description.

    Parameters
    ----------
    parameter : type
        Parameter description.

    Returns
    -------
    type
         Return value description.
    """

    ocioFormatsToExtensions = {'cinespace' : 'csp',
                               'flame'     : '3dl',
                               'icc'       : 'icc',
                               'houdini'   : 'lut',
                               'lustre'    : '3dl'}

    if format in ocioFormatsToExtensions:
        if ocioFormatsToExtensions[format] == 'csp':
            write_CSP_3d(filename,
                         from_min,
                         from_max,
                         data,
                         data_resolution)
    else:
        write_SPI_3d(filename,
                     from_min,
                     from_max,
                     data,
                     data_resolution)

def sampleAndWrite1D(processList,
                     lutPath,
                     lutFileFormat,
                     lutResolution1d,
                     inputMin,
                     inputMax):
    print( "sampleAndWrite1D" )

    # Sample all values in 1D range
    samples = [0.0]*lutResolution1d*3
    for lutIndex in range(lutResolution1d):

        sampleValue = float(lutIndex)/(lutResolution1d-1)*(
            inputMax - inputMin) + inputMin
        lutValue = processList.process([sampleValue]*3)

        samples[lutIndex*3:(lutIndex+1)*3] = lutValue

    # Write 1D LUT
    write_1d(lutPath,
             inputMin,
             inputMax,
             samples,
             lutResolution1d,
             3,
             3,
             lutFileFormat)

def sampleAndWrite3D(processList,
                     lutPath,
                     lutFileFormat,
                     lutResolution3d,
                     inputMin,
                     inputMax):
    print( "sampleAndWrite3D" )

    # Sample all values in 3D range
    #sample = [0.0,0.0,0.0]
    #samples1d = [sample]*lutResolution3d[0]
    #samples2d = [samples1d]*lutResolution3d[1]
    #samples   = [samples2d]*lutResolution3d[2]
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

    # Write 3D LUT
    write_3d(lutPath,
             inputMin,
             inputMax,
             samples,
             lutResolution3d,
             lutFileFormat)

def sampleAndWrite1D3D1D(processList,
                         lutPath,
                         lutFileFormat,
                         lutResolution1d3d1d,
                         inputMin,
                         inputMax):
    print( "sampleAndWrite3D" )


def convertCLFtoLUT(clfPath,
                    lutPath,
                    lutFileFormat,
                    lutDataFormat=LUTDATAFORMAT_1D,
                    lutResolution1d=1024,
                    lutResolution3d=33,
                    inputMin=0.0,
                    inputMax=1.0):
    
    # Load CLF
    print( "Reading CLF : %s" % clfPath )
    processList = clf.ProcessList(clfPath)

    # For each data format, do something different
    if lutDataFormat == LUTDATAFORMAT_1D:
        sampleAndWrite1D(processList,
                         lutPath,
                         lutFileFormat,
                         lutResolution1d,
                         inputMin,
                         inputMax)
    elif lutDataFormat == LUTDATAFORMAT_3D:
        sampleAndWrite3D(processList,
                         lutPath,
                         lutFileFormat,
                         lutResolution3d,
                         inputMin,
                         inputMax)
    elif lutDataFormat == LUTDATAFORMAT_1D_3D_1D:
        sampleAndWrite1D3D1D(processList,
                             lutPath,
                             lutFileFormat,
                             lutResolution1d,
                             inputMin,
                             inputMax)
    else:
        print( "Unsupported LUT data format : %s" % lutDataFormat)

def main():
    import optparse

    p = optparse.OptionParser(description='Convert a LUT to the Common LUT Format',
                                prog='convertLUTtoCLF',
                                version='0.01',
                                usage='%prog [options]')

    p.add_option('--clf', '-c', default=None)
    p.add_option('--lut', '-l', default=None)
    p.add_option('--lutResolution1d', '', type='int', default=1024)
    p.add_option('--lutResolution3d', '', type='int', default=33)
    p.add_option('--inputMinValue', '', type='float', default=0.0)
    p.add_option('--inputMaxValue', '', type='float', default=1.0)
    p.add_option('--generate1d', '', action='store_true')
    p.add_option('--generate3d', '', action='store_true')
    p.add_option('--format', '-f', default=None)

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfPath = options.clf
    lutPath = options.lut
    lutFileFormat = options.format
    lutResolution1d = int(options.lutResolution1d)
    lutResolution3d = int(options.lutResolution3d)
    inputMinValue = float(options.inputMinValue)
    inputMaxValue = float(options.inputMaxValue)
    generate1d = options.generate1d is True
    generate3d = options.generate3d is True

    # Figure out the data format
    lutDataFormat = LUTDATAFORMAT_1D
    if generate1d:
        lutDataFormat = LUTDATAFORMAT_1D
    elif generate3d:
        lutDataFormat = LUTDATAFORMAT_3D

    # Set the 3D LUT resolution
    lutResolution3d = [lutResolution3d]*3

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    print( "%20s : %s" % ("clf", clfPath))
    print( "%20s : %s" % ("lut", lutPath))
    print( "%20s : %s" % ("file format", lutFileFormat))
    print( "%20s : %s" % ("data format", lutDataFormat))
    print( "%20s : %s" % ("1D lut resolution", lutResolution1d))
    print( "%20s : %s" % ("3D lut resolution", lutResolution3d))
    print( "%20s : %s" % ("min input value", inputMinValue))
    print( "%20s : %s" % ("max input value", inputMaxValue))

    #
    # Run 
    #
    if clfPath != None and lutPath != None:
        convertCLFtoLUT(clfPath,
                        lutPath,
                        lutFileFormat,
                        lutDataFormat,
                        lutResolution1d,
                        lutResolution3d,
                        inputMinValue,
                        inputMaxValue)

# main

if __name__ == '__main__':
    main()
