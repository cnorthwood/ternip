"""Representation of documents and timex spans."""

import sys
import libxml2
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl


class Span(object):
    """A span of characters within a document."""

    # index (within document) of first character of span
    start = None

    # index (within document) of first character following span
    end = None

    # span content (string)
    txt = None

    # document object
    document = None

    def __init__(self, start, end, **args):
        self.start = start
        self.end = end
        for n in args:
            getattr(self, n)
            setattr(self, n, args[n])

    def __repr__(self):
        return self.__class__.__name__ + '(' + ','.join(
          [ n + '=' + repr(v) for (n, v) in self.__dict__.iteritems() ]
          ) + ')'

    def __str__(self):
	if self.txt is not None: return self.txt
	return self.document.txt[self.start:self.end]

    def __cmp__(self, other):
        """Compare span positions in document order."""
        return cmp(self.start, other.start) or cmp(other.end, self.end)


class TimexSpan(Span):
    """Span with timex meta data."""

    # normalized value (string)
    val = None

    # additional meta data
    mod = set = None
    anchorDir = anchorVal = None

    # intermediate normalization results
    tmxclass = dirclass = None
    prenorm = None
    prenormval = None

    # the node in the parse tree where this span originates
    parseNodeId = None

    # pointers to other TimexSpan objects for navigating nested timexes
    parentTimexSpan = None
    childTimexSpans = None


class TimexDocument(object):
    """Document with timex meta information."""

    # file name or identifier
    name = None

    # source file names and meta information
    srcTxtFile = None
    srcXmlFile = None
    srcStartAttr = "rstart"
    srcEndAttr = "rend"
    srcDocStart = 0
    srcDocEnd = -1
    srcLabels = None
    srcParseFile = None

    # document content
    txt = None      # plain text characters (character string)
    rawtxt = None   # raw content bytes (byte string)
    encoding = None # encoding of rawtxt

    # handler for loading the document
    loadFn = None
    docUseCnt = 0

    # document timestamp (normalized ISO string)
    timestamp = None

    # timex spans (ordered list)
    timexSpans = None

    # text sections in document (sequence)
    textSpans = None

    # sections where annotations are now allowed (sequence)
    forbiddenSpans = None

    # marked up reference time span
    timestampSpan = None

    # parses for this document
    parsesXml = None
    parseOffsetmap = None
    parseUseCnt = 0

    def __init__(self, **args):
        for n in args:
            getattr(self, n)
            setattr(self, n, args[n])

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' name=' + repr(self.name) + '>'

    def fetchDoc(self):
        """Load the document from its source files."""
        if self.docUseCnt == 0:
            self.loadFn(self)
        self.docUseCnt += 1

    def freeDoc(self):
        """Release document content and span data."""
        assert self.docUseCnt > 0
        assert self.parseUseCnt == 0
        self.docUseCnt -= 1
        if self.docUseCnt == 0:
            self.txt = self.rawtxt = None
            self.timestamp = self.timexSpans = self.textSpans = None

    def fetchParses(self):
        """Load sentence parses from XML file."""
        assert self.docUseCnt > 0
        if self.parseUseCnt == 0:
            loadParsesXml(self, self.srcParseFile)
        self.parseUseCnt += 1

    def freeParses(self):
        """Release sentence parses from memory."""
        assert self.parseUseCnt > 0
        self.parseUseCnt -= 1
        if self.parseUseCnt == 0:
            self.parsesXml.freeDoc()
            self.parsesXml = None
            self.parseOffsetMap = None

    def getNodeSpan(self, xnode):
        """Return the span of the given XML element as a Span object."""
        s = int(xnode.prop(self.srcStartAttr)) - self.srcDocStart
        e = int(xnode.prop(self.srcEndAttr)) + 1 - self.srcDocStart
        s = self.parseOffsetMap[s]
        e = self.parseOffsetMap[e]
        return Span(start=s, end=e, document=self)

    def computeTimexNesting(self):
        """Go through the timexSpans of this document, and (re)compute
        their parentTimexSpan and childTimexSpans properties.
        This method assumes that the list of timexes is sorted in document
        order, and that there are no partly overlapping timexes."""
        stack = [ ]
        for span in self.timexSpans:
            span.parentTimexSpan = None
            span.childTimexSpans = ( )
            while stack and span.start >= stack[-1].end:
                stack.pop()
            if stack:
                parent = stack[-1]
                assert (span.start > parent.start) or \
                       (span.start == parent.start and span.end < parent.end)
                span.parentTimexSpan = parent
                if parent.childTimexSpans:
                    parent.childTimexSpans.append(span)
                else:
                    parent.childTimexSpans = [ span ]
            stack.append(span)


