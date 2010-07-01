#!/usr/bin/env python

import unittest
import ternip.formats.xml_doc

class _xml_doc(ternip.formats.xml_doc.xml_doc):
    
    _timex_tag_name = 'FOO'

class xml_doc_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = _xml_doc("""<?xml version="1.0" ?><root>This is some <FOO attr="timex">annotated <FOO>embedded annotated </FOO>text</FOO>.</root>""")
        t.strip_timexes()
        self.assertTrue(str(t).find("<root>This is some annotated embedded annotated text.</root>") > -1)