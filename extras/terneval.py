#!/usr/bin/env python

import sys
sys.path.append('..')

from glob import glob
import tempfile
import os.path
import shutil
import os
import subprocess
import time

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
    return float(0)

def get_bits(text, type):
    overall_found = False
    i = 0
    lines = text.splitlines()
    for line in lines:
        if not overall_found and line[:9] == '  overall':
            overall_found = True
            if type == None:
                l = lines[i+2].split()
                if len(l) > 4:
                    return (int(l[1]), int(l[2]), int(l[4]))
                else:
                    return (0,0,0)
        if type != None and overall_found and line[7:].startswith(type):
            l = line.split()
            return (int(l[1]), int(l[2]), int(l[4]))
        i += 1
    return (0,0,0)

def compute_f_measure(pos, act, cor):
    prec = float(cor)/float(act)
    rec = float(cor)/float(pos)
    return (2 * prec * rec) / (prec + rec)

print
print "TERNIP TERN evaluator"
print

unannotated = glob(os.path.normpath('../sample_data/tern/data/english/ace_2004/*/*.sgm'))
annotated = glob(os.path.normpath('../sample_data/tern/data/english/ace_2004/*/*.sgml'))

temp = tempfile.mkdtemp()

ternip_dir = os.path.join(temp, 'ternip')
os.mkdir(ternip_dir)

# Load TERNIP
recogniser = ternip.recogniser()
print "TERNIP loaded", recogniser.num_rules, "recognition rules"
normaliser = ternip.normaliser()
print "TERNIP loaded", normaliser.num_rules, "normalisation rules"
print

ternip_recognition_scores = []
ternip_extent_scores = []
ternip_norm_scores = []
ternip_recognition_poss = 0
ternip_recognition_acts = 0
ternip_recognition_cors = 0
ternip_extent_poss = 0
ternip_extent_acts = 0
ternip_extent_cors = 0
ternip_norm_poss = 0
ternip_norm_acts = 0
ternip_norm_cors = 0

start = time.clock()

for i in range(len(unannotated)):
    
    id = os.path.basename(unannotated[i])
    
    # Open the document
    try:
        with open(unannotated[i]) as fd:
            doc = ternip.formats.tern(fd.read())
    except:
        doc = None
        print "Unable to load document", id
        continue
    
    # Get DCT
    dct_sents = doc.get_dct_sents()
    dct_sents = recogniser.tag(dct_sents)
    normaliser.annotate(dct_sents, 'XXXXXXXX')
    doc.reconcile_dct(dct_sents)
    if len(dct_sents) > 0 and len(dct_sents[0]) > 0 and len(dct_sents[0][0][2]) > 0:
        dct = dct_sents[0][0][2].pop().value
    else:
        dct = ''
    sents = recogniser.tag(doc.get_sents())
    normaliser.annotate(sents, dct)
    
    # Add TIMEX tags back in
    doc.reconcile(sents)
    
    # Save output
    ternip_file = os.path.join(ternip_dir, id)
    with open(ternip_file, 'w') as fd:
        fd.write(str(doc)[22:]) # can't have XML header, because score_timex2.pl expects SGML
    
    # Score TERNIP
    output = subprocess.Popen(['perl', 'score_timex2.pl', annotated[i], ternip_file], stdout=subprocess.PIPE).communicate()[0]
    print id
    ternip_recognition_score = get_f_measure(output, None)
    ternip_extent_score = get_f_measure(output, 'TEXT')
    ternip_norm_score = get_f_measure(output, 'VAL')
    print "    recognition", ternip_recognition_score
    print "    extent", ternip_extent_score
    print "    normalisation", ternip_norm_score
    print
    ternip_recognition_scores.append(ternip_recognition_score)
    ternip_extent_scores.append(ternip_extent_score)
    ternip_norm_scores.append(ternip_norm_score)
    (pos, act, cor) = get_bits(output, None)
    ternip_recognition_poss += pos
    ternip_recognition_acts += act
    ternip_recognition_cors += cor
    (pos, act, cor) = get_bits(output, 'TEXT')
    ternip_extent_poss += pos
    ternip_extent_acts += act
    ternip_extent_cors += cor
    (pos, act, cor) = get_bits(output, 'VAL')
    ternip_norm_poss += pos
    ternip_norm_acts += act
    ternip_norm_cors += cor

print
print "MACROAVERAGED F-MEASURES"
print "    successfully tagged", len(ternip_recognition_scores), "documents"
print "    recognition", sum(ternip_recognition_scores)/len(ternip_recognition_scores)
print "    extent", sum(ternip_extent_scores)/len(ternip_extent_scores)
print "    normalisation", sum(ternip_norm_scores)/len(ternip_norm_scores)
print "    run time (CPU seconds)", time.clock() - start
print


print
print "MICROAVERAGED F-MEASURES"
print "    successfully tagged", len(ternip_recognition_scores), "documents"
print "    recognition", compute_f_measure(ternip_recognition_poss, ternip_recognition_acts, ternip_recognition_cors)
print "    extent", compute_f_measure(ternip_extent_poss, ternip_extent_acts, ternip_extent_cors)
print "    normalisation", compute_f_measure(ternip_norm_poss, ternip_norm_acts, ternip_norm_cors)
print
shutil.rmtree(temp)
