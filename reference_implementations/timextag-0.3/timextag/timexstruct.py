"""Recognition and normalization of fully qualified, strutured timexes.

This module implements an annotator interface for rule-based recognition
and normalization of fully qualified timexes that match a very limited
set of patterns.

It is used to process timestamps in document headers etc, where
machine learned recognition/classification does not work (reliably).
"""

import sys, re
from timexval import *
from timexwords import getWordInfo, getWordsByType
from timexdoc import TimexSpan


######## Annotation interface ########

class StructuredTimexAnnotator:
    """Recognize and normalize structured numeric timexes.

    Input:  document text;
    Output: timex spans, span.val, document timestamp"""

    def __init__(self):
        self.matcher = StructuredTimexMatcher()

    def annotateDocument(self, doc):

        timexspans = [ ]
        timestamp = None
        timestampscore = None

        # Walk all recognized spans
        for (start, end, val) in self.matcher.findTimexes(doc.txt):

            # Drop this span if it overlaps with an earlier span
            drop = 0
            for span in timexspans:
                if start < span.end and end > span.start:
                    drop = 1
                    break
            if drop:
                continue

            # Drop this span if it overlaps with a forbidden span
            if doc.forbiddenSpans:
                for span in doc.forbiddenSpans:
                    if start < span.end and end > span.start:
                        drop = 1
                        break
            # AWFUL HACK : exception for 2 documents that have no other reftime
            if doc.name == 'AFP20020328.1.tmx' or \
               doc.name == 'XIN19991125.1.tmx':
                drop = 0
            if drop:
                continue

            # Drop this span if it crosses a TEXT section boundary
            if doc.textSpans:
                for span in doc.textSpans:
                    if (start < span.start and end > span.start) or \
                       (start < span.end and end > span.end):
                        drop = 1
                        break
            if drop:
                continue

            # If this span does not specify a year, merge it with the year
            # from the current best timestamp candidate
            if val.startswith('XXXX'):
                if not timestamp:
                    # There is no reference year; drop this span
                    continue
                # Fetch reference year from current best timestamp
                refyear = int(timestamp[0:4])
                refmonth = int(timestamp[5:7])
                valmonth = int(val[5:7])
                # Tweak to get around year boundaries
                if refyear < 9999 and refmonth == 12 and valmonth == 1:
                    refyear += 1
                elif refyear > 0 and refmonth == 1 and valmonth == 12:
                    refyear -= 1
                # Merge reference year with month,day value
                val = ('%04d' % refyear) + val[4:]

            # Add it as a timex span
            timexspans.append(TimexSpan(start=start, end=end, document=doc,
                                        txt=doc.txt[start:end], val=val))

            # Maintain the best document timestamp candidate
            valscore = timestampPreferenceScore(doc, start, end, val)
            if (not timestamp) or valscore > timestampscore:
                timestamp = val
                timestampscore = valscore

        # Store sorted list of timex spans in document object
        timexspans.sort()
        doc.timexSpans = timexspans

        # Store document timestamp in document object
        doc.timestamp = timestamp


######## StructuredTimexMatcher ########

