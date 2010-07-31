#!/usr/bin/env python

import unittest
from ternip import timex
from ternip.rule_engine import normalisation_rule, normalisation_rule_block, rule_load_error

class normalisation_rule_block_Test(unittest.TestCase):
    
    def testApplyAll(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyAll1', r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyAll2', r'{#2} + "02" + {#1}')]
        b = normalisation_rule_block(None, [], 'all', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960206')
    
    def testApplyUntilSuccess1(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess1A', r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess1B', r'{#2} + "02" + {#1}')]
        b = normalisation_rule_block(None, [], 'until-success', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testApplyUntilSuccess2(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><February~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess2A', r'{#2} + "02" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyUntilSuccess2B', r'{#2} + "01" + {#1}')]
        b = normalisation_rule_block(None, [], 'until-success', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testRaiseError(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testRaiseError1', r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testRaiseError2', r'{#2} + "02" + {#1}')]
        self.assertRaises(rule_load_error, normalisation_rule_block, None, [], 'invalid', rules)