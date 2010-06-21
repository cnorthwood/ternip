#!/usr/bin/env python

import unittest
from ternip.rule_engine.recognition_rule import recognition_rule

class recognition_rule_Test(unittest.TestCase):
    
    def testMatch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date')
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testMatchAppends(self):
        rule = recognition_rule(r'<Friday~.+>', 'date')
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [None])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,2], 'actual result was '+str(sent))
    
    def testPosGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date',
                                guards=[r'<plane~.+>'])
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testPosGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date',
                                guards=[r'<train~.+>'])
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testNegGuard1(self):
        rule = recognition_rule(r'<Friday~.+>', 'date',
                                guards=[r'!<plane~.+>'])
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testNegGuard2(self):
        rule = recognition_rule(r'<Friday~.+>', 'date',
                                guards=[r'!<train~.+>'])
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1], 'actual result was '+str(sent))
    
    def testMatchMulti(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time')
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', []),
                           ('afternoon', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
    
    def testMatchMultiMiddle(self):
        rule = recognition_rule(r'<Friday~.+><afternoon~.+>', 'time')
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', []),
                           ('afternoon', 'POS', []),
                           ('for', 'POS', []),
                           ('Atlanta', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,1,1,0,0], 'actual result was '+str(sent))
        self.assertEquals(sent[4][2], sent[5][2])
    
    def testNoMatch(self):
        rule = recognition_rule(r'<Thursday~.+>', 'date')
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))
    
    def testMatchSquelch(self):
        rule = recognition_rule(r'<Friday~.+>', 'date', squelch=True)
        sent = rule.apply([('the', 'POS', []),
                           ('plane', 'POS', []),
                           ('leaves', 'POS', []),
                           ('on', 'POS', []),
                           ('Friday', 'POS', [None])])
        self.assertEquals([len(s[2]) for s in sent], [0,0,0,0,0], 'actual result was '+str(sent))