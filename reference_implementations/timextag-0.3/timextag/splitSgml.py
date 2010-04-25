#!/usr/bin/env python
"""Usage: splitSgml infile.sgml outfile.xml outfile.blob [baseoffset]

Read an SGML file, split the tags from the text content, output
the content as a blob file and the elements as stand-off XML.
Empty elements, comments and processing instructions are
removed entirely.
"""

import sys, string, re
import sgmllib


def xmlesc(s):
    """Escape special entities amp, lt, gt, and quot."""
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    s = s.replace('"', '&quot;')
    return s


def xmlunesc(s):
    """Unescape special entities amp, lt, gt, quot and apos."""
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&quot;', '"')
    s = s.replace('&apos;', "'")
    s = s.replace('&amp;', '&')
    return s


class SgmlSplitter(sgmllib.SGMLParser):
    """SGML parser customized for splitting tags from content."""

    def __init__(self, outblb):
        sgmllib.SGMLParser.__init__(self)
        self.outblb = outblb

    def reset(self):
        sgmllib.SGMLParser.reset(self)
        self.offset = 0
        self.elemstack = [ ]
        self.xmlstack = [ '' ]
        self.haveCr = 0

    def close(self):
        sgmllib.SGMLParser.close(self)
        # Pop remaining open elements and collect XML fragments
        xmlstr = ''
        while self.elemstack:
            self.elemstack.pop()
            xmlstr = self.xmlstack.pop() + xmlstr
        # Add XML fragment to the top-level context
        self.xmlstack[-1] += xmlstr

    def getXml(self):
        """Return a string containing all extracted XML tags.
        The close() method must be called before callisg getXml()."""
        ( xmlstr, ) = self.xmlstack
        return xmlstr

    def handle_data(self, data):
        # Translate '\r\n' into '\n' and '\r' into '\n'
        if self.haveCr and data[:1] == '\n': data = data[1:]
        self.haveCr = (data[-1:] == '\r')
        data = data.replace('\r\n', '\n')
        data = data.replace('\r', '\n')
        # Write to output
        self.offset += len(data)
        self.outblb.write(data)
        # Use newlines for decent XML formatting
        if not self.xmlstack[-1].endswith('\n') and '\n' in data:
            self.xmlstack[-1] += '\n'

    def unknown_starttag(self, tag, attrs):
        tag = tag.upper()
        # Push this tag on the open element stack
        self.elemstack.append( (tag, attrs, self.offset) )
        self.xmlstack.append('')

    def unknown_endtag(self, tag):
        tag = tag.upper()
        # Look for this tag in the open element stack
        i = len(self.elemstack) - 1
        while i >= 0 and self.elemstack[i][0] != tag: i -= 1
        if i < 0:
            print >>sys.stderr, "WARNING: Close tag for non-open element " + repr(tag)
            return
        # Pop the stack and collect XML fragments until we reach our element
        xmlstr = ''
        opentag = None
        while opentag != tag:
            (opentag, attrs, rstart) = self.elemstack.pop()
            xmlstr = self.xmlstack.pop() + xmlstr
        # Format open and close tags for this element
        rend = self.offset - 1
        if rstart <= rend:
            attrstr = ' rstart="' + str(rstart) + '" rend="' + str(rend) + '"'
            for (attrname, attrvalue) in attrs:
                attrstr += ' ' + attrname + '="' + \
                  xmlesc(xmlunesc(attrvalue)) + '"'
            xmlstr = '<' + tag + attrstr + '>' + xmlstr + '</' + tag + '>'
        # Add XML fragment to the current context
        self.xmlstack[-1] += xmlstr


def splitSgml(sgmldata, outxml, outblb, offset):
    """Split one SGML file into XML tags and data blob."""
    # The SGML parser breaks on empty elements, so strip them away
    sgmldata = re.sub(r'<[^<>]*/>', '', sgmldata)
    sgsplit = SgmlSplitter(outblb)
    sgsplit.offset = offset
    sgsplit.feed(sgmldata)
    sgsplit.close()
    outxml.write(sgsplit.getXml())


# Main program
def main(argv):

    if len(argv) not in (4, 5):
        print >>sys.stderr, __doc__
        return 1

    infile = file(argv[1], "rb")
    sgmldata = infile.read()
    infile.close()

    outxml = file(argv[2], "w")
    outblb = file(argv[3], "wb")

    offset = 0
    if len(argv) == 5: offset = int(argv[4])

    splitSgml(sgmldata, outxml, outblb, offset)

    outxml.close()
    outblb.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
        
# End
