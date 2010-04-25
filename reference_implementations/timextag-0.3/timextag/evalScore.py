#!/usr/bin/env python
"""Compute accuracy of a timex recognition/normalization run.

Usage: evalScore.py [options] testXmlDir goldXmlDir
 --select text/nontext/all  Document sections to process (default: text).
 --savealigned saveDir      Merge correctly recognized timexes with gold
                            attributes and save result to saveDir.
 --keepnonaligned           With --savealigned: don't discard spurious timexes.
"""

import sys, os, os.path, getopt
import libxml2


# Process TEXT or non-TEXT sections (0=all, 1=TEXT, -1=non-TEXT)
textOnly = 1

# Keep non-aligned timexes for the --savealigned function
keepNonAligned = 0


class s:
    nTestSpan = 0
    nGoldSpan = 0
    nExactSpan = 0
    nGoodSpan = 0
    nTestClass = 0
    nTestClassGoodSpan = 0
    nGoodClass = 0
    nTestVal = 0
    nTestValGoodSpan = 0
    nGoodVal = 0
    nGoodMod = 0
    nGoodAnchor = 0
    nGoodValAnchor = 0


def safediv(a, b):
    if a == 0:
        return 0
    else:
        return a / float(b)


def fscore(a, p, q):
    if a == 0:
        return 0
    else:
        return 2 * a / float(p + q)


def getTimexSpans(fname):
    def nodeProp(xnode, propname):
        if xnode.hasProp(propname):
            return xnode.prop(propname)
        propname = propname.upper()
        if xnode.hasProp(propname):
            return xnode.prop(propname)
    xdoc = libxml2.parseFile(fname)
    timexspans = [ ]
    if textOnly < 0:
        # select non-TEXT sections
        pathexpr = '//TIMEX2[not(./ancestor::TEXT)]'
    elif textOnly:
        # select TEXT sections
        pathexpr = '//TEXT//TIMEX2'
    else:
        # select everything
        pathexpr = '//TIMEX2'
    for xnode in xdoc.xpathEval(pathexpr):
        start = int(xnode.prop('rstart'))
        end = int(xnode.prop('rend')) + 1
        timexspans.append({ 'start':start, 'end':end,
          'val': nodeProp(xnode, 'val'),
          'set': nodeProp(xnode, 'set'),
          'tmxclass': xnode.prop('tmxclass'),
          'dirclass': xnode.prop('dirclass'),
          'mod': nodeProp(xnode, 'mod'),
          'anchorDir': nodeProp(xnode, 'anchor_dir'),
          'anchorVal': nodeProp(xnode, 'anchor_val') })
    xdoc.freeDoc()
    return timexspans


def classMatch(testSpan, goldSpan):
    return testSpan['tmxclass'] == goldSpan['tmxclass']


def canonval(v):
    if v is None: v = ''
    if v[:11] == 'XXXX-XX-XXT': v = v[10:]
    if v[:2] == 'P.': v = 'P0.' + v[2:]
    if v[:3] == 'PT.': v = 'PT0.' + v[3:]
    return v


def valMatch(testSpan, goldSpan):
    tset = (testSpan['set'] and testSpan['set'] != '0') or False
    gset = (goldSpan['set'] and goldSpan['set'] != '0') or False
    tval = canonval(testSpan['val'])
    gval = canonval(goldSpan['val'])
    return (tset == gset) and (tval == gval)


def modMatch(testSpan, goldSpan):
    tmod = testSpan['mod'] or ''
    gmod = goldSpan['mod'] or ''
    return tmod == gmod


def anchorMatch(testSpan, goldSpan):
    tdir = testSpan['anchorDir'] or ''
    gdir = goldSpan['anchorDir'] or ''
    tval = canonval(testSpan['anchorVal'])
    gval = canonval(goldSpan['anchorVal'])
    return (tdir == gdir) and (tval == gval)


def pairScore(testSpan, goldSpan):
    tstart, tend = testSpan['start'], testSpan['end']
    gstart, gend = goldSpan['start'], goldSpan['end']
    if (tend <= gstart) or (gend <= tstart):
        # no overlap
        return -1
    if (tstart == gstart) and (tend == gend):
        # prefer perfect span match over anything else
        s = 2000
    else:
        # prefer a good span match
        s = 1000 - 2 * abs(tstart - gstart) - abs(tend - gend)
    if valMatch(testSpan, goldSpan):
        # prefer matching values
        s += 500
    return s


