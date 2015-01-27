#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Print information about a CLF
"""

import array
import os
import sys

import clf

def main():
    import optparse

    p = optparse.OptionParser(description='Print information about a CLF file',
                                prog='clfinfo',
                                version='0.01',
                                usage='%prog [options]')

    p.add_option('--clf', '-c', default='')

    options, arguments = p.parse_args()

    #
    # Get options
    # 
    clfPath = options.clf

    try:
        argsStart = sys.argv.index('--') + 1
        args = sys.argv[argsStart:]
    except:
        argsStart = len(sys.argv)+1
        args = []

    print( "command line : \n%s\n" % " ".join(sys.argv) )
 
    #
    # Run 
    #
    if clfPath:
        pl = clf.ProcessList(clfPath)
        pl.printInfo()

# main

if __name__ == '__main__':
    main()
