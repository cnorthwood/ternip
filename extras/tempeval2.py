#!/usr/bin/env python

import sys
sys.path.append('..')

import ternip.formats
import ternip.rule_engine

import os.path
import tempfile
import shutil
import time

from score_entities import score_entities

print
print "TERNIP TempEval-2 evaluator"
print

# Load TERNIP
recogniser = ternip.rule_engine.recognition_rule_engine()
recogniser.load_rules(os.path.normpath('../rules/recognition/'))
print "TERNIP loaded", recogniser.num_rules, "recognition rules"
normaliser = ternip.rule_engine.normalisation_rule_engine()
normaliser.load_rules(os.path.normpath('../rules/normalisation/'))
print "TERNIP loaded", normaliser.num_rules, "normalisation rules"
print
print "Loading data..."

# Load testing data
data_path = os.path.normpath('../sample_data/tempeval-training-2/english/data/')
with open(os.path.join(data_path, 'base-segmentation.tab')) as fd:
    with open(os.path.join(data_path, 'dct.txt')) as dct_fd:
        docs = ternip.formats.tempeval2.load_multi(fd.read(), dct_fd.read())

temp = tempfile.mkdtemp()

ternip_extents = open(os.path.join(temp, 'ternip-extents.tab'), 'w')
ternip_attrs = open(os.path.join(temp, 'ternip-attrs.tab'), 'w')

start = time.clock()

print

for doc in docs:
    
    print "Annotating", doc.docid
    
    # Annotate
    sents = recogniser.tag(doc.get_sents())
    normaliser.annotate(sents, doc.dct)
    doc.reconcile(sents)
    
    # And store the TERNIP results
    ternip_extents.write(doc.get_extents())
    ternip_attrs.write(doc.get_attrs())

# Close the response files
ternip_extents.close()
ternip_attrs.close()

# Score!
print
print "RESULTS"
print
print "Time to run (in CPU seconds)", time.clock() - start
try:
    score_entities(os.path.join(data_path, 'base-segmentation.tab'), os.path.join(data_path, 'timex-extents.tab'), os.path.join(temp, 'ternip-extents.tab'), os.path.join(data_path, 'timex-attributes.tab'), os.path.join(temp, 'ternip-attrs.tab'))
except ZeroDivisionError:
    print
    print "Nothing was tagged"
    print

# Clean up
shutil.rmtree(temp)