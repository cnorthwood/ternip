"""Timex normalization.

This module implements annotator interfaces for pre-normalization
and final normalization of timexes.
"""

import sys, re
from copy import copy
from patternmatch import *
from timexval import *
from timexwords import getWordInfo, getWordTypeList
from timexref import TimexReferenceTracker
from timexprenormval import *


######## Annotation interface ########

class PreNormAnnotator:
    """Perform pre-normalization on the document's timex spans.

    Input:  span.tmxclass, span.txt;
    Output: span.prenorm, span.mod, span.anchorDir"""

    def annotateDocument(self, doc):

        # For each timex span
        for span in doc.timexSpans:
            span.prenorm = span.mod = span.anchorDir = None

            # Skip span if it has no tmxclass attribute
            if span.tmxclass is None:
                continue

            v = None
            if span.tmxclass == '':
                # Negative class (not-normalizable timex)
                v = None
            else:
                # Run pre-normalization patterns
                (v, mod, anchor) = parseTimex(span.__str__(), span.tmxclass)

            # Store results in attributes
            if v is None:
                span.prenorm = ''
            else:
                preNormValName = 'PreNormVal_' + span.tmxclass
                preNormVal = parseTimex.func_globals[preNormValName]
                span.prenormval = preNormVal(v=v)
                if type(v) is tuple:
                    v = encodeTuple(v)
                span.prenorm = v
                span.mod = mod
                span.anchorDir = anchor


class FinalNormAnnotator:
    """Perform final-normalization on the document's timex spans.

    Input:  span.prenorm, span.tmxclass, span.dirclass, doc.timestamp;
    Output: span.val, span.set, span.anchorVal"""

    def __init__(self, refmodel):
        if refmodel:
            self.refmodel = refmodel
        else:
            self.refmodel = None

    def annotateDocument(self, doc):

        # Get document timestamp
        if not doc.timestamp:
            #raise ValueError('Document without timestamp: ' + repr(doc))
            # No, don't crash on this for ACE2007
            mesg('WARNING [norm] no timestamp for document ' + doc.name + '\n')
            docstamp = None
        else:
            docstamp = TimePoint(doc.timestamp)
            ref_tracker = TimexReferenceTracker(docstamp, doc.timexSpans,
                                                refmodel=self.refmodel)

        # Initialize recent timex to document timex
        recentval = doc.timestamp

        # For each timex span
        for span in doc.timexSpans:
            span.val = span.set = span.anchorVal = None

            # Normalize only spans that have a prenorm attribute
            if span.prenorm is not None:
                if span.prenorm.find('|') == -1:
                    # prenorm is already the final value
                    span.val = span.prenorm
                else:
                    if not span.dirclass and not span.prenorm.startswith('|fq|'):
                        mesg("WARNING: [norm] Missing timex dirclass attribute: " +
                             repr(span) + "\n")
                    # Run final normalization
                    v = decodeTuple(span.prenorm)
                    if not docstamp:
                        # Special case for when we can not use reference times
                        if span.prenormval.ref_type == 'fq':
                            span.val = span.prenormval.datestr
                    else:
                        span.val = normalizePoint(span, ref_tracker)

            # Value of the 'set' attribute follows from timex class
            if span.tmxclass is not None:
                if span.tmxclass == 'recur':
                    span.set = 'YES'
                else:
                    span.set = ''

            # Put the document timestamp in anchorVal
            if span.anchorDir and docstamp:
                span.anchorVal = predictAnchorVal(span.val, span.anchorDir, docstamp)

            # Keep track of most recent point timex
            if span.val and span.tmxclass == 'point':
                recentval = span.val


######## Function call interface ########

def parseTimex(timexString, timexClass):
    """Match timexString against a normalization pattern for timexClass;
    return pre-normalization result, or return None if no match was found."""

    # Force string to pure ASCII
    s = re.sub(r'[^\s -~]', '*', timexString)
    timexString = str(s)

    # Split string into tokens
    rawTokens = tokenize(timexString)

    # Do lookup on the tokens
    tokens, supertok = lookupTokens(rawTokens)

    # Find the transducer for this timex class
    handlerName = 'TimexTransducer_' + timexClass
    handler = parseTimex.func_globals[handlerName]

    # Invoke the transducer
    trans = handler(tokens, supertok, getWordTypeList())
    v = trans.go()
    return v

def normalizePoint(span, ref_tracker):
    v = decodeTuple(span.prenorm)
    pn_point = span.prenormval
    ref_type = pn_point.ref_type
    dirclass = span.dirclass

    if ref_type == 'fq':
        # fully qualified, don't do anything
        t = TimePoint(pn_point.datestr)

    else:
        # reference time is needed
        ref = ref_tracker.resolve(span)
        if ref_type in ('dex', 'ana', 'dem', 'amb'):
            # non-offset point
            t = TimePoint(pn_point.datestr)
            # truncate ref to required precision
            ref_unit = pn_point.ref_unit
            tref = copy(ref)
            if ref_unit:
                tref.truncate(ref_unit)
            p = tref.specific_precision()
            # extend to required precision using placeholders
            if ref_unit and cmpUnit(p, ref_unit) < 0:
                tref.extend_nonspecific(ref_unit)
            # merge with partial timex
            t.merge(tref)
            # slide reference time forward/backward
            if p == U_YEAR and isinstance(t.year, int) and \
                isinstance(t.month, int) and isinstance(t.day, int) and \
                isinstance(t.wday, int):
                # use month,mday,wday to disambiguate the year
                (w, dmin) = date_ymd_to_ywd(t.year - 1, t.month, t.day)
                (w, dplus) = date_ymd_to_ywd(t.year + 1, t.month, t.day)
                if dmin == t.wday: t.year -= 1
                if dplus == t.wday: t.year += 1
                t.week = t.wday = None
            elif dirclass and isSystematicUnit(p):
                # use dirclass to disambiguate at component p
                c = t.compare(ref)
                if (c < 0 and dirclass != 'before') or \
                        (c == 0 and dirclass == 'after'):
                    # try to fix it by adding one unit at component p
                    tt = copy(t)
                    tt.add_units(p, 1)
                    # take this change only if it helps
                    c = tt.compare(ref)
                    if (c == 0 and dirclass == 'same') or \
                            (c > 0 and dirclass == 'after'):
                        t = tt
                elif (c > 0 and dirclass != 'after') or \
                        (c == 0 and dirclass == 'before'):
                    # try to fix it by substracting one unit at component p
                    tt = copy(t)
                    tt.add_units(p, -1)
                    # take this change only if it helps
                    c = tt.compare(ref)
                    if (c == 0 and dirclass == 'same') or \
                            (c < 0 and dirclass == 'before'):
                        t = tt

        elif ref_type in ('offdex', 'offana', 'offdem', 'offtoday'):
            # offset from reference time
            n = pn_point.n
            u = pn_point.unit
            t = TimePoint(pn_point.datestr)
            if isinstance(n, float):
                # non-integral numbers are only allowed for hour, minute, second
                if u == U_YEAR:
                    n = int(12 * n)
                    u = U_MONTH
                elif u == U_DECADE:
                    n = int(10 * n)
                    u = u_YEAR
                elif u == U_CENTURY:
                    n = int(10 * n)
                    u = U_DECADE
                elif u == U_MILLENNIUM:
                    n = int(10 * n)
                    u = U_CENTURY
                elif u not in (U_HOUR, U_SECOND, U_MINUTE):
                    # we don't know how to handle this; truncate to integer
                    mesg("WARNING: [norm] non-integral offset: %f%s\n" %
                         (n, str(u)))
                    n = int(n)
            # truncate ref to the expressed precision
            tref = copy(ref)
            if ref_type == 'offtoday':
                tref.truncate(U_DAY)
            else:
                tref.truncate(u)
            # add the offset
            if cmpUnit(tref.specific_precision(), u) < 0:
                # reference is not specific enough; extend it with placeholders
                tref.extend_nonspecific(u)
            elif n == 'X':
                # put a placeholder in the last component
                tref.set_component_unknown(u)
            else:
                tref.add_units(u, n)
            # merge with partial timex
            t.merge(tref)

        else:
            mesg("Something wrong with prenormval: %s" % pn_point)

    # Suppress week,wday when we have a full date
    if type(t.year) is type(t.month) is int and type(t.day) is int:
        t.week = t.wday = None

    # Return ISO string
    return str(t)

