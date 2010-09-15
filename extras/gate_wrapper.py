#!/usr/bin/env python

import sys

sys.path.append('..')

import ternip
ternip.no_NLTK = True

from ternip.formats import gate

recogniser = ternip.recogniser()
normaliser = ternip.normaliser()

infile = open(sys.argv[1])
doc = gate(infile.read())
infile.close()
sents = recogniser.tag(doc.get_sents())
normaliser.annotate(sents, doc._dct)
doc.reconcile(sents)

sys.stdout.write(str(doc))
