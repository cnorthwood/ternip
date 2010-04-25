#!/usr/bin/env python

import sys
import itertools
import unittest
from timexdoc import TimexSpan
from timexval import *
from timexprenormval import PreNormVal, PreNormVal_point

# There is a question as to what kind of object resolution should return:
# - a span
# - a val string
# - a TimePoint
# In timexnorm, the reffn returns a TimePoint
# Here, it also returns a TimePoint

class TimexReferenceTracker(object):
    def __init__(self, timestamp, timexSpans,
                 refmodel=None):
        self.timestamp = timestamp
        self.points = [ (span.end, span) for span in timexSpans
                        if span.tmxclass == 'point' ]
        self.points = filter(lambda (end, span): span.val == '' or span.val is None or span.val[0].isdigit(),
                             self.points)
        self.points.sort()
        self.points.reverse()
        self.resolve = {
            'heuristic' : self.resolve_heuristic,
            'timestamp' : self.resolve_timestamp,
            'recent' : self.resolve_recent
            }.get(refmodel, self.resolve_heuristic)

    def resolve_timestamp(self, timex_span):
        return self.timestamp

    def resolve_recent(self, timex_span):
        if not timex_span.tmxclass == 'point':
            return None
        if timex_span.prenormval.ref_type == 'fq':
            return self.timestamp
        end = timex_span.end
        ref_unit = timex_span.prenormval.ref_unit
        for i, cand in itertools.dropwhile(lambda (i, s): i >= end,
                                           self.points):
            if cand.val:
                tref = TimePoint(cand.val)
                if ref_unit == 0 or \
                        cmpUnit(tref.specific_precision(), ref_unit) > -1:
                    return tref
        return self.timestamp

    def resolve_heuristic(self, timex_span):
        def antecedent(ref_unit, end):
            candidates = itertools.dropwhile(
                lambda (i, s): i >= end, self.points)
            try:
                i, cand = candidates.next()
            except StopIteration:
                return self.timestamp
            if not cand.val:
                return self.timestamp
            tref = TimePoint(cand.val)
            if ref_unit == 0 or \
                    cmpUnit(tref.specific_precision(), ref_unit) > -1:
                return tref
            else:
                return self.timestamp
        if not timex_span.tmxclass == 'point':
            return None
        end = timex_span.end
        prenormval = timex_span.prenormval
        reference = {
            'dex' : lambda ru, e: self.timestamp,
            'ana' : antecedent,
            'dem' : antecedent,
            'amb' : lambda ru, e: self.timestamp,
            'offdex' : lambda ru, e: self.timestamp,
            'offtoday' : lambda ru, e: self.timestamp,
            'offana' : antecedent,
            'offdem' : antecedent,
            'embedded': lambda ru, e: None,
            'fq' : lambda ru, e: self.timestamp
            }.get(prenormval.ref_type,
                  lambda ru, e: None)(prenormval.ref_unit, end)
        return reference


class TestTimexReferenceTracker(unittest.TestCase):
    def setUp(self):
        self.timestamp = TimePoint('2006-09-29')
        self.timexspans = [
            TimexSpan(1, 5,
                      parseNodeId=1,
                      txt='today',
                      val='2006-09-29',
                      tmxclass='point',
                      prenormval=PreNormVal_point(v=('dex', U_DAY, ''))),
            TimexSpan(7, 10,
                      parseNodeId=2,
                      val='',
                      tmxclass='recur',
                      prenormval=None), 
            TimexSpan(11, 20,
                      parseNodeId=3,
                      txt='last year',
                      val='2005',
                      tmxclass='point',
                      prenormval=PreNormVal_point(v=('dex', U_YEAR, ''))),
            TimexSpan(25, 27,
                      parseNodeId=4,
                      val='',
                      tmxclass='duration',
                      prenormval=None), 
            TimexSpan(21, 30,
                      parseNodeId=5,
                      txt='March',
                      val='2005-03',
                      tmxclass='point',
                      prenormval=PreNormVal_point(v=('ana', U_YEAR, 'XXXX-03'))),
            TimexSpan(35, 37,
                      parseNodeId=6,
                      val='',
                      tmxclass='gendur',
                      prenormval=None), 
            TimexSpan(31, 40,
                      parseNodeId=7,
                      txt='three days ago',
                      val='2006-09-26',
                      tmxclass='point',
                      prenormval=PreNormVal_point(v=('offdex', U_DAY, 3, ''))),
            TimexSpan(41, 50,
                      parseNodeId=8,
                      txt='one day later',
                      val='2006-09-27',
                      tmxclass='point',
                      prenormval=PreNormVal_point(v=('offana', U_DAY, 1, ''))) ]
        self.tracker = TimexReferenceTracker(self.timestamp, self.timexspans)

    def test_timestamp(self):
        for timex in self.timexspans:
            reference = self.tracker.resolve_timestamp(timex)
            self.assertEqual(reference, self.timestamp)

    def test_recent(self):
        for timex in self.timexspans:
            reference = self.tracker.resolve_recent(timex)
            if timex.parseNodeId in (2, 4, 6):
                self.assert_(reference is None)
            elif timex.parseNodeId == 1:
                self.assertEqual(reference, self.timestamp)
            elif timex.parseNodeId == 3:
                self.assertEqual(
                    reference.__str__(),
                    filter(lambda s: s.parseNodeId == 1,
                           self.timexspans)[0].val)
            elif timex.parseNodeId == 5:
                self.assertEqual(
                    reference.__str__(),
                    filter(lambda s: s.parseNodeId == 3,
                           self.timexspans)[0].val)
            elif timex.parseNodeId == 7:
                self.assertEqual(
                    reference.__str__(),
                    filter(lambda s: s.parseNodeId == 1,
                           self.timexspans)[0].val)
            elif timex.parseNodeId == 8:
                self.assertEqual(
                    reference.__str__(),
                    filter(lambda s: s.parseNodeId == 7,
                           self.timexspans)[0].val)

    def test_heuristic(self):
        for timex in self.timexspans:
            reference = self.tracker.resolve_heuristic(timex)
            if timex.parseNodeId in (2, 4, 6):
                self.assert_(reference is None)
            elif timex.parseNodeId in (1, 3, 7):
                self.assertEqual(reference, self.timestamp)
            else:
                if timex.parseNodeId == 5:
                    self.assertEqual(
                        reference.__str__(),
                        filter(lambda s: s.parseNodeId == 3,
                               self.timexspans)[0].val)
                elif timex.parseNodeId == 8:
                    self.assertEqual(
                        reference.__str__(),
                        filter(lambda s: s.parseNodeId == 7,
                               self.timexspans)[0].val)

if __name__ == '__main__':
    unittest.main()