def _normalizePoint(datespec, reffn, dirclass):
    """Compute final normalized value from decoded timex and reference time."""

    typ = datespec[0]
    if typ == 'fq':
        # fully qualified, don't do anything
        (typ, datestr) = datespec
        t = TimePoint(datestr)

    elif typ in ('dex', 'ana', 'dem', 'amb'):
        # incomplete date; resolve using reference time and dirclass
        (typ, u, datestr) = datespec
        t = TimePoint(datestr)
        # get reference time
        ref = reffn(typ, u)
        # truncate to the required precision
        tref = copy(ref)
        if u:
            tref.truncate(u)
        p = tref.specific_precision()
        # extend to required precision using placeholders
        if u and cmpUnit(p, u) < 0:
            tref.extend_nonspecific(u)
        # merge with partial timex
        t.merge(tref)
        # slide reference time forward/backward
        if p == U_YEAR and type(t.year) is int and type(t.month) is int and \
           type(t.day) is int and type(t.wday) is int:
            # use month,mday,wday to disambiguate the year
            (w, dmin) = date_ymd_to_ywd(t.year - 1, t.month, t.day)
            (w, dplus) = date_ymd_to_ywd(t.year + 1, t.month, t.day)
            if dmin == t.wday: t.year -= 1
            if dplus == t.wday: t.year += 1
            t.week = t.wday = None
        elif dirclass and isSystematicUnit(p):
            # use dirclass to disambiguate at component p
            c = t.compare(ref)
            if (c < 0 and dirclass != 'before') or \
               (c == 0 and dirclass == 'after'):
                # try to fix it by adding one unit at component p
                tt = copy(t)
                tt.add_units(p, 1)
                # take this change only if it helps
                c = tt.compare(ref)
                if (c == 0 and dirclass == 'same') or \
                   (c > 0 and dirclass == 'after'):
                    t = tt
            elif (c > 0 and dirclass != 'after') or \
                 (c == 0 and dirclass == 'before'):
                # try to fix it by substracting one unit at component p
                tt = copy(t)
                tt.add_units(p, -1)
                # take this change only if it helps
                c = tt.compare(ref)
                if (c == 0 and dirclass == 'same') or \
                   (c < 0 and dirclass == 'before'):
                    t = tt

    elif typ in ('offdex', 'offana', 'offdem', 'offtoday'):
        # offset from reference time
        (typ, u, n, datestr) = datespec
        t = TimePoint(datestr)
        if type(n) is float:
            # non-integral numbers are only allowed for hour, minute, second
            if u == U_YEAR:
                n = int(12 * n)
                u = U_MONTH
            elif u == U_DECADE:
                n = int(10 * n)
                u = u_YEAR
            elif u == U_CENTURY:
                n = int(10 * n)
                u = U_DECADE
            elif u == U_MILLENNIUM:
                n = int(10 * n)
                u = U_CENTURY
            elif u not in (U_HOUR, U_SECOND, U_MINUTE):
                # we don't know how to handle this; just truncate to an integer
                mesg("WARNING: [norm] non-integral offset: %f%s\n" %
                     (n, str(u)))
                n = int(n)
        # get reference time
        if typ == 'offdex': ref = reffn('dex', u)
        if typ == 'offana': ref = reffn('ana', u)
        if typ == 'offdem': ref = reffn('dem', u)
        if typ == 'offtoday': ref = reffn('dex', U_DAY)
        # truncate to the expressed precision
        tref = copy(ref)
        if typ == 'offtoday':
            tref.truncate(U_DAY)
        else:
            tref.truncate(u)
        # add the offset
        if cmpUnit(tref.specific_precision(), u) < 0:
            # reference is not specific enough; extend it with placeholders
            tref.extend_nonspecific(u)
        elif n == 'X':
            # put a placeholder in the last component
            tref.set_component_unknown(u)
        else:
            tref.add_units(u, n)
        # merge with partial timex
        t.merge(tref)

    # Suppress week,wday when we have a full date
    if type(t.year) is type(t.month) is int and type(t.day) is int:
        t.week = t.wday = None

    # Return ISO string
    return str(t)

def predictAnchorVal(tmxval, anchorDir, docstamp):
    """Given the normalized timex value and anchor direction, predict
    the anchored value. This function simply returns the document timestamp,
    possibly truncated to the precision of the timex value."""
    p = None
    aval = docstamp
    if tmxval[:1] == 'P':
        suff = tmxval[-2:]
        if suff == 'CE': p = U_CENTURY
        elif suff == 'DE': p = U_DECADE
        elif suff in ('WI', 'SP', 'SU', 'FA'): p = U_YEAR
        elif suff in ('HX', 'QX'): p = U_MONTH
        elif suff in ('MO', 'MI', 'AF', 'EV', 'NI'): p = U_DAY
        else:
            suff = tmxval[-1:]
            if 'T' in tmxval:
                if suff == 'H': p = U_HOUR
                elif suff == 'M': p = U_MINUTE
                elif suff == 'S': p = U_SECOND
            else:
                if suff == 'Y': p = U_YEAR
                elif suff == 'M': p = U_MONTH
                elif suff == 'W': p = U_WEEK
                elif suff == 'D': p = U_DAY
    if p:
        aval = copy(docstamp)
        aval.truncate(p)
    return str(aval)


######## Internal functions ########

def mesg(s):
    import timextool
    timextool.mesg(s)


def encodeTuple(v):
    """Encode a tuple as a string."""
    def f(x):
        if type(x) is str:
            if x == '' or x[0] in '_|-+.0123456789':
                x = '_' + x
            return x.replace('|', '||')
        if type(x) in (int, long, float):
            return str(x)
        raise ValueError("Unsupported value type: " + repr(v))
    return '|' + '|'.join(map(f, v))


