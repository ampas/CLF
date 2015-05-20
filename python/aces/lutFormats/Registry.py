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