def loadDocFromPlainTxt(doc):
    """Load document content from a plain text file."""

    if isinstance(doc.srcTxtFile, file):
        doc.rawtxt = doc.srcTxtFile.read()
    else:
        f = file(doc.srcTxtFile)
        doc.rawtxt = f.read()
        f.close()
    if doc.encoding:
        doc.txt = doc.rawtxt.decode(doc.encoding)
    else:
        doc.txt = doc.rawtxt


def loadDocFromTernSoXml(doc):
    """Load document from a stand-off XML file with TERN-style markup."""

    # Set defaults for offset attributes
    startAttr = doc.srcStartAttr
    endAttr = doc.srcEndAttr
    docStart = doc.srcDocStart
    docEnd = doc.srcDocEnd

    # Read text file
    f = file(doc.srcTxtFile)
    if docStart != 0:
        f.seek(docStart)
    if docEnd == -1:
        doc.rawtxt = f.read()
    else:
        doc.rawtxt = f.read(docEnd+1 - docStart)
    f.close()
    if doc.encoding:
        doc.txt = doc.rawtxt.decode(doc.encoding)
    else:
        doc.txt = doc.rawtxt

    # Read XML markup; build byte-to-character offset map
    xdoc = libxml2.parseFile(doc.srcXmlFile)
    offsetmap = { }
    for xnode in xdoc.walk_depth_first():
        if xnode.hasProp(startAttr) or xnode.hasProp(endAttr):
            s = int(xnode.prop(startAttr))
            e = int(xnode.prop(endAttr)) + 1
            offsetmap[s] = s - docStart
            offsetmap[e] = e - docStart
    if doc.encoding:
        decodeOffsets(offsetmap, doc.txt, doc.rawtxt, doc.encoding)

    # Find TEXT sections in XML markup
    doc.textSpans = [ ]
    for xnode in xdoc.xpathEval('//TEXT') + xdoc.xpathEval('//text'):
        s = offsetmap[int(xnode.prop(startAttr))]
        e = offsetmap[int(xnode.prop(endAttr)) + 1]
        doc.textSpans.append(Span(start=s, end=e, document=doc))
    doc.textSpans.sort()

    # Find marked up reference time span
    doc.timestampSpan = None
    for p in ('//reftime', '//STORY_REF_TIME', '//story_ref_time',
              '//DATE_TIME', '//date_time', '//DATETIME', '//datetime'):
        for xnode in xdoc.xpathEval(p):
            if xnode.hasProp(startAttr) or xnode.hasProp(endAttr):
                s = offsetmap[int(xnode.prop(startAttr))]
                e = offsetmap[int(xnode.prop(endAttr)) + 1]
                doc.timestampSpan = Span(start=s, end=e, document=doc)
                break

    # Never look inside DOCNO sections
    doc.forbiddenSpans = [ ]
    for xnode in xdoc.xpathEval('//DOCNO') + xdoc.xpathEval('//docno') + \
                 xdoc.xpathEval('//DOCID') + xdoc.xpathEval('//docid'):
        s = offsetmap[int(xnode.prop(startAttr))]
        e = offsetmap[int(xnode.prop(endAttr)) + 1]
        doc.forbiddenSpans.append(Span(start=s, end=e, document=doc))

    # Find TIMEX2 elements in XML markup
    doc.timexSpans = [ ]
    for xnode in xdoc.xpathEval('//TIMEX2') + xdoc.xpathEval('//timex2'):
        s = offsetmap[int(xnode.prop(startAttr))]
        e = offsetmap[int(xnode.prop(endAttr)) + 1]
        span = TimexSpan(start=s, end=e, txt=doc.txt[s:e], document=doc)
        for n in ('val', 'mod', 'set', 'tmxclass', 'dirclass', 'prenorm'):
            if xnode.hasProp(n):
                setattr(span, n, xnode.prop(n))
            elif xnode.hasProp(n.upper()):
                setattr(span, n, xnode.prop(n.upper()))
        for n, nn in ( ('anchor_dir','anchorDir'),
                       ('anchor_val','anchorVal') ):
            if xnode.hasProp(n):
                setattr(span, nn, xnode.prop(n))
            elif xnode.hasProp(n.upper()):
                setattr(span, nn, xnode.prop(n.upper()))
        if xnode.hasProp('parsenode'):
            span.parseNodeId = tuple(xnode.prop('parsenode').split())
        doc.timexSpans.append(span)
    doc.timexSpans.sort()

    # Find reference time
    doc.timestamp = None
    for xnode in xdoc.xpathEval('//reftime'):
        if xnode.hasProp('val'):
            doc.timestamp = xnode.prop('val')
            break
    if (not doc.timestamp) and doc.timestampSpan:
        for span in doc.timexSpans:
            if span.start >= doc.timestampSpan.start and \
               span.end <= doc.timestampSpan.end and \
               span.val:
                doc.timestamp = span.val
                break

    xdoc.freeDoc()