def decodeTuple(s):
    """Decode an encoded tuple string."""
    assert s[0] == '|'
    if s == '|':
        return ( )
    v = [ ]
    p = None
    for t in s[1:].split('|'):
        if p:
            v[-1] += p + t
            p = None
        elif t == '':
            p = '|'
        elif t[0] == '_':
            v.append(t[1:])
        else:
            if t[0] in '-+.0123456789':
                try:
                    t = int(t)
                except ValueError:
                    t = float(t)
            v.append(t)
    return tuple(v)


def lookupTokens(tokens):
    """Convert tokens to lower case, look up each token against a list
    of special words and patterns and create a SuperToken for each match."""
    tokens = [ tok.lower() for tok in tokens ]
    supertok = [ [ ] for tok in tokens ]
    for i in range(len(tokens)):
        s = tokens[i]
        # look up the token against a list of special words
        w = getWordInfo(s)
        if w:
            for (typ, val) in w:
                supertok[i].append(
                  SuperToken(start=i, end=i+1, name=typ, val=val, raw=s))
    return tokens, supertok


def expandYear(y):
    """Expand a 2-digit year into a full 4-digit year."""
    if y < 20:
        return y + 2000
    else:
        return y + 1900


def applyAmPmToHour(h, ampm):
    """Translate a 12-hour number to a 24-hour number using AM/PM info."""
    if h < 12 and (ampm == 'PM' or h >= 8 and ampm == 'NI'):
        return h + 12
    elif h == 12 and (ampm == 'AM' or ampm == 'NI'):
        return 0
    else:
        return h


######## Common timex patterns ########

# For every timex category, there is a specialized TimexTransducer class
# with pre-normalization rules for that category. The go() method
# runs all rules and returns a tuple
#   ( prenorm value, mod attribute, anchorDir attribute)
# The base class TimexTransducer contains some common patterns.

class TimexTransducer(Transducer):
    """Transduction rules for timex strings."""

    # Compute numeric value of a group of number words
    def NumberWords(self, args):
        """ { NUMWORD ( ("and"|"-")? NUMWORD )* } """
        stack = [ ]
        for tok in args[0]:
            if isinstance(tok, SuperToken):
                v = tok.val
                if v >= 100 and stack and stack[-1] < v:
                    t = 0
                    while stack and stack[-1] < v:
                        t += stack.pop()
                    stack.append(t * v)
                else:
                    stack.append(v)
        return sum(stack)

    # Compute numeric value of a number with thousand separators
    def SegmentedNumber(self, args):
        """ { NUM ( "," NUM )+ } """
        t = args[0][0]
        if len(t.raw) > 3:
            return
        v = t.val
        for t in args[0][2::2]:
            if len(t.raw) != 3:
                return
            v = v * 1000 + t.val
        return v

    # Match any numeric form
    def Numeric(self, args):
        """ { NUM | NumberWords | SegmentedNumber } """
        return args[0][0].val

    # Match rankword or digital rank expression
    def Rank(self, args):
        """ { RANKWORD | NUM ("st"|"nd"|"rd"|"th") } """
        return args[0][0].val

    # Match rank or digital number with value at most 31
    def Num31OrRank(self, args):
        """ { RANKWORD | NUM31 ("st"|"nd"|"rd"|"th")? } """
        return args[0][0].val

    # Match word groups that indicate approximation
    def Approx(self, args):
        """ { "by" | ("right"|"just")? "about" | ("right"|"just")? "around" |
              "approximately" | "some" } |
            { "almost" | "nearly" | "less" "than" | ("most"|"much") "of" } |
            { "more" "than" } |
            { "at" "most" } |
            { "at" "least" }"""
        if args[1]: return 'LESS_THAN'
        if args[2]: return 'MORE_THAN'
        if args[3]: return 'EQUAL_OR_LESS'
        if args[4]: return 'EQUAL_OR_MORE'
        return 'APPROX'

    # Match a prefix that indicates an approximation modifier
    def ApproxMod(self, args):
        """ ^ {Approx} """
        return args[0][0].val

    # Match a prefix that indicates a start/mid/end modifier
    def StartEndMod(self, args):
        """ ^ "the"? { "early" | "late" | "mid" "-" |
                       ("start" | "beginning" | "end") "of" } """
        if args[0][0] in ('early', 'start', 'beginning'):
            return 'START'
        if args[0][0] in ('late', 'end'):
            return 'END'
        if args[0][0] == 'mid':
            return 'MID'

    # Match a prefix that indicates anchoring of a duration
    def AnchorPrefix(self, args):
        """ ^ { ("the"|"these") ("next" | "coming") } |
              { ("the"|"these") ("last"|"past") } |
              { "recent" | "past" } |
              { "coming" | "the"? "future" } """
        if args[0]: return 'STARTING'
        if args[1]: return 'ENDING'
        if args[2]: return 'BEFORE'
        if args[3]: return 'AFTER'

    # Match a suffix that indicates anchoring of a duration
    def AnchorSuffix(self, args):
        """ { "old" } | { "to" "come" } $ """
        if args[0]: return 'ENDING'
        if args[1]: return 'AFTER'


######## Patterns for class "recur" ########

class TimexTransducer_recur(TimexTransducer):
    """Normalization patterns for class "recur"."""

    def Everyday(self, args):
        """ ^ "everyday" $ """
        return 'XXXX-XX-XX'

    def NthDayOfMonth(self, args):
        """ {Rank} "day" ("of"|"in") {MONTHNAME} """
        d = args[0][0].val
        m = args[1][0].val
        return 'XXXX-%02d-%02d' % (m, d)

    def NthDayOfEveryMonth(self, args):
        """ {Rank} "day" ("of"|"in")? ("the"|"a"|"each"|"every")? "month" """
        d = args[0][0].val
        return 'XXXX-XX-%02d' % d

    def EveryUnit(self, args):
        """ ("every"|"each"|"a"|"an"|"the"|"per") {UNIT} """
        return mkGenericTimePointFromUnit(args[0][0].val)

    def EveryNUnits(self, args):
        """ ("every"|"per") {Numeric} {UNITS} """
        n = args[0][0].val
        u = args[1][0].val
        return mkTimeDurationFromUnit(n, u)

    def PastUnits(self, args):
        """ "past" .* UNITS """
        return 'PAST_REF'

    def Units(self, args):
        """ { UNITS | UNIT | UNITLY } """
        return mkGenericTimePointFromUnit(args[0][0].val)

    def Daypart(self, args):
        """ { DAYPART | DAYPARTS } """
        v = args[0][0].val
        return 'T%s' % v

    def Season(self, args):
        """ { SEASON | SEASONS } """
        v = args[0][0].val
        return 'XXXX-%s' % v

    def Monthname(self, args):
        """ { MONTHNAME } """
        m = args[0][0].val
        return 'XXXX-%02d' % m

    def Dayname(self, args):
        """ { DAYNAME | DAYNAMES } """
        d = args[0][0].val
        return 'XXXX-WXX-%d' % d

    def go(self):
        v = ( self.firstmatch( self.Everyday ) or
              self.firstmatch( self.NthDayOfMonth ) or
              self.firstmatch( self.NthDayOfEveryMonth ) or
              self.firstmatch( self.EveryUnit ) or
              self.firstmatch( self.EveryNUnits ) or
              self.firstmatch( self.PastUnits ) or
              self.firstmatch( self.Units ) or
              self.firstmatch( self.Daypart ) or
              self.firstmatch( self.Season ) or
              self.firstmatch( self.Monthname ) or
              self.firstmatch( self.Dayname ) )
        mod = self.firstmatch( self.ApproxMod )
        mod = mod and 'APPROX'
        return v, mod, None


