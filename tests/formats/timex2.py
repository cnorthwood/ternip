#!/usr/bin/env python

import unittest
import xml.dom.minidom

import ternip.formats
import ternip

class timex2_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = ternip.formats.timex2('<root>This is some <TIMEX2 attr="timex">annotated <TIMEX2>embedded annotated </TIMEX2>text</TIMEX2>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())
    
    def test_reconcile_TIMEX(self):
        s = ternip.formats.timex2('<root>This is some annotated text.</root>')
        t = ternip.timex(type='date')
        t.value = "20100710"
        t.mod = "BEFORE"
        t.freq = "1M"
        t.comment = "Test"
        t.granuality = "1D"
        t.non_specific = True
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t])), ('annotated', 'POS', set([t])), ('text', 'POS', set([t])), ('.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is <TIMEX2 VAL="20100710" MOD="BEFORE" PERIODICITY="F1M" COMMENT="Test" GRANUALITY="G1D" NON_SPECIFIC="YES">some annotated text</TIMEX2>.</root>').toxml())
    
    def test_reconcile_TIMEX_SET(self):
        s = ternip.formats.timex2('<root>This is some annotated text.</root>')
        t = ternip.timex(type='set')
        t.value = "20100710"
        t.mod = "BEFORE"
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t])), ('annotated', 'POS', set([t])), ('text', 'POS', set([t])), ('.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is <TIMEX2 VAL="20100710" MOD="BEFORE" SET="YES">some annotated text</TIMEX2>.</root>').toxml())