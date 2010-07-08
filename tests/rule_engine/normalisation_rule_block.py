#!/usr/bin/env python

import unittest
from ternip import timex
from ternip.rule_engine import normalisation_rule, normalisation_rule_block, rule_load_error

class normalisation_rule_block_Test(unittest.TestCase):
    
    def testApplyAll(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "02" + {#1}')]
        b = normalisation_rule_block(None, [], 'all', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', [t]), ('th', 'POS', [t]), ('January', 'POS', [t]), ('1996', 'POS', [t])], [], [])[0])
        self.assertEquals(t.value, '19960206')
    
    def testApplyUntilSuccess1(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "02" + {#1}')]
        b = normalisation_rule_block(None, [], 'until-success', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', [t]), ('th', 'POS', [t]), ('January', 'POS', [t]), ('1996', 'POS', [t])], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testApplyUntilSuccess2(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><February~.+><(\d{4})~.+>', 'date', None, r'{#2} + "02" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}')]
        b = normalisation_rule_block(None, [], 'until-success', rules)
        t = timex(type='date')
        self.assertTrue(b.apply(t, '', '', [('06', 'POS', [t]), ('th', 'POS', [t]), ('January', 'POS', [t]), ('1996', 'POS', [t])], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testRaiseError(self):
        rules = [normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}'),
                 normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "02" + {#1}')]
        self.assertRaises(rule_load_error, normalisation_rule_block, None, [], 'invalid', rules)