######## Patterns for class "gendur" ########

class TimexTransducer_gendur(TimexTransducer):

    def Units(self, args):
        """ { UNIT | UNITS } """
        return mkTimeDurationFromUnit('X', args[0][0].val)

    def Seasons(self, args):
        """ { SEASONS } """
        return 'PX' + args[0][0].val

    def Dayparts(self, args):
        """ { DAYPARTS } """
        return 'PX' + args[0][0].val

    def go(self):
        v = ( self.firstmatch( self.Units ) or
              self.firstmatch( self.Seasons ) or
              self.firstmatch( self.Dayparts ) )
        mod = self.firstmatch( self.ApproxMod )
        anchor = ( self.firstmatch( self.AnchorPrefix ) or
                   self.firstmatch( self.AnchorSuffix ) or
                   'BEFORE' )
        return v, mod, anchor


######## Patterns for class "duration" ########

class TimexTransducer_duration(TimexTransducer):

    def Combined(self, args):
        """ { Numeric (UNIT | UNITS) } "and"? { Numeric (UNIT | UNITS) } """
        xn, xu = args[0][0].val, args[0][1].val
        yn, yu = args[1][0].val, args[1][1].val
        if xu == yu:
            return mkTimeDurationFromUnit(xn + yn, xu)
        if cmpUnit(xu, yu) > 0:
            xn, xu, yn, yu = yn, yu, xn, xu
        s = 'P'
        if xu[0] == 'T' and yu[0] == 'T':
            return 'PT' + str(xn) + xu[1:] + str(yn) + yu[1:]
        elif yu[0] == 'T':
            return 'P' + str(xn) + xu + 'T' + str(yn) + yu[1:]
        else:
            assert xu[0] != 'T'
            return 'P' + str(xn) + xu + str(yn) + yu

    def NUnitsPlusHalf(self, args):
        """ { Numeric } ( "1" "/" "2" | "-"? "and" "-"? "a" "-"? "half")
            { UNIT | UNITS } """
        return mkTimeDurationFromUnit(args[0][0].val + 0.5, args[1][0].val)

    def OneAndHalfUnit(self, args):
        """ ("a"|"an") { UNIT } "and" "a" "half" """
        return mkTimeDurationFromUnit(1.5, args[0][0].val)

    def HalfUnit(self, args):
        """ "half" ("a"|"an"|"-")? { UNIT } """
        return mkTimeDurationFromUnit(0.5, args[0][0].val)

    def ThirdUnit(self, args):
        """ { "one" "-"? "third" | "two" "-"? "thirds" | ("1"|"2") "/" "3" }
            ("of"? ("a"|"an"))? { UNIT } """
        if args[0][0] in ('one', '1'): n = 0.33
        if args[0][0] in ('two', '2'): n = 0.66
        return mkTimeDurationFromUnit(n, args[1][0].val)

    def UnitLong(self, args):
        """ { "yearlong" | "monthlong" | "weeklong" | "daylong" |
              "hourlong" | "overnight" } """
        m = { 'yearlong': 'P1Y',  'monthlong': 'P1M',
              'weeklong': 'P1W',  'daylong':   'P1DT',
              'hourlong': 'PT1H',  'overnight': 'P1NI' }
        return m[args[0][0]]

    def Num_Unit(self, args):
        """ { Numeric } "-"? { UNIT | UNITS } """
        return mkTimeDurationFromUnit(args[0][0].val, args[1][0].val)

    def NumUnits(self, args):
        """ { Numeric } .? { UNITS } """
        return mkTimeDurationFromUnit(args[0][0].val, args[1][0].val)

    def Num_SeasonOrDaypart(self, args):
        """ { Numeric } "-"? { SEASON | DAYPART } """
        return 'P' + str(args[0][0].val) + args[1][0].val

    def NumSeasonsOrDayparts(self, args):
        """ { Numeric } .? { SEASONS | DAYPARTS } """
        return 'P' + str(args[0][0].val) + args[1][0].val

    def OneUnit(self, args):
        """ ("a"|"an"|"the"|"one") .? { UNIT } """
        return mkTimeDurationFromUnit(1, args[0][0].val)

    def Unit(self, args):
        """ { UNIT } """
        return mkTimeDurationFromUnit(1, args[0][0].val)

    def SeasonOrDaypart(self, args):
        """ { SEASON | DAYPART } """
        return 'P1' + args[0][0].val

    def go(self):
        v = ( self.firstmatch( self.Combined ) or
              self.firstmatch( self.NUnitsPlusHalf ) or
              self.firstmatch( self.OneAndHalfUnit ) or
              self.firstmatch( self.HalfUnit ) or
              self.firstmatch( self.ThirdUnit ) or
              self.firstmatch( self.UnitLong ) or
              self.firstmatch( self.Num_Unit ) or
              self.firstmatch( self.NumUnits ) or
              self.firstmatch( self.Num_SeasonOrDaypart ) or
              self.firstmatch( self.NumSeasonsOrDayparts ) or
              self.firstmatch( self.OneUnit ) or
              self.firstmatch( self.Unit ) or
              self.firstmatch( self.SeasonOrDaypart ) )
        mod = self.firstmatch( self.ApproxMod )
        anchor = ( self.firstmatch( self.AnchorPrefix ) or
                   self.firstmatch( self.AnchorSuffix ) or
                   'BEFORE' )
        return v, mod, anchor


######## Patterns for class "genpoint" ########

