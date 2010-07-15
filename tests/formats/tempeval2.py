#!/usr/bin/env python

import ternip.formats
import unittest
import os.path

class tempeval2_test(unittest.TestCase):
    
    def test_get_sents(self):
        with open(os.path.normpath('tests/formats/base-segmentation-single.tab')) as fd:
            d = ternip.formats.tempeval2(fd.read(), 'ABC1')
        self.assertEquals('ABC1', d.docid)
        self.assertEquals([[('The', 'DT', set()), ('first', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())], [('The', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]], d.get_sents())
    
    def test_load_multi(self):
        with open(os.path.normpath('tests/formats/base-segmentation-multi.tab')) as fd:
            ds = ternip.formats.tempeval2.load_multi(fd.read())
        self.assertEquals(2, len(ds))
        self.assertTrue('ABC1' in [d.docid for d in ds])
        self.assertTrue('ABC2' in [d.docid for d in ds])