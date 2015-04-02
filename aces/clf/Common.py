import struct

import numpy as np

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
    return struct.unpack(">d", hex32Value.decode("hex"))[0]