class StructuredTimexMatcher:
    """Match structured numeric timexes in a text string using
    regular expressions."""

    # Regular subexpression which matches a year between 1000 and 2999
    reYear = r'(?P<year>[12]\d{3})' 

    # Regular subexpression which matches a month number or month name
    reMon = r'(?P<mon>0?[1-9]|1[012]|(?:' + \
      '|'.join(map(re.escape, getWordsByType('MONTHNAME'))) + r')\.?)'

    # Regular subexpression which matches a month name
    reMonthName = r'(?:(?P<mon>' + \
      '|'.join(map(re.escape, getWordsByType('MONTHNAME'))) + r')\.?)'

    # Regular subexpression which matches a day number
    reDay = r'(?P<day>0?[1-9]|[12]\d|3[01])'

    # Regular subexpression matching a time zone abbreviation
    reTimezone = r'(?P<tz>' + \
      r'[-+][0-9]{2}(?::?[0-9]{2})?|' + \
      r'eastern (?:standard )?time|universal time|' + \
      '|'.join(map(re.escape, getWordsByType('TIMEZONE'))) + r')'

    # Regular subexpression which matches digital time with optional time zone
    reTime = r'(?:(?P<hour>0?\d|1\d|2[0-4]):(?P<min>[0-6]\d)' + \
      r'(?::(?P<sec>[0-6]\d)(?:[.,](?P<sub>\d+))?)?' + \
      r'(?:\s*' + reTimezone + r')?)'

    # Regular subexpression matching day-of-week names
    reDayname = r'(?:' + \
      '|'.join(map(re.escape, getWordsByType('DAYNAME'))) + r')'

    # Match unseparated YYYYMMDD date with optional time
    # (restrict year to range 1000 ... 2999)
    reDateTimeIso = re.compile(
      r'(?<!\d)' +                              # not preceded by a digit
      r'(?P<year>[12][0-9]{3})(?P<mon>0[1-9]|1[012])' +
      r'(?P<day>0[1-9]|[12][0-9]|3[01])' +      # YYYYMMDD part
      r'(?:\s*[-t ]' + reTime + r')?' +         # optional time
      r'(?!\d)',                                # not followed by a digit
      re.IGNORECASE)

    # Match separated YYYY-M-D date with optional time
    reDateTimeYMD = re.compile(
      r'(?<!\d)' +                              # not preceded by a digit
      reYear + r'(?P<sep>[-/.])' + reMon +
      r'(?P=sep)' + reDay +                     # YYYY-M-D
      r'(?:\s*[ t]' + reTime + r')?' +          # optional time
      r'(?!\w)',                                # not followed by an alphanum
      re.IGNORECASE)

    # Match separated M/D/YYYY date with optional time
    reDateTimeMDY = re.compile(
      r'(?<!\w)' +                              # not preceded by an alphanum
      reMon + r'(?P<sep>[-/.])' + reDay +
      r'(?P=sep)' + reYear +                    # M-D-YYYY
      r'(?:\s*[t ]' + reTime + r')?' +          # optional time
      r'(?!\w)',                                # not followed by an alphanum
      re.IGNORECASE)

    # Match M D, YYYY date with optional time
    # (the ugly optional dayname is just to recognize a few
    # occurrences in news message headers)
    reDateTimeTextMDY = re.compile(
      r'(?<!\w)' +                              # not preceded by an alphanum
      reMonthName + r'\s+' + reDay +
      r'[, ]\s*' + reYear +                     # M D YYYY
      r'(?:;?\s*(?:' + reDayname + r')?' +      # optional dayname (ignored)
      r'\s*[t ]' + reTime + r')?' +             # optional time
      r'(?!\w)',                                # not followed by an alphanum
      re.IGNORECASE)

    # Match separated D M YYYY date with optional time
    # (also match an optional day-of-week name)
    reDateTimeTextDMY = re.compile(
      r'(?<!\w)' +                              # not preceded by an alphanum
      r'(?:' + reDayname + r'[,\s]\s*)?' +      # optional dayname (ignored)
      reDay + r'\s+' + reMon +
      r'[., ]\s*' + reYear +                    # D sep M sep YYYY
      r'(?:,?\s*[t ]' + reTime + r')?' +        # optional time
      r'(?!\w)',                                # not followed by an alphanum
      re.IGNORECASE)

    # Match Month Day partial date
    reMonthDay = re.compile(
      r'(?<!\w)(?<!\d\s)' +                     # not preceded by numeric stuff
      reMonthName + r'\s+' + reDay +            # month name and day
      r'(?:st|nd|rd|th)?' +                     # optional rankword suffix
      r'(?!,?\s*\d)',                           # not followed by a number
      re.IGNORECASE)

    # Match Day Month partial date
    reDayMonth = re.compile(
      r'(?<!\w)(?<!\d\s)' +                     # not preceded by numeric stuff
      reDay + r'\s+' + reMonthName +            # day and month name
      r'(?!\w)(?!,?\s*\d)',                     # not followed by a number
      re.IGNORECASE)

    # Match timestamps in New York Times style
    reDateTimeNYT = re.compile(
      r'(?<=[A-Z]-)' +                          # preceded by NYT- or NY-
      r'(?P<mon>[01]\d)-(?P<day>[0-3]\d)-(?P<year>\d{2})' + # MM-DD-YY
      r'\s+(?P<hour>[0-2]\d)(?P<min>[0-6]\d)' + # HHMM
      r'\s*' + reTimezone,                      # timezone
      re.IGNORECASE)

    # Match timestamp with ? wildcards (used in ACE email documents)
    reWildcardTimeIso = re.compile(
      r'(?<!\d)' +                              # not preceded by a digit
      r'\?\?\?\?-\?\?-\?\?' +                   # wildcard date
      r'\s*[-t ]' + reTime +                    # time
      r'(?!\d)',                                # not followed by a digit
      re.IGNORECASE)


    def findTimexes(self, txt):
        """Recognize structured numeric timexes in a text string
        and return a list of (start, end, val) tuples.
        If a span has multiple possible interpretations as a timex,
        return all of them in order of preference."""

        timexList = [ ]

        for pat in (self.reDateTimeNYT,
                    self.reWildcardTimeIso,
                    self.reDateTimeYMD,
                    self.reDateTimeMDY,
                    self.reDateTimeTextMDY,
                    self.reDateTimeTextDMY,
                    self.reDateTimeIso,
                    self.reMonthDay,
                    self.reDayMonth):
            for m in pat.finditer(txt):
                # normalize date
                mgroup = m.groupdict()
                if ('year' not in mgroup) and ('mon' not in mgroup):
                    # wildcard date
                    s = ''
                else:
                    year = mgroup.get('year')
                    if not year:
                        # month/day expression without year
                        year = 'XXXX'
                    elif len(year) != 4:
                        # expand 2-digit year
                        assert len(year) == 2
                        if int(year) < 20:
                            year = '20' + year
                        else:
                            year = '19' + year
                    mon = mgroup['mon']
                    if mon.isdigit():
                        mon = int(mon)
                    else:
                        # lookup month name in word list
                        (typ, mon) = getWordInfo(mon.rstrip('.'))[0]
                        assert typ == 'MONTHNAME'
                    day = int(mgroup['day'])
                    s = '%s-%02d-%02d' % (year, mon, day)
                # normalize time
                hour = mgroup.get('hour')
                min = mgroup.get('min')
                sec = mgroup.get('sec')
                sub = mgroup.get('sub')
                if hour: s += 'T%02d' % int(hour)
                if min:  s += ':%02d' % int(min)
                if sec:  s += ':%02d' % int(sec)
                if sub:  s += '.' + sub
                # normalize timezone
                tz = mgroup.get('tz')
                if tz:
                    if tz[0] in '+-':
                        if len(tz) == 6 and tz[3] == ':':
                            tz = tz[:3] + tz[4:6]
                        if len(tz) == 5 and tz[3:5] == '00':
                            tz = tz[:3]
                        assert len(tz) in (3, 5)
                        if tz[1:] == '00':
                            tz = 'Z'
                    elif tz.lower() == 'universal time':
                        tz = 'Z'
                    elif tz.lower() == 'eastern time':
                        tz = '-05'
                    elif tz.lower() == 'eastern standard time':
                        tz = '-05'
                    else:
                        # lookup timezone in word list
                        (typ, tz) = getWordInfo(tz)[0]
                        assert typ == 'TIMEZONE'
                    if not hour: s += 'T'
                    s += tz
                # add normalized timex to list
                timexList.append( (m.start(), m.end(), s) )

        return timexList


