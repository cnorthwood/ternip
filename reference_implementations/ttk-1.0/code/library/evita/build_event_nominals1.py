#!/usr/bin/python

"""
Take all WordNet 2.0 nouns and create text files and dbm dictionaries
with words grouped in three bins: (i) those whose primary sense is an
event, (ii) those where all senses are events and (iii) those where
some senses are events. note that the third bin is currently not used
by Evita.

New dbm files and text files are written to current directory. They
can be used to overwrite the data in Dicts. It is NOT necessary to run
this script as part of the Evita installation. The txt files are
already in the Dicts directory and the dbm files can be created or
updated for your Python distribution by running the script
buildEventNominals2.py.
"""

import os
import sys
import forms
import anydbm
from wntools import *

DEBUG = False

#retrieve these synsets once
EVENT = N['event'][0].synset
ACT =  N['act'][1].synset
PHENOMENON = N['phenomenon'][0].synset 
COGPROC = N['cognitive process'][0].synset
DECLARATION = N['declaration'][0].synset
ANNOUNCEMENT = N['announcement'][0].synset
CONVERSATION = N['conversation'][0].synset
DISCUSSION = N['discussion'][1].synset
ENERGY = N['energy'][0].synset
CLOUD = N['cloud'][0].synset
CAUSE = N['cause'][0].synset
ACTIVITY = N['activity'][0].synset
REMARK = N['remark'][0].synset
STATEMENT = N['statement'][0].synset
FORMULA2 = N['formula'][2].synset
FORMULA3 = N['formula'][3].synset
MSTATEMENT = N['mathematical statement'][0].synset
PROPOSITION = N['proposition'][0].synset
AGREEMENT = N['agreement'][0].synset
AMENDMENT = N['amendment'][1].synset
PLAN = N['plan'][0].synset
DESIRE = N['desire'][0].synset
HOPE = N['hope'][1].synset
PROPOSAL = N['proposal'][0].synset
REQUEST = N['request'][0].synset
CONFIRMATION = N['confirmation'][1].synset
APPROVAL = N['approval'][3].synset
DISAPPROVAL = N['disapproval'][1].synset
THINKING = N['thinking'][0].synset
POLICY = N['policy'][0].synset
EXPLANATION = N['explanation'][1].synset

# Put newly created dbms and text files in current directory, not in
# Dicts directory where they would overwrite the current ones.
dbm1 = anydbm.open(forms.wnPrimSenseIsEvent + '.dbm', 'n')
dbm2 = anydbm.open(forms.wnAllSensesAreEvents + '.dbm', 'n')
dbm3 = anydbm.open(forms.wnSomeSensesAreEvents + '.dbm', 'n')
file1 = open(forms.wnPrimSenseIsEvent + '.txt', 'w')
file2 = open(forms.wnAllSensesAreEvents + '.txt', 'w')
file3 = open(forms.wnSomeSensesAreEvents + '.txt', 'w')



def wnPrimarySenseIsEvent(form):
    try:
        return isWNEvent(N[str(form)][0])
    except:
        return False

def wnAllSensesAreEvents(form):
    try:
        return checkWNEvent(N[str(form)]) > 0
    except:
        return False

def wnSomeSensesAreEvents(form):
    try:
        return checkWNEvent(N[str(form)]) >= 0
    except:
        return False

def isWNEvent(sense):
    clos = closure(sense.synset, HYPERNYM)
    if EVENT in clos and not CAUSE in clos: return True
    elif ACT in clos: return True
    elif PHENOMENON in clos and not ENERGY in clos and not CLOUD in clos: return True
    elif STATEMENT in clos and not AGREEMENT in clos and not AMENDMENT in clos and not PROPOSITION in clos and not MSTATEMENT in clos and not FORMULA2 in clos and not FORMULA3 in clos: return True
    elif CONVERSATION in clos: return True
    elif DISCUSSION in clos: return True
    elif PLAN in clos: return True
    elif DESIRE in clos: return True
    elif HOPE in clos: return True
    elif APPROVAL in clos: return True
    elif PROPOSAL in clos: return True
    elif REQUEST in clos: return True
    elif CONFIRMATION in clos: return True
    elif DISAPPROVAL in clos: return True
    elif THINKING in clos and not POLICY in clos and not EXPLANATION in clos: return True
    else: return False    

def checkWNEvent(wnWord):
    """Returns 1 if all wordnet senses are events, returns -1 if no
    senses are events and returns 0 otherwise."""
    senses = map(isWNEvent,wnWord.getSenses())
    all = True
    one = False
    for sense in senses:
        one = one or sense
        all = all and sense
    if all: return 1
    elif one: return 0
    else: return -1



# Open wordnet index.noun file and check for each entry whether senses
# are events.

IN = open(forms.WORDNET_NOUNS_FILE,'r');

count = 0

for line in IN:

    count = count + 1
    if not (count % 1000):
        print count
    token = line.split()[0]

    # first sense is event
    if (isWNEvent(N[str(token)][0])):
        if DEBUG:
            print token
            print "  ", N[str(token)], "\n  ", N[str(token)][0]
            print "   primSenseIsEvent"
        file1.write(token+"\n")
        dbm1[token] = '1'

    if (wnAllSensesAreEvents(token)):
        if DEBUG:
            print token
            print "  ", N[str(token)], "\n  ", N[str(token)][0]
            print "   isAlwaysEvent"
        file2.write(token+"\n")
        dbm2[token] = '1'

    if (wnSomeSensesAreEvents(token)):
        if DEBUG:
            print token
            print "  ", N[str(token)], "\n  ", N[str(token)][0]
            print "   isAmbiguous"
        file3.write(token+"\n")
        dbm3[token] = '1'



