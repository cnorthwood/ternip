#!/usr/bin/env python

from glob import glob
import time
import os
import sys
sys.path.append('..')

import ternip.formats

ternip_time = time.clock()
recogniser = ternip.recogniser()
normaliser = ternip.normaliser()
for file in glob(os.path.normpath('preprocessed/*.sgm')):
    with open(file) as fd:
        doc = ternip.formats.tern(fd.read())
    dct_sents = doc.get_dct_sents()
    dct_sents = recogniser.tag(dct_sents)
    normaliser.annotate(dct_sents, 'XXXXXXXX')
    doc.reconcile_dct(dct_sents)
    if len(dct_sents) > 0 and len(dct_sents[0][0][2]) > 0:
        dct = dct_sents[0][0][2].pop().value
    else:
        dct = ''
    sents = recogniser.tag(doc.get_sents())
    normaliser.annotate(sents, dct)
    doc.reconcile(sents)
    final = str(doc)

ternip_time = time.clock() - ternip_time

# Count document size
bits = 0
for file in glob(os.path.normpath('extras/preprocessed/*.sgm')):
    with open(file) as fd:
        bits += len(fd.read())

print "TERNIP:", ternip_time, "seconds"
print "       ", bits/ternip_time/1024, "kb/s"