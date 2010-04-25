#!/usr/bin/python

"""
Create a dbm dictionaries with words whose primary sense in WordNet is
an event and a dictionary of words where all senses are events.

New dbm files are written to the Dicts directory, where they will
overwrite existing dbm files if present. This script may improve Evita
performance. This scripts requires the files

     Dicts/wnAllSensesAreEvents.txt
     Dicts/wnPrimSenseIsEvent.txt

The third WordNet derived file (wnSomeSensesAreEvents.txt, with nouns
where some senses are events) is currently not used by Evita.
"""

import os
import sys
import forms
import anydbm

# Open text versions of DBM files in Dicts directory.
file1 = open('Dicts/' + forms.wnPrimSenseIsEvent + '.txt', 'r')
file2 = open('Dicts/' + forms.wnAllSensesAreEvents + '.txt', 'r')

# Put newly created dbms in the Dicts directory, where they will
# overwrite the current ones.
dbm1 = anydbm.open('Dicts/' + forms.wnPrimSenseIsEvent + '.dbm', 'n')
dbm2 = anydbm.open('Dicts/' + forms.wnAllSensesAreEvents + '.dbm', 'n')

for line in file1:
    token = line.split()[0]
    dbm1[token] = '1'
    
for line in file2:
    token = line.split()[0]
    dbm2[token] = '1'


