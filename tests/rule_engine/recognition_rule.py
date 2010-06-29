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