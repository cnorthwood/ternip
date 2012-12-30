#!/usr/bin/env python

import unittest
from ternip.formats.timeml import TimeMlDocument
import xml.dom.minidom

class TimeMlDocumentTest(unittest.TestCase):
    
    def test_create_from_sents(self):
        s = TimeMlDocument.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                                          [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<TimeML>This is some annotated text. This is a second sentence.</TimeML>').toxml())
    
    def test_create_from_sents_with_offsets(self):
        s = TimeMlDocument.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                                          [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]],
                tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<TimeML>  This is  some annotated   text.   This is  asecond sentence.</TimeML>').toxml())
    
    def test_create_from_sents_with_offsets_tags(self):
        sents = [[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                 [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]]
        s = TimeMlDocument.create(sents, tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]], add_S='s', add_LEX='lex', pos_attr='pos')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<TimeML>  <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">some</lex> <lex pos="POS">annotated</lex>   <lex pos="POS">text.</lex></s>   <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">a</lex><lex pos="POS">second</lex> <lex pos="POS">sentence.</lex></s></TimeML>').toxml())
        self.assertEquals(sents, s.get_sents())