#!/usr/bin/env python

import sys
import re

with open(sys.argv[1]) as fd:
    
    i = 0
    
    for line in fd:
        if re.match(r'# \d+', line) == None:
            print line,
        if line.strip() == '---':
            i += 1
            print '# ' + str(i)