#!/usr/bin/env python

import unittest
import ternip.formats.xml_doc
import xml.dom.minidom

class _xml_doc(ternip.formats.xml_doc.xml_doc):
    
    _timex_tag_name = 'FOO'

class xml_doc_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())
    
    def test_to_sents(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>. This is the second sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', []), ('is', 'VBZ', []), ('some', 'DT', []), ('annotated', 'VBN', []), ('embedded', 'VBN', []), ('annotated', 'VBN', []), ('text', 'NN', []), ('.', '.', [])], [('This', 'DT', []), ('is', 'VBZ', []), ('the', 'DT', []), ('second', 'JJ', []), ('sentence', 'NN', []), ('.', '.', [])]])
    
    def test_to_sents_tag_crossing_sentence_boundary(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text. This is the second </FOO>sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', []), ('is', 'VBZ', []), ('some', 'DT', []), ('annotated', 'VBN', []), ('embedded', 'VBN', []), ('annotated', 'VBN', []), ('text', 'NN', []), ('.', '.', [])], [('This', 'DT', []), ('is', 'VBZ', []), ('the', 'DT', []), ('second', 'JJ', []), ('sentence', 'NN', []), ('.', '.', [])]])
    
    def test_to_sents_tag_whole_sentence(self):
        t = _xml_doc('<root><a>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text. </FOO></a>This is the second sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', []), ('is', 'VBZ', []), ('some', 'DT', []), ('annotated', 'VBN', []), ('embedded', 'VBN', []), ('annotated', 'VBN', []), ('text', 'NN', []), ('.', '.', [])], [('This', 'DT', []), ('is', 'VBZ', []), ('the', 'DT', []), ('second', 'JJ', []), ('sentence', 'NN', []), ('.', '.', [])]])
    
    def test_to_sents_s_tags(self):
        t = _xml_doc('<root><s>This is sentence 1. This is the</s> <s>second sentence.</s></root>', has_S='s')
        self.assertEquals(t.get_sents(), [[('This', 'DT', []), ('is', 'VBZ', []), ('sentence', 'NN', []), ('1.', 'CD', []), ('This', 'DT', []), ('is', 'VBZ', []), ('the', 'DT', [])], [('second', 'JJ', []), ('sentence', 'NN', []), ('.', '.', [])]])
    
    def test_to_sents_lex_tags(self):
        t = _xml_doc('<root><s><lex>This</lex> <lex>is</lex> <lex>sentence 1.</lex> <lex>This</lex> <lex>is</lex> <lex>the</lex></s> <s><lex>second</lex> <lex>sentence.</lex></s></root>', has_S='s', has_LEX='lex')
        self.assertEquals(t.get_sents(), [[('This', 'DT', []), ('is', 'VBZ', []), ('sentence 1.', 'NNP', []), ('This', 'DT', []), ('is', 'VBZ', []), ('the', 'DT', [])], [('second', 'JJ', []), ('sentence.', 'NNP', [])]])
        
    def test_to_sents_pos_attr(self):
        t = _xml_doc('<root><s><lex pos="POS1">This</lex> <lex pos="POS1">is</lex> <lex pos="POS1">sentence 1</lex><lex pos="POS2">.</lex> <lex pos="POS1">This</lex> <lex pos="POS1">is</lex> <lex pos="POS1">the</lex></s> <s><lex pos="POS1">second</lex> <lex pos="POS1">sentence.</lex></s></root>', has_S='s', has_LEX='lex', pos_attr='pos')
        self.assertEquals(t.get_sents(), [[('This', 'POS1', []), ('is', 'POS1', []), ('sentence 1', 'POS1', []), ('.', 'POS2', []), ('This', 'POS1', []), ('is', 'POS1', []), ('the', 'POS1', [])], [('second', 'POS1', []), ('sentence.', 'POS1', [])]])