#!/usr/bin/env python
"""Unit tests for the "timexval" module."""

import unittest
from operator import eq, lt
from timexval import *


class UnitOrderTestCase(unittest.TestCase):
    """Test precision ordering of units as reported by cmpUnit."""

    unitOrder = [
      U_ERA, U_MILLENNIUM, U_CENTURY, U_DECADE, U_YEAR, U_YEARPART,
      U_MONTH, U_WEEK, U_DAY, U_DAYPART, U_HOUR, U_MINUTE, U_SECOND ]

    def testunitorder(self):
        def sample(u1, u2, c):
            self.assertEqual(cmpUnit(u1, u2), c,
              'incorrect unit order: %s,%s' % (u1, u2))
        for i in range(len(self.unitOrder)):
            for j in range(len(self.unitOrder)):
                sample(self.unitOrder[i], self.unitOrder[j], cmp(i, j))
        for u in self.unitOrder:
            if u != U_YEARPART:
                c = cmpUnit(u, U_YEARPART)
                sample(u, U_HALFYEAR, c)
                sample(u, U_QUARTER, c)


class TimePointTestCase(unittest.TestCase):
    """Test the TimePoint class.
    This is more a regression test than a real functionality test,
    because in many cases it is not obvious what the correct behaviour
    should be."""

    valsamples = [
        ( 'BC',         U_ERA, U_ERA ),
        ( 'BC1',        U_YEAR, U_YEAR ),
        ( 'BC1234567',  U_YEAR, U_YEAR ),
        ( 'X',          U_MILLENNIUM, U_ERA ),
        ( 'XX',         U_CENTURY, U_ERA ),
        ( 'XXXX',       U_YEAR, U_ERA ),
        ( 'XXXX-WXX',   U_WEEK, U_ERA ),
        ( 'XXXX-XX-XX', U_DAY, U_ERA ),
        ( '1',          U_MILLENNIUM, U_MILLENNIUM ),
        ( '2X',         U_CENTURY, U_MILLENNIUM ),
        ( '3XXX-XX-XX', U_DAY, U_MILLENNIUM ),
        ( '12',         U_CENTURY, U_CENTURY ),
        ( '40X3-XX',    U_MONTH, U_CENTURY ),
        ( '160',        U_DECADE, U_DECADE ),
        ( '190X-W39',   U_WEEK, U_DECADE ),
        ( '0193',       U_YEAR, U_YEAR ),
        ( '1234-XX-XX', U_DAY, U_YEAR ),
        ( '1234-WXX-X', U_DAY, U_YEAR ),
        ( '1961-02-W04-X', U_DAY, U_WEEK ),
        ( '1961-FA-WXX', U_WEEK, U_YEARPART ),
        ( '2000-SP-WXX-4', U_DAY, U_YEARPART ),
        ( '2000-SP-W11-X', U_DAY, U_WEEK ),
        ( 'XXXX-WXX-3', U_DAY, U_ERA ),
        ( '199X-03-XX', U_DAY, U_DECADE ),
        ( '2000-09',    U_MONTH, U_MONTH ),
        ( '1979-08-21', U_DAY, U_DAY ),
        ( '2006-W35-5', U_DAY, U_DAY ),
        ( 'T18:15',     U_MINUTE, 0 ),
        ( 'XXXX-XX-XXTXX', U_HOUR, U_ERA ),
        ( 'TEV',        U_DAYPART, 0 ),
        ( '2006-09-01TEV', U_DAYPART, U_DAYPART ),
        ( '2006-09-01T17:14:03', U_SECOND, U_SECOND ),
        ( 'TXX:14:60',  U_SECOND, 0 ),
        ( 'TXX:XX:XX',  U_SECOND, 0 ),
        ( 'T18:14:59.99', U_SECOND, 0 ),
        ( '2006-09-04T18.5', U_HOUR, U_HOUR, '2006-09-04T18.50' ),
        ( '2006-09-05T09:55.25', U_MINUTE, U_MINUTE ),
        ( '2006-09-01T+02', U_DAY, U_DAY ),
        ( '2006-09-01T17+02', U_HOUR, U_HOUR ),
        ( '2006-09-01T15:21Z', U_MINUTE, U_MINUTE ),
        ( 'T18:35-0930', U_MINUTE, 0 ),
        ( 'T15:21:13+00', U_SECOND, 0, 'T15:21:13Z' ),
        ( 'T18:35+0200', U_MINUTE, 0, 'T18:35+02' ),
        ( 'T18:35+05:30', U_MINUTE, 0, 'T18:35+0530' ),
        ( '2006-QX', U_YEARPART, U_YEAR, '2006-QX' ) ]

    sortsamples = [
        ( 'BC',         eq, 'BC' ),
        ( 'BC700',      eq, 'BC' ),
        ( 'BC',         lt, 'X' ),
        ( 'BC',         lt, '2' ),
        ( 'BC',         lt, '1201' ),
        ( 'BC10000',    lt, 'BC500' ),
        ( 'X',          eq, '1961' ),
        ( 'X',          eq, '2006-09-05T10:55' ),
        ( '1',          lt, '2006-09-05' ),
        ( '19',         lt, '2XXX' ),
        ( '19XX',       eq, '198'  ),
        ( '18XX',       lt, '1978' ),
        ( '195',        eq, '1951' ),
        ( '1960',       lt, '1961' ),
        ( '1960',       eq, '1960-XX-XX' ),
        ( '2000-SP',    eq, '2000-05-05' ),
        ( '2000-08',    lt, '2000-FA' ),
        ( '2000-Q2',    lt, '2000-H2' ),
        ( '2000-03',    lt, '2000-04' ),
        ( '2000-W10',   eq, '2000-WI' ),
        ( '2000-W10',   eq, '2000-03-09' ),
        ( '2000-W13',   eq, '2000-03' ),
        ( '2000-W13',   eq, '2000-04' ),
        ( '2000-W11',   lt, '2000-04' ),
        ( '2000-W11',   lt, '2000-W12' ),
        ( '2000-W12-3', eq, '2000-W12' ),
        ( '2000-W12-WE', eq, '2000-W12-WE' ),
        ( '2000-W12-6', eq, '2000-W12-WE' ),
        ( '2000-W12-5', lt, '2000-W12-WE' ),
        ( '2000-W12-6', lt, '2000-W12-7' ),
        ( '2000-W10-4', eq, '2000-03-09' ),
        ( '2006-08-21', lt, '2006-W34-2' ),
        ( '2006-09-05T11:41', eq, '2006-09-05' ),
        ( '2006-09-05T11:41', eq, '2006-09-05TMO' ),
        ( '2006-09-05T11:41', lt, '2006-09-05TMI' ),
        ( '2006-09-05T11:41', lt, '2006-09-05T12:30' ),
        ( '2006-09-05T12:30', eq, '2006-09-05T12:30:51' ),
        ( '2006-09-05T12:30:00', lt, '2006-09-05T12:30:51' ) ]

    def testval(self):
        for test in self.valsamples:
            q = s = test[0]
            t = TimePoint(s)
            if len(test) > 3: q = test[3]
            self.assertEqual(str(t), q,
              'str() failed on ' + repr(s))
            self.assertEqual(t.precision(), test[1],
              'precision() failed on ' + repr(s))
            self.assertEqual(t.specific_precision(), test[2],
              'specific_precision() failed on ' + repr(s))

    def testsort(self):
        for (a, op, b) in self.sortsamples:
            ta = TimePoint(a)
            tb = TimePoint(b)
            x = ta.compare(tb)
            y = tb.compare(ta)
            self.failUnless(op(x, 0) and op(0, y),
              'compare() failed on ' + repr(a) + ',' + repr(b))

    def testmerge(self):
        for (x, y, z) in (
          ( '2006-09-05', 'T11:57', '2006-09-05T11:57' ),
          ( '2006-09', 'XXXX-WXX-5', '2006-09-WXX-5' ),
          ( '2006-W36-XT11+02', 'XXXX-WXX-2', '2006-09-05T11+02' ) ):
            t = TimePoint(x)
            t.merge(TimePoint(y))
            self.assertEqual(str(t), z,
              'merge() failed on ' + repr(x) + ',' + repr(y))

    def testtruncate(self):
        t = TimePoint('2006-09-05T13:19:12.21')
        for (u, v) in (
          (U_SECOND,  '2006-09-05T13:19:12'),
          (U_MINUTE,  '2006-09-05T13:19'),
          (U_HOUR,    '2006-09-05T13'),
          (U_DAY,     '2006-09-05'),
          (U_WEEK,    '2006-W36'),
          (U_MONTH,   '2006') ):
            t.truncate(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
        t = TimePoint('2006-09-05T13:19:12.21')
        for (u, v) in (
          (U_MONTH,   '2006-09'),
          (U_QUARTER, '2006-Q3'),
          (U_HALFYEAR,'2006-H2'),
          (U_YEAR,    '2006'),
          (U_DECADE,  '200'),
          (U_CENTURY, '20'),
          (U_MILLENNIUM,'2') ):
            t.truncate(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
        t = TimePoint('2006-W36-2')
        for (u, v) in (
          (U_MONTH, '2006-09'),
          (U_HALFYEAR, '2006-H2') ):
            t.truncate(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
        t = TimePoint('2006-W36')
        t.truncate(U_MONTH)
        self.assertEqual(str(t), '2006', repr(str(t)) + "!='2006'")

    def testextend(self):
        for (u, v) in (
          (U_MILLENNIUM,  '1'),
          (U_CENTURY,     '1X'),
          (U_DECADE,      '1XX'),
          (U_YEAR,        '1XXX'),
          (U_HALFYEAR,    '1XXX-HX'),
          (U_QUARTER,     '1XXX-QX'),
          (U_MONTH,       '1XXX-XX'),
          (U_WEEK,        '1XXX-WXX'),
          (U_DAY,         '1XXX-XX-XX'),
          (U_HOUR,        '1XXX-XX-XXTXX'),
          (U_MINUTE,      '1XXX-XX-XXTXX:XX'),
          (U_SECOND,      '1XXX-XX-XXTXX:XX:XX') ):
            t = TimePoint('1')
            t.extend_nonspecific(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
        t = TimePoint('T13:47')
        t.extend_nonspecific(U_SECOND)
        self.assertEqual(str(t), 'XXXX-XX-XXT13:47:XX', 'extend U_SECOND')
        t = TimePoint('2006-09')
        t.extend_nonspecific(U_WEEK)
        self.assertEqual(str(t), '2006-09-WXX', 'extend Y-M to U_WEEK')
        t.extend_nonspecific(U_DAY)
        self.assertEqual(str(t), '2006-09-XX', 'extend Y-M-W to U_DAY')
        t = TimePoint('2006-W36')
        t.extend_nonspecific(U_DAY)
        self.assertEqual(str(t), '2006-W36-X', 'extend Y-W to U_DAY')

    def testunknown(self):
        t = TimePoint('2006-09-06T15:13:31')
        for (u, v) in (
          (U_SECOND, '2006-09-06T15:13:XX'),
          (U_MINUTE, '2006-09-06T15:XX:XX'),
          (U_HOUR,   '2006-09-06TXX:XX:XX'),
          (U_DAY,    '2006-09-XXTXX:XX:XX'),
          (U_MONTH,  '2006-XX-XXTXX:XX:XX'),
          (U_YEAR, 'XXXX-XX-XXTXX:XX:XX') ):
            t.set_component_unknown(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
        for (x, u, v) in (
          ('2006-W36-3',  U_DAY,    '2006-W36-X'),
          ('2006-W36',    U_WEEK,   '2006-WXX'),
          ('2006-W36',    U_DECADE, 'XXXX-W36'),
          ('2006-09-WXX-3', U_DAY,  '2006-09-XX'),
          ('2006-09-W36', U_WEEK,   '2006-09-WXX'),
          ('2006',        U_CENTURY, 'XX') ):
            t = TimePoint(x)
            t.set_component_unknown(u)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))
 
    def testadd(self):
        for (x, u, n, v) in (
          ('2006-09-06T15:36:31', U_SECOND, 40, '2006-09-06T15:37:11'),
          ('2006-09-06T15:36', U_MINUTE, -9, '2006-09-06T15:27'),
          ('2006-09-06T15', U_HOUR,   40, '2006-09-08T07'),
          ('2006-09-06',  U_DAY,     -14, '2006-08-23'),
          ('2006-09-06',  U_WEEK,      4, '2006-10-04'),
          ('2006-W36',    U_WEEK,     18, '2007-W02'),
          ('2006-09',     U_MONTH,     1, '2006-10'),
          ('2006-Q3',     U_QUARTER,   2, '2007-Q1'),
          ('2006-H2',     U_HALFYEAR, -1, '2006-H1'),
          ('2006',        U_YEAR,    -28, '1978'),
          ('199',         U_DECADE,   -2, '197'),
          ('20',          U_CENTURY,  -1, '19'),
          ('2006',        U_YEAR,    -100000, 'BC97994') ):
            t = TimePoint(x)
            t.add_units(u, n)
            self.assertEqual(str(t), v, repr(str(t)) + '!=' + repr(v))


class DateYmdToYwdTestCase(unittest.TestCase):
    """Test the function date_ymd_to_ywd."""

    # values obtained using the Unix 'date' command
    fixedsamples = [
        ( 0001,  1,  1,  1, 1 ),
        ( 1978,  3,  9, 10, 4 ),  ( 1979,  8, 21, 34, 2 ),
        ( 1970,  1,  1,  1, 4 ),
        ( 2006,  8, 31, 35, 4 ),
        ( 2005, 12, 26, 52, 1 ),  ( 2005, 12, 27, 52, 2 ),
        ( 2005, 12, 28, 52, 3 ),  ( 2005, 12, 29, 52, 4 ),
        ( 2005, 12, 30, 52, 5 ),  ( 2005, 12, 31, 52, 6 ),
        ( 2006,  1,  1,  0, 7 ),  ( 2006,  1,  2,  1, 1 ),
        ( 2006,  1,  3,  1, 2 ),  ( 2006,  1,  4,  1, 3 ),
        ( 2006,  1,  5,  1, 4 ),  ( 2006,  1,  6,  1, 5 ),
        ( 2006,  1,  7,  1, 6 ),  ( 2006,  1,  8,  1, 7 ),
        ( 2006,  1,  9,  2, 1 ),  ( 2006,  1, 31,  5, 2 ),
        ( 2006,  2,  1,  5, 3 ),  ( 2006,  2, 28,  9, 2 ),
        ( 2006,  3,  1,  9, 3 ),  ( 2006, 12, 31, 52, 7 ),
        ( 2000,  1,  1,  0, 6 ),  ( 2000,  2, 28,  9, 1 ),
        ( 2000,  2, 29,  9, 2 ),  ( 2000,  3,  1,  9, 3 ),
        ( 2000, 12, 31, 52, 7 ),
        ( 2001,  1,  1,  1, 1 ),  ( 2001,  2, 28,  9, 3 ),
        ( 2001,  3,  1,  9, 4 ),  ( 2001, 12, 31, 53, 1 ),
        ( 2002,  1,  1,  1, 2 ),  ( 2002,  2, 28,  9, 4 ),
        ( 2002,  3,  1,  9, 5 ),  ( 2002, 12, 31, 53, 2 ),
        ( 2003,  1,  1,  1, 3 ),  ( 2003,  2, 28,  9, 5 ),
        ( 2003,  3,  1,  9, 6 ),  ( 2003, 12, 31, 53, 3 ),
        ( 2004,  1,  1,  1, 4 ),  ( 2004,  2, 28,  9, 6 ),
        ( 2004,  2, 29,  9, 7 ),  ( 2004,  3,  1, 10, 1 ),
        ( 2004, 12, 31, 53, 5 ),
        ( 2005,  1,  1,  0, 6 ),  ( 2005,  2, 28,  9, 1 ),
        ( 2005,  3,  1,  9, 2 ) ]

    def testfixed(self):
        for (y, m, d, wk, wd) in self.fixedsamples:
            self.assertEqual(date_ymd_to_ywd(y, m, d), (wk, wd),
              'failed for ymd=%04d-%02d-%02d' % (y, m, d))

    def testwalk(self):
        y = m = d = wk = wd = 1
        while y < 3000:
            self.assertEqual(date_ymd_to_ywd(y, m, d), (wk, wd),
              'failed walk at ymd=%04d-%02d-%02d' % (y, m, d))
            wd += 1
            if wd > 7:
                wd = 1
                wk += 1
            d += 1
            if (d > 31) or \
               (d > 30 and m in (4, 6, 9, 11)) or \
               (d > 29 and m == 2) or \
               (d > 28 and m == 2 and
                (y % 4 != 0 or (y % 100 == 0 and y % 400 != 0))):
                d = 1
                m += 1
            if m > 12:
                m = 1
                y += 1
                wk = 1
                if wd > 4: wk = 0


class DateYmdAbsdateTestCase(unittest.TestCase):
    """Test the functions date_ymd_to_absdate and date_absdate_to_ymd."""

    def testwalk(self):
        y = m = d = a = 1
        while y < 3000:
            self.assertEqual(date_ymd_to_absdate(y, m, d), a,
              'date_ymd_to_absdate failed for ymd=%04d-%02d-%02d' % (y, m, d))
            self.assertEqual(date_absdate_to_ymd(a), (y, m, d),
              'date_absdate_to_ymd failed for ymd=%04d-%02d-%02d' % (y, m, d))
            a += 1
            d += 1
            if (d > 31) or \
               (d > 30 and m in (4, 6, 9, 11)) or \
               (d > 29 and m == 2) or \
               (d > 28 and m == 2 and
                (y % 4 != 0 or (y % 100 == 0 and y % 400 != 0))):
                d = 1
                m += 1
            if m > 12:
                m = 1
                y += 1


class DateYwdAbsdateTestCase(unittest.TestCase):
    """Tests for the function date_ywd_to_absdate and date_absdate_to_ywd."""

    def testwalk(self):
        y = m = d = wk = wd = a = 1
        while y < 3000:
            self.assertEqual(date_ywd_to_absdate(y, wk, wd), a,
              'date_ywd_to_absdate failed for ywd=%04d-W%02d-%d' % (y, wk, wd))
            self.assertEqual(date_absdate_to_ywd(a), (y, wk, wd),
              'date_absdate_to_ywd failed for ywd=%04d-W%02d-%d' % (y, wk, wd))
            a += 1
            d += 1
            if (d > 31) or \
               (d > 30 and m in (4, 6, 9, 11)) or \
               (d > 29 and m == 2) or \
               (d > 28 and m == 2 and
                (y % 4 != 0 or (y % 100 == 0 and y % 400 != 0))):
                d = 1
                m += 1
                if m > 12: m = 1
            wd += 1
            if wd > 7:
                wd = 1
                wk += 1
                if wk > 53 or (wk > 52 and (m == 1 or d >= 29)):
                    wk = 1
                    y += 1

    def testboundaries(self):
        for y in xrange(1, 3000):
            for (w, d) in ((0,1), (0,7), (1,1), (1,7)):
                a = date_ywd_to_absdate(y, w, d)
                ap = date_ywd_to_absdate(y, w + 2, d) - 14
                self.assertEqual(a, ap,
                  'date_ywd_to_absdate failed for ywd=%04d-W%02d-%02d' %
                  (y, w, d))
            for (w, d) in ((52,1), (52,7), (53,1), (53,7)):
                a = date_ywd_to_absdate(y, w, d)
                ap = date_ywd_to_absdate(y, w - 2, d) + 14
                self.assertEqual(a, ap,
                  'date_absdate_to_ywd failed for ywd=%04d-W%02d-%02d' %
                  (y, w, d))


# Main
if __name__ == "__main__":
    unittest.main()

