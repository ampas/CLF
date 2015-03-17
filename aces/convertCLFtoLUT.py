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
import convertLUTtoCLF

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

    #print( ' '.join(map(str, resolution)) )

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


def write_CSP_1d_3d(lutPath,
                    samples1dIn,
                    lutResolution1dIn,
                    inputMin,
                    inputMax,
                    samples3d,
                    lutResolution3d):

    #print( ' '.join(map(str, lutResolution3d)) )

    with open(lutPath, 'w') as fp:
        fp.write('CSPLUTV100\n')
        fp.write('3D\n')
        fp.write('\n')
        fp.write('BEGIN METADATA\n')
        fp.write('END METADATA\n')

        fp.write('\n')

        for c in range(3):
            fp.write('%d\n' % lutResolution1dIn)

            for s in range(lutResolution1dIn):
                value = (float(s)/(lutResolution1dIn-1))*(
                    inputMax - inputMin) + inputMin
                fp.write('%f ' % value)
            fp.write('\n')

            for s in range(lutResolution1dIn):
                fp.write('%f ' % samples1dIn[s*3 + c])
            fp.write('\n')

        fp.write('\n')

        fp.write('%s\n' % ' '.join(map(str, lutResolution3d)) )
 
        # Note: CSP increments red fastest
        for b in range(lutResolution3d[0]):
            for g in range(lutResolution3d[1]):
                for r in range(lutResolution3d[2]):
                    entry = " ".join(map(lambda x : "%3.6f" % x, samples3d[r][g][b]))
                    fp.write('%s\n' % entry)


