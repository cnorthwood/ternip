#!/usr/bin/env python

import unittest
import ternip.rule_engine

class recognition_rule_engine_Test(unittest.TestCase):
    
    def testTag(self):
        e = ternip.rule_engine.recognition_rule_engine()
        e.load_rules('tests/rule_engine/test_recognition_rules/')
        tagged = e.tag([[('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('on', 'POS'), ('Friday', 'POS')],
                        [('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('last', 'POS'), ('Thursday', 'POS')]])
        self.assertEquals([[len(s[2]) for s in sent] for sent in tagged], [[0,0,0,0,1],[0,0,0,0,0]], 'actual result was '+str([[len(s[2]) for s in sent] for sent in tagged]))
    
    def testBadErrors(self):
        r = ternip.rule_engine.recognition_rule_engine()
        try:
            r.load_rules('tests/rule_engine/test_recognition_rules_malformed/')
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 7, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testAfterAndDuplicateIDErrors(self):
        r = ternip.rule_engine.recognition_rule_engine()
        try:
            r.load_rules('tests/rule_engine/test_recognition_rules_after/')
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 2, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testCircularErrors(self):
        r = ternip.rule_engine.recognition_rule_engine()
        try:
            r.load_rules('tests/rule_engine/test_recognition_rules_circular/')
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 2, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')
    
    def testLoadBlock(self):
        e = ternip.rule_engine.recognition_rule_engine()
        e.load_rules('tests/rule_engine/test_recognition_rule_blocks/')
        tagged = e.tag([[('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('on', 'POS'), ('Friday', 'POS')],
                        [('We', 'POS'), ('went', 'POS'), ('shopping', 'POS'), ('last', 'POS'), ('Thursday', 'POS')]])
        self.assertEquals([[len(s[2]) for s in sent] for sent in tagged], [[0,0,0,0,1],[0,0,0,0,0]], 'actual result was '+str([[len(s[2]) for s in sent] for sent in tagged]))
    
    def testBadBlockErrors(self):
        r = ternip.rule_engine.recognition_rule_engine()
        try:
            r.load_rules('tests/rule_engine/test_recognition_rule_blocks_malformed/')
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 4, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')