#!/usr/bin/env python

import ternip
import ternip.formats
import unittest
import os.path

class tempeval2_test(unittest.TestCase):
    
    def test_get_sents(self):
        with open(self.filepath('base-segmentation-single.tab')) as fd:
            d = ternip.formats.tempeval2(fd.read(), 'ABC1')
        self.assertEquals('ABC1', d.docid)
        self.assertEquals([[('The', 'DT', set()), ('first', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())], [('The', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]], d.get_sents())
    
    def test_load_multi(self):
        with open(self.filepath('base-segmentation-multi.tab')) as fd:
            ds = ternip.formats.tempeval2.load_multi(fd.read(), '')
        self.assertEquals(2, len(ds))
        self.assertTrue('ABC1' in [d.docid for d in ds])
        self.assertTrue('ABC2' in [d.docid for d in ds])
    
    def test_extents(self):
        t1 = ternip.timex(id=1)
        t2 = ternip.timex(id=2)
        sents = [[('The', 'DT', set()), ('first', 'JJ', set([t1])), ('sentence', 'NN', set()), ('.', '.', set())], [('The', 'DT', set()), ('second', 'JJ', set([t2])), ('sentence', 'NN', set([t2])), ('.', '.', set())]]
        d = ternip.formats.tempeval2.create(sents, 'ABC1')
        with open(self.filepath('timex-extents.tab')) as fd:
            self.assertEquals(sorted(d.get_extents().splitlines()), sorted(fd.read().splitlines()))
    
    def test_attr(self):
        t1 = ternip.timex(id=1, type='date')
        t2 = ternip.timex(id=2)
        t3 = ternip.timex(id=3)
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
        sents = [[('The', 'DT', set()), ('first', 'JJ', set([t1])), ('sentence', 'NN', set()), ('.', '.', set())], [('The', 'DT', set()), ('second', 'JJ', set([t2])), ('sentence', 'NN', set([t2])), ('.', '.', set([t3]))]]
        d = ternip.formats.tempeval2.create(sents, 'ABC1')
        with open(self.filepath('timex-attr.tab')) as fd:
            self.assertEquals(sorted(d.get_attrs().splitlines()), sorted(fd.read().splitlines()))

    def filepath(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)