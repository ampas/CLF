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

import numpy as np
import struct

#
# Functions to manage which feature sets are supported at run-time
#
featureSets = {
    "CLF"              : 0x0, 
    "Autodesk"         : 0x1,
    "Duiker Research"  : 0x2,
    "All"              : 0xf
}

compatibility = featureSets["All"]

def setFeatureCompatibility(featureSet):
    global compatibility
    compatibility = featureSet

def getFeatureCompatibility():
    global compatibility
    return compatibility

# Simple utility functions
def clamp(value, minValue=0.0, maxValue=1.0):
    return min( maxValue, max( minValue, value ) )
# clamp

def mix(value1, value2, mixAmount):
    outValue = [0] * len(value1)
    for i in range(len(value1)):
        outValue[i] = (1.0 - mixAmount)*value1[i] + mixAmount*value2[i]
    return outValue
# mix

# Utilities for bit-wise conversion between half-float, float, double and 
# 16, 32 and 64 bit-integer representations
def uint16ToHalf(uint16Value):
    return np.frombuffer(np.getbuffer(np.uint16(uint16Value)), dtype=np.float16)[0]

def halfToUInt16(halfValue):
    return np.frombuffer(np.getbuffer(np.float16(halfValue)), dtype=np.uint16)[0]

# Utilities for bit-wise conversion between float and 32 bit-integer representations
def uint32ToFloat32(uint32Value):
    return np.frombuffer(np.getbuffer(np.uint32(uint32Value)), dtype=np.float32)[0]

def float32ToUInt32(float32Value):
    return np.frombuffer(np.getbuffer(np.float32(float32Value)), dtype=np.uint32)[0]

# Utilities for bit-wise conversion between double and 64 bit-integer representations
def uint64ToDouble(uint64Value):
    return np.frombuffer(np.getbuffer(np.uint64(uint64Value)), dtype=np.float64)[0]

def doubleToUInt64(doubleValue):
    return np.frombuffer(np.getbuffer(np.float64(doubleValue)), dtype=np.uint64)[0]


# Utilities for bit-wise conversion between half-float, float, double and 
# 16, 32 and 64 bit-integer representations
def halfToHex(halfValue):
    uint16Value = halfToUInt16(halfValue)
    return struct.pack(">H", uint16Value).encode("hex")

def hexToHalf(hex16Value):
    uint16Value = struct.unpack(">H", hex16Value.decode("hex"))[0]
    return uint16ToHalf(uint16Value)

def float32ToHex(float32Value):
    return struct.pack(">f", float32Value).encode("hex")

def hexToFloat32(hex32Value):
    return struct.unpack(">f", hex32Value.decode("hex"))[0]

def doubleToHex(doubleValue):
    return struct.pack(">d", doubleValue).encode("hex")

def hexToDouble(hex64Value):
    return struct.unpack(">d", hex64Value.decode("hex"))[0]