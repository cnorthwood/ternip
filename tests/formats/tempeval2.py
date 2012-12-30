#!/usr/bin/env python

import ternip
from ternip.formats.tempeval2 import TempEval2Document
import unittest
import os.path
from ternip.timex import Timex

class TempEval2DocumentTest(unittest.TestCase):
    
    def test_get_sents(self):
        with open(self.filepath('base-segmentation-single.tab')) as fd:
            d = TempEval2Document(fd.read(), 'ABC1')
        self.assertEquals('ABC1', d.docid)
        self.assertEquals([[('The', 'DT', set()), ('first', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())],
                           [('The', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]],
            d.get_sents())
    
    def test_load_multi(self):
        with open(self.filepath('base-segmentation-multi.tab')) as fd:
            ds = TempEval2Document.load_multi(fd.read(), '')
        self.assertEquals(2, len(ds))
        self.assertTrue('ABC1' in [d.docid for d in ds])
        self.assertTrue('ABC2' in [d.docid for d in ds])
    
    def test_extents(self):
        t1 = Timex(id=1)
        t2 = Timex(id=2)
        sents = [[('The', 'DT', set()), ('first', 'JJ', {t1}), ('sentence', 'NN', set()), ('.', '.', set())],
                 [('The', 'DT', set()), ('second', 'JJ', {t2}), ('sentence', 'NN', {t2}), ('.', '.', set())]]
        d = TempEval2Document.create(sents, 'ABC1')
        with open(self.filepath('timex-extents.tab')) as fd:
            self.assertEquals(sorted(d.get_extents().splitlines()), sorted(fd.read().splitlines()))
    
    def test_attr(self):
        t1 = Timex(id=1, type='date')
        t2 = Timex(id=2)
        t3 = Timex(id=3)
        t1.value = "20100710"
        t1.mod = "BEFORE"
        t1.freq = "1M"
        t1.comment = "Test"
        t1.granuality = "1D"
        t1.non_specific = True
        t1.quant = 'EVERY'
        t1.temporal_function = True
        t1.document_role = 'MODIFICATION_TIME'
        t1.begin_timex = t1
        t1.end_timex = t2
        t1.context = t3
        sents = [[('The', 'DT', set()), ('first', 'JJ', {t1}), ('sentence', 'NN', set()), ('.', '.', set())],
                 [('The', 'DT', set()), ('second', 'JJ', {t2}), ('sentence', 'NN', {t2}), ('.', '.', {t3})]]
        d = TempEval2Document.create(sents, 'ABC1')
        with open(self.filepath('timex-attr.tab')) as fd:
            self.assertEquals(sorted(d.get_attrs().splitlines()), sorted(fd.read().splitlines()))

    def filepath(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)