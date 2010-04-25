#!/usr/bin/env python
"""Parsing and sentence splitting of English text.
Usage: parseCharniak.py [--splitblocks] [-p] txtDir xmlDir parseDir

Reads plain text files from txtDir with stand-off markup from xmlDir;
writes parses to parseDir. Only the TEXT sections of documents are
parsed.

The Charniak parser is invoked through the command "charniak-dep-parser",
or through the command specified in environment variable CHARNIAK_DEP_PARSER.

The input text must be encoded in ASCII or Latin-1.
"""

import sys, re, os, os.path
import getopt
import itertools
import libxml2
import sentSplit

proper_dep_parse_flag = False
split_blocks_flag = False

######## Utility function ########

def flatten(lsts):
    return list(itertools.chain(*lsts))

######## Alignment functions ########

spaceRe = re.compile(r'''\s*''')
ignorableRe = re.compile(r'''\^''')


class AlignmentError(ValueError):
    """Used when a parse tree doesn't match the current position of the string."""


charniakSpecials = {
  "-LRB-": ( '(', 1 ),          # LRB matches ( with length 1
  "-RRB-": ( ')', 1 ),          # RRB matches ) with length 1
  "-LCB-": ( '{', 1 ),          # LCB matches { with length 1
  "-RCB-": ( '}', 1 ),          # RCB matches } with length 1
  "-LSB-": ( '[', 1 ),          # LSB matches [ with length 1
  "-RSB-": ( ']', 1 ),          # RSB matches ] with length 1
  "``":  ( ( '"', 1 ),          # `` matches " with length 1
           ( "'", 1 ),          # `` matches ' with length 1
           ( "`", 1 ) ),        # `` matches ` with length 1
  "''":  ( ( '"', 1 ),          # '' matches " with length 1
           ( "'", 1 ),          # '' matches ' with length 1
           ( "`", 1 ) ),        # '' matches ` with length 1
  "will":  ( "won't", 2 ),      # "will n't" matches "won't" with length 2 (wo)
  "Will":  ( "Won't", 2 ),      # "Will n't" matches "Won't" with length 2 (Wo)
  "n't":   ( "'t", 2 ),         # "can n't" matches "can't" with length 2 ('t)
  "IS":  ( ( "ain't", 2 ),      # "IS n't" matches "ain't" with length 2 (ai)
           ( "Ain't", 2 ) ),    # "IS n't" matches "Ain't" with length 2 (Ai)
}


def charniakMatch(word, suffix, cur, restFringe):
    """Try to match parser output <word> at position <cur> in the
    original text <suffix>, and return the number of characters
    to skip in the original text, or return -1 if there is no match.
    """
    s = suffix[cur:]
    if word in charniakSpecials:
        v = charniakSpecials[word]
        if type(v[0]) is not tuple: v = ( v, )
        for (tstr, tlen) in v:
            if s.startswith(tstr):
                return tlen
    elif word == "." and restFringe == []:
        # Parser adds extra period to sentence ending with abbreviation
        return 0
    return -1


def charniakScan(word, suffix, cur):
    """Scan forward in original text <suffix> starting at <cur> until
    a match with parser output <word> is found; return number of characters
    to skip, or -1 if no match was found at all.
    """
    if word in charniakSpecials:
        v = charniakSpecials[word]
        if type(v[0]) is not tuple: v = ( v, )
        bestp = -1
        for (tstr, tlen) in v:
            p = suffix.find(tstr, cur)
            if p >= 0 and (p < bestp or bestp < 0):
                bestp = p
        return bestp - cur
    elif word == ".":
        # Parser adds extra period to sentence ending with abbreviation
        # For these purposes, though, period should act like anything else
        return -1
    return -1