def pairSpans(testSpans, goldSpans):
    pairs = [ ]
    markg = [ 0 for g in goldSpans ]
    for t in testSpans:
        bests = -1
        besti = None
        for i in range(len(goldSpans)):
            if not markg[i]:
                s = pairScore(t, goldSpans[i])
                if s >= 0 and s > bests:
                    bests = s
                    besti = i
        if bests >= 0:
            pairs.append( (t, goldSpans[besti]) )
            markg[besti] = 1
    for i in range(len(markg)):
        if not markg[i]:
            #print "MISS:", goldSpans[i]
            pass
    return pairs


def saveAlignedSpans(testFile, alignedSaveFile, pairs):
    """For every timex in the test file that can be matched with a gold timex,
    replace its attributes with the gold attribute values (except for the
    offsets); discard timexes that can not be matched with a gold timex;
    output the result of this operation as a new XML file."""
    def setProp(xnode, propname, propval):
        if propval is not None:
            xnode.setProp(propname, propval)
    # Map recognized spans to gold timexes
    spanmap = dict()
    for (testSpan, goldSpan) in pairs:
        spanmap[(testSpan['start'], testSpan['end'])] = goldSpan
    # Process all recognized timexes
    xdoc = libxml2.parseFile(testFile)
    for xnode in xdoc.xpathEval('//TIMEX2'):
        start = int(xnode.prop('rstart'))
        end = int(xnode.prop('rend')) + 1
        # Remove attributes
        proplist = list()
        p = xnode.get_properties()
        while p:
            proplist.append(p.name)
            p = p.next
        for p in proplist:
            if p not in ('rstart', 'rend'):
                xnode.unsetProp(p)
        goldSpan = spanmap.get((start, end))
        if goldSpan:
            # Correctly recognized; add gold attribute values
            setProp(xnode, 'val', goldSpan['val'])
            setProp(xnode, 'set', goldSpan['set'])
            setProp(xnode, 'mod', goldSpan['mod'])
            setProp(xnode, 'anchor_dir', goldSpan['anchorDir'])
            setProp(xnode, 'anchor_val', goldSpan['anchorVal'])
        elif not keepNonAligned:
            # Spurious timex; drop it completely
            p = xnode.get_children()
            while p:
                xnode.addNextSibling(p)
                p = xnode.get_children()
            xnode.unlinkNode()
            xnode.freeNode()
    # Save modified XML file
    xdoc.saveFileEnc(alignedSaveFile, 'UTF-8')
    xdoc.freeDoc()


def doFile(testFile, goldFile, alignedSaveFile=None):
    testSpans = getTimexSpans(testFile)
    goldSpans = getTimexSpans(goldFile)
    s.nTestSpan += len(testSpans)
    s.nGoldSpan += len(goldSpans)
    for span in testSpans:
        if span['tmxclass'] is not None:
            s.nTestClass += 1
        if span['val'] is not None:
            s.nTestVal += 1
    pairs = pairSpans(testSpans, goldSpans)
    s.nGoodSpan += len(pairs)
    s.nExactSpan += sum(map(
      (lambda x: x[0]['start']==x[1]['start'] and x[0]['end']==x[1]['end']),
      pairs))
    for (testSpan, goldSpan) in pairs:
        if testSpan['tmxclass'] is not None:
            s.nTestClassGoodSpan += 1
            if classMatch(testSpan, goldSpan):
                s.nGoodClass += 1
        if testSpan['val'] is not None:
            s.nTestValGoodSpan += 1
            if valMatch(testSpan, goldSpan):
                s.nGoodVal += 1
                if anchorMatch(testSpan, goldSpan):
                    s.nGoodValAnchor += 1
            if modMatch(testSpan, goldSpan):
                s.nGoodMod += 1
            if anchorMatch(testSpan, goldSpan):
                s.nGoodAnchor += 1
    if alignedSaveFile:
        saveAlignedSpans(testFile, alignedSaveFile, pairs)


