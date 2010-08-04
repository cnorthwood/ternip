#!/usr/bin/env python

import ternip
import unittest
from ternip import timex
from ternip.rule_engine import normalisation_rule

class warning_hider:
    
    def __init__(self):
        self.num = 0
    
    def parse_warning(self, message, e):
        self.num += 1

class warning_Test(unittest.TestCase):
    
    def setUp(self):
        # Set up warning handler
        self.w = warning_hider()
        ternip.warn = self.w.parse_warning
    
    def test_warn(self):
        # Do something that generates a warning
        t = timex()
        r = normalisation_rule('test', value='non_existent_function()')
        r.apply(t, '', '', [('test', 'POS', set([t]))], [], [])
        self.assertEquals(1, self.w.num)
    
    def tearDown(self):
        ternip.warn = ternip._warn