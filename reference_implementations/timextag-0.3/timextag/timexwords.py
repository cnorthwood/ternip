"""Word lookup.

This module implements word lookup. It assigns to a particular
word a category and optionally a value.

Word lookup is needed at a number of points in the system, and
the needs are slightly different:

During feature extraction for machine learning, word lookup is used
to enforce generalization (the machine learner must not see a difference
between words of the same category).
This is implemented by the getWordCategory() interface.

The normalization patterns use word lookup to turn words of a category
into tokens for subsequent pattern matching. The dirclass feature extractor
also uses this interface for one very specific reason.
This is implemented in getWordInfo() and getTypeList().

The structured timex recognizer/normalizer needs word lookup to
recognize month names. It uses getWordInfo() and getWordsByType().
"""

from timexval import *

# Only export these names
__all__ = [ 'getWordCategory', 'getWordInfo', 'getWordTypeList',
            'getWordsByType' ]


# All word types that may be returned by getWordInfo()
wordTypes = (
  'DAYNAME', 'DAYNAMES', 'MONTHNAME', 'SEASON', 'SEASONS',
  'DAYPART', 'DAYPARTS', 'UNIT', 'UNITS', 'UNITLY',
  'NUMWORD', 'RANKWORD', 'TIMEZONE', 'DECADE',
  'NUM', 'NUMXX', 'NUMXXXX', 'NUMXXX0', 'NUM12', 'NUM24', 'NUM31', 'NUM60' )


