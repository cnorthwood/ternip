#!/usr/bin/env python

import unittest
import ternip.rule_engine
import ternip

class normalisation_rule_engine_Test(unittest.TestCase):
    
    def testTag(self):
        e = ternip.rule_engine.normalisation_rule_engine()
        e.load_rules('tests/rule_engine/test_normalisation_rules/')
        t = ternip.timex(type='date')
        e.annotate([[('We', 'POS', []),
             ('took', 'POS', []),
             ('a', 'POS', []),
             ('plane', 'POS', []),
             ('on', 'POS', []),
             ('the', 'POS', []),
             ('06', 'POS', [t]),
             ('th', 'POS', [t]),
             ('January', 'POS', [t]),
             ('1996', 'POS', [t]),
             ('to', 'POS', []),
             ('Atlanta', 'POS', [])]])
        self.assertEquals(t.value, '19960106')
    
    def testBadErrors(self):
        r = ternip.rule_engine.normalisation_rule_engine()
        try:
            r.load_rules('tests/rule_engine/test_normalisation_rules_malformed/')
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 7, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')