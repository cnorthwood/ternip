import unittest
from ternip.timex import Timex
from ternip.rule_engine.normalisation_rule import NormalisationRule
from ternip.rule_engine.normalisation_rule_block import NormalisationRuleBlock
from ternip.rule_engine.rule_engine import RuleLoadError

class NormalisationRuleBlockTest(unittest.TestCase):
    
    def testApplyAll(self):
        rules = [NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyAll1', r'{#2} + "01" + {#1}'),
                 NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyAll2', r'{#2} + "02" + {#1}')]
        b = NormalisationRuleBlock(None, [], 'all', rules)
        t = Timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', {t}), ('th', 'POS', {t}), ('January', 'POS', {t}), ('1996', 'POS', {t})], [], [])[0])
        self.assertEquals(t.value, '19960206')
    
    def testApplyUntilSuccess1(self):
        rules = [NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess1A', r'{#2} + "01" + {#1}'),
                 NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess1B', r'{#2} + "02" + {#1}')]
        b = NormalisationRuleBlock(None, [], 'until-success', rules)
        t = Timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', {t}), ('th', 'POS', {t}), ('January', 'POS', {t}), ('1996', 'POS', {t})], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testApplyUntilSuccess2(self):
        rules = [NormalisationRule(r'<(\d+)~.+><th~.+><February~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess2A', r'{#2} + "02" + {#1}'),
                 NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess2B', r'{#2} + "01" + {#1}')]
        b = NormalisationRuleBlock(None, [], 'until-success', rules)
        t = Timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', {t}), ('th', 'POS', {t}), ('January', 'POS', {t}), ('1996', 'POS', {t})], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testRaiseError(self):
        rules = [NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testRaiseError1', r'{#2} + "01" + {#1}'),
                 NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testRaiseError2', r'{#2} + "02" + {#1}')]
        self.assertRaises(RuleLoadError, NormalisationRuleBlock, None, [], 'invalid', rules)