# The list
wordList = {

# day names
  'monday':    ('DAYNAME', 1),  'mon': ('DAYNAME', 1),
  'tuesday':   ('DAYNAME', 2),  'tue': ('DAYNAME', 2),  'tues': ('DAYNAME', 2),
  'wednesday': ('DAYNAME', 3),  'wed': ('DAYNAME', 3),
  'thursday':  ('DAYNAME', 4),  'thu': ('DAYNAME', 4),  'thurs': ('DAYNAME', 4),
  'friday':    ('DAYNAME', 5),  'fri': ('DAYNAME', 5),
  'saturday':  ('DAYNAME', 6),  'sat': ('DAYNAME', 6),
  'sunday':    ('DAYNAME', 7),  'sun': ('DAYNAME', 7),
  'mondays':   ('DAYNAMES', 1),
  'tuesdays':  ('DAYNAMES', 2),
  'wednesdays':('DAYNAMES', 3),
  'thursdays': ('DAYNAMES', 4),
  'fridays':   ('DAYNAMES', 5),
  'saturdays': ('DAYNAMES', 6),
  'sundays':   ('DAYNAMES', 7),

# month names
  'january':   ('MONTHNAME',  1),   'jan': ('MONTHNAME',  1),
  'february':  ('MONTHNAME',  2),   'feb': ('MONTHNAME',  2),
  'march':     ('MONTHNAME',  3),   'mar': ('MONTHNAME',  3),
  'april':     ('MONTHNAME',  4),   'apr': ('MONTHNAME',  4),
  'may':       ('MONTHNAME',  5),
  'june':      ('MONTHNAME',  6),   'jun': ('MONTHNAME',  6),
  'july':      ('MONTHNAME',  7),   'jul': ('MONTHNAME',  7),
  'august':    ('MONTHNAME',  8),   'aug': ('MONTHNAME',  8),
  'september': ('MONTHNAME',  9),   'sep': ('MONTHNAME',  9),
  'sept':      ('MONTHNAME',  9),
  'october':   ('MONTHNAME', 10),   'oct': ('MONTHNAME', 10),
  'november':  ('MONTHNAME', 11),   'nov': ('MONTHNAME', 11),
  'december':  ('MONTHNAME', 12),   'dec': ('MONTHNAME', 12),

# seasons
  'spring':    ('SEASON', 'SP'),    'springs': ('SEASONS', 'SP'),
  'summer':    ('SEASON', 'SU'),    'summers': ('SEASONS', 'SU'),
  'autumn':    ('SEASON', 'FA'),    'autumns': ('SEASONS', 'FA'),
  'fall':      ('SEASON', 'FA'),    'falls':   ('SEASONS', 'FA'),
  'winter':    ('SEASON', 'WI'),    'winters': ('SEASONS', 'WI'),

# day parts
  'morning':   ('DAYPART', 'MO'),   'mornings':  ('DAYPARTS', 'MO'),
  'midday':    ('DAYPART', 'MI'),
  'afternoon': ('DAYPART', 'AF'),   'afternoons':('DAYPARTS', 'AF'),
  'evening':   ('DAYPART', 'EV'),   'evenings':  ('DAYPARTS', 'EV'),
  'night':     ('DAYPART', 'NI'),   'nights':    ('DAYPARTS', 'NI'),

# units
  'day':       ('UNIT', U_DAY),     'days':      ('UNITS', U_DAY),
  'week':      ('UNIT', U_WEEK),    'weeks':     ('UNITS', U_WEEK),
  'month':     ('UNIT', U_MONTH),   'months':    ('UNITS', U_MONTH),
  'quarter':   ('UNIT', U_QUARTER), 'quarters':  ('UNITS', U_QUARTER),
  'year':      ('UNIT', U_YEAR),    'years':     ('UNITS', U_YEAR),
  'decade':    ('UNIT', U_DECADE),  'decades':   ('UNITS', U_DECADE),
  'century':   ('UNIT', U_CENTURY), 'centuries': ('UNITS', U_CENTURY),
  'millennium':('UNIT', U_MILLENNIUM), 'millennia': ('UNITS', U_MILLENNIUM),
  'hour':      ('UNIT', U_HOUR),    'hours':     ('UNITS', U_HOUR),
  'minute':    ('UNIT', U_MINUTE),  'minutes':   ('UNITS', U_MINUTE),
  # second is handled separately
  'hourly':    ('UNITLY', U_HOUR),
  'daily':     ('UNITLY', U_DAY),
  'weekly':    ('UNITLY', U_WEEK),
  'monthly':   ('UNITLY', U_MONTH),
  'quarterly': ('UNITLY', U_QUARTER),
  'yearly':    ('UNITLY', U_YEAR),
  'annual':    ('UNITLY', U_YEAR),  'annually':  ('UNITLY', U_YEAR),
  'biannual':  ('UNITLY', U_HALFYEAR), 'biannually':('UNITLY', U_HALFYEAR),
  'semiannual':('UNITLY', U_HALFYEAR), 'semianually':('UNITLY', U_HALFYEAR),

# numeric words
  'zero':      ('NUMWORD',  0),
  'one':       ('NUMWORD',  1),
  'two':       ('NUMWORD',  2),
  'three':     ('NUMWORD',  3),
  'four':      ('NUMWORD',  4),
  'five':      ('NUMWORD',  5),
  'six':       ('NUMWORD',  6),
  'seven':     ('NUMWORD',  7),
  'eight':     ('NUMWORD',  8),
  'nine':      ('NUMWORD',  9),
  'ten':       ('NUMWORD', 10),
  'eleven':    ('NUMWORD', 11),
  'twelve':    ('NUMWORD', 12),
  'thirteen':  ('NUMWORD', 13),
  'fourteen':  ('NUMWORD', 14),
  'fifteen':   ('NUMWORD', 15),
  'sixteen':   ('NUMWORD', 16),
  'seventeen': ('NUMWORD', 17),
  'eighteen':  ('NUMWORD', 18),
  'nineteen':  ('NUMWORD', 19),
  'twenty':    ('NUMWORD', 20),
  'thirty':    ('NUMWORD', 30),
  'forty':     ('NUMWORD', 40),
  'fourty':    ('NUMWORD', 40),
  'fifty':     ('NUMWORD', 50),
  'sixty':     ('NUMWORD', 60),
  'seventy':   ('NUMWORD', 70),
  'eighty':    ('NUMWORD', 80),
  'ninety':    ('NUMWORD', 90),
  'hundred':   ('NUMWORD', 100),
  'thousand':  ('NUMWORD', 1000),
  'million':   ('NUMWORD', 1000000),
  'billion':   ('NUMWORD', 1000000000),

# numeric rank words
  'first':     ('RANKWORD',  1),
  # second is handled separately
  'third':     ('RANKWORD',  3),
  'fourth':    ('RANKWORD',  4),
  'fifth':     ('RANKWORD',  5),
  'sixth':     ('RANKWORD',  6),
  'seventh':   ('RANKWORD',  7),
  'eighth':    ('RANKWORD',  8),
  'ninth':     ('RANKWORD',  9),
  'tenth':     ('RANKWORD', 10),

# (some) timezones
  'gmt':       ('TIMEZONE', 'Z'),   'utc':       ('TIMEZONE', 'Z'),
  'bst':       ('TIMEZONE', '+01'),
  'cet':       ('TIMEZONE', '+01'), 'cest':      ('TIMEZONE', '+02'),
  'ast':       ('TIMEZONE', '-04'), 'adt':       ('TIMEZONE', '-03'),
  'est':       ('TIMEZONE', '-05'), 'edt':       ('TIMEZONE', '-04'),
  'cst':       ('TIMEZONE', '-06'), 'cdt':       ('TIMEZONE', '-05'),
  'mst':       ('TIMEZONE', '-07'), 'mdt':       ('TIMEZONE', '-06'),
  'pst':       ('TIMEZONE', '-08'), 'pdt':       ('TIMEZONE', '-07'),

# nostalgic decade references
  'fifties':   ('DECADE', 50),      'sixties':   ('DECADE', 60),
  'seventies': ('DECADE', 70),      'eighties':  ('DECADE', 80),
  'nineties':  ('DECADE', 90),

}