def doDir(testDir, goldDir, alignedSaveDir=None):
    files = os.listdir(testDir)
    for f in files:
        alignedSaveFile = None
        if alignedSaveDir:
            alignedSaveFile = os.path.join(alignedSaveDir, f)
        doFile(os.path.join(testDir, f), os.path.join(goldDir, f),
               alignedSaveFile)

    print "nTestSpan = %d" % s.nTestSpan
    print "nGoldSpan = %d" % s.nGoldSpan
    print "nGoodSpan = %d" % s.nGoodSpan
    print "nExactSpan = %d" % s.nExactSpan
    print "span exact: recall=%0.4f prec=%0.4f F=%0.4f" % (
            safediv(s.nExactSpan, s.nGoldSpan),
            safediv(s.nExactSpan, s.nTestSpan),
            fscore(s.nExactSpan, s.nTestSpan, s.nGoldSpan))
    print "span overlap: recall=%0.4f prec=%0.4f F=%0.4f" % (
            safediv(s.nGoodSpan, s.nGoldSpan),
            safediv(s.nGoodSpan, s.nTestSpan),
            fscore(s.nGoodSpan, s.nTestSpan, s.nGoldSpan))
    print

    print "nTestClass = %d" % s.nTestClass
    print "nTestClassGoodSpan = %d" % s.nTestClassGoodSpan
    print "nGoodClass = %d" % s.nGoodClass
    print "class: accuracy=%0.4f (on recognized spans only)" % safediv(s.nGoodClass, s.nTestClassGoodSpan)
    print

    print "nTestVal = %d" % s.nTestVal
    print "nTestValGoodSpan = %d" % s.nTestValGoodSpan
    print "nGoodVal = %d" % s.nGoodVal
    print "val: accuracy=%0.4f  (on recognized spans only)" % safediv(s.nGoodVal, s.nTestValGoodSpan)
    print

    print "end-to-end val: recall=%0.4f prec=%0.4f F=%0.4f" % (
            safediv(s.nGoodVal, s.nGoldSpan),
            safediv(s.nGoodVal, s.nTestVal),
            fscore(s.nGoodVal, s.nTestVal, s.nGoldSpan))
    print

    print "nGoodMod = %d" % s.nGoodMod
    print "mod: accuracy=%0.4f recall=%0.4f prec=%0.4f F=%0.4f" % (
             safediv(s.nGoodMod, s.nTestValGoodSpan),
             safediv(s.nGoodMod, s.nGoldSpan),
             safediv(s.nGoodMod, s.nTestVal),
             fscore(s.nGoodMod, s.nTestVal, s.nGoldSpan))
    print

    print "nGoodAnchor = %d" % s.nGoodAnchor
    print "anchor: accuracy=%0.4f recall=%0.4f prec=%0.4f F=%0.4f" % (
             safediv(s.nGoodAnchor, s.nTestValGoodSpan), 
             safediv(s.nGoodAnchor, s.nGoldSpan),
             safediv(s.nGoodAnchor, s.nTestVal),
             fscore(s.nGoodAnchor, s.nTestVal, s.nGoldSpan))
    print "end-to-end combined val and anchor: recall=%0.4f prec=%0.4f F=%0.4f" % (
             safediv(s.nGoodValAnchor, s.nGoldSpan),
             safediv(s.nGoodValAnchor, s.nTestVal),
             fscore(s.nGoodValAnchor, s.nTestVal, s.nGoldSpan))
    print



class UsageError(Exception):
    pass


def main(argv):
    global textOnly, keepNonAligned
    opts, args = getopt.getopt(argv[1:], '', [
      'select=', 'savealigned=', 'keepnonaligned' ])
    if len(args) != 2:
        raise UsageError()
    alignedSaveDir = None
    for (opt, val) in opts:
        if opt == '--select':
            if val == 'text': textOnly = 1
            elif val == 'all': textOnly = 0
            elif val == 'nontext': textOnly = -1
            else: raise UsageError()
        if opt == '--savealigned':
            alignedSaveDir = val
        if opt == '--keepnonaligned':
            keepNonAligned = 1
    doDir(args[0], args[1], alignedSaveDir)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except (getopt.GetoptError, UsageError):
        print >>sys.stderr, __doc__
        sys.exit(1)