def write_CLF_1d_3d_1d(lutPath,
                       samples1dIn,
                       lutResolution1dIn,
                       inputMin,
                       inputMax,
                       samples3d,
                       lutResolution3d,
                       samples1dOut,
                       lutResolution1dOut,
                       outputMin,
                       outputMax,
                       inversesUseIndexMaps=True,
                       inversesUseHalfDomain=True):

    lutpns = []

    # Create the input shaper
    if samples1dIn:
        if inversesUseIndexMaps:
            print( "Generating inverse of 1D LUT using Index Maps")
            lutpnInverses = convertLUTtoCLF.generateLUT1DInverseIndexMap([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax)
        elif inversesUseHalfDomain:
            print( "Generating full half-domain inverse of 1D LUT")
            lutpnInverses = convertLUTtoCLF.generateLUT1DInverseHalfDomain([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax, rawHalfs=True)
        else:
            print( "Generating resampled inverse of 1D LUT")
            lutpnInverses = convertLUTtoCLF.generateLUT1DInverseResampled([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax)            
        lutpns.extend(lutpnInverses)

    # Create the 3D LUT
    clfSamples = [0.0]*(lutResolution3d[0]*lutResolution3d[1]*lutResolution3d[2])*3
    index = 0
    for r in range(lutResolution3d[0]):
        for g in range(lutResolution3d[1]):
            for b in range(lutResolution3d[2]):
                for c in range(3):
                    clfSamples[index] = samples3d[r][g][b][c]
                    index += 1

    interpolation = 'trilinear'
    lut3dpn = clf.LUT3D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut3d", "lut3d", interpolation=interpolation)
    lut3dpn.setArray([lutResolution3d[0], lutResolution3d[1], lutResolution3d[2]], clfSamples)

    lutpns.append(lut3dpn)

    # Create the output shaper
    if samples1dOut:
        interpolation = 'linear'
        lutpn = clf.LUT1D(clf.bitDepths["FLOAT16"], clf.bitDepths["FLOAT16"], "lut1d", "lut1d", interpolation=interpolation)
        lutpn.setArray(3, samples1dOut)

        lutpns.append(lutpn)

    # Wrap in a ProcessList and write to disk
    pl = clf.ProcessList()

    # Populate
    pl.setID('Converted lut')
    pl.setCompCLFversion(1.0)
    pl.setName('Converted lut')

    for lutpn in lutpns:
        pl.addProcess(lutpn)

    # Write CLF to disk
    pl.writeFile(lutPath) 

def write_CTL_1d(filename, 
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
        fp.write('// %d x %d 1D LUT generated by "convertCLFtoLUT"\n' % (
          entries, components))
        fp.write('\n')
        fp.write('const float min1d = %3.9f;\n' % from_min)
        fp.write('const float max1d = %3.9f;\n' % from_max)
        fp.write('\n')

        # Write LUT
        if components == 1:
          fp.write('const float lut[] = {\n')
          for i in range(0, entries):
              fp.write('%s' % data[i * channels])
              if i != (entries-1):
                fp.write(',')
              fp.write('\n')
          fp.write('};\n')
          fp.write('\n')
        else:
          for j in range(components):
            fp.write('const float lut%d[] = {\n' % j)
            for i in range(0, entries):
                fp.write('%s' % data[i * channels])
                if i != (entries-1):
                  fp.write(',')
                fp.write('\n')
            fp.write('};\n')
            fp.write('\n')

        fp.write('void main\n')
        fp.write('(\n')
        fp.write('  input varying float rIn,\n')
        fp.write('  input varying float gIn,\n')
        fp.write('  input varying float bIn,\n')
        fp.write('  input varying float aIn,\n')
        fp.write('  output varying float rOut,\n')
        fp.write('  output varying float gOut,\n')
        fp.write('  output varying float bOut,\n')
        fp.write('  output varying float aOut\n')
        fp.write(')\n')
        fp.write('{\n')
        fp.write('  float r = rIn;\n')
        fp.write('  float g = gIn;\n')
        fp.write('  float b = bIn;\n')
        fp.write('\n')
        fp.write('  // Apply LUT\n')
        if components == 1:
          fp.write('  r = lookup1D(lut, min1d, max1d, r);\n')
          fp.write('  g = lookup1D(lut, min1d, max1d, g);\n')
          fp.write('  b = lookup1D(lut, min1d, max1d, b);\n')
        elif components == 3:
          fp.write('  r = lookup1D(lut0, min1d, max1d, r);\n')
          fp.write('  g = lookup1D(lut1, min1d, max1d, g);\n')
          fp.write('  b = lookup1D(lut2, min1d, max1d, b);\n')          
        fp.write('\n')
        fp.write('  rOut = r;\n')
        fp.write('  gOut = g;\n')
        fp.write('  bOut = b;\n')
        fp.write('  aOut = aIn;\n')
        fp.write('}\n')

def write_CTL_3d(filename, 
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

    with open(filename, 'w') as fp:
        fp.write('// %d x %d x %d 3D LUT generated by "convertCLFtoLUT"\n' % (
          resolution[0], resolution[1], resolution[2]))
        fp.write('\n')
        fp.write('const float min3d[3] = {%3.9f, %3.9f, %3.9f};\n' % (
            from_min, from_min, from_min))
        fp.write('const float max3d[3] = {%3.9f, %3.9f, %3.9f};\n' % (
            from_max, from_max, from_max))
        fp.write('\n')

        # Write LUT
        fp.write('const float cube[%d][%d][%d][3] = \n' % (
            resolution[0], resolution[1], resolution[2]))

        fp.write('{\n')
        for r in range(resolution[0]):
            fp.write('\t{\n')
            for g in range(resolution[1]):
                fp.write('\t\t{ ')
                for b in range(resolution[2]):
                    fp.write('{')
                    entry = ", ".join(map(lambda x : "%3.6f" % x, data[r][g][b]))
                    fp.write('%s' % entry)
                    fp.write('}')
                    if b != resolution[2]-1:
                        fp.write(',\n\t\t  ')
                    else:
                        fp.write('\n ')
                fp.write('}')
                if g != resolution[1]-1:
                    fp.write(',\n')
                else:
                    fp.write('\n')
            fp.write('\t}')
            if r != resolution[0]-1:
                fp.write(', ')
            else:
                fp.write('\n')
        fp.write('};\n')
        fp.write('\n')

        fp.write('void main\n')
        fp.write('(\n')
        fp.write('  input varying float rIn,\n')
        fp.write('  input varying float gIn,\n')
        fp.write('  input varying float bIn,\n')
        fp.write('  input varying float aIn,\n')
        fp.write('  output varying float rOut,\n')
        fp.write('  output varying float gOut,\n')
        fp.write('  output varying float bOut,\n')
        fp.write('  output varying float aOut\n')
        fp.write(')\n')
        fp.write('{\n')
        fp.write('  float r = rIn;\n')
        fp.write('  float g = gIn;\n')
        fp.write('  float b = bIn;\n')
        fp.write('\n')
        fp.write('  // Apply LUT\n')
        fp.write('  lookup3D_f(cube, min3d, max3d, r, g, b, r, g, b);\n')
        fp.write('\n')
        fp.write('  rOut = r;\n')
        fp.write('  gOut = g;\n')
        fp.write('  bOut = b;\n')
        fp.write('  aOut = aIn;\n')
        fp.write('}\n')


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

    print( "Writing LUT : %s" % filename )

    ocioFormatsToExtensions = {'cinespace' : 'csp',
                               'flame'     : '3dl',
                               'icc'       : 'icc',
                               'houdini'   : 'lut',
                               'lustre'    : '3dl',
                               'ctl'       : 'ctl'}

    if format in ocioFormatsToExtensions:
        if ocioFormatsToExtensions[format] == 'csp':
            write_CSP_1d(filename,
                         from_min,
                         from_max,
                         data,
                         data_entries,
                         data_channels,
                         lut_components)
        elif ocioFormatsToExtensions[format] == 'ctl':
            write_CTL_1d(filename,
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
                               'lustre'    : '3dl',
                               'ctl'       : 'ctl'}

    print( "Writing LUT : %s" % filename )

    if format in ocioFormatsToExtensions:
        if ocioFormatsToExtensions[format] == 'csp':
            write_CSP_3d(filename,
                         from_min,
                         from_max,
                         data,
                         data_resolution)
        elif ocioFormatsToExtensions[format] == 'ctl':
            write_CTL_3d(filename,
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


def write_1d_3d_1d(lutPath,
                   samples1dIn,
                   lutResolution1dIn,
                   inputMin,
                   inputMax,
                   samples3d,
                   lutResolution3d,
                   samples1dOut,
                   lutResolution1dOut,
                   outputMin,
                   outputMax,
                   lutFileFormat):
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

    print( "Writing LUT : %s" % lutPath )

    ocioFormatsToExtensions = {'cinespace' : 'csp',
                               'clf'       : 'clf'}

    #print( lutPath )
    #print( lutFileFormat )

    if lutFileFormat in ocioFormatsToExtensions:
        if ocioFormatsToExtensions[lutFileFormat] == 'csp':
            if samples1dOut == None:
                write_CSP_1d_3d(lutPath,
                                samples1dIn,
                                lutResolution1dIn,
                                inputMin,
                                inputMax,
                                samples3d,
                                lutResolution3d)
            else:
                print( "write_1d_3d_1d - Cinespace (.csp) does not support an output shaper")
        elif ocioFormatsToExtensions[lutFileFormat] == 'clf':
            write_CLF_1d_3d_1d(lutPath,
                               samples1dIn,
                               lutResolution1dIn,
                               inputMin,
                               inputMax,
                               samples3d,
                               lutResolution3d,
                               samples1dOut,
                               lutResolution1dOut,
                               outputMin,
                               outputMax)

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

def sampleAndWrite1D3D1D(processList,
                         lutPath,
                         lutFileFormat,
                         lutResolution1d3d1d,
                         shaperIn,
                         shaperOut):
    print( "sampleAndWrite1D3D1D" )

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
        print( "sampleAndWrite1D3D1D - create input shaper" )

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
    print( "sampleAndWrite1D3D1D - create 3D LUT" )

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
        print( "sampleAndWrite1D3D1D - create output shaper" )

        samples1dOut = [0.0]*lutResolution1dOut*3
        for lutIndex in range(lutResolution1dOut):
            sampleValue = float(lutIndex)/(lutResolution1dOut-1)

            lutValue = shaperInPLInverse.process([sampleValue]*3)

            samples1dOut[lutIndex*3:(lutIndex+1)*3] = lutValue
    else:
        samples1dOut = None

    #
    # Write 1D 3D 1D LUT
    #
    write_1d_3d_1d(lutPath,
                   samples1dIn,
                   lutResolution1dIn,
                   inputMin,
                   inputMax,
                   samples3d,
                   lutResolution3d,
                   samples1dOut,
                   lutResolution1dOut,
                   outputMin,
                   outputMax,
                   lutFileFormat)

def convertCLFtoLUT(clfPath,
                    lutPath,
                    lutFileFormat,
                    lutDataFormat=LUTDATAFORMAT_1D,
                    lutResolution1d=1024,
                    lutResolution3d=33,
                    lutResolution1d3d1d=[1024,33,2],
                    inputMin=0.0,
                    inputMax=1.0,
                    shaperIn=['linear',0.0,1.0],
                    shaperOut=['linear',0.0,1.0]):
    
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
                             lutResolution1d3d1d,
                             shaperIn,
                             shaperOut)
    else:
        print( "Unsupported LUT data format : %s" % lutDataFormat)

def main():
    import optparse

    usage  = '%prog [options]\n'
    usage += '\n'
    usage += 'Command line examples'
    usage += '\n'
    usage += 'Convert CLF to CLF   : convertCLFtoLUT --generate1d3d1d --shaperIn linear 0 1 -f clf --shaperOut linear 0 1 --lutResolution1d3d1d 11 33 11 -c complex.clf -l simplified.clf'
    usage += '\n'
    usage += 'Convert CLF to CSP   : convertCLFtoLUT --generate1d3d1d --shaperIn log2 -8.5 4 -f cinespace --lutResolution1d3d1d 1024 33 0 -c complex_hdr_tonemap.clf -l complex_hdr_tonemap.csp'
    usage += '\n'
    usage += 'Convert CLF to spi1d : convertCLFtoLUT --generate1d --lutResolution1d 1024 -c lut1d.clf -l lut1d.spi1d'
    usage += '\n'
    usage += 'Convert CLF to spi3d : convertCLFtoLUT --generate3d --lutResolution3d 33 33 33 -c lut3d.clf -l lut3d.spi3d'
    usage += '\n'
    usage += 'Convert CLF to CTL   : convertCLFtoLUT --generate3d --lutResolution3d 33 33 33 -c lut3d.clf -l lut3d.ctl -f ctl'
    usage += '\n'

    p = optparse.OptionParser(description='Convert from the Common LUT Format to other LUT formats',
                                prog='convertLUTtoCLF',
                                version='0.01',
                                usage=usage)

    p.add_option('--clf', '-c', default=None)
    p.add_option('--lut', '-l', default=None)
    p.add_option('--lutResolution1d', '', type='int', default=1024)
    p.add_option('--lutResolution3d', '', type='int', default=33)
    p.add_option('--lutResolution1d3d1d', '', type='int', nargs=3, 
        action='append')
    p.add_option('--inputMinValue', '', type='float', default=0.0)
    p.add_option('--inputMaxValue', '', type='float', default=1.0)
    p.add_option('--generate1d', '', action='store_true')
    p.add_option('--generate3d', '', action='store_true')
    p.add_option('--generate1d3d1d', '', action='store_true')
    p.add_option('--format', '-f', default=None)
    p.add_option('--shaperIn', '', type='string', nargs=3,
                 action='append', help="3 values: shaperType (linear, log2) min max")

    p.add_option('--shaperOut', '', type='string', nargs=3,
                 action='append', help="3 values: shaperType (linear, log2) min max")

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
    generate1d3d1d = options.generate1d3d1d is True

    if options.shaperIn is not None:
        #print( options.shaperIn )
        shaperInType = options.shaperIn[0][0]
        shaperInMin = float(options.shaperIn[0][1])
        shaperInMax = float(options.shaperIn[0][2])
    else:
        (shaperInType, shaperInMin, shaperInMax) = (None,0.0,1.0)

    if options.shaperOut is not None:
        #print( options.shaperIn )
        shaperOutType = options.shaperOut[0][0]
        shaperOutMin = float(options.shaperOut[0][1])
        shaperOutMax = float(options.shaperOut[0][2])
    else:
        (shaperOutType, shaperOutMin, shaperOutMax) = (None,0.0,1.0)

    if options.lutResolution1d3d1d is not None:
        #print( options.shaperIn )
        shaperInLutResolution = int(options.lutResolution1d3d1d[0][0])
        lutResolution3d = int(options.lutResolution1d3d1d[0][1])
        shaperOutLutResolution = int(options.lutResolution1d3d1d[0][2])
    else:
        (shaperInLutResolution, lutResolution3d, shaperOutLutResolution) = (1024, 33, 2)

    # Figure out the data format
    lutDataFormat = LUTDATAFORMAT_1D
    if generate1d:
        lutDataFormat = LUTDATAFORMAT_1D
    elif generate3d:
        lutDataFormat = LUTDATAFORMAT_3D
    elif generate1d3d1d:
        lutDataFormat = LUTDATAFORMAT_1D_3D_1D

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    print( "%25s : %s" % ("clf", clfPath))
    print( "%25s : %s" % ("lut", lutPath))
    print( "%25s : %s" % ("file format", lutFileFormat))
    print( "%25s : %s" % ("data format", lutDataFormat))
    print( "%25s : %s" % ("1D lut resolution", lutResolution1d))
    print( "%25s : %s" % ("3D lut resolution", lutResolution3d))
    print( "%25s : %s" % ("1D/3D/1D lut resolution", "%s, %s, %s" % (shaperInLutResolution, lutResolution3d, shaperOutLutResolution)))
    print( "%25s : %s" % ("min input value", inputMinValue))
    print( "%25s : %s" % ("max input value", inputMaxValue))
    print( "%25s : %s" % ("shaper in", "%s, %s, %s" % (shaperInType, shaperInMin, shaperInMax)))
    print( "%25s : %s" % ("shaper out", "%s, %s, %s" % (shaperOutType, shaperOutMin, shaperOutMax)))

    # Set the 3D LUT resolution
    lutResolution3d = [lutResolution3d]*3

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
                        [shaperInLutResolution, lutResolution3d, shaperOutLutResolution],
                        inputMinValue,
                        inputMaxValue,
                        [shaperInType, shaperInMin, shaperInMax],
                        [shaperOutType, shaperOutMin, shaperOutMax])

# main

if __name__ == '__main__':
    main()
