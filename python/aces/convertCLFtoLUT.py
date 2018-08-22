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

"""
Functions to convert from CLF to different LUT formats
"""

import array
import math
import os
import sys

import aces.clf as clf
import lutFormats

def convertCLFtoLUT(clfPath,
                    lutPath,
                    lutFileFormat,
                    lutDataFormat=lutFormats.LUTDATAFORMAT_1D,
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

    # Write new LUT format
    print( "Writing LUT : %s" % lutPath )
    lutFormats.Registry.write(processList,
                              lutPath,
                              #lutFileFormat,    # Currently not used
                              lutDataFormat,
                              lutResolution1d,
                              lutResolution3d,
                              lutResolution1d3d1d,
                              inputMin,
                              inputMax,
                              shaperIn,
                              shaperOut)

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
    usage += 'Convert CLF to spi3d : convertCLFtoLUT --generate3d --lutResolution3d 33 -c lut3d.clf -l lut3d.spi3d'
    usage += '\n'
    usage += 'Convert CLF to CTL   : convertCLFtoLUT --generate3d --lutResolution3d 33 -c lut3d.clf -l lut3d.ctl -f ctl'
    usage += '\n'

    usage += '\n'

    usage += "CLF can be stored as 1D LUTs using the following formats:\n"
    for format in lutFormats.Registry.getFormats():
        for description, extension in zip(format.descriptions(), format.extensions()):
            if format.canWrite1D(extension):
                usage += "\t%s\n" % description
    usage += '\n'

    usage += "CLF can be stored as 3D LUTs using the following formats:\n"
    for format in lutFormats.Registry.getFormats():
        for description, extension in zip(format.descriptions(), format.extensions()):
            if format.canWrite3D(extension):
                usage += "\t%s\n" % description
    usage += '\n'

    usage += "CLF can be stored as 1D/3D/1D LUTs using the following formats:\n"
    for format in lutFormats.Registry.getFormats():
        for description, extension in zip(format.descriptions(), format.extensions()):
            if format.canWrite1D3D1D(extension):
                usage += "\t%s\n" % description
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
    lutDataFormat = lutFormats.LUTDATAFORMAT_1D
    if generate1d:
        lutDataFormat = lutFormats.LUTDATAFORMAT_1D
    elif generate3d:
        lutDataFormat = lutFormats.LUTDATAFORMAT_3D
    elif generate1d3d1d:
        lutDataFormat = lutFormats.LUTDATAFORMAT_1D_3D_1D

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
