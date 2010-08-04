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
    
    def test_warn(self):
        
        # Set up warning handler
        w = warning_hider()
        ternip.warn = w.parse_warning
        
        # Do something that generates a warning
        t = timex()
        r = normalisation_rule('test', value='non_existent_function()')
        r.apply(t, '', '', [('test', 'POS', set([t]))], [], [])
        self.assertEquals(1, w.num)