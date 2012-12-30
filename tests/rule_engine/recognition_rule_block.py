#!/usr/bin/env python

import unittest
from ternip.rule_engine.recognition_rule import RecognitionRule
from ternip.rule_engine.recognition_rule_block import RecognitionRuleBlock
from ternip.rule_engine.rule_engine import RuleLoadError

class RecognitionRuleBlockTest(unittest.TestCase):
    
    def testApplyAll(self):
        rules = [RecognitionRule(r'<Thursday~.+>', 'date', 'test'),
                 RecognitionRule(r'<Friday~.+>', 'date', 'test2')]
        b = RecognitionRuleBlock(None, [], 'all', rules)
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
        rules = [RecognitionRule(r'<Thursday~.+>', 'date', 'test'),
                 RecognitionRule(r'<Friday~.+>', 'date', 'test2')]
        b = RecognitionRuleBlock(None, [], 'until-success', rules)
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
        rules = [RecognitionRule(r'<Thursday~.+>', 'date', 'test'),
                 RecognitionRule(r'<Friday~.+>', 'date', 'test2')]
        self.assertRaises(RuleLoadError, RecognitionRuleBlock, None, [], 'invalid', rules)