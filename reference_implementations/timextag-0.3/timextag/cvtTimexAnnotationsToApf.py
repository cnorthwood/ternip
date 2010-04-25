#!/usr/bin/python
"""Convert TIMEX2 annotations from TERN standoff XML format into ACE APF format.
Usage: cvtTimexAnnotationsToApf [ -f origXmlInDir ] sgmlInDir xmlInFileOrDir outFileOrDir
"""

import sys, re, os.path, cStringIO
import lxml.etree, xml.sax
from xml.sax.xmlreader import AttributesImpl
from xml.sax.saxutils import XMLGenerator, XMLFilterBase

# Only output timex elements from document sections that are
# relevant for ACE: TEXT elements and/or DATETIME elements.
only_relevant_sections = 0

class TernToApf(XMLFilterBase):

    pStartDoc = XMLFilterBase.startDocument
    pEndDoc = XMLFilterBase.endDocument
    pEndElem = XMLFilterBase.endElement
    pChars = XMLFilterBase.characters

    def __init__(self, docid, docuri, docsource, sections, offsetmap):
        XMLFilterBase.__init__(self)
        self.docid = docid
        self.docuri = docuri
        self.docsource= docsource
        self.sections = sections
        self.offsetmap = offsetmap

    def pStartElem(self, name, attr):
        XMLFilterBase.startElement(self, name, AttributesImpl(attr))

    def pNewline(self):
        XMLFilterBase.ignorableWhitespace(self, '\n')

    def startDocument(self):
        self.timexCounter = 0
        self.timexAttrStack = [ ]
        self.timexStringStack = [ ]
        self.pStartDoc()
        attr = { 'URI': self.docuri, 'SOURCE': self.docsource, 'TYPE': 'text' }
        self.pStartElem('source_file', attr)
        self.pNewline()
        attr = { 'DOCID': self.docid }
        self.pStartElem('document', attr)
        self.pNewline()

    def endDocument(self):
        assert not self.timexAttrStack
        self.pEndElem('document')
        self.pNewline()
        self.pEndElem('source_file')
        self.pNewline()
        self.pEndDoc()

    def startElement(self, name, attr):
        if name == 'TIMEX2':
            self.timexAttrStack.append(attr.items())
            self.timexStringStack.append('')

    def endElement(self, name):
        if name == 'TIMEX2':
            assert self.timexAttrStack
            tmxattr = self.timexAttrStack[-1]
            s = self.timexStringStack[-1]
            self.timexAttrStack.pop()
            self.timexStringStack.pop()
            if self.timexStringStack:
                self.timexStringStack[-1] += s
            self.timexCounter += 1
            timexid = self.docid + '-Q' + str(self.timexCounter)
            attr = { 'ID': timexid }
            for (n, v) in tmxattr:
                if n == 'rstart':
                    rstart = int(v)
                elif n == 'rend':
                    rend = int(v)
                elif n.upper() in ('VAL', 'SET', 'MOD', 'ANCHOR_VAL', 'ANCHOR_DIR'):
                    if v: # ACE tool does not like empty attributes
                        attr[n.upper()] = v
            if only_relevant_sections:
                # drop timex elements from irrelevant document sections
                if not [ 1 for (secstart, secend) in self.sections if (secstart <= int(rstart) and secend >= int(rend)) ]:
                    return
            self.pStartElem('timex2', attr)
            self.pNewline()
            attr = { 'ID': timexid + '-1' }
            self.pStartElem('timex2_mention', attr)
            self.pNewline()
            self.pStartElem('extent', { })
            attr = { 'START': str(self.offsetmap[rstart]),
                     'END': str(self.offsetmap[rend+1]-1) }
            self.pStartElem('charseq', attr)
            self.pChars(s)
            self.pEndElem('charseq')
            self.pEndElem('extent')
            self.pNewline()
            self.pEndElem('timex2_mention')
            self.pNewline()
            self.pEndElem('timex2')
            self.pNewline()

    def characters(self, data):
        if self.timexStringStack:
            self.timexStringStack[-1] += data

    def ignorableWhitespace(self, name, attr):
        assert False
 

