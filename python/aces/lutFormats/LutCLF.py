#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import clf

import Sampling
import LutFormat

class LutFormatCLF(LutFormat.LutFormat):
    "A class that implements IO for the Academy / ASC Common LUT Format .clf"

    # Descriptions, extensions and capabilities for this class
    formatType = "Academy / ASC Common LUT Format"
    formats = [
        ["clf - 1D, 3D or 1D/3D LUT format",
         "clf",
         [LutFormat.IO_CAPABILITY_WRITE_1D3D1D]
         ]
        ]

    def __init__(self): 
        "%s - Initialize the standard class variables" % LutFormatCLF.formatType
        LutFormat.LutFormat.__init__(self)
    # __init__

    @classmethod
    def write1D3D1D(cls,
                    lutPath,
                    samples1dIn,
                    lutResolution1dIn,
                    inputMin,
                    inputMax,
                    samples3d,
                    lutResolution3d,
                    samples1dOut,
                    lutResolution1dOut,
                    outputMin,
                    outputMax):
        #print( "%s format write 1D 3D 1D - %s" % (LutFormatCLF.formatType, lutPath) )
        return LutFormatCLF.writeCLF1D3D1D(lutPath,
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

    @staticmethod
    def writeCLF1D3D1D(lutPath,
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
                #print( "Generating inverse of 1D LUT using Index Maps")
                lutpnInverses = Sampling.generateLUT1DInverseIndexMap([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax)
            elif inversesUseHalfDomain:
                #print( "Generating full half-domain inverse of 1D LUT")
                lutpnInverses = Sampling.generateLUT1DInverseHalfDomain([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax, rawHalfs=True)
            else:
                #print( "Generating resampled inverse of 1D LUT")
                lutpnInverses = Sampling.generateLUT1DInverseResampled([lutResolution1dIn, 3], samples1dIn, inputMin, inputMax)            
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

        return True
    # writeCLF1D3D1D

# LutFormatCLF