# Construct a separate dictionary for the feature extraction interface
wordToCategory = { }
for (w, v) in wordList.iteritems():
    (typ, val) = v
    if ( typ not in ('SEASONS', 'DAYPARTS', 'RANKWORD',
                     'TIMEZONE', 'DECADE') and
         w not in ('quarter', 'quarters') and
         (typ != 'NUMWORD' or (val >= 2 and val <= 20)) ):
        wordToCategory[w] = typ
        if len(w) <= 4:
            wordToCategory[w + '.'] = typ


def getWordCategory(w):
    """Return the word category to which the string w belongs,
    or return None if it does not fit in any category.

    This interface is used by the feature extraction.
    """

    # Lookup in the dictionary
    t = w.lower()
    v = wordToCategory.get(t)
    if v:
        return v

    # Match against digit string patterns
    if w.isdigit():
        if len(w) == 1: return 'NumX'
        if len(w) == 2: return 'NumXX'
        if len(w) == 4: return 'NumXXXX'
        return 'Num'
    if len(t) == 5 and t[-1] == 's' and t[:4].isdigit(): return 'YYYYs'
    if len(t) == 3 and t[-1] == 's' and t[:2].isdigit(): return 'YYs'

    # No category
    return


def getWordInfo(w):
    """Return a list of (type, value) pairs that fit the string w,
    or return None if it does not fit any pattern.

    This interface is used by the normalization patterns.
    """

    # Lookup in dictionary
    t = w.lower()
    v = wordList.get(t)
    if v:
        z = [ v ]
    else:
        z = [ ]

    # Special case for ambiguous UNIT words
    if t == 'second':
        z = [ ('UNIT', U_SECOND), ('RANKWORD', 2) ]
    elif t == 'seconds':
        z = [ ('UNITS', U_SECOND) ]

    # Match against digit string patterns
    if w.isdigit():
        v = int(w)
        z.append( ('NUM', v) )
        n = len(w)
        if n == 4:
            z.append( ('NUMXXXX', v) )
        if n == 2:
            z.append( ('NUMXX', v) )
        if n in (2, 4) and w[-1] == '0':
            z.append( ('NUMXXX0', v) )
        if n <= 2:
            if v <= 60:
                z.append( ('NUM60', v) )
            if v <= 31:
                z.append( ('NUM31', v) )
            if v <= 24:
                z.append( ('NUM24', v) )
            if v <= 12:
                z.append( ('NUM12', v) )

    if not z:
        z = None
    return z


def getWordTypeList():
    """Return a sequence of all word types supported by getWordInfo()."""
    return wordTypes 


def getWordsByType(t):
    """Return a list of words that have type t."""
    # Not used often so no need to optimize
    z = [ ]
    for (w, v) in wordList.iteritems():
        (typ, val) = v
        if typ == t:
            z.append(w)
    if t == 'UNIT':       z.append('second')
    elif t == 'UNITS':    z.append('seconds')
    elif t == 'RANKWORD': z.append('second')
    return z

# End
