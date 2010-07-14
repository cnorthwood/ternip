#!/usr/bin/env python

import unittest
import xml.dom.minidom

import ternip.formats

class timex3_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = ternip.formats.timex3('<root>This is some <TIMEX3 attr="timex">annotated <TIMEX3>embedded annotated </TIMEX3>text</TIMEX3>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())