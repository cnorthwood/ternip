#!/usr/bin/env python

import sys

sys.path.append('..')

import ternip
from ternip.formats.gate import gate

recogniser = ternip.recogniser()
normaliser = ternip.normaliser()

doc = gate(sys.stdin.read())
sents = recogniser.tag(doc.get_sents())
normaliser.annotate(sents, doc._dct)
doc.reconcile(sents)

sys.stdout.write(str(doc))