class TimexTransducer_genpoint(TimexTransducer):

    def Now(self, args):
        """ ^ "right"? "now" | "the" ("moment"|"time") | 
              "today" | "nowadays" | "current" | "currently" |
              "present" | "presently" $ """
        return 'PRESENT_REF'

    def PresentTime(self, args):
        """ ("present"|"current")
            (UNIT|UNITS|"age"|"point"|"moment"|"time"|"times") """
        return 'PRESENT_REF'

    def TheseDays(self, args):
        """ ^ ("this"|"these"|"our")
            (UNIT|UNITS|"age"|"point"|"moment"|"moments"|"time"|"times") """
        return 'PRESENT_REF'

    def TheTime(self, args):
        """ ^ "the" ("moment"|"time") """
        return 'PRESENT_REF'

    def Past(self, args):
        """ "past" """
        return 'PAST_REF'

    def Ago(self, args):
        """ "ago" | "recently" | "earlier" $ """
        return 'PAST_REF'

    def Recent(self, args):
        """ ^ "recent" | ("the"|"a"|"an"|"some")? "earlier" """
        return 'PAST_REF'

    def Former(self, args):
        """ ^ "former" | "formerly" | "previous" | "previously" |
              "onetime" | "once" $ """
        return 'PAST_REF'

    def Future(self, args):
        """ "future" """
        return 'FUTURE_REF'

    def Later(self, args):
        """ "later" $ """
        return 'FUTURE_REF'

    def Upcoming(self, args):
        """ ^ ("the"|"a"|"an"|"some")? ("upcoming"|"coming") """
        return 'FUTURE_REF'

    def NthQuarter(self, args):
        """ {Rank} "quarter" """
        q = args[0][0].val
        if q >= 1 and q <= 4:
            return 'XXXX-Q%d' % q

    def Season(self, args):
        """ {SEASON} """
        m = args[0][0].val
        return 'XXXX-%s' % m

    def NOClock(self, args):
        """ {NUM24|NUMWORD} "o" "'" "clock" """
        h = args[0][0].val
        if h <= 24:
            h = args[0][0].val
            if h > 0 and h < 6: h += 12
            return 'T%02d:00' % h

    def NAmPm(self, args):
        """ {NUM24} {"am"|"pm"|"a" "." "m"|"p" "." "m"} """
        h = args[0][0].val
        ampm = args[1][0][0].upper() + 'M'
        h = applyAmPmToHour(h, ampm)
        return 'T%02d' % h

    def DaynameDaypart(self, args):
        """ { DAYNAME DAYPART } """
        d = args[0][0].val
        h = args[0][1].val
        return 'XXXX-WXX-%d-T%s' % (d, h)

    def Monthname(self, args):
        """ { MONTHNAME } """
        m = args[0][0].val
        return 'XXXX-%02d' % m

    def Dayname(self, args):
        """ { DAYNAME } """
        wday = args[0][0].val
        return 'XXXX-WXX-%d' % wday

    def Weekend(self, args):
        """ "weekend" """
        return 'XXXX-WXX-WE'

    def Daypart(self, args):
        """ { DAYPART | "tonight" | "daytime" | "midnight" | "noon" | "eve" } """
        if args[0][0] == 'tonight': return 'TNI'
        if args[0][0] == 'daytime': return 'TDT'
        if args[0][0] == 'midnight': return 'T00:00'
        if args[0][0] == 'noon': return 'T12:00'
        if args[0][0] == 'eve': return 'TEV'
        return 'T%s' % args[0][0].val

    def Unit(self, args):
        """ { UNIT | UNITLY } """
        return mkGenericTimePointFromUnit(args[0][0].val)

    def EarlierNonAnchor(self, args):
        """ "earlier" """
        return True

    def go(self):
        v = ( self.firstmatch( self.Now ) or
              self.firstmatch( self.PresentTime ) or
              self.firstmatch( self.TheseDays ) or
              self.firstmatch( self.TheTime ) or
              self.firstmatch( self.Past ) or
              self.firstmatch( self.Ago ) or
              self.firstmatch( self.Recent ) or
              self.firstmatch( self.Former ) or
              self.firstmatch( self.Future ) or
              self.firstmatch( self.Later ) or
              self.firstmatch( self.Upcoming ) or
              self.firstmatch( self.NthQuarter ) or
              self.firstmatch( self.Season ) or
              self.firstmatch( self.NOClock ) or
              self.firstmatch( self.NAmPm ) or
              self.firstmatch( self.DaynameDaypart ) or
              self.firstmatch( self.Monthname ) or
              self.firstmatch( self.Dayname ) or
              self.firstmatch( self.Weekend ) or
              self.firstmatch( self.Daypart ) or
              self.firstmatch( self.Unit ) )
        mod = self.firstmatch( self.ApproxMod )
        mod = mod and 'APPROX'
        anchor = None
        if v == 'PRESENT_REF':
            anchor = 'AS_OF'
        if v == 'PAST_REF' and not self.firstmatch( self.EarlierNonAnchor ):
            anchor = 'BEFORE'
        if v == 'FUTURE_REF' and not self.firstmatch( self.Later ):
            anchor = 'AFTER'
        return v, mod, anchor


######## Patterns for class "point" ########
# DDA: 18-09-2006
#
# This is far and away the most complicated set of patterns
#
# Fully qualified timex patterns:
# - DigitalDateMDY, DigitalDateYMD, NthMillennium, NthCentury,
#   CenturyOrDecade, FqDecade, FqYearExplicit, FqYear,
#   FqYearMonth, FqYearSeason, FqYearQuarter, FqYearDayMonth,
#   FqDayMonthYear
# 
# Underspecified point timex patterns:
# - Deictic patterns:
#   - RefToday
# - Demonstrative patterns:
#   - RefSame
# - Deictic or anaphoric or demonstrative patterns:
#   - RefWeekdayDayMonth, RefDayMonth, RefMonth, RefSeason, RefQuarter,
#     RefWeekday, RefDaypart, RefUnit
#
# Offset point timex patterns:
# - Deictic patterns:
#   - OffYesterday, OffTomorrow
# - Deictic or anaphoric or demonstrative:
#   - OffUnit, OffNUnits, OffFuzzyUnits

