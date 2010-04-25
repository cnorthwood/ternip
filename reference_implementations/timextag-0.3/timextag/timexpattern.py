"""Pattern-based timex recognition and normalization.

This module implements an annotator interface for old-fashioned
pattern-based timex recognition and normalization. It handles
cases that our trained recognition would frequently miss.
"""

import sys, re
from timexval import *
from timexwords import getWordInfo, getWordsByType
from timexdoc import TimexSpan
from timexnorm import predictAnchorVal


class PatternBasedAnnotator:
    """Run pattern-based timex recognition and normalization for
    special cases.

    Input:  document text, already recognized timex spans;
    Output: timex spans"""

    reNumWord = 'oh|' + '|'.join(map(re.escape, getWordsByType('NUMWORD')))

    reNineEleven = re.compile(
      r'(?<!\w)nine[-\s]\s*eleven(th)?(?!\w)',
      re.I)

    reYearOld = re.compile(
      r'(?<!\w)([0-9,]+)[-\s]years?(?:-?\s?olds?)?(?!\w)',
      re.I)

    reYearOldWord = re.compile(
      r'(?<!\w)(' + reNumWord + r')[-\s]years?(?:-?\s?olds?)?(?!\w)',
      re.I)

    reTimeWords = re.compile(
      r'(?<!\w)' +
      r'(' + reNumWord + ')' +
      r'-(' + reNumWord + ')' +
      r'(?:-(' + reNumWord + '))?' +
      r'\s+([ap])\.?m\.?' +
      r'(?:\s+(eastern))?',
      re.I)

    reYearWords = re.compile(
      r'(?<!\w)nineteen\s+(' + reNumWord +
      r')(?:\s+(' + reNumWord + r'))?(?!\w)',
      re.I)

    def annotateDocument(self, doc):

        if not doc.timestamp:
            print >>sys.stderr, 'WARNING [pattern] no timestamp for document', doc.name
            docstamp = None
        else:
            docstamp = TimePoint(doc.timestamp)

        # Get already recognized spans
        timexspans = doc.timexSpans
        if timexspans is None:
            timexspans = [ ]

        hits = self.matchTimexPatterns(doc.txt)
        for (start, end, prio, val, adir) in hits:

            if prio:
                # Drop all earlier recognized spans that overlap the new one
                timexspans = [ span for span in timexspans
                               if start >= span.end or end <= span.start ]
            else:
                # Drop the new span if it overlaps with an earlier span
                drop = 0
                for span in timexspans:
                    if start < span.end and end > span.start:
                        drop = 1
                        break
                if drop:
                    continue

            # Add the new span
            span = TimexSpan(start=start, end=end, document=doc,
                             txt=doc.txt[start:end], val=val)
            if adir and docstamp:
                span.anchorVal = predictAnchorVal(val, adir, docstamp)
                span.anchorDir = adir
            timexspans.append(span)

        # Sort timex spans and put them back in the document
        timexspans.sort()
        doc.timexSpans = timexspans


    def getWordValue(self, w):
        """Return the numeric value of a word."""
        if w.lower() == 'oh':
            return 0
        else:
            (typ, v) = getWordInfo(w)[0]
            assert typ == 'NUMWORD'
            return v


    def matchTimexPatterns(self, txt):
        """Match patterns against the full document text and return a list
        of recognized timexes in order of preference."""

        hits = [ ]

        for m in self.reNineEleven.finditer(txt):
            hits.append( (m.start(), m.end(), 1, 'XXXX-09-11', None) )

        for m in self.reYearOld.finditer(txt):
            val = 'P%dY' % int(m.group(1).replace(',', ''))
            hits.append( (m.start(), m.end(), 0, val, 'ENDING') ) 

        for m in self.reYearOldWord.finditer(txt):
            val = 'P%dY' % self.getWordValue(m.group(1))
            hits.append( (m.start(), m.end(), 0, val, 'ENDING') ) 

        for m in self.reTimeWords.finditer(txt):
            hour = self.getWordValue(m.group(1))
            minute = self.getWordValue(m.group(2))
            if m.group(3):
                if minute > 0 and minute < 10:
                    continue
                minute += self.getWordValue(m.group(2))
            if hour > 24 or minute > 60:
                continue
            ampm = m.group(4).lower()
            if hour < 12 and ampm == 'p':
                hour += 12
            if hour == 12 and ampm == 'a':
                hour = 0
            val = 'T%02d:%02d' % (hour, minute)
            if m.group(5):
                val += '-05'
            hits.append( (m.start(), m.end(), 0, val, None) )

        for m in self.reYearWords.finditer(txt):
            y = self.getWordValue(m.group(1))
            if m.group(2):
                if y % 10 != 0:
                    continue
                y += self.getWordValue(m.group(2))
            if y < 100:
                val = '19%2d' % y
                hits.append( (m.start(), m.end(), 0, val, None) ) 

        return hits

# End