def findNextSentence(suffix, sent, specialCaseScan=charniakScan):
    firstWord = sent[0]
    leadingWSMatch = spaceRe.match(suffix)
    nonWSStart = leadingWSMatch.end()
    print >>sys.stderr, "Attempt to re-align: word=" + repr(firstWord) + " suffix=" + repr(suffix[:100]) + "..."
    # +1 to find _next_ match
    # Joris: I don't get the +1 thing ...
    i = suffix.find(firstWord, nonWSStart + 1)
    j = specialCaseScan(firstWord, suffix, nonWSStart + 1)
    if j >= 0 and (j + nonWSStart + 1 < i or i < 0):
        i = j + nonWSStart + 1
    return i


def align(origSuffix, processedFringe, cur, specialCaseMatch=charniakMatch):
    # If there turn out to be other punctuation issues,
    # put them in specialCaseMatch
    suffix = origSuffix
    offsets = []
    restFringe = list(processedFringe)
    word = None
    if restFringe: word = restFringe.pop(0)
    while word:
        leadingWSMatch = spaceRe.match(suffix)
        nonWSStart = leadingWSMatch.end()
        if suffix[nonWSStart:].startswith(word):
            begin, end = cur+nonWSStart, cur+nonWSStart+len(word)
            offsets.append((begin, end))
            skip = nonWSStart + len(word)
            if restFringe:
                word = restFringe.pop(0)
            else:
                word = None
        elif specialCaseMatch(word, suffix, nonWSStart, restFringe) >= 0:
            length = specialCaseMatch(word, suffix, nonWSStart, restFringe)
            begin, end = cur+nonWSStart, cur+nonWSStart+length
            offsets.append((begin, end))
            skip = nonWSStart + length
            if restFringe:
                word = restFringe.pop(0)
            else:
                word = None
        else:
            ignorableMatch = ignorableRe.match(suffix[nonWSStart:])
            if ignorableMatch:
                skip = nonWSStart + ignorableMatch.end()
            else:
                raise AlignmentError("Alignment failed: word=" + repr(word) + " suffix=" + repr(suffix[:100]) + "...")
        cur += skip
        suffix = suffix[skip:]
    return offsets, suffix, cur


def alignSentence(suffix, sent, cur):
    """Align one sentence on an original string and try to recover from
    mismatches by skipping forward in the original string."""
    try:
        return align(suffix, sent, cur)
    except AlignmentError, e:
        print >>sys.stderr, e
        next = findNextSentence(suffix, sent)
        if next <= 0:
            raise # Could not recover from alignment error
        print >>sys.stderr, "New suffix: suffix=" + repr(suffix[next:next+100]) + "..."
        return alignSentence(suffix[next:], sent, cur + next)


def alignParse(origStr, parses):
    """Align a list of parsed sentences on an original string and return
    aligned offsets for each successfully aligned word."""
    suffix = origStr
    cur = 0
    aligned = [ ]
    for sent in parses:
        offsets, suffix, cur = alignSentence(suffix, sent, cur)
        aligned.append(offsets)
    return aligned


######## Wrapper around Charniak parser ########


class ParseError(ValueError):
    pass


def runParser(textToParse):
    """Run Charniak parser and return output."""
    parserCmd = os.getenv('CHARNIAK_DEP_PARSER', 'charniak-dep-parser')
    (parserIn, parserOut) = os.popen2(parserCmd)
    parserIn.write(textToParse)
    parserIn.close()
    parseOutput = parserOut.read()
    parserOut.close()
    return parseOutput


