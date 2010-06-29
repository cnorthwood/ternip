#!/usr/bin/env python

import unittest
import ternip.rule_engine

class recognition_rule_engine_Test(unittest.TestCase):
    
    def testTag(self):
        e = ternip.rule_engine.normalisation_rule_engine()
        e.load_rules('tests/rule_engine/test_normalisation_rules/')
    
    def testBadErrors(self):
        r = ternip.rule_engine.normalisation_rule_engine()
        #try:
        #    r.load_rules('tests/rule_engine/test_normalisation_rules_malformed/')
        #except ternip.rule_engine.rule_load_errors as e:
        #    self.assertEquals(len(e.errors), 8, "These errors were raised: " + str(e))
        #else:
        #    self.fail('No exceptions were raised/caught')