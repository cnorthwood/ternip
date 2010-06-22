#!/usr/bin/env python

import unittest
import ternip.rule_engine

class recognition_rule_engine_Test(unittest.TestCase):
    
    def testTag(self):
        e = ternip.rule_engine.recognition_rule_engine('tests/rule_engine/test_recognition_rules/')
        tagged = e.tag([[('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('on', 'POS'), ('Friday', 'POS')],
                        [('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('last', 'POS'), ('Thursday', 'POS')]])
        self.assertEquals([[len(s[2]) for s in sent] for sent in tagged], [[0,0,0,0,1],[0,0,0,0,0]], 'actual result was '+str([[len(s[2]) for s in sent] for sent in tagged]))