#!/usr/bin/env python

import unittest
import ternip.formats
import ternip.timex
import xml.dom.minidom

class tern_Test(unittest.TestCase):
    
    def test_create_from_sents(self):
        s = ternip.formats.tern.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                                        [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], 'ABC123')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<DOC><DOCNO>ABC123</DOCNO><BODY><TEXT>This is some annotated text. This is a second sentence.</TEXT></BODY></DOC>').toxml())
    
    def test_create_from_sents_with_dct(self):
        s = ternip.formats.tern.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                                        [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], 'ABC123',
                                        dct='20100802')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<DOC><DOCNO>ABC123</DOCNO><DATE_TIME>08/02/2010</DATE_TIME><BODY><TEXT>This is some annotated text. This is a second sentence.</TEXT></BODY></DOC>').toxml())
    
    def test_create_from_sents_with_offsets(self):
        s = ternip.formats.tern.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                                        [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]],
                'ABC123',
                tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<DOC><DOCNO>ABC123</DOCNO><BODY><TEXT>  This is  some annotated   text.   This is  asecond sentence.</TEXT></BODY></DOC>').toxml())
    
    def test_create_from_sents_with_offsets_tags(self):
        sents = [[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                 [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]]
        s = ternip.formats.tern.create(sents, 'ABC123', tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]], add_S='s', add_LEX='lex', pos_attr='pos')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<DOC><DOCNO>ABC123</DOCNO><BODY><TEXT>  <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">some</lex> <lex pos="POS">annotated</lex>   <lex pos="POS">text.</lex></s>   <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">a</lex><lex pos="POS">second</lex> <lex pos="POS">sentence.</lex></s></TEXT></BODY></DOC>').toxml())
        self.assertEquals(sents, s.get_sents())
    
    def test_get_DCT_sents(self):
        d = ternip.formats.tern('<DOC><DOCNO>ABC123</DOCNO><DATE_TIME>20100801</DATE_TIME><BODY><TEXT>This is some annotated text. This is a second sentence.</TEXT></BODY></DOC>')
        self.assertEquals([[('20100801', 'CD', set())]], d.get_dct_sents())
    
    def test_reconcile_DCT_sents(self):
        d = ternip.formats.tern('<DOC><DOCNO>ABC123</DOCNO><DATE_TIME>20100801</DATE_TIME><BODY><TEXT>This is some annotated text. This is a second sentence.</TEXT></BODY></DOC>')
        s = d.get_dct_sents()
        t = ternip.timex()
        t.value = 'ABCDEF'
        s[0][0][2].add(t)
        d.reconcile_dct(s)
        self.assertEquals(str(d), xml.dom.minidom.parseString('<DOC><DOCNO>ABC123</DOCNO><DATE_TIME><TIMEX2 VAL="ABCDEF">20100801</TIMEX2></DATE_TIME><BODY><TEXT>This is some annotated text. This is a second sentence.</TEXT></BODY></DOC>').toxml())
        