def doFile(fname, sgmlFile, inFile, outFile, origXmlFile):

    print >>sys.stderr, "Processing '%s'" % fname

    sections = None
    if only_relevant_sections:
        xdoc = lxml.etree.parse(origXmlFile)
        sections = [ ]
        for xnode in xdoc.xpath('//text|//TEXT|//datetime|//DATETIME|//date_time|//DATE_TIME'):
            sections.append( (int(xnode.get('rstart')), int(xnode.get('rend'))) )
        xnode = None
        del xdoc
    print "sections =", sections

    # We need the SOURCE attribute from the SGML file
    inf = file(sgmlFile)
    for s in inf:
        m = re.match(r'<DOCTYPE\s+SOURCE="([^<>"]*)"', s)
        if m:
            docSource = m.group(1)
            break
    inf.close()

    # Scan the SGML file and build a map that translates our rstart/rend
    # offsets to APF START/END offsets.
    # rstart/rend offsets are byte offsets into a UTF8-encoded plain text file.
    # APF offsets are character offsets into the SGML file, after decoding
    # UTF8 and after stripping tags but before processing entity references.
    inf = file(sgmlFile, 'rb')
    sgmldata = inf.read()
    inf.close()
    sgmltxt = re.sub(r'<[^<>]*>', '', sgmldata).decode('utf8')
    offsetmap = [ ]
    i = 0
    reEntityref = re.compile('&([a-zA-Z][a-zA-Z0-9]*)')
    reCharref = re.compile('&#([0-9]+)')
    while i < len(sgmltxt):
        if sgmltxt[i] == '&':
            m = reCharref.match(sgmltxt, i)
            if m:
                offsetmap.append(i)
                i = m.end()
                if sgmltxt[i] == ';': i += 1
                continue
            m = reEntityref.match(sgmltxt, i)
            if m:
                if m.group(1) in ('amp', 'quot', 'apos', 'lt', 'gt'):
                    offsetmap.append(i)
                i = m.end()
                if sgmltxt[i] == ';': i += 1
                continue
        offsetmap.append(i)
        for j in range(len(sgmltxt[i].encode('utf8'))-1):
            offsetmap.append(None)
        i += 1
    offsetmap.append(len(sgmltxt))

    # Run the TernToApf SAX filter over our system's output file to produce APF
    inf = file(inFile)
    outbuf = cStringIO.StringIO()
    xmlgen = XMLGenerator(outbuf, 'UTF-8')
    handler = TernToApf(fname, fname + '.sgml', docSource, sections, offsetmap)
    handler.setContentHandler(xmlgen)
    xml.sax.parse(inFile, handler)
    inf.close()
    
    # insert DOCTYPE line
    doctype = '<!DOCTYPE source_file SYSTEM "apf.v5.1.2.dtd">\n'
    outdata = outbuf.getvalue()
    m = re.match(r'<\?[^<>]+\?>\n', outdata)
    outdata = outdata[:m.end()] + doctype + outdata[m.end():]

    # Write final APF file
    outf = file(outFile, 'wb')
    outf.write(outdata)
    outf.close()


def main(sgmlInDir, xmlInFileOrDir, outFileOrDir, origXmlInDir=None):
    if not os.path.isdir(sgmlInDir):
        print >>sys.stderr, "Need a directory name for sgmlInDir."
        sys.exit(1)
    if os.path.isdir(xmlInFileOrDir):
        if not os.path.isdir(outFileOrDir):
            print >>sys.stderr, "Can't convert from directory to single file."
            sys.exit(1)
        for fname in os.listdir(xmlInFileOrDir):
            sgmlFile = os.path.join(sgmlInDir, fname + '.sgml')
            inFile = os.path.join(xmlInFileOrDir, fname)
            outFile = os.path.join(outFileOrDir, fname + '.system.apf.xml')
            origXmlFile = origXmlInDir and os.path.join(origXmlInDir, fname)
            doFile(fname, sgmlFile, inFile, outFile, origXmlFile)
    else:
        fname = os.path.basename(xmlInFileOrDir)
        if os.path.isdir(outFileOrDir):
            outFile = os.path.join(outFileOrDir, fname)
        else:
            outFile = outFileOrDir
        sgmlFile = os.path.join(sgmlInDir, fname + '.sgml')
        origXmlFile = origXmlInDir and os.path.join(origXmlInDir, fname)
        doFile(fname, sgmlFile, xmlInFileOrDir, outFile, origXmlFile)


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == '-f':
        only_relevant_sections = 1
        main(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[2])
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print >>sys.stderr, __doc__
        sys.exit(1)

