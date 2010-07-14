#!/usr/bin/env python

import unittest
import xml.dom.minidom

import ternip.formats

class timex2_Test(unittest.TestCase):
    
    def test_strip_timexes(self):
        t = ternip.formats.timex2('<root>This is some <TIMEX2 attr="timex">annotated <TIMEX2>embedded annotated </TIMEX2>text</TIMEX2>.</root>')
        t.strip_timexes()
        self.assertEquals(str(t), xml.dom.minidom.parseString('<root>This is some annotated embedded annotated text.</root>').toxml())