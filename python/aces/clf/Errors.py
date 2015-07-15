#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class UnknownProcessNodeError(Error):
    """Exception raised for ProcessNodes types that are unknown or unsupported.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class UnsupportedExtensionError(Error):
    """Exception raised for errors related to unsupported extensions.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
