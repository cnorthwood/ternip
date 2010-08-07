#!/usr/bin/env python

import ternip.formats
import ternip.rule_engine

import subprocess
import os.path
import tempfile
import shutil
import time
import sys

sys.path.append('extras')

import score_entities

print
print "TERNIP vs. GUTime TempEval-2 evaluator"
print

# Load TERNIP
recogniser = ternip.recogniser()
print "TERNIP loaded", recogniser.num_rules, "recognition rules"
normaliser = ternip.normaliser()
print "TERNIP loaded", normaliser.num_rules, "normalisation rules"

# Load testing data
data_path = os.path.normpath('sample_data/tempeval-training-2/english/data/')
with open(os.path.join(data_path, 'base-segmentation.tab')) as fd:
    with open(os.path.join(data_path, 'dct.txt')) as dct_fd:
        docs = ternip.formats.tempeval2.load_multi(fd.read(), dct_fd.read())

# Get DCTs


temp = tempfile.mkdtemp()

gutime_extents = open(os.path.join(temp, 'gutime-extents.tab'), 'w')
gutime_attrs = open(os.path.join(temp, 'gutime-attrs.tab'), 'w')
ternip_extents = open(os.path.join(temp, 'ternip-extents.tab'), 'w')
ternip_attrs = open(os.path.join(temp, 'ternip-attrs.tab'), 'w')

ternip_time = float()
gutime_time = float()

for doc in docs:
    
    print "Annotating", doc.docid
    
    # Convert into a GUTime friendly format
    gutime_in = os.path.join(temp, doc.docid + '.input')
    gutime_out = os.path.join(temp, doc.docid)
    start = time.clock()
    xml_doc = ternip.formats.tern.create(doc.get_sents(), doc.docid, add_S='s', add_LEX='lex', pos_attr='pos', dct=doc.dct)
    with open(gutime_in, 'w') as fd:
        fd.write(str(xml_doc)[22:])
    
    # Now run GU Time
    subprocess.Popen(['perl', 'gutime.pl', gutime_in, gutime_out], stdout=subprocess.PIPE, cwd='gutime').communicate()
    gutime_time += time.clock() - start
    
    # Load that back in
    with open(gutime_out) as fd:
        try:
            xml_doc = ternip.formats.tern(fd.read(), has_S='s', has_LEX='lex', pos_attr='pos')
        except Exception as e:
            print "    GUTime corrupted the XML:", str(e)
    
    # Now transform this back into the TempEval-2 format
    gutime_doc = ternip.formats.tempeval2.create(xml_doc.get_sents(), doc.docid)
    
    # Store these results
    gutime_extents.write(gutime_doc.get_extents())
    gutime_attrs.write(gutime_doc.get_attrs())
    
    # Now do it in TERNIP
    start = time.clock()
    sents = recogniser.tag(doc.get_sents())
    normaliser.annotate(sents, doc.dct)
    doc.reconcile(sents)
    ternip_time += time.clock() - start
    
    # And store the TERNIP rules
    ternip_extents.write(doc.get_extents())
    ternip_attrs.write(doc.get_attrs())

# Close the key files
gutime_extents.close()
gutime_attrs.close()
ternip_extents.close()
ternip_attrs.close()

# Score!
print
print "GUTime"
print
print "Time to run", gutime_time
try:
    score_entities.score_entities(os.path.join(data_path, 'base-segmentation.tab'), os.path.join(data_path, 'timex-extents.tab'), os.path.join(temp, 'gutime-extents.tab'), os.path.join(data_path, 'timex-attributes.tab'), os.path.join(temp, 'gutime-attrs.tab'))
except ZeroDivisionError:
    print
    print "Nothing was tagged"
    print

print
print "TERNIP"
print
print "Time to run", ternip_time
try:
    score_entities.score_entities(os.path.join(data_path, 'base-segmentation.tab'), os.path.join(data_path, 'timex-extents.tab'), os.path.join(temp, 'ternip-extents.tab'), os.path.join(data_path, 'timex-attributes.tab'), os.path.join(temp, 'ternip-attrs.tab'))
except ZeroDivisionError:
    print
    print "Nothing was tagged"
    print



# Clean up
shutil.rmtree(temp)