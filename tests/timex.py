#!/usr/bin/env python

import unittest
from ternip.timex import Timex, add_timex_ids

class TimexTest(unittest.TestCase):
    
    def test_assign_IDs(self):
        # Get some sample IDs
        ts = set([Timex(), Timex(), Timex()])
        add_timex_ids(ts)
        
        # Get the assigned IDs
        tids = set()
        for t in ts:
            tids.add(t.id)
        
        # Should be exactly 3 unique IDs
        self.assertEquals(len(tids), 3)
        
        # Should be consecutive
        self.assertTrue(1 in tids)
        self.assertTrue(2 in tids)
        self.assertTrue(3 in tids)
    
    def test_assign_IDs_no_reassign(self):
        # Get some sample IDs
        ts = set([Timex(), Timex(), Timex()])
        at = Timex()
        at.id = 6
        ts.add(at)
        add_timex_ids(ts)
        
        # Get the assigned IDs
        tids = set()
        for t in ts:
            tids.add(t.id)
        
        # Should be exactly 4 unique IDs and pre-assigned one hasn't changed
        self.assertEquals(len(tids), 4)
        self.assertEquals(6, at.id)
        
        # Should be consecutive for new ones
        self.assertTrue(1 in tids)
        self.assertTrue(2 in tids)
        self.assertTrue(3 in tids)
        self.assertTrue(6 in tids)
    
    def test_assign_IDs_consecutive(self):
        # Get some sample IDs
        ts = set([Timex(), Timex(), Timex()])
        at = Timex()
        at.id = 2
        ts.add(at)
        add_timex_ids(ts)
        
        # Get the assigned IDs
        tids = set()
        for t in ts:
            tids.add(t.id)
        
        # Should be exactly 4 unique IDs and pre-assigned one hasn't changed
        self.assertEquals(len(tids), 4)
        self.assertEquals(2, at.id)
        
        # Should be consecutive for new ones
        self.assertTrue(1 in tids)
        self.assertTrue(2 in tids)
        self.assertTrue(3 in tids)
        self.assertTrue(4 in tids)