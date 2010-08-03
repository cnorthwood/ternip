#!/usr/bin/env python

import unittest
from ternip.rule_engine import recognition_rule

class recognition_rule_Test(unittest.TestCase):
    
    def testMatch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testMatchCaseSensitive1(self):
        rule = recognition_rule(r'<wednesday~.+>', 'date', 'test', case_sensitive=True)
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Wednesday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testMatchCaseSensitive2(self):
        rule = recognition_rule(r'<wednesday~.+>', 'date', 'test', case_sensitive=True)
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('wednesday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testMatchAppends(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set([None]))])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,2], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'<plane~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'<train~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'!<plane~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'!<train~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testMatchMulti(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('afternoon', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
        self.assertTrue(success)
    
    def testMatchMultiMiddle(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('afternoon', 'POS', set()),
                           ('for', 'POS', set()),
                           ('Atlanta', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1,0,0], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
        self.assertTrue(success)
    
    def testNoMatch(self):
        rule = recognition_rule(r'<Thursday~.+>', 'date', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testMatchSquelch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test', squelch=True)
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set([None]))])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testMatchInsensitive(self):
        rule = recognition_rule(r'<friday~.+>', 'date', 'test')
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosBefore1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                before_guards=[r'<last~.+>$'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('left', 'POS', set()),
                           ('last', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosBefore2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                before_guards=[r'<at~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('at', 'POS', set()),
                           ('2', 'POS', set()),
                           ('pm', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegBefore1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                before_guards=[r'!<next~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('next', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegBefore2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                before_guards=[r'!<next~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('left', 'POS', set()),
                           ('last', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('and', 'POS', set()),
                           ('next', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,0,0,0], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosAfter1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                after_guards=[r'^<for~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('for', 'POS', set()),
                           ('Atlanta', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,0,0], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testPosAfter2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                after_guards=[r'<plane~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegAfter1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                after_guards=[r'!<for~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('for', 'POS', set()),
                           ('Atlanta', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0,0,0], 'actual result was '+str(sent))
        self.assertFalse(success)
    
    def testNegAfter2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                after_guards=[r'!<plane~.+>'])
        (sent, success) = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('for', 'POS', set()),
                           ('Atlanta', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,0,0], 'actual result was '+str(sent))
        self.assertTrue(success)
    
    def testDeliminateNumbers1(self):
        rule = recognition_rule(r'NUM_START<twenty~.+><one~.+>NUM_END', 'date', 'test', deliminate_numbers=True)
        (sent, success) = rule.apply([('there', 'POS', set()), ('are', 'POS', set()), ('twenty', 'POS', set()), ('one', 'POS', set()), ('balloons', 'POS', set())])
        self.assertTrue(success)
    
    def testDeliminateNumbers2(self):
        rule = recognition_rule(r'NUM_START<twenty-one~.+>NUM_END', 'date', 'test', deliminate_numbers=True)
        (sent, success) = rule.apply([('there', 'POS', set()), ('are', 'POS', set()), ('twenty-one', 'POS', set()), ('balloons', 'POS', set())])
        self.assertTrue(success)
    
    def testDeliminateNumbers3(self):
        rule = recognition_rule(r'NUM_ORD_START<twenty~.+><first~.+>NUM_ORD_END', 'date', 'test', deliminate_numbers=True)
        (sent, success) = rule.apply([('this', 'POS', set()), ('is', 'POS', set()), ('the', 'POS', set()), ('twenty', 'POS', set()), ('first', 'POS', set()), ('balloon', 'POS', set())])
        self.assertTrue(success)
    
    def testDeliminateNumbers4(self):
        rule = recognition_rule(r'NUM_ORD_START<first~.+>NUM_ORD_ENDNUM_START<two~.+>NUM_END', 'date', 'test', deliminate_numbers=True)
        (sent, success) = rule.apply([('these', 'POS', set()), ('are', 'POS', set()), ('the', 'POS', set()), ('first', 'POS', set()), ('two', 'POS', set()), ('balloons', 'POS', set())])
        self.assertTrue(success)
    
    def testDeliminateNumbers5(self):
        rule = recognition_rule(r'NUM_START<two~.+><hundred~.+><and~.+><sixty~.+><eight~.+>NUM_END', 'date', 'test', deliminate_numbers=True)
        (sent, success) = rule.apply([('these', 'POS', set()), ('are', 'POS', set()), ('the', 'POS', set()), ('first', 'POS', set()), ('two', 'POS', set()), ('hundred', 'POS', set()), ('and', 'POS', set()), ('sixty', 'POS', set()), ('eight', 'POS', set()), ('balloons', 'POS', set())])
        self.assertTrue(success)