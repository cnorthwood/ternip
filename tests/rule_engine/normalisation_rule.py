#!/usr/bin/env python

import unittest
from ternip.timex import Timex
from ternip.rule_engine.normalisation_rule import NormalisationRule

class normalisation_rule_Test(unittest.TestCase):
    
    def testApplyValue(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyValue', r'{#2} + "01" + {#1}')
        t = Timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testApplyChangeType(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyChangeType', change_type=r'"non-date"')
        t = Timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.type, 'non-date')
    
    def testApplyFreq(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyFreq', freq=r'"1D"')
        t = Timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.freq, '1D')
    
    def testApplyQuant(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyQuant', quant=r'"EVERY"')
        t = Timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.quant, 'EVERY')
    
    def testApplyInsensitive(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><january~.+><(\d{4})~.+>', 'date', 'testApplyInsensitive', r'{#2} + "01" + {#1}')
        t = Timex(type='date')
        self.assertTrue(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, '19960106')
    
    def testNoApply(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><February~.+><(\d{4})~.+>', 'date', 'testNoApply', r'{#2} + "01" + {#1}')
        t = Timex(type='date')
        self.assertFalse(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
        self.assertEquals(t.value, None)
    
    def testApplyCorrectType(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testApplyCorrectType', r'{#2} + "01" + {#1}')
        t = Timex(type='time')
        self.assertFalse(rule.apply(t, '', '', [('06', 'POS', set([t])), ('th', 'POS', set([t])), ('January', 'POS', set([t])), ('1996', 'POS', set([t]))], [], [])[0])
    
    def testPosGuardAllows(self):
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosGuardAllows', r'{#2} + "01" + {#1}',
                                  guards = [r'<th~.+><January~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosGuardBlocks', r'{#2} + "01" + {#1}',
                                  guards = [r'<th~.+><February~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegGuardAllows', r'{#2} + "01" + {#1}',
                                  guards = [r'!<th~.+><February~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegGuardBlocks', r'{#2} + "01" + {#1}',
                                  guards = [r'!<th~.+><January~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosBeforeAllows', r'{#2} + "01" + {#1}',
                                  before_guards = [r'<on~.+><the~.+>$'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosBeforeBlocks', r'{#2} + "01" + {#1}',
                                  before_guards = [r'<to~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegBeforeAllows', r'{#2} + "01" + {#1}',
                                  before_guards = [r'!<to~.+><Atlanta~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegBeforeBlocks', r'{#2} + "01" + {#1}',
                                  before_guards = [r'!<a~.+><plane~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosAfterAllows', r'{#2} + "01" + {#1}',
                                  after_guards = [r'<to~.+><Atlanta~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testPosAfterBlocks', r'{#2} + "01" + {#1}',
                                  after_guards = [r'<a~.+><plane~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegAfterAllows', r'{#2} + "01" + {#1}',
                                  after_guards = [r'!<a~.+><plane~.+>'])
        t = Timex(type='date')
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
        rule = NormalisationRule(r'<(\d+)~.+><th~.+><January~.+><(\d{4})~.+>', 'date', 'testNegAfterBlocks', r'{#2} + "01" + {#1}',
                                  after_guards = [r'!<to~.+><Atlanta~.+>'])
        t = Timex(type='date')
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