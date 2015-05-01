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
ACES Python Utilities
=====================

Usage
-----

Python
******

>>> from aces_ocio.create_aces_config import create_ACES_config
>>> aces_CTL_directory = '/path/to/github/checkout/releases/v1.0.0/transforms/ctl'
>>> config_directory = '/path/to/configuration/dir'
>>> create_ACES_config(aces_CTL_directory, config_directory, 1024, 33, True)

Command Line
************

Using the *create_aces_config* binary:

$ create_aces_config -a '/path/to/github/checkout/releases/v0.7.1/transforms/ctl' -c '/path/to/config/dir' --lutResolution1d 1024 --lutResolution3d 33 --keepTempImages

It is possible to set the following environment variables to avoid passing
the paths to the binary:

- *ACES_OCIO_CTL_DIRECTORY*
- *ACES_OCIO_CONFIGURATION_DIRECTORY*

The above command line call would be done as follows:

$ create_aces_config --lutResolution1d 1024 --lutResolution3d 33 --keepTempImages

Testing the generated configuration is needs the
*ACES_OCIO_CTL_DIRECTORY* environment variable to be set and is done as
follows:

$ tests_aces_config

Build
-----

Mac OS X - Required packages
****************************

OpenColorIO
___________

$ brew install -vd opencolorio --with-python

OpenImageIO
___________

$ brew tap homebrew/science

Optional Dependencies
_____________________

$ brew install -vd libRaw
$ brew install -vd OpenCV
$ brew install -vd openimageio --with-python

CTL
___

$ brew install -vd CTL

OpenColorIO
___________

*ociolutimage* will build with *openimageio* installed.

$ brew uninstall -vd opencolorio
$ brew install -vd opencolorio --with-python
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