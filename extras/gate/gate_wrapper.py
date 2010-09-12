#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join('..', '..'))

import ternip
from ternip.formats.gate import gate

recogniser = ternip.recogniser()
normaliser = ternip.normaliser()

doc = gate(sys.stdin.read())
sents = recogniser.tag(doc.get_sents())
normaliser.annotate(sents, '')
doc.reconcile(sents)

sys.stdin.write(str(doc))