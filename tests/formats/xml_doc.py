#!/usr/bin/env python

import unittest
import ternip.formats.xml_doc
import xml.dom.minidom

class _xml_doc(ternip.formats.xml_doc.xml_doc):
    
    _timex_tag_name = 'TIMEX'
    
    def _timex_from_node(self, node):
        return ternip.timex()
    
    def _annotate_node_from_timex(self, timex, node):
        pass
    
    @staticmethod
    def create(sents, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, 'root', None)
        
        # Add text to document
        _xml_doc._add_words_to_node_from_sents(doc, doc.documentElement, sents, tok_offsets)
        
        # Create a document with just text nodes
        x = _xml_doc(doc)
        
        # Now reconcile to add the S, LEX and TIMEX tags
        x.reconcile(sents, add_S, add_LEX, pos_attr)
        
        return x

class xml_doc_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = _xml_doc('<root>This is some <TIMEX attr="timex">annotated <TIMEX>embedded annotated </TIMEX>text</TIMEX>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())
    
    def test_to_sents(self):
        t = _xml_doc('<root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>. This is the second sentence.</root>')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('some', 'DT', set()), ('annotated', 'VBN', set()), ('embedded', 'VBN', set()), ('annotated', 'VBN', set()), ('text', 'NN', set()), ('.', '.', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_only_node(self):
        t = _xml_doc('<root>This is outside of the body. <body>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>. This is the second sentence.</body></root>', nodename='body')
        self.assertEquals(t.get_sents(), [[('This', 'DT', set()), ('is', 'VBZ', set()), ('some', 'DT', set()), ('annotated', 'VBN', set()), ('embedded', 'VBN', set()), ('annotated', 'VBN', set()), ('text', 'NN', set()), ('.', '.', set())], [('This', 'DT', set()), ('is', 'VBZ', set()), ('the', 'DT', set()), ('second', 'JJ', set()), ('sentence', 'NN', set()), ('.', '.', set())]])
    
    def test_to_sents_only_single_node(self):
        self.assertRaises(ternip.formats.xml_doc.bad_node_name_error, _xml_doc, '<root>This is outside of the body. <body>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>. This is the second sentence.</body><body>Oh dear.</body></root>', nodename='body')
    
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
    
    def test_reconcile_S(self):
        t = _xml_doc('<root>This is some annotated text.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s>This is some annotated text.</s></root>').toxml())
    
    def test_reconcile_S_strip(self):
        t = _xml_doc('<root><t>This is some annotated text.</t> <t>This is a second sentence.</t></root>', has_S='t')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set()),
                      ('This', 'POS', set()), ('is', 'POS', set())], [('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s>This is some annotated text. This is</s> <s>a second sentence.</s></root>').toxml())
    
    def test_reconcile_2S(self):
        t = _xml_doc('<root>This is some annotated text. This is a second sentence.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                     [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s>This is some annotated text.</s> <s>This is a second sentence.</s></root>').toxml())
    
    def test_reconcile_2S1(self):
        t = _xml_doc('<root><reader>This is some annotated text.</reader> This is a second sentence.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                     [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><reader><s>This is some annotated text.</s></reader> <s>This is a second sentence.</s></root>').toxml())
    
    def test_reconcile_2S2(self):
        t = _xml_doc('<root><reader>This is some annotated</reader> text. This is a second sentence.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                     [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s><reader>This is some annotated</reader> text.</s> <s>This is a second sentence.</s></root>').toxml())
    
    def test_reconcile_2S3(self):
        t = _xml_doc('<root>This is some <reader>annotated</reader> text. This is a second sentence.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                     [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s>This is some <reader>annotated</reader> text.</s> <s>This is a second sentence.</s></root>').toxml())

    def test_reconcile_2S4(self):
        t = _xml_doc('<root><reader>This is some annotated text. This is a second sentence.</reader></root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                     [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]], add_S='s')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><reader><s>This is some annotated text.</s> <s>This is a second sentence.</s></reader></root>').toxml())
    
    def test_reconcile_2S5(self):
        s = _xml_doc('<root>This is some <p>annotated</p> text. This is <b>a second timex.</b></root>')
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text', 'POS', set()), ('.', 'POS', set())], [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('timex.', 'POS', set())]], add_S='s')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root><s>This is some <p>annotated</p> text.</s> <s>This is <b>a second timex.</b></s></root>').toxml())
    
    def test_reconcile_LEX_S(self):
        t = _xml_doc('<root>This is some annotated text.</root>')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())]], add_S='s', add_LEX='lex')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><s><lex>This</lex> <lex>is</lex> <lex>some</lex> <lex>annotated</lex> <lex>text.</lex></s></root>').toxml())
    
    def test_reconcile_LEX_strip(self):
        t = _xml_doc('<root><t>This</t> <t>is</t> <t>some</t> <t>annotated</t> <t>text</t><t>.</t></root>', has_LEX='t')
        t.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text', 'POS', set()), ('.', 'POS', set())]], add_LEX='lex')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><lex>This</lex> <lex>is</lex> <lex>some</lex> <lex>annotated</lex> <lex>text</lex><lex>.</lex></root>').toxml())
    
    def test_reconcile_POS(self):
        t = _xml_doc('<root>This is some annotated text.</root>')
        t.reconcile([[('This', 'POS1', set()), ('is', 'POS2', set()), ('some', 'POS3', set()), ('annotated', 'POS4', set()), ('text.', 'POS5', set())]], add_LEX='lex', pos_attr='pos')
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root><lex pos="POS1">This</lex> <lex pos="POS2">is</lex> <lex pos="POS3">some</lex> <lex pos="POS4">annotated</lex> <lex pos="POS5">text.</lex></root>').toxml())
    
    def test_reconcile_TIMEX(self):
        s = _xml_doc('<root>This is some annotated text.</root>')
        t = ternip.timex()
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t])), ('annotated', 'POS', set([t])), ('text', 'POS', set([t])), ('.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is <TIMEX>some annotated text</TIMEX>.</root>').toxml())
    
    def test_reconcile_TIMEX_S(self):
        s = _xml_doc('<root>This is some annotated text. This is a second timex.</root>')
        t1 = ternip.timex()
        t2 = ternip.timex()
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t1])), ('annotated', 'POS', set([t1])), ('text', 'POS', set([t1])), ('.', 'POS', set())], [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t2])), ('second', 'POS', set([t2])), ('timex.', 'POS', set([t2]))]], add_S='s')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root><s>This is <TIMEX>some annotated text</TIMEX>.</s> <s>This is <TIMEX>a second timex.</TIMEX></s></root>').toxml())
    
    def test_reconcile_TIMEX_S_start(self):
        s = _xml_doc('<root>This is some annotated text. This is a second timex.</root>')
        t1 = ternip.timex()
        t2 = ternip.timex()
        s.reconcile([[('This', 'POS', set([t1])), ('is', 'POS', set([t1])), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text', 'POS', set()), ('.', 'POS', set())], [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t2])), ('second', 'POS', set([t2])), ('timex.', 'POS', set([t2]))]], add_S='s')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root><s><TIMEX>This is</TIMEX> some annotated text.</s> <s>This is <TIMEX>a second timex.</TIMEX></s></root>').toxml())
    
    def test_reconcile_TIMEX_embedded(self):
        s = _xml_doc('<root>This is some <p>annotated</p> text. This is <b>a second timex.</b></root>')
        t1 = ternip.timex()
        t2 = ternip.timex()
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t1])), ('annotated', 'POS', set([t1])), ('text', 'POS', set([t1])), ('.', 'POS', set())], [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t2])), ('second', 'POS', set([t2])), ('timex.', 'POS', set([t2]))]], add_S='s')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root><s>This is <TIMEX>some <p>annotated</p> text</TIMEX>.</s> <s>This is <TIMEX><b>a second timex.</b></TIMEX></s></root>').toxml())
    
    def test_reconcile_TIMEX_embedded_nonconsuming(self):
        s = _xml_doc('<root>This is some <p>annotated</p> text. This is <b>a second timex.</b></root>')
        t1 = ternip.timex()
        t2 = ternip.timex()
        t3 = ternip.timex()
        t3.non_consuming = True
        s.reconcile([[('This', 'POS', set([t3])), ('is', 'POS', set()), ('some', 'POS', set([t1])), ('annotated', 'POS', set([t1])), ('text', 'POS', set([t1])), ('.', 'POS', set())], [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t2])), ('second', 'POS', set([t2])), ('timex.', 'POS', set([t2]))]], add_S='s')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root><s><TIMEX />This is <TIMEX>some <p>annotated</p> text</TIMEX>.</s> <s>This is <TIMEX><b>a second timex.</b></TIMEX></s></root>').toxml())
    
    def test_create_from_sents(self):
        s = _xml_doc.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                             [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is some annotated text. This is a second sentence.</root>').toxml())
    
    def test_create_from_sents_with_offsets(self):
        s = _xml_doc.create([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                             [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]],
                tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>  This is  some annotated   text.   This is  asecond sentence.</root>').toxml())
    
    def test_create_from_sents_with_offsets_tags(self):
        sents = [[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set()), ('annotated', 'POS', set()), ('text.', 'POS', set())],
                 [('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence.', 'POS', set())]]
        s = _xml_doc.create(sents, tok_offsets=[[2, 7, 11, 16, 28], [36, 41, 45, 46, 53]], add_S='s', add_LEX='lex', pos_attr='pos')
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>  <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">some</lex> <lex pos="POS">annotated</lex>   <lex pos="POS">text.</lex></s>   <s><lex pos="POS">This</lex> <lex pos="POS">is</lex>  <lex pos="POS">a</lex><lex pos="POS">second</lex> <lex pos="POS">sentence.</lex></s></root>').toxml())
        self.assertEquals(sents, s.get_sents())