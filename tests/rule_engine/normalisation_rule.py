#!/usr/bin/env python

import unittest
from ternip import timex
from ternip.rule_engine import normalisation_rule

class normalisation_rule_Test(unittest.TestCase):
    
    def testApply(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}')
        t = timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testApplyInsensitive(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><january~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}')
        t = timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testNoApply(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><February~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}')
        t = timex(type='date')
        self.assertFalse(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, None)
    
    def testApplyCorrectType(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}')
        t = timex(type='time')
        self.assertFalse(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
    
    def testPosGuardAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  guards = [r'<on~.+><the~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testPosGuardBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  guards = [r'<a~.+><train~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])
        
    def testNegGuardAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  guards = [r'!<a~.+><train~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testNegGuardBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  guards = [r'!<on~.+><the~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])
        
    def testPosBeforeAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  before_guards = [r'<on~.+><the~.+>$'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testPosBeforeBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  before_guards = [r'<to~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])
        
    def testNegBeforeAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  before_guards = [r'!<to~.+><Atlanta~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testNegBeforeBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  before_guards = [r'!<a~.+><plane~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])
        
    def testPosAfterAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  after_guards = [r'<to~.+><Atlanta~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testPosAfterBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  after_guards = [r'<a~.+><plane~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])
        
    def testNegAfterAllows(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  after_guards = [r'!<a~.+><plane~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertTrue(rule.apply(t, '', '', body, before, after)[0])
        self.assertEquals(t.value, '19960106')
    
    def testNegAfterBlocks(self):
        rule = normalisation_rule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', None, r'{#2} + "01" + {#1}',
                                  after_guards = [r'!<to~.+><Atlanta~.+>'])
        t = timex(type='date')
        (before, body, after) = (
            [('We', 'POS', set()),
             ('took', 'POS', set()),
             ('a', 'POS', set()),
             ('plane', 'POS', set()),
             ('on', 'POS', set()),
             ('the', 'POS', set())],
            [('06', 'POS', set()),
             ('th', 'POS', set()),
             ('January', 'POS', set()),
             ('1996', 'POS', set())],
            [('to', 'POS', set()),
             ('Atlanta', 'POS', set())]
        )
        self.assertFalse(rule.apply(t, '', '', body, before, after)[0])