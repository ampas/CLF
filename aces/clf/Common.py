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

# Utilities for bit-wise conversion between half-float and 16 bit-integer representations
def uint16ToHalf(uint16value):
    return np.frombuffer(np.getbuffer(np.uint16(uint16value)), dtype=np.float16)[0]

def halfToUInt16(halfValue):
    return np.frombuffer(np.getbuffer(np.float16(halfValue)), dtype=np.uint16)[0]
