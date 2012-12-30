import os.path
import unittest
from ternip.rule_engine.normalisation_rule_engine import NormalisationRuleEngine
from ternip.rule_engine.rule_engine import RuleLoadErrors
from ternip.timex import Timex

class NormalisationRuleEngineTest(unittest.TestCase):
    
    def testTag(self):
        e = NormalisationRuleEngine()
        e.load_rules(os.path.join(os.path.dirname(__file__), 'test_normalisation_rules'))
        t = Timex(type='date')
        e.annotate([[('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set()),
             ('06', 'POS', {t}),
             ('th', 'POS', {t}),
             ('January', 'POS', {t}),
             ('1996', 'POS', {t}),
             ('to', 'POS', set()),
             ('Atlanta', 'POS', set())]], '')
        self.assertEquals(t.value, '19960106')
    
    def testBadErrors(self):
        r = NormalisationRuleEngine()
        try:
            r.load_rules(os.path.join(os.path.dirname(__file__), 'test_normalisation_rules_malformed/'))
        except RuleLoadErrors as e:
            self.assertEquals(len(e.errors), 12, "These errors were raised: " + str(e))
        else:
            self.fail('No exceptions were raised/caught')