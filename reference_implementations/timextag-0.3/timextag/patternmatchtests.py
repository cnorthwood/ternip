#!/usr/bin/env python
"""Unit tests for the "patternmatch" module."""

import unittest, random
from patternmatch import *


class TokenizeTestCase(unittest.TestCase):
    """Test the function tokenize()."""

    fixedsamples = [
        ( '', [] ),
        ( 'test', ['test'] ),
        ( 'Short sentence.', ['Short','sentence','.'] ),
        ( 'Cu l8t3r!', ['Cu','l','8','t','3','r','!'] ),
        ( '100.000<100,000', ['100','.','000','<','100',',','000'] ),
        ( 'Say "hello".', ['Say','"','hello','"','.'] ),
        ( ' 2 be |!   to  be ? ', ['2','be','|','!','to','be','?'] ) ]

    def testfixed(self):
        for (s, tok) in self.fixedsamples:
            self.assertEqual(tokenize(s), tok, 'tokenize failed on ' + repr(s))

    def testrandom(self):
        toks = [ 'aap', u'noot', 'Mies', 'Wim', ' ', u'0', '149', '.', '$',
                 '\\', '?', '"' ]
        random.seed(101)
        for i in xrange(250):
            s = ''
            tok = [ ]
            for j in xrange(random.randint(0, 100)):
                q = random.randint(0, len(toks)-1)
                t = toks[q]
                if t != ' ':
                    tok.append(t)
                    if (s and t[0].isalpha() and s[-1].isalpha()) or \
                       (s and t[0].isdigit() and s[-1].isdigit()):
                        s += ' '
                    s += t
            self.assertEqual(tokenize(s), tok, 'tokenize failed on ' + repr(s))


class SuperTokenTestCase(unittest.TestCase):
    """Test the SuperToken class."""

    def testfixed(self):
        taap = SuperToken(3, 8, 'aap')
        tnoot = SuperToken(9, 10, 'NOOT', val=123, raw=u'123')
        self.assertEqual(taap, 'aap')
        self.assertNotEqual(taap, 'AAP')
        self.assertNotEqual(taap, 'aaps')
        self.assertEqual(tnoot, 'NOOT')
        self.assertNotEqual(tnoot, 'noot')
        self.assertEqual(taap.start, 3)
        self.assertEqual(taap.end, 8)
        self.assertEqual(taap.val, None)
        self.assertEqual(taap.raw, None)
        self.assertEqual(tnoot.val, 123)
        self.assertEqual(tnoot.raw, '123')


