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
from Common import *

class Registry:
    "A registry for LUT format IO functionality"

    # LutFormat registry
    lutFormats = {}

    @staticmethod
    def registerLutFormat(name, cls):
        if cls.extensions():
            #print( "LutFormatRegistry register : %s, %s" % (name, cls))
            Registry.lutFormats[name] = cls

    @staticmethod
    def getFormats():
        return Registry.lutFormats.values()

    @staticmethod
    def read(lutPath, 
             inverse=False, 
             interpolation='linear',
             inversesUseIndexMaps=True, 
             inversesUseHalfDomain=True,
             returnProcessNodes=False):
        extension = os.path.splitext(lutPath)[1][1:].strip().lower()

        #print( "Reading lut %s" % lutPath )

        # Step through each of the lut format classes
        for cls in Registry.getFormats():
            #print( "Lut format class %s can load extensions %s" % (
            #    cls, cls.extensions()) )

            # If the class can read files and it can read this extension
            # Note: More than one format may use the same extension
            if extension in cls.extensions() and cls.canRead(extension):
                #print( "Reading lut %s" % lutPath )

                # Call reader class read method
                lutProcessNodes = cls.read(lutPath, inverse, interpolation, 
                    inversesUseIndexMaps, inversesUseHalfDomain)

                #print( "Read lut %s" % lutPath )

                # Create the CLF/ProcessList
                if lutProcessNodes:
                    # Return the list of ProcessNodes
                    if returnProcessNodes:
                        return lutProcessNodes

                    else:
                    # Wrap the ProcessNodes in a ProcessList
                        # Initialize
                        pl = clf.ProcessList()

                        # Populate
                        pl.setID('Converted lut')
                        pl.setCompCLFversion(1.0)
                        pl.setName('Converted lut')

                        for lutpn in lutProcessNodes:
                            pl.addProcess(lutpn)

                        return pl

                # Or warn the user and keep trying
                else:
                    print( "Reading failed for some reason. We'll keep trying." )

        print( "Reading LUTs in the %s format is not currently supported" % extension )
        return None
    # read

    @staticmethod
    def write(processList,
              lutPath,
              lutDataFormat=LUTDATAFORMAT_1D,
              lutResolution1d=1024,
              lutResolution3d=33,
              lutResolution1d3d1d=[1024,33,2],
              inputMin=0.0,
              inputMax=1.0,
              shaperIn=['linear',0.0,1.0],
              shaperOut=['linear',0.0,1.0]):
        extension = os.path.splitext(lutPath)[1][1:].strip().lower()
        #print( "Registry::write - %s, %s" % (lutPath, extension) )

        #print( "Writing lut %s, file format %s, data format %s" % (lutPath, lutDataFormat) )

        # XXX
        # Should use either the LUTDATAFORMAT* constants here or the IO_CAPABILITY_* constants in LutFormat
        if lutDataFormat == LUTDATAFORMAT_1D:
            writeStyle = IO_CAPABILITY_WRITE_1D
        elif lutDataFormat == LUTDATAFORMAT_3D:
            writeStyle = IO_CAPABILITY_WRITE_3D
        else:
            writeStyle = IO_CAPABILITY_WRITE_1D3D1D

        # XXX
        # Should we have a 'default' writeStyle that allows the format to choose the highest quality
        # option?

        # Step through each of the lut format classes
        for cls in Registry.getFormats():
            #print( "Lut format class %s can write extensions %s" % (
            #    cls, cls.extensions()) )

            # If the class can write files and it can write this extension
            # Note: More than one format may use the same extension
            if extension in cls.extensions() and cls.isCapable(writeStyle, extension):
                #print( "Writing lut %s, data format %s" % (lutPath, lutDataFormat) )

                # Call reader class read method
                wrote = cls.write(processList,
                         lutPath,
                         writeStyle,
                         lutResolution1d,
                         lutResolution3d,
                         lutResolution1d3d1d,
                         inputMin,
                         inputMax,
                         shaperIn,
                         shaperOut)

                if wrote:
                    #print( "Wrote lut %s" % lutPath )
                    return
                else:
                    print( "Error writing lut %s. We'll keep trying." % lutPath)

        print( "Writing LUTs in the %s format is not currently supported" % extension )
        return None
    # write   
# Registry