def parseString(s, baseOffset=0, forcecuts=[]):
    """Parse a string containing a plain text document;
    return a libxml2 object containing the XML parses re-aligned on
    the input string."""

    # Split blocks
    forcecuts.sort()
    p = 0
    blocks = [ ]
    for q in forcecuts:
        q -= baseOffset
        if q > p:
            blocks.append(s[p:q])
            p = q
    if len(s) > p:
        blocks.append(s[p:])

    # Split sentences
    sentences = [ ]
    for block in blocks:
        sentences.extend(sentSplit.splitSentences(block))

    # Format sentences for parser
    if proper_dep_parse_flag:
        sentences = flatten(zip(sentences, map(str, range(len(sentences)))))
    textToParse = '\n'.join(sentences) + '\n'

    # Run parser
    parseOutput = runParser(textToParse)

    # Read XML parser output
    assert parseOutput[:21] == '<?xml version="1.0"?>'
    parseOutput = parseOutput[:19] + ' encoding="' + encoding + '"' + parseOutput[19:]
    xmlparses = libxml2.parseDoc(parseOutput)

    # Align parser output with input string
    xmlwords = [
      [ word for word in sent.xpathEval('.//word') ]
      for sent in xmlparses.xpathEval('/charniak-deps/sentence') ]
    words = [ [ word.content.decode('utf8').encode(encoding)
                for word in sent ]
              for sent in xmlwords ]
    aligned = alignParse(s, words)

    # Add offset attributes to words
    pchar = pbyte = 0
    for (offsets, sent) in zip(aligned, xmlwords):
        for (off, word) in zip(offsets, sent):
            (begin, end) = off
            word.setProp('rstart', str(begin + baseOffset))
            word.setProp('rend', str(end-1 + baseOffset))

    # Propagate offsets to phrases
    for phrase in xmlparses.xpathEval('//phrase'):
        begin = phrase.xpathEval('./descendant::word[1]/@rstart')[0].content
        end = phrase.xpathEval('./descendant::word[last()]/@rend')[0].content
        phrase.setProp('rstart', begin)
        phrase.setProp('rend', end)

    # Return XML document object
    return xmlparses


######## Command-line processing ########


encoding = 'ISO-8859-1'

def parseSplitCorpus(txtDir, xmlDir, outputDir):
    """Parse a set of document from a split-xml/txt corpus."""

    for fname in os.listdir(txtDir):

        print >>sys.stderr, "Parsing " + repr(fname)

        forcecuts = [ ]

        # Read XML markup
        xdoc = libxml2.parseFile(os.path.join(xmlDir, fname))

        # Locate TEXT section in XML markup
        xnodes = xdoc.xpathEval('//TEXT')
        if len(xnodes) != 1:
            print >>sys.stderr, "ERROR: not exactly 1 TEXT element in document"
            xdoc.freeDoc()
            continue
        textStart = int(xnodes[0].prop('rstart'))
        textEnd = int(xnodes[0].prop('rend'))

        if split_blocks_flag:
            # Force sentence splits on certain XML tags
            for p in ('POSTER', 'POSTDATE', 'SUBJECT', 'TURN', 'SPEAKER'):
                for xnode in xdoc.xpathEval('//' + p):
                    if xnode.hasProp('rstart'):
                        forcecuts.append(int(xnode.prop('rstart')))
                    if xnode.hasProp('rend'):
                        forcecuts.append(int(xnode.prop('rend')) + 1)
                xnode = None

        xdoc.freeDoc()
        del xdoc, xnodes

        # Read text file
        f = file(os.path.join(txtDir, fname))
        txtdoc = f.read()
        f.close()

        if split_blocks_flag:
            # Force sentence splits on paragraph boundaries (double newline)
            for m in re.compile(r'\n\s*\n').finditer(txtdoc):
                forcecuts.append(m.start())
    
        # Parse TEXT section
        txt = txtdoc[textStart:textEnd+1]
        parses = parseString(txt, textStart, forcecuts)

        # Write out XML file
        f = file(os.path.join(outputDir, fname), 'wb')
        f.write(parses.serialize(encoding))
        f.close()


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "p", ['splitblocks'])
    opts = dict(opts)
    if '-p' in opts:
        proper_dep_parse_flag = True
    if '--splitblocks' in opts:
        split_blocks_flag = True
    if len(args) != 3:
        print >>sys.stderr, __doc__
        sys.exit(1)
    parseSplitCorpus(args[0], args[1], args[2])

# End
