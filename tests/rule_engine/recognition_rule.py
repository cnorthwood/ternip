#!/usr/bin/env python

import unittest
from ternip.rule_engine.recognition_rule import recognition_rule

class recognition_rule_Test(unittest.TestCase):
    
    def testMatch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testMatchAppends(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set([None]))])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,2], 'actual result was '+str(sent))
    
    def testPosGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'<plane~.+>'])
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testPosGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'<train~.+>'])
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testNegGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'!<plane~.+>'])
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testNegGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test',
                                guards=[r'!<train~.+>'])
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testMatchMulti(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('afternoon', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
    
    def testMatchMultiMiddle(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set()),
                           ('afternoon', 'POS', set()),
                           ('for', 'POS', set()),
                           ('Atlanta', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1,0,0], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
    
    def testNoMatch(self):
        rule = recognition_rule(r'<Thursday~.+>', 'date', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testMatchSquelch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', 'test', squelch=True)
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set([None]))])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testMatchInsensitive(self):
        rule = recognition_rule(r'<friday~.+>', 'date', 'test')
        sent = rule.apply([('the', 'POS', set()),
                           ('plane', 'POS', set()),
                           ('leaves', 'POS', set()),
                           ('on', 'POS', set()),
                           ('Friday', 'POS', set())])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))