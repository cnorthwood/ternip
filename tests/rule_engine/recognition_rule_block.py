#!/usr/bin/env python

import unittest
import ternip.rule_engine

class recognition_rule_block_Test(unittest.TestCase):
    
    def testApplyAll(self):
        rules = [ternip.rule_engine.recognition_rule(r'<Thursday~.+>', 'date', 'test'),
                 ternip.rule_engine.recognition_rule(r'<Friday~.+>', 'date', 'test2')]
        b = ternip.rule_engine.recognition_rule_block(None, [], 'all', rules)
        (sent, success) = b.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Thursday', 'POS', set()),
                           ('and', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testApplyUntilSuccess(self):
        rules = [ternip.rule_engine.recognition_rule(r'<Thursday~.+>', 'date', 'test'),
                 ternip.rule_engine.recognition_rule(r'<Friday~.+>', 'date', 'test2')]
        b = ternip.rule_engine.recognition_rule_block(None, [], 'until-success', rules)
        (sent, success) = b.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Thursday', 'POS', set()),
                           ('and', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,0,0], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testRaiseError(self):
        rules = [ternip.rule_engine.recognition_rule(r'<Thursday~.+>', 'date', 'test'),
                 ternip.rule_engine.recognition_rule(r'<Friday~.+>', 'date', 'test2')]
        self.assertRaises(ternip.rule_engine.rule_load_error, ternip.rule_engine.recognition_rule_block, None, [], 'invalid', rules)