#!/usr/bin/env python

from glob import glob
import tempfile
import os.path
import shutil
import os
import subprocess

import ternip.formats
import ternip.rule_engine

def get_f_measure(text):
    i = 0
    lines = text.splitlines()
    for line in lines:
        if line[:9] == '  overall':
            break
        i += 1
    i += 2
    return float(lines[i][-5:])

unannotated = glob('sample_data/tern/data/english/ace_2004/nwire/*.sgm')
annotated = glob('sample_data/tern/data/english/ace_2004/nwire/*.sgml')

temp = tempfile.mkdtemp()

gutime_dir = os.path.join(temp, 'gutime')
os.mkdir(gutime_dir)

ternip_dir = os.path.join(temp, 'ternip')
os.mkdir(ternip_dir)

# Load TERNIP
recogniser = ternip.rule_engine.recognition_rule_engine()
recogniser.load_rules('rules/recognition/')
normaliser = ternip.rule_engine.normalisation_rule_engine()
normaliser.load_rules('rules/normalisation/')

gutime_scores = []
ternip_scores = []

for i in range(len(unannotated)):
    
    id = os.path.basename(unannotated[i])
    
    print
    print "Annotating", id
    
    try:
        # Open this document
        with open(unannotated[i]) as fd:
            doc = ternip.formats.timex2(fd.read(), 'TEXT')
        
        # Add S, LEX and POS tags for GUTime
        doc.reconcile(doc.get_sents(), add_S='s', add_LEX='lex', pos_attr='pos')
        
        # Save that file for GUTime
        gutime_in_file = os.path.join(gutime_dir, id + ".input")
        gutime_out_file = os.path.join(gutime_dir, id)
        with open(gutime_in_file, 'w') as fd:
            fd.write(str(doc)[22:])
        
        # Now run GUTime
        os.chdir('gutime')
        print subprocess.Popen(['perl', 'gutime.pl', gutime_in_file, gutime_out_file], stdout=subprocess.PIPE).communicate()[0]
        os.chdir('..')
        
        # Strip LEX and S tags
        with open(gutime_out_file) as fd:
            doc = ternip.formats.timex2(fd.read(), 'TEXT')
        doc.strip_tag('s')
        doc.strip_tag('lex')
        with open(gutime_out_file, 'w') as fd:
            fd.write(str(doc)[22:]) # can't have XML header, because score_timex2.pl expects SGML
        
        # Score GUTime
        gutime_score = get_f_measure(subprocess.Popen(['perl', 'score_timex2.pl', annotated[i], gutime_out_file], stdout=subprocess.PIPE).communicate()[0])
        print "GUTime:", gutime_score
        gutime_scores.append(gutime_score)
        
        # Now reopen this document cleanly for TERNIP
        with open(unannotated[i]) as fd:
            doc = ternip.formats.timex2(fd.read(), 'TEXT')
        sents = recogniser.tag(doc.get_sents())
        normaliser.annotate(sents, "")
        
        # Add TIMEX tags back in
        doc.reconcile(sents)
        
        # Save output
        ternip_file = os.path.join(ternip_dir, id)
        with open(ternip_file, 'w') as fd:
            fd.write(str(doc)[22:]) # can't have XML header, because score_timex2.pl expects SGML
        
        # Score TERNIP
        ternip_score = get_f_measure(subprocess.Popen(['perl', 'score_timex2.pl', annotated[i], ternip_file], stdout=subprocess.PIPE).communicate()[0])
        print "TERNIP:", ternip_score
        ternip_scores.append(ternip_score)
    except Exception as e:
        print "EXCEPTION:", str(e)

print
print "OVERALL F-MEASURE"
print "GUTime:", sum(gutime_scores)/len(gutime_scores)
print "TERNIP:", sum(ternip_scores)/len(ternip_scores)

shutil.rmtree(temp)