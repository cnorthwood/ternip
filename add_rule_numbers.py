#!/usr/bin/env python

import sys

with open(sys.argv[1]) as fd:
    
    i = 0
    
    for line in fd:
        print line,
        if line.strip() == '---':
            i += 1
            print '# ' + str(i)