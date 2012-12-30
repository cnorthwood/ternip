#!/usr/bin/env python

import os.path
import unittest
import ternip.rule_engine
import ternip

class normalisation_rule_engine_Test(unittest.TestCase):
    
    def testTag(self):
        e = ternip.rule_engine.normalisation_rule_engine()
        e.load_rules(os.path.join(os.path.dirname(__file__), 'test_normalisation_rules'))
        t = ternip.timex(type='date')
        e.annotate([[('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set()),
             ('06', 'POS', set([t])),
             ('th', 'POS', set([t])),
             ('January', 'POS', set([t])),
             ('1996', 'POS', set([t])),
             ('to', 'POS', set()),
             ('Atlanta', 'POS', set())]], '')
        self.assertEquals(t.value, '19960106')
    
    def testBadErrors(self):
        r = ternip.rule_engine.normalisation_rule_engine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_normalisation_rules_malformed/'))
        except ternip.rule_engine.rule_load_errors as e:
            self.assertEquals(len(e.errors), 12, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')