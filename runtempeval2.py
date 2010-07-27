#!/usr/bin/env python

import ternip.formats
import ternip.rule_engine

import subprocess
import os.path
import tempfile
import shutil
import time

import score_entities

# Load TERNIP
recogniser = ternip.rule_engine.recognition_rule_engine()
recogniser.load_rules(os.path.normpath('rules/recognition/'))
normaliser = ternip.rule_engine.normalisation_rule_engine()
normaliser.load_rules(os.path.normpath('rules/normalisation/'))

# Load testing data
data_path = os.path.normpath('sample_data/tempeval-training-2/english/data/')
with open(os.path.join(data_path, 'base-segmentation.tab')) as fd:
    docs = ternip.formats.tempeval2.load_multi(fd.read())

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
    xml_doc = ternip.formats.tern.create(doc.get_sents(), doc.docid, add_S='s', add_LEX='lex', pos_attr='pos')
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
    normaliser.annotate(sents, "")
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