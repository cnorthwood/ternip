#!/usr/bin/env python

import unittest
import ternip.formats.xml_doc
import xml.dom.minidom

class _xml_doc(ternip.formats.xml_doc.xml_doc):
    
    _timex_tag_name = 'TIMEX'
    
    def _timex_from_node(self, node):
        return ternip.timex()

class xml_doc_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = _xml_doc('<root>This is some <TIMEX attr="timex">annotated <TIMEX>embedded annotated </TIMEX>text</TIMEX>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())
    
    def test_to_sents(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>. This is the second sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('some', 'DT', set()), ('annotated', 'VBN', set()), ('embedded', 'VBN', set()), ('annotated', 'VBN', set()), ('text', 'NN', set()), ('.', '.', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_tag_crossing_sentence_boundary(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text. This is the second </FOO>sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('some', 'DT', set()), ('annotated', 'VBN', set()), ('embedded', 'VBN', set()), ('annotated', 'VBN', set()), ('text', 'NN', set()), ('.', '.', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_tag_whole_sentence(self):
        t = _xml_doc('<root><a>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text. </FOO></a>This is the second sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('some', 'DT', set()), ('annotated', 'VBN', set()), ('embedded', 'VBN', set()), ('annotated', 'VBN', set()), ('text', 'NN', set()), ('.', '.', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_s_tags(self):
        t = _xml_doc('<root><s>This is sentence 1. This is the</s> <s>second sentence.</s></root>', has_S='s')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('sentence', 'NN', set()), ('1.', 'CD', set()), ('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set())], [('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_lex_tags(self):
        t = _xml_doc('<root><s><lex>This</lex> <lex>is</lex> <lex>sentence 1.</lex> <lex>This</lex> <lex>is</lex> <lex>the</lex></s> <s><lex>second</lex> <lex>sentence.</lex></s></root>', has_S='s', has_LEX='lex')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('sentence 1.', 'NNP', set()), ('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set())], [('second', 'JJ', set()), ('sentence.', 'NNP', set())]])
    
    def test_to_sents_lex_tags_1sent(self):
        t = _xml_doc('<root><lex>This</lex> <lex>is</lex> <lex>sentence 1.</lex></root>', has_LEX='lex')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('sentence 1.', 'NNP', set())]])
    
    def test_to_sents_lex_tags_no_S(self):
        t = _xml_doc('<root><lex>This</lex> <lex>is</lex> <lex>sentence 1.</lex> <lex>This</lex> <lex>is</lex> <lex>the</lex> <lex>second</lex> <lex>sentence.</lex></root>', has_LEX='lex')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('sentence 1.', 'NNP', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence.', 'NNP', set())]])
    
    def test_to_sents_pos_attr(self):
        t = _xml_doc('<root><s><lex pos="POS1">This</lex> <lex pos="POS1">is</lex> <lex pos="POS1">sentence 1</lex><lex pos="POS2">.</lex> <lex pos="POS1">This</lex> <lex pos="POS1">is</lex> <lex pos="POS1">the</lex></s> <s><lex pos="POS1">second</lex> <lex pos="POS1">sentence.</lex></s></root>', has_S='s', has_LEX='lex', pos_attr='pos')
        self.assertEquals(t.get_sents(), [[('This', 'POS1', set()), ('is', 'POS1', set()), ('sentence 1', 'POS1', set()), ('.', 'POS2', set()), ('This', 'POS1', set()), ('is', 'POS1', set()), ('the', 'POS1', set())], [('second', 'POS1', set()), ('sentence.', 'POS1', set())]])
    
    def test_to_sents_timexes(self):
        t = _xml_doc('<root><s><lex pos="POS1">This</lex> <TIMEX><lex pos="POS1">is</lex> <TIMEX><lex pos="POS1">sentence 1</lex></TIMEX></TIMEX><lex pos="POS2">.</lex> <lex pos="POS1">This</lex> <lex pos="POS1">is</lex> <lex pos="POS1">the</lex></s> <s><TIMEX><lex pos="POS1">second</lex></TIMEX> <lex pos="POS1">sentence.</lex></s></root>', has_S='s', has_LEX='lex', pos_attr='pos')
        self.assertEquals([[len(timexes) for (tok, pos, timexes) in sent] for sent in t.get_sents()], [[0, 1, 2, 0, 0, 0, 0], [1, 0]])