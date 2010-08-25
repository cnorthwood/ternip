#!/usr/bin/env python

from glob import glob
import tempfile
import os.path
import shutil
import os
import subprocess
import time
import traceback
import sys

import ternip.formats
import ternip.rule_engine

def get_f_measure(text, type):
    overall_found = False
    i = 0
    lines = text.splitlines()
    for line in lines:
        if not overall_found and line[:9] == '  overall':
            overall_found = True
            if type == None:
                if lines[i+2][-5:] != '':
                    return float(lines[i+2][-5:])
        if type != None and overall_found and line[7:].startswith(type):
            return float(line[-5:])
        i += 1
    return float(1)

print
print "TERNIP vs. GUTime TERN evaluator"
print

unannotated = glob(os.path.normpath('sample_data/tern/data/english/ace_2004/*/*.sgm'))
annotated = glob(os.path.normpath('sample_data/tern/data/english/ace_2004/*/*.sgml'))

temp = tempfile.mkdtemp()

gutime_dir = os.path.join(temp, 'gutime')
os.mkdir(gutime_dir)

ternip_dir = os.path.join(temp, 'ternip')
os.mkdir(ternip_dir)

# Load TERNIP
recogniser = ternip.recogniser()
print "TERNIP loaded", recogniser.num_rules, "recognition rules"
normaliser = ternip.normaliser()
print "TERNIP loaded", normaliser.num_rules, "normalisation rules"

gutime_recognition_scores = []
gutime_extent_scores = []
gutime_norm_scores = []
ternip_recognition_scores = []
ternip_extent_scores = []
ternip_norm_scores = []

gutime_time = float()
ternip_time = float()
bytes = 0

for i in range(len(unannotated)):
    
    id = os.path.basename(unannotated[i])
    
    print
    print "Annotating", id
    print '-' * 80
    
    with open(unannotated[i]) as fd:
        bytes += len(fd.read())
    
    try:
        start = time.clock()
        # Open this document
        with open(unannotated[i]) as fd:
            doc = ternip.formats.tern(fd.read())
        
        # Add S, LEX and POS tags for GUTime
        doc.reconcile(doc.get_sents(), add_S='s', add_LEX='lex', pos_attr='pos')
        
        # Save that file for GUTime
        gutime_in_file = os.path.join(gutime_dir, id + ".input")
        gutime_out_file = os.path.join(gutime_dir, id)
        with open(gutime_in_file, 'w') as fd:
            fd.write(str(doc)[22:])
        
        # Now run GUTime
        subprocess.Popen(['perl', 'gutime.pl', gutime_in_file, gutime_out_file], stdout=subprocess.PIPE, cwd='gutime').communicate()
        
        # Strip LEX and S tags
        with open(gutime_out_file) as fd:
            doc = ternip.formats.tern(fd.read())
        doc.strip_tag('s')
        doc.strip_tag('lex')
        with open(gutime_out_file, 'w') as fd:
            fd.write(str(doc)[22:]) # can't have XML header, because score_timex2.pl expects SGML
        gutime_time += time.clock() - start
        
        # Score GUTime
        output = subprocess.Popen(['perl', 'score_timex2.pl', annotated[i], gutime_out_file], stdout=subprocess.PIPE).communicate()[0]
        gutime_recognition_score = get_f_measure(output, None)
        gutime_extent_score = get_f_measure(output, 'TEXT')
        gutime_norm_score = get_f_measure(output, 'VAL')
        print "GUTime"
        print "    recognition", gutime_recognition_score
        print "    extent", gutime_extent_score
        print "    normalisation", gutime_norm_score
        gutime_recognition_scores.append(gutime_recognition_score)
        gutime_extent_scores.append(gutime_extent_score)
        gutime_norm_scores.append(gutime_norm_score)
        
        start = time.clock()
        # Now reopen this document cleanly for TERNIP
        with open(unannotated[i]) as fd:
            doc = ternip.formats.tern(fd.read())
        
        # Get DCT
        dct_sents = doc.get_dct_sents()
        dct_sents = recogniser.tag(dct_sents)
        normaliser.annotate(dct_sents, 'XXXXXXXX')
        doc.reconcile_dct(dct_sents)
        dct = dct_sents[0][0][2].pop().value
        sents = recogniser.tag(doc.get_sents())
        normaliser.annotate(sents, dct)
        
        # Add TIMEX tags back in
        doc.reconcile(sents)
        
        # Save output
        ternip_file = os.path.join(ternip_dir, id)
        with open(ternip_file, 'w') as fd:
            fd.write(str(doc)[22:]) # can't have XML header, because score_timex2.pl expects SGML
        ternip_time += time.clock() - start
        
        # Score TERNIP
        output = subprocess.Popen(['perl', 'score_timex2.pl', annotated[i], ternip_file], stdout=subprocess.PIPE).communicate()[0]
        ternip_recognition_score = get_f_measure(output, None)
        ternip_extent_score = get_f_measure(output, 'TEXT')
        ternip_norm_score = get_f_measure(output, 'VAL')
        print "TERNIP"
        print "    recognition", ternip_recognition_score
        print "    extent", ternip_extent_score
        print "    normalisation", ternip_norm_score
        ternip_recognition_scores.append(ternip_recognition_score)
        ternip_extent_scores.append(ternip_extent_score)
        ternip_norm_scores.append(ternip_norm_score)
        
    except Exception as e:
        print "EXCEPTION:", str(e)
        traceback.print_exc(file=sys.stdout)

print
print "MACROAVERAGED F-MEASURES"
print

# Macroaveraging
print "GUTime"
print "    successfully tagged", len(gutime_recognition_scores), "documents"
print "    recognition", sum(gutime_recognition_scores)/len(gutime_recognition_scores)
print "    extent", sum(gutime_extent_scores)/len(gutime_extent_scores)
print "    normalisation", sum(gutime_norm_scores)/len(gutime_norm_scores)
print "    time", gutime_time
print "    throughput", bytes / gutime_time
print
print "TERNIP"
print "    successfully tagged", len(ternip_recognition_scores), "documents"
print "    recognition", sum(ternip_recognition_scores)/len(ternip_recognition_scores)
print "    extent", sum(ternip_extent_scores)/len(ternip_extent_scores)
print "    normalisation", sum(ternip_norm_scores)/len(ternip_norm_scores)
print "    time", ternip_time
print "    throughput", bytes / ternip_time
print

shutil.rmtree(temp)
