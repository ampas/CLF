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
Functions to convert from different LUT formats to CLF
"""

import array
import math
import os
import sys

import clf
import lutFormats

def main():
    import optparse

    usage  = '%prog [options]\n'
    usage += "The following formats can be converted to CLF:\n"
    for format in lutFormats.Registry.getFormats():
        for description, extension in zip(format.descriptions(), format.extensions()):
            if format.canRead(extension):
                usage += "\t%s\n" % description

    p = optparse.OptionParser(description='Convert a LUT to the Common LUT Format',
                                prog='convertLUTtoCLF',
                                version='0.01',
                                usage=usage)

    p.add_option('--lut', '-l', default=None)
    p.add_option('--clf', '-c', default=None)
    p.add_option('--inverse', '', action='store_true', default=False)
    p.add_option('--inversesUseIndexMaps', '', action='store_true', default=False)
    p.add_option('--inversesUseHalfDomain', '', action='store_true', default=False)

    options, arguments = p.parse_args()

    #
    # Get options
    #
    lutPath = options.lut
    clfPath = options.clf
    inverse = options.inverse
    inversesUseIndexMaps = options.inversesUseIndexMaps
    inversesUseHalfDomain = options.inversesUseHalfDomain

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    #print( "command line : \n%s\n" % " ".join(sys.argv) )

    #
    # Run
    #
    if lutPath != None and clfPath != None:
        clf = lutFormats.Registry.read(lutPath,
            inverse=inverse,
            inversesUseIndexMaps=inversesUseIndexMaps,
            inversesUseHalfDomain=inversesUseHalfDomain)

        if clf:
            clf.writeFile(clfPath)

# main

if __name__ == '__main__':
    main()
