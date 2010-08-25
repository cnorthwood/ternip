#!/usr/bin/env python

from glob import glob
import ternip
import subprocess
import tempfile
import time
import os

# Time GUTime
gutime = time.clock()
for file in glob(os.path.normpath('extras/preprocessed/*.sgm')):
    (fd, temp) = tempfile.mkstemp()
    subprocess.Popen(['perl', 'gutime.pl', os.path.join('..', file), temp], stdout=subprocess.PIPE, cwd='gutime').communicate()
    os.close(fd)
    os.remove(temp)

gutime = time.clock() - gutime

# Time TERNIP
ternip_time = time.clock()
for file in glob(os.path.normpath('extras/preprocessed/*.sgm')):
    subprocess.Popen(['python', 'annotate_timex', '-t', 'tern', '--s-tag', 's', '--lex-tag', 'lex', '--pos-attr', 'pos', file], stdout=subprocess.PIPE).communicate()

ternip_time = time.clock() - ternip_time

# Count document size
bits = 0
for file in glob(os.path.normpath('extras/preprocessed/*.sgm')):
    with open(file) as fd:
        bits += len(fd.read())

print "GUTime:", gutime, "seconds"
print "       ", bits/gutime/1024, "kb/s"
print "TERNIP:", ternip_time, "seconds"
print "       ", bits/ternip_time/1024, "kb/s"