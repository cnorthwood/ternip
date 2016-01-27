#!/usr/bin/env python

from glob import glob
import sys
import os
import os.path
import logging

sys.path.append('..')
from ternip.formats.tern import TernDocument

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s'))
logging.getLogger().addHandler(console)
logging.getLogger('ternip').setLevel(logging.INFO)

LOGGER = logging.getLogger()

if not os.path.isdir('preprocessed'):
    os.mkdir('preprocessed')

for fpath in glob(os.path.normpath('../sample_data/tern/data/english/ace_2004/*/*.sgm')):
    with open(fpath) as fd:
        try:
            doc = TernDocument(fd.read())
            LOGGER.info("Pre-processing " + os.path.basename(fpath))
            doc.reconcile_dct(doc.get_dct_sents(), add_S='s', add_LEX='lex', pos_attr='pos')
            doc.reconcile(doc.get_sents(), add_S='s', add_LEX='lex', pos_attr='pos')
            with open(os.path.join('preprocessed', os.path.basename(fpath)), 'w') as ppfd:
                ppfd.write(str(doc)[22:])
        except Exception:
            LOGGER.exception('Can not load document ' + os.path.basename(fpath))