def loadDocFromLabels(doc):
    """Load document content from a plain text file and assign spans from
    a list of span labels."""
    loadDocFromPlainTxt(doc)
    doc.textSpans = [ ]
    doc.timexSpans = [ ]
    for (p, n, t) in doc.srcLabels:
        if t == 'TEXT' or t == 'text':
            doc.textSpans.append(Span(start=p, end=p+n, document=doc))
        elif t == 'TIMEX2' or t == 'timex2':
            s = TimexSpan(start=p, end=p+n, txt=doc.txt[p:p+n], document=doc)
            doc.timexSpans.append(s)
        elif t[:8] == 'reftime':
            doc.timestampSpan = Span(start=p, end=p+n, document=doc)
        elif t[:8] == 'reftime_':
            doc.timestamp = t[8:]
    doc.textSpans.sort()
    doc.timexSpans.sort()


def loadParsesXml(doc, fname):
    """Load sentence parses for a document from an XML file."""
    startAttr = doc.srcStartAttr
    endAttr = doc.srcEndAttr
    docStart = doc.srcDocStart
    doc.parsesXml = libxml2.parseFile(fname)
    offsetmap = { }
    for xnode in doc.parsesXml.walk_depth_first():
        if xnode.hasProp(startAttr) or xnode.hasProp(endAttr):
            s = int(xnode.prop(startAttr))
            e = int(xnode.prop(endAttr)) + 1
            offsetmap[s] = s - docStart
            offsetmap[e] = e - docStart
    if doc.encoding:
        decodeOffsets(offsetmap, doc.txt, doc.rawtxt, doc.enc)
    doc.parseOffsetMap = offsetmap


