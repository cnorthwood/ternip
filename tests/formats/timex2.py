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
    
    #def test_reconcile_TIMEX(self):
    #    s = ternip.formats.timex2('<root>This is some annotated text.</root>')
    #    t = ternip.timex()
    #    t.value = "20100710"
    #    s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t])), ('annotated', 'POS', set([t])), ('text', 'POS', set([t])), ('.', 'POS', set())]])
    #    self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is <TIMEX2 val="20100710">some annotated text</TIMEX2>.</root>').toxml())