#!/usr/bin/env python

import unittest
import os.path
from ternip.rule_engine.recognition_rule_engine import RecognitionRuleEngine
from ternip.rule_engine.rule_engine import RuleLoadErrors

class RecognitionRuleEngineTest(unittest.TestCase):
    
    def testTag(self):
        e = RecognitionRuleEngine()
        e.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rules/'))
        tagged = e.tag([[('We', 'POS', set()), ('went', 'POS', set()), ('shopping', 'POS', set()), ('on', 'POS', set()), ('Friday', 'POS', set())],
                        [('We', 'POS', set()), ('went', 'POS', set()), ('shopping', 'POS', set()), ('last', 'POS', set()), ('Thursday', 'POS', set())]])
        self.assertEquals([[len(s[2]) for s in sent] for sent in tagged], [[0,0,0,0,1],[0,0,0,0,0]], 'actual result was '+str([[len(s[2]) for s in sent] for sent in tagged]))
    
    def testBadErrors(self):
        r = RecognitionRuleEngine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rules_malformed/'))
        except RuleLoadErrors as e:
            self.assertEquals(len(e.errors), 12, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testAfterAndDuplicateIDErrors(self):
        r = RecognitionRuleEngine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rules_after/'))
        except RuleLoadErrors as e:
            self.assertEquals(len(e.errors), 2, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testCircularErrors(self):
        r = RecognitionRuleEngine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rules_circular/'))
        except RuleLoadErrors as e:
            self.assertEquals(len(e.errors), 2, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testLoadBlock(self):
        e = RecognitionRuleEngine()
        e.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rule_blocks/'))
        tagged = e.tag([[('We', 'POS', set()), ('went', 'POS', set()), ('shopping', 'POS', set()), ('on', 'POS', set()), ('Friday', 'POS', set())],
                        [('We', 'POS', set()), ('went', 'POS', set()), ('shopping', 'POS', set()), ('last', 'POS', set()), ('Thursday', 'POS', set())]])
        self.assertEquals([[len(s[2]) for s in sent] for sent in tagged], [[0,0,0,0,1],[0,0,0,0,0]], 'actual result was '+str([[len(s[2]) for s in sent] for sent in tagged]))
    
    def testBadBlockErrors(self):
        r = RecognitionRuleEngine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_recognition_rule_blocks_malformed/'))
        except RuleLoadErrors as e:
            self.assertEquals(len(e.errors), 9, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')