def writeDocAsTernSoXml(doc, fname):
    """Write spans as stand-off XML with TERN-style markup."""

    # Make a list of elements to write out, sorted in depth-first prefix order
    elemlist = [ ]
    if doc.textSpans:
        elemlist += [ (span, 1, 'TEXT') for span in doc.textSpans ]
    if doc.forbiddenSpans:
        elemlist += [ (span, 1, 'DOCID') for span in doc.forbiddenSpans ]
    if doc.timestampSpan:
        elemlist.append( (doc.timestampSpan, 2, 'reftime') )
    if doc.timexSpans:
        elemlist += [ (span, 3, 'TIMEX2') for span in doc.timexSpans ]
    elemlist.sort()

    # Build character-to-byte offset map
    startAttr = doc.srcStartAttr
    endAttr = doc.srcEndAttr
    docStart = doc.srcDocStart
    offsetmap = { }
    for (span, prio, name) in elemlist:
        offsetmap[span.start] = span.start
        offsetmap[span.end] = span.end
    if doc.encoding:
        encodeOffsets(offsetmap, doc.txt, doc.rawtxt, doc.encoding)
    for k in offsetmap:
        offsetmap[k] += docStart

    # Create XML output stream
    f = file(fname, 'w')
    xmlout = XMLGenerator(f, 'UTF-8')

    # Abbreviated commands for XML output generation
    def startelem(n, a={}): xmlout.startElement(n, AttributesImpl(a))
    def endelem(n): xmlout.endElement(n)
    def newline(): xmlout.ignorableWhitespace('\n')
    def putstr(s): xmlout.characters(s)

    # Start document
    xmlout.startDocument()
    startelem('DOC', { 'generator': 'timexdoc.py' })
    newline()

    # Write document timestamp
    if doc.timestamp and not doc.timestampSpan:
        startelem('reftime', { 'val': doc.timestamp })
        endelem('reftime')
        newline()

    # Write spans as XML elements; try proper nesting if possible
    spanstack = [ ]
    inlinedepth = 0
    p = 0
    for (span, prio, name) in elemlist:
        # close pending elements
        while spanstack and spanstack[-1][0] <= span.start:
            (q, endname, isinline) = spanstack[-1]
            if inlinedepth:
                putstr(doc.txt[p:q])
            p = q
            endelem(endname)
            if isinline:
                inlinedepth -= 1
            if not inlinedepth:
                newline()
            spanstack.pop()
        # handle pending character data
        q = span.start
        if inlinedepth:
            putstr(doc.txt[p:q])
        p = q
        # start a new element
        attr = {
          startAttr: str(offsetmap[span.start]),
          endAttr: str(offsetmap[span.end]-1) }
        if isinstance(span, TimexSpan):
            for n in ('val', 'mod', 'set', 'tmxclass', 'dirclass', 'prenorm'):
                v = getattr(span, n)
                if n == 'set' and v:
                    v = 'YES'
                if v is not None:
                    attr[n] = v
            for n, nn in ( ('anchor_dir','anchorDir'),
                           ('anchor_val','anchorVal') ):
                v = getattr(span, nn)
                if v is not None:
                    attr[n] = v
            if span.parseNodeId is not None:
                attr['parsenode'] = ' '.join(span.parseNodeId)
        elif span is doc.timestampSpan:
            if doc.timestamp:
                attr['val'] = doc.timestamp
        startelem(name, attr)
        isinline = (span.txt is not None)
        if isinline:
            inlinedepth += 1
        if spanstack and span.end > spanstack[-1][0]:
            # improper nesting! make this an empty element
            print >>sys.stderr, "WARNING: improper nesting in", repr(fname)
            endelem(name)
            if span.txt is not None:
                inlinedepth -= 1
        else:
            spanstack.append( (span.end, name, isinline) )
        if not inlinedepth:
            newline()
    # close pending elements
    while spanstack:
        (q, endname, isinline) = spanstack[-1]
        if inlinedepth:
            putstr(doc.txt[p:q])
        p = q
        endelem(endname)
        if isinline:
            inlinedepth -= 1
        if not inlinedepth:
            newline()
        spanstack.pop()
    assert inlinedepth == 0

    # End XML output
    xmlout.endElement('DOC')
    newline()
    xmlout.endDocument()
    f.close()


def getLabelsFromDoc(doc):
    """Return MinorThird style span labels."""
    labels = [ ]
    if doc.timestamp is not None:
        # faked label to capture the reference time
        labels.append( (0, 0, 'reftime_' + doc.timestamp) )
    if doc.timestampSpan is not None:
        span = doc.timestampSpan
        labels.append( (span.start, span.end - span.start, 'reftime') )
    labels += [ (span.start, span.end - span.start, 'TEXT')
                for span in doc.textSpans ]
    labels += [ (span.start, span.end - span.start, 'TIMEX2')
                for span in doc.timexSpans ]
    return labels