######## Document timestamp selection ########

def timestampPreferenceScore(doc, start, end, val):
    """Return a preference score for this span as the document timestamp;
    the span with largest score is selected as document timestamp."""

    # Rule 1: Prefer the timex which is indicated as timestamp by
    #         the document markup.
    if ( doc.timestampSpan and
         start >= doc.timestampSpan.start and end <= doc.timestampSpan.end ):
        return (-1, -start)

    # Rule 2: Prefer the first timex that starts within the first
    #         20 characters of the TEXT section.
    if ( doc.textSpans and
         start >= doc.textSpans[0].start and end <= doc.textSpans[0].end and
         start <= doc.textSpans[0].start + 20 ):
        return (-2, -start)

    # Measure value precision
    prec = len(val)

    # Rule 3: Prefer the timex with greatest precision that starts before
    #         the TEXT section; of these, prefer the one that occurs last.
    if ( doc.textSpans and
         start < doc.textSpans[0].start ):
        return (-3, prec, start)

    # Rule 4: Prefer the timex with greatest precision; of these,
    #         prefer the one that occurs first.
    return (-4, prec, -start)


######## Test program ########

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Test recognition of structured timexes."
        print "Usage: python timexstruct.py input.txt"
        sys.exit(1)
    f = file(sys.argv[1])
    s = f.read()
    f.close()
    m = StructuredTimexMatcher()
    for (start, end, val) in m.findTimexes(s):
        print (start, end, val, s[start:end])

# End
