#!/usr/bin/env python
"""Merge XML timex annotations back into the original SGML documents.

Usage: mergeSgmlWithXmlTimexes.py sgmlFileSpec xmlFileSpec outputDir
Example: mergeSgmlWithXmlTimexes.py 'sgml/*.sgml' 'xml/*.timex.xml' outdir

Merge TIMEX2 elements from an XML file in stand-off rstart/rend format
into the original SGML file, removing any existing TIMEX2 elements from
the SGML file.

Limited wildcard processing is done on the filename arguments.
"""

import sys, re, os, os.path
from xml.sax.saxutils import escape as xmlEscape
import libxml2


class SgmlMerger:

    entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*);?')
    charref = re.compile('&#([0-9]+);?')
    starttag = re.compile('<([-_.A-Za-z0-9]*)[^>]*>')

    entitydefs = {
      'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': "'" }

    def __init__(self, data, elemlist, tagName, outFile):

        self.outFile = outFile
        self.tagName = tagName

        self.startPos = { }
        self.endPos = { }
        for (start, end, attr) in elemlist:
            if start not in self.startPos: self.startPos[start] = [ ]
            if end not in self.endPos: self.endPos[end] = 0
            self.startPos[start].append(attr)
            self.endPos[end] += 1

        self.offset = 0
        self.haveCr = 0

        i = 0
        while i < len(data):
            if data[i] == '<':
                i = self.parseTag(data, i)
            elif data[i] == '&':
                i = self.parseRef(data, i)
            else:
                j = data.find('<', i)
                k = data.find('&', i)
                if k >= 0 and (j < 0 or k < j): j = k
                if j < 0: j = len(data)
                self.handleData(data[i:j])
                i = j

        if self.offset in self.endPos:
            for k in range(self.endPos[self.offset]):
                outFile.write('</' + self.tagName + '>')


    def parseTag(self, data, i):
        if data[i:i+2] == '</':
            # close tag
            j = data.find('>', i+1)
            if j < 0:
                raise "Unclosed tag"
            if data[i+2:j].strip().upper() != self.tagName.upper():
                self.outFile.write(data[i:j+1])
            return j + 1
        else:
            # open tag
            m = self.starttag.match(data, i)
            if not m:
                raise "Strange tag format"
            if m.group(1).upper() != self.tagName.upper():
                self.outFile.write(data[i:m.end(0)])
            return m.end(0)


    def parseRef(self, data, i):
        m = self.charref.match(data, i)
        if m:
            n = int(m.group(1))
            if n > 65535:
                raise "Unknown character reference " + m.group(0)
            elif n > 127:
                self.handleData(unichr(n))
            else:
                self.handleData(chr(n))
        else:
            m = self.entityref.match(data, i)
            if m:
                name = m.group(1)
                if name in self.entitydefs:
                    s = self.entitydefs[name]
                    self.handleData(s)
                else:
                    # unknown entity reference
                    self.outFile.write(m.group(0))
            else:
                self.handleData('&')
                return i + 1
        return m.end(0)


    def handleData(self, data):
        i = 0
        outBuf = ''
        if self.haveCr and data[:1] == '\n':
            outbuf = data[:1]
            i += 1
        self.haveCr = 0
        while i < len(data):
            if self.offset in self.endPos:
                for k in range(self.endPos[self.offset]):
                    outBuf += '</' + self.tagName + '>'
            if self.offset in self.startPos:
                for attr in self.startPos[self.offset]:
                    attrbuf = ' '.join([
                      xmlEscape(n) + '="' + xmlEscape(v) + '"'
                      for (n, v) in attr ])
                    if attrbuf: attrbuf = ' ' + attrbuf
                    outBuf += '<' + self.tagName + attrbuf + '>'
            if data[i] == '\r':
                if i+1 >= len(data):
                    self.haveCr = 1
                elif data[i+1] == '\n':
                    outBuf += data[i]
                    i += 1
            outBuf += data[i]
            self.offset += 1
            i += 1
        self.outFile.write(outBuf)


class UsageError(Exception):
    pass


# Process one file
def doFile(sgmlFile, xmlFile, outFile):

    print >>sys.stderr, "Processing %s + %s -> %s" % (repr(sgmlFile),
      repr(xmlFile), repr(outFile))

    if os.path.exists(outFile):
        raise UsageError("Output file " + repr(outFile) + " already exists")

    # Read xml file
    elemlist = [ ]
    xdoc = libxml2.parseFile(xmlFile)
    for xnode in xdoc.xpathEval('//TIMEX2'):
        attr = [ ]
        start = end = None
        p = xnode.get_properties()
        while p:
            if p.name == 'rstart':
                start = int(p.content)
            elif p.name == 'rend':
                end = int(p.content) + 1
            else:
                attr += [ (p.name, p.content) ]
            p = p.next
        elemlist.append( (start, end, attr) )
    xdoc.freeDoc()

    # Read sgml file
    f = file(sgmlFile)
    sgmltxt = f.read()
    f.close()

    # Merge timex elements into sgml file
    f = file(outFile, 'w')
    SgmlMerger(sgmltxt, elemlist, 'TIMEX2', f)
    f.close()


# Main program
def main(sgmlFileSpec, xmlFileSpec, outDir):

    nwild = sgmlFileSpec.count('*')
    if nwild > 1:
        raise UsageError("Only zero or one '*' wildcard supported")
    if nwild != xmlFileSpec.count('*'):
        raise UsageError("SGML and XML filespecs must have the same number of wildcards")

    if not os.path.isdir(outDir):
        raise UsageError("Output directory " + repr(outDir) + " not found")

    if nwild:
        sgmldir = os.path.dirname(sgmlFileSpec)
        namepattern = os.path.basename(sgmlFileSpec)
        if '*' in sgmldir:
            raise UsageError("Wildcard only supported in last filename component")
        p = namepattern.find('*')
        assert p >= 0
        namepattern = re.compile(re.escape(namepattern[:p]) + '(.*)' +
                                 re.escape(namepattern[p+1:]) + '$')
        for fname in os.listdir(sgmldir):
            m = namepattern.match(fname)
            if m:
                sgmlfile = os.path.join(sgmldir, fname)
                xmlfile = xmlFileSpec.replace('*', m.group(1))
                doFile(sgmlfile, xmlfile, os.path.join(outDir, fname))
    else:
        fname = os.path.basename(sgmlFileSpec)
        doFile(sgmlFileSpec, xmlFileSpec, os.path.join(outDir, fname))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print __doc__
        sys.exit(1)
    try:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    except UsageError, e:
        print >>sys.stderr, "ERROR:", e
        sys.exit(1)

# End