def decodeOffsets(offsetmap, txt, rawtxt, enc):
    """Convert byte offsets to character offsets."""
    v = offsetmap.keys()
    v.sort()
    p = q = 0
    for k in v:
        t = offsetmap[k]
        if t != p:
            assert t > p
            q += len(rawtxt[p:t].decode(enc))
            p = t
        offsetmap[k] = q
    t = len(rawtxt)
    if t != p:
        assert t > p
        q += len(rawtxt[p:t].encode(enc))
    assert q == len(txt)


def encodeOffsets(offsetmap, txt, rawtxt, enc):
    """Convert character offsets to byte offsets."""
    v = offsetmap.keys()
    v.sort()
    p = q = 0
    for k in v:
        t = offsetmap[k]
        if t != p:
            assert t > p
            q += len(txt[p:t].encode(enc))
            p = t
        offsetmap[k] = q
    t = len(txt)
    if t != p:
        assert t > p
        q += len(txt[p:t].encode(enc))
    assert q == len(rawtxt)


if __name__ == "__main__":
    # Run unit tests
    import unittest

    class TimexNestingTestCase(unittest.TestCase):
        def checkParents(self, doc):
            m = dict()
            for span in doc.timexSpans:
                for child in span.childTimexSpans:
                    self.assertEqual(child.parentTimexSpan, span)
                    m[child] = 1
            for span in doc.timexSpans:
                if span not in m:
                    self.assertEqual(span.parentTimexSpan, None)
        def testOne(self):
            doc = TimexDocument(name='testdoc')
            doc.timexSpans = ts = [
              TimexSpan(start=5, end=10, document=doc),
              TimexSpan(start=10, end=15, document=doc),
              TimexSpan(start=10, end=11, document=doc),
              TimexSpan(start=13, end=15, document=doc),
              TimexSpan(start=14, end=15, document=doc) ]
            doc.computeTimexNesting()
            self.assertEqual(len(ts[0].childTimexSpans), 0)
            self.assertEqual(ts[1].childTimexSpans, [ ts[2], ts[3] ])
            self.assertEqual(len(ts[2].childTimexSpans), 0)
            self.assertEqual(ts[3].childTimexSpans, [ ts[4] ])
            self.assertEqual(len(ts[4].childTimexSpans), 0)
            self.checkParents(doc)
        def testTwo(self):
            doc = TimexDocument(name='testdoc')
            doc.timexSpans = ts = [
              TimexSpan(start=20, end=25, document=doc),
              TimexSpan(start=25, end=30, document=doc) ]
            doc.computeTimexNesting()
            self.assertEqual(len(ts[0].childTimexSpans), 0)
            self.assertEqual(len(ts[1].childTimexSpans), 0)
            self.checkParents(doc)
            doc.timexSpans.append(TimexSpan(start=5, end=10, document=doc))
            doc.timexSpans.append(TimexSpan(start=15, end=25, document=doc))
            doc.timexSpans.sort()
            doc.computeTimexNesting()
            self.assertEqual(len(ts[0].childTimexSpans), 0)
            self.assertEqual(ts[1].childTimexSpans, [ ts[2] ])
            self.assertEqual(len(ts[2].childTimexSpans), 0)
            self.assertEqual(len(ts[3].childTimexSpans), 0)
            self.checkParents(doc)
        def unsorted(self):
            doc = TimexDocument(name='testdoc')
            doc.timexSpans = [
              TimexSpan(start=5, end=20, document=doc),
              TimexSpan(start=15, end=18, document=doc),
              TimexSpan(start=13, end=19, document=doc) ]
            doc.computeTimexNesting()
        def testUnsorted(self):
            self.assertRaises(AssertionError, self.unsorted)

    unittest.main()


