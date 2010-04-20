#!/usr/bin/env python

import os
from stat import ST_SIZE

def binarySearchFile(file, key, sep=' ',  cache={}, cacheDepth=-1):
    key = key + sep
    keylen = len(key)
    start, end = 0, os.stat(file.name)[ST_SIZE]
    currentDepth = 0
    #count = 0
    while start < end:
        #print start, end
        #count = count + 1
        #if count > 20:
        #    raise "infinite loop"
        lastState = start, end
        middle = (start + end) / 2
        if cache.get(middle):
            offset, line = cache[middle]
        else:
            file.seek(max(0, middle - 1))
            if middle > 0:
                file.readline()
            offset, line = file.tell(), file.readline()
            if currentDepth < cacheDepth:
                cache[middle] = (offset, line)
        #print start, middle, end, offset, line,
        if offset > end:
            assert end != middle - 1, "infinite loop"
            end = middle - 1
        elif line[:keylen] == key:# and line[keylen + 1] == ' ':
            return line
        elif line > key:
            assert end != middle - 1, "infinite loop"
            end = middle - 1
        elif line < key:
            start = offset + len(line) - 1
        currentDepth = currentDepth + 1
        thisState = start, end
        if lastState == thisState:
            # detects the condition where we're searching past the end
            # of the file, which is otherwise difficult to detect
            return None
    return None