class PatternMatcherTestCase(unittest.TestCase):
    """Test the PatternMatcher class."""

    def dotest(self, pstr, pm, s, tok, stok, res):
        errmsg = 'failed with %s and %s' % (repr(pstr), repr(s))

        for i in range(len(tok) + 1):
            m = pm.match(tok, stok, i)
            w = filter((lambda p: p[0] == i), res)
            self.assertEqual(m, w, 'match(start=%d) %s' % (i, errmsg))
            if pm.forcebegin: break

        m = pm.matchall(tok, stok)
        self.assertEqual(m, res, 'matchall() ' + errmsg)

        m = pm.matchfull(tok, stok)
        w = None
        for (start, end, z) in res:
            if start == 0 and end == len(tok):
                w = (start, end, z)
        self.assertEqual(m, w, 'matchfull() ' + errmsg)

        m = pm.matchfirst(tok, stok)
        w = None
        for (start, end, z) in res:
            if w is None or w[0] == start:
                w = (start, end, z)
        self.assertEqual(m, w, 'matchfirst()' + errmsg)

    flatsamples = [
      ( '"aap"|"noot" "mies"', [
        ('aap', [ (0, 1, ()) ]),
        ('noot', [ ]),
        ('mies', [ ]),
        ('noot mies', [ (0, 2, ()) ]),
        ('aap noot', [ (0, 1, ()) ]),
        (u'aap noot mies', [ (0, 1, ()), (1, 3, ()) ]),
        ('noot aap mies', [ (1, 2, ()) ]),
        ('mies noot Aap', [ ]),
        ('noot mies aap', [ (0, 2, ()), (2, 3, ()) ]) ]),
      ( '("aap" |"ape") "noot" ? "mies"', [
        ('aape noot mies', [ ]),
        ('aap noot mies', [ (0, 3, ()) ]),
        ('aap noot ape mies noot mies', [ (2, 4, ()) ]),
        ('ape mies aap noot noot mies aap mies noot', [ (0, 2, ()), (6, 8, ())
          ]) ]),
      ( ' ^"aap"+ .? ( "noot" "mies" )*', [
        ('aap', [ (0, 1, ()) ]),
        ('noot aap', [ ]),
        ('aap apen aap', [ (0, 1, ()), (0, 2, ()) ]),
        ('aap, noot noot mies', [ (0, 1, ()), (0, 2, ()) ]),
        ('aap, noot mies aap noot mies',
         [ (0, 1, ()), (0, 2, ()), (0, 4, ()) ]),
        ('aap noot mies noot mies noot',
         [ (0, 1, ()), (0, 2, ()), (0, 3, ()), (0, 5, ()) ]) ]),
      ( ' "aap" ("noot"|"mies")* ("wim"|"zus")', [
        ('aap noot mies', [ ]),
        ('noot aap zus', [ (1, 3, ()) ]),
        ('slaap noot aap mies noot wim', [ (2, 6, ()) ]),
        ('aap, aap aap noot mies noot zus', [ (3, 8, ()) ]),
        ('aap noot zus wim aap noot wim noot wim', [ (0, 3, ()), (4, 7, ()) ]),
        ]),
      ( ' "aap" ("noot"*|"mies"*) $', [
        ('aap zus aap noot mies', [ ]),
        ('aap noot aap noot noot', [ (2, 5, ()) ]),
        ('aap zus aap', [ (2, 3, ()) ]),
        ('aap mies', [ (0, 2, ()) ]) ]),
      ( ' "aap" (("noot"+ "mies")|"wim")+', [
        ('aap wim noot wim', [ (0, 2, ()) ]),
        ('aap aap mies mies aap noot mies wim', [ (4, 7, ()), (4, 8, ()) ]),
        ('aap noot noot mies wim noot mies',
         [ (0, 4, ()), (0, 5, ()), (0, 7, ()) ]) ]),
      ( ' "aap" | { "noot" "mies" }', [
        (u'aap noot mies', [ (0, 1, ((),)), (1, 3, (('noot', 'mies'),)) ]) ]),
      ( ' ( {"aap"+} | {"noot"}? ) {"wim"+} ', [
        ('wim', [ (0, 1, ((),(),('wim',))) ]),
        ('aap wim',
         [ (0, 2, (('aap',),(),('wim',))), (1, 2, ((),(),('wim',))) ]),
        ('aap aap wim aap noot wim wim',
         [ (0, 3, (('aap','aap'),(),('wim',))),
           (1, 3, (('aap',),(),('wim',))),
           (2, 3, ((),(),('wim',))),
           (4, 6, ((),('noot',),('wim',))),
           (4, 7, ((),('noot',),('wim','wim'))),
           (5, 6, ((),(),('wim',))),
           (5, 7, ((),(),('wim','wim'))),
           (6, 7, ((),(),('wim',))) ]) ]) ]

    def testflat(self):
        for (pstr, tests) in self.flatsamples:
            pm = PatternMatcher(pstr)

            for (s, res) in tests:
                tok = tokenize(s)
                stok = len(tok) * [ [ ] ]
                self.dotest(pstr, pm, s, tok, stok, res)

    def teststok(self):
        s = 'aap noot noot mies noot wim'
        tok = tokenize(s)

        noot = SuperToken(1, 2, 'Noot')
        nootmies = SuperToken(2, 4, 'NootMies')
        mies = SuperToken(3, 4, 'Mies')
        miesnootwim = SuperToken(3, 6, 'MiesNootWim')

        stok = [ [], [ noot ], [ nootmies ], [ mies, miesnootwim ], [], [] ]

        # TODO : fix last examples
        # TODO : example with nested capturing
        for (pstr, res) in (
          ( ' { "aap" | "noot" | Noot } Mies ',
            [ (2, 4, (('noot',),)) ] ),
          ( ' "noot"? { NootMies } ',
            [ (1, 4, ((nootmies,),)), (2, 4, ((nootmies,),)) ] ),
          ( ' ^ { "aap"? } "noot" Noot? ',
            [ (0, 2, (('aap',),)) ] ),
          ( ' "noot" { "mies" | MiesNootWim }? { "noot"? } ',
            [ (1, 2, ((),())), (1, 3, ((),('noot',))),
              (2, 3, ((),())), (2, 4, (('mies',),())),
              (2, 5, (('mies',),('noot',),)), (2, 6, ((miesnootwim,),())), 
              (4, 5, ((),())) ] ),
          ( ' { "noot"? . } $ ',
            [ (4, 6, (('noot','wim'),)), (5, 6, (('wim',),)) ] ),
          ( ' { { "noot" }+ { MiesNootWim } } $ ',
            [ (1, 6, (('noot','noot',miesnootwim),('noot','noot'),(miesnootwim,))),
              (2, 6, (('noot',miesnootwim),('noot',),(miesnootwim,))) ] ) ):
            pm = PatternMatcher(pstr)
            self.dotest(pstr, pm, s, tok, stok, res)


# Main
if __name__ == "__main__":
    unittest.main()