class TimexTransducer_point(TimexTransducer):

    specifier2type_mapping = { 'Deictic':'dex',
                               'Anaphoric':'ana',
                               'Demonstrative':'dem',
                               'Ambiguous':'amb' }

    def specifier2type(self, specifier_lst, default='dex'):
        if specifier_lst:
            return TimexTransducer_point.specifier2type_mapping.get(specifier_lst[0].name, default)
        else:
            return default

    ####################
    # Junk patterns
    ####################
    # ignore common left modifiers
    def LeftJunk(self, args):
        """ "the" | "in" | "on" | ("beginning"|"end"|"start") "of" |
            "early" | "earlier" | "late" | "later" | "mid" "-" | "end" "-" |
            "as" ("far" "back"|"early"|"late"|"recent") "as" """
        return True

    def LeftJunkNoThe(self, args):
        """ "in" | "on" | "the"? ("beginning"|"end"|"start") "of" |
            "early" | "earlier" | "late" | "later" | "mid" "-" | "end" "-" |
            "as" ("far" "back"|"early"|"late"|"recent"|"recently") "as" """
        return True

    ####################
    # Specifiers
    ####################
    # Deictic specifiers
    def Deictic(self, args):
        """ ( "next" | "last" |
              ("the" | "this" | "these")? ("coming" | "past") ) """
        return True

    # Anaphoric specifiers
    def Anaphoric(self, args):
        """ ( "the" ( "next" | "last" | "previous" | "following" )? ) """
        return True

    # Demonstrative specifiers
    def Demonstrative(self, args):
        """ ( "that" | "those" |
              ("the" | "this" | "these" | "that" | "those")? "same" ) """
        return True

    # Ambiguous
    def Ambiguous(self, args):
        """ ( "this" ) """
        return True

    # match a phrase indicating offset and direction
    def OffsetDir(self, args):
        """ { "before" "that"? | "ago" | "earlier" |
              "after" "that"? | "later" | "from" "now" } """

        if args[0][0] in ('before', 'ago', 'earlier'):
            n = -1
        else: # ('after', 'later', from')
            n = 1
        if len(args[0]) == 2 and args[0][1] == 'that':
            t = 'offdem'
        elif args[0][0] in ('earlier', 'later', 'before', 'after'):
            t = 'offana'
        else: # ('ago', 'from' 'now')
            t = 'offdex'
        return t, n

    #######################
    # Underspecified points
    #######################

    def RefWeekdayDayMonth(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              {DAYNAME} ","?
              ( {MONTHNAME} "."? {Num31OrRank} |
                "the"? {Num31OrRank} "of"? {MONTHNAME} "."? ) """
        t = self.specifier2type(args[1])
        wday = args[2][0].val
        m = (args[3] or args[6])[0].val
        d = (args[4] or args[5])[0].val
        return t, U_YEAR, 'XXXX-%02d-%02d-WXX-%d' % (m, d, wday)

    def RefDayMonth(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              ( {MONTHNAME} "."? {Num31OrRank} |
                {Num31OrRank} "of"? {MONTHNAME} "."? ) """
        t = self.specifier2type(args[1])
        m = (args[2] or args[5])[0].val
        d = (args[3] or args[4])[0].val
        return t, U_YEAR, 'XXXX-%02d-%02d' % (m, d)

    def RefMonth(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              {MONTHNAME} "."? """
        t = self.specifier2type(args[1])
        m = args[2][0].val
        return t, U_YEAR, 'XXXX-%02d' % m

    def RefSeason(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              {SEASON} """
        t = self.specifier2type(args[1])
        m = args[2][0].val
        return t, U_YEAR, 'XXXX-%s' % m

    def RefQuarter(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              ("year" "'" "s")?
              {Rank} "-"? "quarter" """
        t = self.specifier2type(args[1])
        q = args[2][0].val
        if q >= 1 and q <= 4:
            return t, U_YEAR, 'XXXX-Q%d' % q

    def RefWeekday(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              ({DAYNAME}|"weekend") {DAYPART}? """
        t = self.specifier2type(args[1])
        if args[2]:
            s = 'XXXX-WXX-%d' % args[2][0].val
        else:
            s = 'XXXX-WXX-WE'
        if args[3]:
            s += 'T%s' % args[3][0].val
        return t, U_WEEK, s

    def RefDaypart(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              {DAYPART | "tonight" | "overnight"} """
        t = self.specifier2type(args[1])
        if args[2][0] in ('tonight', 'overnight'):
            h = 'NI'
        else:
            h = args[2][0].val
        return t, U_DAY, 'T%s' % h

    def RefToday(self, args):
        """ ^ {Approx}? LeftJunkNoThe* "right"? {"today" | "now"} """
        if args[1][0] == 'today': return 'dex', U_DAY, ''
        if args[1][0] == 'now': return 'dex', 0, ''

    def RefSame(self, args):
        """ ^ ("that" "same"? | "the"? "same")  ("time" | "point") """
        return 'dem', 0, ''

    def RefUnit(self, args):
        """ ^ {Approx}? LeftJunkNoThe*
              {Deictic|Anaphoric|Demonstrative|Ambiguous}?
              {UNIT}"""
        t = self.specifier2type(args[1])
        u = args[2][0].val
        return t, u, ''

    ########################
    # Underspecified offsets
    ########################
    #########
    # Deictic
    #########
    # Yesterday
    def OffYesterday(self, args):
        """ ^ {Approx}? LeftJunk* { ("day"|{DAYPART}) "before" }?
              "yesterday" {DAYPART}? """
        n = -1
        if args[1]: n = -2
        s = ''
        h = None
        if args[3]: s = 'T%s' % args[3][0].val
        if args[2]: s = 'T%s' % args[2][0].val
        return 'offdex', U_DAY, n, s
 
    # Tomorrow
    def OffTomorrow(self, args):
        """ ^ {Approx}? LeftJunk* { ("day"|{DAYPART}) "after" }?
              "tomorrow" {DAYPART}? """
        n = 1
        if args[1]: n = 2
        s = ''
        h = None
        if args[3]: s = 'T%s' % args[3][0].val
        if args[2]: s = 'T%s' % args[2][0].val
        return 'offdex', U_DAY, n, s

    # This could be handled by RefDaypart. We added a special pattern to
    # keep track of the fact that this timex always refers to the same day
    # as the document timestamp; therefore the final normalizer should not
    # try to apply the direction classifier.
    def OffDaypart(self, args):
        """ ^ {"this" DAYPART} | {"tonight"} """
        if args[0]:
            return 'offdex', U_DAY, 0, 'T%s' % args[0][1].val
        elif args[1]:
            return 'offdex', U_DAY, 0, 'TNI'

    #######
    # Other
    #######
    # Offsets of one unit: "A day ago"
    def OffUnit(self, args):
        """ ^ {Approx}? {"half"}? ("a"|"an"|"one") {"half" "-"?}? {UNIT}
              {"and" "a" "half"}? {OffsetDir} {"today"}? """
        t, n = args[5][0].val
        if args[1] or args[2]: n = 0.5 * n
        elif args[4]: n = 1.5 * n
        u = args[3][0].val
        if args[6]: t = 'offtoday'
        return t, u, n, ''

    # Offsets of N units: "Three and a half days later"
    def OffNUnits(self, args):
        """ ^ {Approx}? {Numeric} {"and" "a" "half"}? {UNITS}
              {OffsetDir} {"today"}? """
        t, n = args[4][0].val
        m = args[1][0].val
        if args[2]: m += 0.5
        n = n * m
        u = args[3][0].val
        if args[5]: t = 'offtoday'
        return t, u, n, ''

    # Fuzzy offset: "Several months earlier"
    def OffFuzzyUnits(self, args):
        """ ^ ("a" "few"|"some"|"several")? {UNITS} {OffsetDir} """
        t, n = args[1][0].val
        u = args[0][0].val
        return t, u, 'X', ''

    ########################
    # Time specifications
    ########################

    # match AM or PM spec
    def TimeAmPm(self, args):
        """ { "am" | "pm" | ("a"|"p") "." "m" "."? } |
            { "noon" | "midnight" } |
            "in" "the" { "morning" | "afternoon" | "evening" | "night" } """
        if args[0]:
            if args[0][0][0] == 'a': return 'AM'
            if args[0][0][0] == 'p': return 'PM'
        if args[1]:
            if args[1][0] == 'noon': return 'PM' # 12 noon = 12 PM
            if args[1][0] == 'midnight': return 'NI' # 12 midnight = 12 AM
        if args[2]:
            if args[2][0] == 'morning': return 'AM'
            if args[2][0] == 'night': return 'NI' # very late or very early
            if args[2][0] in ('afternoon', 'evening'): return 'PM'

    # match timezone spec
    def TimeZone(self, args):
        """ { TIMEZONE } | { ("universal" | "eastern") "saving"? "time"? } """
        if args[0]:
            return args[0][0].val
        if args[1]:
            if args[1][0] == 'universal':
                return 'Z'
            if args[1][0] == 'eastern':
                if len(args[1]) > 1 and args[1][1] == 'saving':
                    return '-04'
                else:
                    return '-05'

    # digital time: "08:56 AM"
    def TimeDigital(self, args):
        """ {NUM24} ( {TimeAmPm} | ":" {NUM60} ( ":" {NUM60} ("." {NUM})? )?
            {TimeAmPm}? ) {TimeZone}? """
        h = args[0][0].val
        m = 0
        s = None
        sfrac = None
        ampm = None
        tz = None
        if args[1]: ampm = args[1][0].val
        if args[2]: m = args[2][0].val
        if args[3]: s = args[3][0].val
        if args[4]: sfrac = args[4][0].raw
        if args[5]: ampm = args[5][0].val
        if args[6]: tz = args[6][0].val
        h = applyAmPmToHour(h, ampm)
        if s is not None:
            t = 'T%02d:%02d:%02d' % (h, m, s)
            if sfrac is not None: t += '.' + sfrac
        else:
            t = 'T%02d:%02d' % (h, m)
        if tz is not None:
            t += tz
        return t

    # full hours: 'two o'clock in the afternoon"
    def TimeFullHour(self, args):
        """ { NUM24 | NUMWORD } "o" "'" "clock" {TimeAmPm}? """
        h = args[0][0].val
        ampm = (args[1] or None) and args[1][0].val
        h = applyAmPmToHour(h, ampm)
        return 'T%02d:00' % h

    # military time: "1700 GMT"
    def TimeMil(self, args):
        """ { NUMXXXX } { TimeZone } """
        h = args[0][0].val / 100
        m = args[0][0].val % 100
        tz = args[1][0].val
        return 'T%02d:%02d%s' % (h, m, tz)

    # named time: "noon"
    def TimeNamed(self, args):
        """ { "noon" | "midnight" | "daytime" } {TimeZone}? """
        t = args[0][0]
        tz = ''
        if args[1] and args[1][0]: tz = args[1][0].val
        if t == 'noon':     return 'T12:00' + tz
        if t == 'midnight': return 'T00:00' + tz
        if t == 'daytime':  return 'TDT' + tz

    # match any time form
    def TimeSpec(self, args):
        """ { TimeDigital | TimeFullHour | TimeMil | TimeNamed } """
        return args[0][0].val

    ########################
    # Fully qualified points
    ########################

    # match year with 4 digits or 2 digits: "1978" or "'78"
    def YearNum(self, args):
        """ {NUMXXXX} | "'" {NUMXX} """
        if args[0]:
            return args[0][0].val
        if args[1]:
            return expandYear(args[1][0].val)

    # match A.D. or B.C. indication
    def YearAdBc(self, args):
        """ { "a" "." "d" "." } | { "b" "." "c" "." } """
        if args[0]: return 'AD'
        if args[1]: return 'BC'

    # digital date: mm/dd/yyyy
    def DigitalDateMDY(self, args):
        """ ^ {NUM12} ("/"|"-") {NUM31} ("/"|"-") ({NUMXXXX} | {NUMXX}) """
        if args[2]: y = args[2][0].val
        if args[3]: y = expandYear(args[3][0].val)
        m = args[0][0].val
        d = args[1][0].val
        return 'fq', '%04d-%02d-%02d' % (y, m, d)

    # digital ISO date: yyyy-mm-dd
    def DigitalDateYMD(self, args):
        """ ^ {NUMXXXX} ("/"|"-") {NUM12} ("/"|"-") {NUM31} """
        y = args[0][0].val
        m = args[1][0].val
        d = args[2][0].val
        return 'fq', '%04d-%02d-%02d' % (y, m, d)

    # FQ millennium: "the 2nd millennium"
    def NthMillennium(self, args):
        """ "the" {Rank} "millennium" """
        return 'fq', '%d' % (args[0][0].val - 1)

    # FQ century: "the 17th century"
    def NthCentury(self, args):
        """ ^ ( .* "the" )? {Rank} "-"? "century" """
        return 'fq', '%02d' % (args[0][0].val - 1)

    # FQ century or decade: "the 1800s", "the '80s"
    def CenturyOrDecade(self, args):
        """ ^ {Approx}? (LeftJunk)* "'"? {NUMXXX0} "'"? "s" """
        y = args[1][0].val
        if y % 100 == 0:
            return 'fq', '%02d' % (y // 100) # century
        elif y < 100:
            return 'fq', '%03d' % (190 + y // 10) # abbr decade
        else:
            return 'fq', '%03d' % (y // 10) # full decade

    # FQ decade: "the fifties"
    def FqDecade(self, args):
        """ ^ {Approx}? (LeftJunk)* {DECADE} """
        y = args[1][0].val
        return 'fq', '%03d' % (190 + y / 10)

    # FQ explicit year: "the year 314"
    def FqYearExplicit(self, args):
        """ ^ {Approx}? (LeftJunk)*
            ( ("year" {YearAdBc}? | {YearAdBc}) {NUM} {YearAdBc}? |
              {NUM} {YearAdBc} ) """
        y = (args[3] or args[5])[0].val
        y = '%04d' % y
        if (args[1] and args[1][0].val == 'BC') or \
           (args[2] and args[2][0].val == 'BC') or \
           (args[4] and args[4][0].val == 'BC') or \
           (args[6] and args[6][0].val == 'BC'):
            y = 'BC' + y
        return 'fq', y

    # FQ year: "1980", "'78"
    def FqYear(self, args):
        """ ^ {Approx}? (LeftJunk)* {YearNum} {TimeZone}? """
        if args[2]:
            # NO! we are looking at 1900 GMT or something like that
            return
        return 'fq', '%04d' % args[1][0].val

    # FQ year and month: "July 2006"
    def FqYearMonth(self, args):
        """ ^ {Approx}? LeftJunk* {MONTHNAME} ","? {YearNum} """
        y = args[2][0].val
        m = args[1][0].val
        return 'fq', '%04d-%02d' % (y, m)

    # FQ year and season: "the summer of 2006"
    def FqYearSeason(self, args):
        """ ^ {Approx}? (LeftJunk)* {SEASON} "of"? {YearNum} """
        y = args[2][0].val
        m = args[1][0].val
        return 'fq', '%04d-%s' % (y, m)

    # FQ year and quarter: "the 3rd quarter of 2006"
    def FqYearQuarter(self, args):
        """ ^ {Approx}? (LeftJunk)* {Rank} "quarter"
              ("of"|"in") {YearNum} """
        y = args[2][0].val
        q = args[1][0].val
        if q >= 1 and q <= 4:
            return 'fq', '%04d-Q%d' % (y, q)

    # FQ full date in month day year format: July 6, 2004"
    def FqYearDayMonth(self, args):
        """ ^ {Approx}? DAYNAME? {MONTHNAME} "."? {Num31OrRank}
              ","? {YearNum} """
        y = args[3][0].val
        m = args[1][0].val
        d = args[2][0].val
        return 'fq', '%04d-%02d-%02d' % (y, m, d)

    # FQ full date in day month year format: "6 July 2004"
    def FqDayMonthYear(self, args):
        """ ^ {Approx}? LeftJunk* (DAYNAME "the"?)? {Num31OrRank} "of"?
            {MONTHNAME} "."? ","? {YearNum} """
        y = args[3][0].val
        m = args[2][0].val
        d = args[1][0].val
        return 'fq', '%04d-%02d-%02d' % (y, m, d)

    def go(self):
        timespec = (
          self.firstmatch( self.TimeDigital ) or
          self.firstmatch( self.TimeFullHour ) or
          self.firstmatch( self.TimeMil ) or
          self.firstmatch( self.TimeNamed ) )
        v =  (
          self.firstmatch( self.DigitalDateMDY ) or
          self.firstmatch( self.DigitalDateYMD ) or
          self.firstmatch( self.NthMillennium ) or
          self.firstmatch( self.NthCentury ) or
          self.firstmatch( self.CenturyOrDecade ) or
          self.firstmatch( self.FqDecade ) or
          self.firstmatch( self.FqYearExplicit ) or
          self.firstmatch( self.FqYear ) or
          self.firstmatch( self.FqYearMonth ) or
          self.firstmatch( self.FqYearSeason ) or
          self.firstmatch( self.FqYearDayMonth ) or
          self.firstmatch( self.FqDayMonthYear ) or
          self.firstmatch( self.RefWeekdayDayMonth ) or
          self.firstmatch( self.RefDayMonth ) or
          self.firstmatch( self.RefMonth ) or
          self.firstmatch( self.RefSeason ) or
          self.firstmatch( self.RefQuarter ) or
          self.firstmatch( self.RefWeekday ) or
          self.firstmatch( self.OffDaypart ) or
          self.firstmatch( self.RefDaypart ) or
          self.firstmatch( self.RefToday ) or
          self.firstmatch( self.RefSame ) or
          self.firstmatch( self.OffYesterday ) or
          self.firstmatch( self.OffTomorrow ) or
          self.firstmatch( self.RefUnit ) or
          self.firstmatch( self.OffUnit ) or
          self.firstmatch( self.OffNUnits ) or
          self.firstmatch( self.OffFuzzyUnits ) )
        if timespec:
            if v:
                t = TimePoint(v[-1])
                t.truncate(U_DAY)
                t.merge(TimePoint(timespec))
                v = v[:-1] + ( str(t), )
            else:
                v = ('dex', U_DAY, timespec)
        mod = self.firstmatch( self.StartEndMod )
        approx = self.firstmatch( self.ApproxMod )
        if approx:
            mod = 'APPROX'
            if v and v[0][:3] == 'off' and v[2] < 0:
                if approx == 'LESS_THAN': mod = 'AFTER'
                if approx == 'EQUAL_OR_LESS': mod = 'ON_OR_AFTER'
                if approx == 'MORE_THAN': mod = 'BEFORE'
                if approx == 'EQUAL_OR_MORE': mod = 'ON_OR_BEFORE'
            if v and v[0][:3] == 'off' and v[2] > 0:
                if approx == 'LESS_THAN': mod = 'BEFORE'
                if approx == 'EQUAL_OR_LESS': mod = 'ON_OR_BEFORE'
                if approx == 'MORE_THAN': mod = 'AFTER'
                if approx == 'EQUAL_OR_MORE': mod = 'ON_OR_AFTER'
        return v, mod, None

    def fq(self):
        timespec = (
          self.firstmatch( self.TimeDigital ) or
          self.firstmatch( self.TimeFullHour ) or
          self.firstmatch( self.TimeMil ) or
          self.firstmatch( self.TimeNamed ) )
        v =  (
          self.firstmatch( self.DigitalDateMDY ) or
          self.firstmatch( self.DigitalDateYMD ) or
          self.firstmatch( self.NthMillennium ) or
          self.firstmatch( self.NthCentury ) or
          self.firstmatch( self.CenturyOrDecade ) or
          self.firstmatch( self.FqDecade ) or
          self.firstmatch( self.FqYearExplicit ) or
          self.firstmatch( self.FqYear ) or
          self.firstmatch( self.FqYearMonth ) or
          self.firstmatch( self.FqYearSeason ) or
          self.firstmatch( self.FqYearDayMonth ) or
          self.firstmatch( self.FqDayMonthYear ) )
        if timespec:
            if v:
                t = TimePoint(v[-1])
                t.truncate(U_DAY)
                t.merge(TimePoint(timespec))
                v = v[:-1] + ( str(t), )
            else:
                v = ('dex', U_DAY, timespec)
        mod = self.firstmatch( self.StartEndMod )
        approx = self.firstmatch( self.ApproxMod )
        if approx:
            mod = 'APPROX'
            if v and v[0][:3] == 'off' and v[2] < 0:
                if approx == 'LESS_THAN': mod = 'AFTER'
                if approx == 'EQUAL_OR_LESS': mod = 'ON_OR_AFTER'
                if approx == 'MORE_THAN': mod = 'BEFORE'
                if approx == 'EQUAL_OR_MORE': mod = 'ON_OR_BEFORE'
            if v and v[0][:3] == 'off' and v[2] > 0:
                if approx == 'LESS_THAN': mod = 'BEFORE'
                if approx == 'EQUAL_OR_LESS': mod = 'ON_OR_BEFORE'
                if approx == 'MORE_THAN': mod = 'AFTER'
                if approx == 'EQUAL_OR_MORE': mod = 'ON_OR_AFTER'
        return v, mod, None

######## Patterns for numbers ########
#
# Not a timex class but support
# for parse-based pre-normalization
#

class NumericTransducer(TimexTransducer):

    def Foo(self, args):
        """ Numeric """
        return True

    def Bar(self, args):
        """ Num31OrRank """
        return True

    def num(self):
        v = self.firstmatch( self.Foo )
        return v

    def num_offset(self):
        numeric_pattern = self.Foo.__doc__
        m = self.mkmatcher(numeric_pattern)
        foo = m.matchall(self.tokens, self.supertok)
        num31OrRank_pattern = self.Bar.__doc__
        m = self.mkmatcher(num31OrRank_pattern)
        bar = m.matchall(self.tokens, self.supertok)
        return foo or bar

######## Test program ########

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Test pre-normalization patterns."
        print "Usage: python timexnorm.py tmxclass 'timex string'"
        sys.exit(1)
    print parseTimex(sys.argv[2], sys.argv[1])

# End
