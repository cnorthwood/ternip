#!/usr/bin/env python

import unittest
import xml.dom.minidom

import ternip.formats

class timex3_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = ternip.formats.timex3('<root>This is some <TIMEX3 attr="timex">annotated <TIMEX3>embedded annotated </TIMEX3>text</TIMEX3>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())
    
    def test_reconcile_TIMEX(self):
        s = ternip.formats.timex3('<root>This is some annotated text.</root>')
        t = ternip.timex(type='date')
        t1 = ternip.timex(id=1)
        t2 = ternip.timex(id=2)
        t3 = ternip.timex(id=3)
        t.value = "20100710"
        t.id = 6
        t.mod = "BEFORE"
        t.freq = "1M"
        t.comment = "Test"
        t.granuality = "1D"
        t.non_specific = True
        t.quant = 'EVERY'
        t.temporal_function = True
        t.document_role = 'MODIFICATION_TIME'
        t.begin_timex = t1
        t.end_timex = t2
        t.context = t3
        s.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('some', 'POS', set([t])), ('annotated', 'POS', set([t])), ('text', 'POS', set([t])), ('.', 'POS', set())]])
        self.assertEquals(str(s), xml.dom.minidom.parseString('<root>This is <TIMEX3 tid="t6" beginPoint="t1" endPoint="t2" anchorTimeID="t3" functionInDocument="MODIFICATION_TIME" temporalFunction="true" type="DATE" value="20100710" mod="BEFORE" freq="1M" comment="Test" quant="EVERY">some annotated text</TIMEX3>.</root>').toxml())
    
    #def test_timex_to_sents(self):
    #    d = ternip.formats.timex3('<root>This is <TIMEX3 tid="t6" beginPoint="t1" endPoint="t2" anchorTimeID="t3" functionInDocument="MODIFICATION_TIME" temporalFunction="true" type="DATE" value="20100710" mod="BEFORE" freq="1M" comment="Test" quant="EVERY">some annotated text</TIMEX3>.</root>')
    #    s = d.get_sents()
    #    t = s[0][2][2].pop()
    #    self.assertEquals(t.value, "20100710")
    #    self.assertEquals(t.id, 6)
    #    self.assertEquals(t.mod, "BEFORE")
    #    self.assertEquals(t.freq, "1M")
    #    self.assertEquals(t.comment, "Test")
    #    self.assertEquals(t.granuality, "1D")
    #    self.assertEquals(t.non_specific, True)
    #    self.assertEquals(t.quant, 'EVERY')
    #    self.assertEquals(t.temporal_function, True)
    #    self.assertEquals(t.document_role, 'MODIFICATION_TIME')
    #    self.assertEquals(t.begin_timex, t1)
    #    self.assertEquals(t.end_timex, t2)
    #    self.assertEquals(t.context, t3)