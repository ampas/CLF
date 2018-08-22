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

from itertools import chain

from Registry import Registry
import Sampling
from Common import *

class LutFormatMeta(type):
    "Metaclass for LUT formats that will register with LutRegistry"
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        Registry.registerLutFormat(name, cls)
        return cls
# LUTFormatMeta

#
# LutFormat
#
class LutFormat():
    "The base class for classes that implement LUT Format IO"

    # Ensures that this class and children will show up in the LUT Registry
    __metaclass__ = LutFormatMeta

    # Static class variables
    formatType = "LutFormat base"

    # Formats should be a list of tuples
    # Each tuple should have a description string, an extension string and
    # the list of reading and writing capabilities implemented for that extension / format
    formats = []

    def __init__(self):
        "%s - Initialize the standard class variables" % LutFormat.formatType
    # __init__

    # Descriptions
    @classmethod
    def descriptions(cls):
        return [f[0] for f in cls.formats]

    # Extensions
    @classmethod
    def extensions(cls):
        return [f[1].lower() for f in cls.formats]

    # Capabilities
    @classmethod
    def capabilities(cls, extension=None):
        if extension:
            caps = [f[2] for f in cls.formats if f[1].lower() == extension.lower()]
        else:
            caps = [f[2] for f in cls.formats]
        return set(list(chain.from_iterable(caps)))

    # Query capabilities of class
    @classmethod
    def isCapable(cls, capability, extension=None):
        return capability in cls.capabilities(extension)

    @classmethod
    def canRead(cls, extension=None):
        return cls.isCapable(IO_CAPABILITY_READ, extension)

    @classmethod
    def canWrite1D(cls, extension=None):
        return cls.isCapable(IO_CAPABILITY_WRITE_1D, extension)
    @classmethod
    def canWrite3D(cls, extension=None):
        return cls.isCapable(IO_CAPABILITY_WRITE_3D, extension)
    @classmethod
    def canWrite1D3D1D(cls, extension=None):
        return cls.isCapable(IO_CAPABILITY_WRITE_1D3D1D, extension)

    # Methods covering reading and writing
    @classmethod
    def read(cls,
             lutPath,
             inverse=False,
             interpolation='linear',
             inversesUseIndexMaps=True,
             inversesUseHalfDomain=True):
        print( "Format %s can not be read" % self.formatType )
        return False

    @classmethod
    def write(cls,
              processList,
              lutPath,
              lutStyle=IO_CAPABILITY_WRITE_1D,
              lutResolution1d=1024,
              lutResolution3d=33,
              lutResolution1d3d1d=[1024,33,2],
              inputMin=0.0,
              inputMax=1.0,
              shaperIn=['linear',0.0,1.0],
              shaperOut=['linear',0.0,1.0]):

        # Expand 3D LUT resolutions
        expandedlutResolution3d = [lutResolution3d]*3
        expandedlutResolution1d3d1d = list(lutResolution1d3d1d)
        expandedlutResolution1d3d1d[1] = [lutResolution1d3d1d[1]]*3

        if lutStyle == IO_CAPABILITY_WRITE_1D:
            #print( "Sample the CLF ProcessList into a 1D LUT" )
            samples = Sampling.sample1D(processList,
                                      lutResolution1d,
                                      inputMin,
                                      inputMax)

            return cls.write1D(lutPath,
                               samples,
                               lutResolution1d,
                               inputMin,
                               inputMax)
        elif lutStyle == IO_CAPABILITY_WRITE_3D:
            #print( "Sample the CLF ProcessList into a 3D LUT" )
            samples = Sampling.sample3D(processList,
                                      expandedlutResolution3d,
                                      inputMin,
                                      inputMax)

            return cls.write3D(lutPath,
                               samples,
                               expandedlutResolution3d,
                               inputMin,
                               inputMax)

        elif lutStyle == IO_CAPABILITY_WRITE_1D3D1D:
            #print( "Sample the CLF ProcessList into a 1D 3D 1D LUT" )
            (samples1dIn,
             inputMin, inputMax,
             samples3d,
             samples1dOut,
             outputMin, outputMax) = Sampling.sample1D3D1D(processList,
                                                           expandedlutResolution1d3d1d,
                                                           shaperIn,
                                                           shaperOut)

            # Unpack a bunch of values before calling the write method
            (lutResolution1dIn, lutResolution3d, lutResolution1dOut) = expandedlutResolution1d3d1d
            (shaperInType, shaperInMin, shaperInMax) = shaperIn
            (shaperOutType, shaperOutMin, shaperOutMax) = shaperOut

            return cls.write1D3D1D(lutPath,
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
        else:
            return False

    @classmethod
    def write1D(cls,
                lutPath,
                samples,
                lutResolution1d,
                inputMin,
                inputMax):
        print( "Format %s can not be used to write 1D LUT data" % LutFormat.formatType )
        return False

    @classmethod
    def write3D(cls,
                lutPath,
                samples,
                lutResolution3d,
                inputMin,
                inputMax):
        print( "Format %s can not be used to write 3D LUT data" % LutFormat.formatType )
        return False

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
        print( "Format %s can not be used to write 1D/3D/1D LUT data" % LutFormat.formatType )
        return False
# LutFormat
