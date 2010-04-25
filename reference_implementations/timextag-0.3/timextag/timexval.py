"""Representation of normalized time values and date arithmetic."""

import re, datetime


# Regular expressions used for ISO value parsing
_re_tpoint_bcyear= re.compile(r'(-|BC)(\d*)')
_re_tpoint_year =  re.compile(r'(FY)?([0-9X]{1,4})')
_re_tpoint_month = re.compile(r'(XX|0[1-9]|1[012]|WI|SP|SU|FA|H[12X]|Q[1234X])-?')
_re_tpoint_week =  re.compile(r'W(XX|[0-5][0-9])-?')
_re_tpoint_mday =  re.compile(r'(XX|0[1-9]|[12][0-9]|3[01])-?')
_re_tpoint_wday =  re.compile(r'(X?X|0?[0-7]|WE)')
_re_tpoint_hour =  re.compile(r'[T ]((XX|([01][0-9]|2[0-4])(\.\d+)?|MO|MI|AF|EV|NI|PM|DT):?)?')
_re_tpoint_min =   re.compile(r'(XX|[0-5][0-9](\.\d+)?):?')
_re_tpoint_sec =   re.compile(r'(XX|[0-5][0-9]|60)(\.\d*)?')
_re_tpoint_timez = re.compile(r'(Z|[+-]\d\d(:?\d\d)?)')

# Regular expressions used for ISO duration parsing
_re_duration_date = re.compile(
  r'P((X|[0-9.]+)ML)?((X|[0-9.]+)CE)?((X|[0-9.]+)DE)?((X|[0-9.]+)Y)?' + \
  r'((X|[0-9.]+)M)?((X|[0-9.]+)W)?((X|[0-9.]+)D)?')
_re_duration_time = re.compile(
  r'T((X|[0-9.]+)H)?((X|[0-9.]+)M)?((X|[0-9.]+)S)?')

# For comparing fuzzy year parts
_yearpart_month_range = {
  'WI': ( 1, 3 ), 'SP': ( 3, 6 ), 'SU': ( 6, 9 ), 'FA': ( 9, 12 ),
  'Q1': ( 1, 3 ), 'Q2': ( 4, 6 ), 'Q3': ( 7, 9 ), 'Q4': ( 10, 12 ),
  'H1': ( 1, 6 ), 'H2': ( 7, 12 ) }

# For comparing fuzzy day parts
_daypart_hour_range = {
  'MO': (  0, 11 ), 'MI': ( 12, 15 ), 'AF': ( 15, 18 ),
  'EV': ( 18, 21 ), 'NI': ( 20, 24 ),
  'PM': ( 12, 23 ), 'DT': (  8, 18 ) }

# For day-of-month computations
_month_ndays = ( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 )


# ========================================================
#   Unit contants
# ========================================================

U_ERA = '_ERA'
U_MILLENNIUM = 'ML'
U_CENTURY = 'CE'
U_DECADE = 'DE'
U_YEAR = 'Y'
U_YEARPART = '_YEARPART'
U_MONTH = 'M'
U_WEEK = 'W'
U_DAY = 'D'
U_DAYPART = '_DAYPART'
U_HOUR = 'TH'
U_MINUTE = 'TM'
U_SECOND = 'TS'
U_QUARTER = 'QX'
U_HALFYEAR = 'HX'

_unitSystematic = {
  U_MILLENNIUM:1, U_CENTURY:1, U_DECADE:1, U_YEAR:1, U_MONTH:1, U_WEEK:1,
  U_DAY:1, U_HOUR:1, U_MINUTE:1, U_SECOND:1 }

_unitSortOrder = {
  U_ERA: 1, U_MILLENNIUM: 2, U_CENTURY: 3, U_DECADE: 4,
  U_YEAR: 5, U_YEARPART: 6, U_HALFYEAR: 7, U_QUARTER: 8,
  U_MONTH: 9, U_WEEK: 10, U_DAY: 11,
  U_DAYPART: 12, U_HOUR: 13, U_MINUTE: 14, U_SECOND: 15 }

def cmpUnit(xu, yu):
    """Compare two unit constants and return -1, 0 or 1
    when xu represents a less, same, or more fine grained unit than yu."""
    return cmp(_unitSortOrder[xu], _unitSortOrder[yu])

def isSystematicUnit(u):
    """Return true if the unit behaves in a precise and systematic way.
    Some operations on TimePoint support only systematic units."""
    return u in _unitSystematic


# ========================================================
#   Construct ISO value from unit
# ========================================================

def mkGenericTimePointFromUnit(u):
    """Return ISO string for a non-specific time point with given precision."""
    if u == U_MILLENNIUM: return 'X'
    elif u == U_CENTURY:  return 'XX'
    elif u == U_DECADE:   return 'XXX'
    elif u == U_YEAR:     return 'XXXX'
    elif u == U_HALFYEAR: return 'XXXX-HX'
    elif u == U_QUARTER:  return 'XXXX-QX'
    elif u == U_MONTH:    return 'XXXX-XX'
    elif u == U_WEEK:     return 'XXXX-WXX'
    elif u == U_DAY:      return 'XXXX-XX-XX'
    elif u == U_HOUR:     return 'TXX'
    elif u == U_MINUTE:   return 'TXX:XX'
    elif u == U_SECOND:   return 'TXX:XX:XX'
    raise ValueError("Unsupported unit " + repr(u))


def mkTimeDurationFromUnit(n, u):
    """Return duration of n times u in ISO format."""
    if u[0] == '_' or (u not in _unitSortOrder):
        raise ValueError("Unsupported unit " + repr(u))
    if u[0] == 'T':
        return 'PT' + str(n) + u[1:]
    else:
        return 'P' + str(n) + u


# ========================================================
#   TimePoint Class
# ========================================================

class TimePoint:
    """Represent a point-like ISO time value.

    The value may have low resolution (eg. only year).
    The value may be underspecified (eg. only month and day).
    The value may be expressed using fuzzy specifications (season, daypart).

    This is an attempt to represent all possible normalized values of
    point-like TIMEX2 objects (excluding XXX_REF)."""

    def __init__(self, s=''):
        """Parse point value from ISO string."""

        self.fiscal_year = 0
        year = month = day = week = wday = hour = min = sec = tz = None
 
        s = s.upper()
        i = 0

        # Parse the year description
        m = _re_tpoint_bcyear.match(s, i)
        if m:
            # Negative year description
            i = m.end()
            if i != len(s):
                raise ValueError("Invalid BC-year ISO time string '" + s + "'")
            year = 'BC' + m.group(2)
            m = None
        else:
            m = _re_tpoint_year.match(s, i)
        if m:
            # Positive year description
            i = m.end()
            (fy, year) = m.group(1, 2)
            if fy:
                self.fiscal_year = 1
            if len(year) == 4:
                if year.isdigit(): year = int(year)
                if i < len(s) and s[i] == '-': i += 1

        if (year is not None) and (type(year) is int or len(year) == 4):

            # Parse the month description
            m = _re_tpoint_month.match(s, i)
            if m:
                i = m.end()
                month = m.group(1)
                if month.isdigit():
                    month = int(month)
                # Parse the day-of-month description
                m = _re_tpoint_mday.match(s, i)
                if m:
                    i = m.end()
                    day = m.group(1)
                    if day.isdigit(): day = int(day)

            # Parse the week description
            m = _re_tpoint_week.match(s, i)
            if m:
                i = m.end()
                week = m.group(1)
                if week.isdigit(): week = int(week)
                # Parse the day-of-week number
                m = _re_tpoint_wday.match(s, i)
                if m:
                    i = m.end()
                    wday = m.group(1)
                    if wday.isdigit(): wday = int(wday)
                    if wday == 'XX': wday = 'X'
    
        # Parse the hour description
        m = _re_tpoint_hour.match(s, i)
        if m:
            i = m.end()
        if m and m.group(2):
            hour = m.group(2)
            if hour.isdigit(): hour = int(hour)
            elif hour[0].isdigit(): hour = float(hour)
    
            # Parse the minute description
            m = _re_tpoint_min.match(s, i)
            if m:
                i = m.end()
                min = m.group(1)
                if min.isdigit(): min = int(min)
                elif min[0].isdigit(): min = float(min)
    
                # Parse the second description
                m = _re_tpoint_sec.match(s, i)
                if m:
                    i = m.end()
                    sec, sec100 = m.group(1, 2)
                    if sec.isdigit():
                        sec = int(sec)
                        if sec100 != None:
                            sec += float(sec100 + '0')
 
        # Parse a timezone description
        m = _re_tpoint_timez.match(s, i)
        if m:
            i = m.end()
            tz = m.group()
            if len(tz) == 3:
                tz = 60 * int(tz)
            elif len(tz) in (5, 6):
                tz = 60 * int(tz[:3]) + int(tz[0] + tz[-2:])
            else:
                assert tz == 'Z'
                tz = 0
 
        # Verify that we parsed the whole string
        if i < len(s):
            raise ValueError("Invalid ISO time string '" + s + "'")

        # Store values in object
        self.year = year
        self.month = month
        self.day = day
        self.week = week
        self.wday = wday
        self.hour = hour
        self.min = min
        self.sec = sec
        self.tz = tz


    def __str__(self):
        """Return the ISO string representation of this time value."""

        s = ''
        if self.year == None and self.hour == None:
            # We know nothing
            return ''

        if self.year is not None:
            # A date specification is needed
            year, mon, day = self.year, self.month, self.day
            week, wday = self.week, self.wday
            assert (day is None) or (mon is not None)
            assert (wday is None) or (week is not None)
            # Specify year
            if type(year) is int:
                if self.fiscal_year:
                    s += 'FY%04d' % year
                else:
                    s += '%04d' % year
            else:
                s += year
            # Specify month
            if mon is not None:
                if type(mon) is int:
                    s += '-%02d' % mon
                else:
                    s += '-%s' % mon
            if day is not None:
                if type(day) is int:
                    s += '-%02d' % day
                else:
                    s += '-%s' % day
            # Specify week number and day of week
            if week is not None:
                if type(week) is int:
                    s += '-W%02d' % week
                else:
                    s += '-W%s' % week
            if wday is not None:
                if type(wday) is int:
                    s += '-%d' % wday
                else:
                    s += '-%s' % wday

        if self.hour is not None or self.tz is not None:
            # A time-of-day specification is needed
            hour, min, sec, tz = self.hour, self.min, self.sec, self.tz
            if hour == None: min = None
            if min == None: sec = None
            s += 'T'
            # Specify hour
            if hour is not None:
                if type(hour) is int:
                    s += '%02d' % hour
                elif type(hour) is float:
                    s += '%05.2f' % hour
                else:
                    s += hour
            # Specify minute
            if min is not None:
                if type(min) is int:
                    s += ':%02d' % min
                elif type(min) is float:
                    s += ':%05.2f' % min
                else:
                    s += ':%s' % min
            # Specify seconds
            if sec is not None:
                if type(sec) == int:
                    s += ':%02d' % sec
                elif type(sec) == float:
                    s += ':%05.2f' % sec
                else:
                    s += ':%s' % sec
            # Specify timezone
            if tz is not None:
                if tz < 0:
                    if tz % 60 == 0: s += '-%02d' % ((-tz) // 60)
                    else: s += '-%02d%02d' % ((-tz) // 60, (-tz) % 60)
                elif tz > 0:
                    if tz % 60 == 0: s += '+%02d' % (tz // 60)
                    else: s += '+%02d%02d' % (tz // 60, tz % 60)
                else:
                    s += 'Z'

        return s


    def precision(self):
        """Return the implied precision of this time point as a unit constant.
        The precision of a time point may include components that are unknown,
        for example: 2006-XX (some month in 2006) still has precision U_MONTH.
        """
        if self.sec is not None: return U_SECOND
        if self.min is not None: return U_MINUTE
        if type(self.hour) in (int, float) or self.hour == 'XX': return U_HOUR
        if self.hour is not None: return U_DAYPART
        if (self.day is not None) or (self.wday is not None): return U_DAY
        if self.week is not None: return U_WEEK
        if type(self.month) is int or self.month == 'XX': return U_MONTH
        if self.month is not None: return U_YEARPART
        if type(self.year) is int: return U_YEAR
        if self.year is not None:
            if self.year == 'BC': return U_ERA
            if self.year[:2] == 'BC': return U_YEAR
            if len(self.year) == 4: return U_YEAR
            if len(self.year) == 3: return U_DECADE
            if len(self.year) == 2: return U_CENTURY
            if len(self.year) == 1: return U_MILLENNIUM
        return 0


    def specific_precision(self):
        """Return the explicit precision of this time point.
        The specific precision considers only date components which
        are fully specified: 2006-XX has specific_precision U_YEAR.
        """
        if self.year == None: return 0
        if type(self.year) != int:
            y = self.year
            if y == 'BC': return U_ERA
            if y[:2] == 'BC': return U_YEAR
            if len(y) == 0 or y[0] == 'X': return U_ERA
            if len(y) == 1 or y[1] == 'X': return U_MILLENNIUM
            if len(y) == 2 or y[2] == 'X': return U_CENTURY
            return U_DECADE
        if self.week is None or self.week == 'XX':
            if self.month is None or self.month == 'XX': return U_YEAR
            if type(self.month) is not int:
                if self.month[1] == 'X': return U_YEAR
                return U_YEARPART
            if type(self.day) is not int: return U_MONTH
        elif (type(self.wday) is not int) and \
             (type(self.month) is not int or type(self.day) is not int):
            return U_WEEK
        if self.hour == None or self.hour == 'XX': return U_DAY
        if type(self.hour) not in (int, float): return U_DAYPART
        if type(self.min) not in (int, float): return U_HOUR
        if type(self.sec) not in (int, float): return U_MINUTE
        return U_SECOND


    def compare(self, other):
        """Return -1 if this time is earlier than the other time,
        1 if it is later, 0 if it overlaps or None if nothing is known
        about the relative order."""

        # Determine precision at which we compare the times
        p = self.specific_precision()
        p2 = other.specific_precision()
        if cmpUnit(p, p2) > 0: p = p2
        if p == 0: return None

        t = 0

        # Compare partial years
        y1 = str(self.year)
        y2 = str(other.year)
        if y1[:2] == 'BC' and y2[:2] != 'BC': return -1
        if y1[:2] != 'BC' and y2[:2] == 'BC': return 1
        if p == U_ERA: return 0
        if y1[:2] == 'BC':
            # Compare BC years
            assert y2[:2] == 'BC'
            return cmp(int(y2[2:]), int(y1[2:]))
        if p == U_MILLENNIUM: return cmp(y1[0], y2[0])
        if p == U_CENTURY: return cmp(y1[:2], y2[:2])
        if p == U_DECADE: return cmp(y1[:3], y2[:3])

        # Compare full years
        t = cmp(self.year, other.year)
        if t or p == U_YEAR: return t

        # Compare at month level, possibly using fuzzy indications
        if p == U_YEARPART or p == U_MONTH:
            m1 = self.fuzzy_month_range()
            m2 = other.fuzzy_month_range()
            if m1[1] < m2[0]: return -1
            if m1[0] > m2[1]: return 1
            return 0

        # Compare at week level
        if p == U_WEEK:
            w1, d1 = self.week, self.wday
            w2, d2 = other.week, other.wday
            if type(w1) != int:
                # Compute week from full date
                (w1, d1) = date_ymd_to_ywd(self.year, self.month, self.day)
            if type(w2) != int:
                # Compute week from full date
                (w2, d2) = date_ymd_to_ywd(other.year, other.month, other.day)
            if w1 != w2:
                return cmp(w1, w2)
            # Same week, try to compare at weekend level
            if (type(d1) is int) and (d1 < 6) and d2 == 'WE':
                return -1
            if (d1 == 'WE') and (type(d2) is int) and (d2 < 6):
                return 1
            return 0

        # Compare exact calendar days
        y1, m1, d1 = self.year, self.month, self.day 
        y2, m2, d2 = other.year, other.month, other.day
        if (type(m1) is not int) or (type(d1) is not int):
            # Compute month,day from week,wday
            y1, m1, d1 = date_absdate_to_ymd(
              date_ywd_to_absdate(self.year, self.week, self.wday))
        if type(m2) != int:
            # Compute month,day from week,wday
            y2, m2, d2 = date_absdate_to_ymd(
              date_ywd_to_absdate(other.year, other.week, other.wday))
        t = cmp(y1, y2) or cmp(m1, m2) or cmp(d1, d2)
        if t or p == U_DAY: return t

        # Compare fuzzy day parts
        if p == U_DAYPART:
            h1 = self.fuzzy_hour_range()
            h2 = other.fuzzy_hour_range()
            if h1[1] < h2[0]: return -1
            if h1[0] > h2[1]: return 1
            return 0

        # Compare time of day (disregarding time zone)
        t = cmp(self.hour, other.hour)
        if t or p == U_HOUR: return t
        t = cmp(self.min, other.min)
        if t or p == U_MINUTE: return t
        t = cmp(self.sec, other.sec)
        assert p == U_SECOND
        return t


    def merge(self, p):
        """Merge information from another TimePoint into the self object."""
        # merge all fields
        for c in ('year', 'month', 'day', 'week', 'wday',
                  'hour', 'min', 'sec', 'tz'):
            v = self.__dict__[c]
            pv = p.__dict__[c]
            if pv is None:
                continue
            if v is None:
                v = pv
            elif type(v) is str and v[0] == 'X':
                if (type(pv) is not str) or pv[0] != 'X' or len(pv) > len(v):
                    v = pv
            elif (type(pv) is not str) or pv[0] != 'X':
                raise ValueError('Merge conflict for ' + c + ' field')
            self.__dict__[c] = v
        if type(self.year) is int and type(self.week) is int and \
           type(self.wday) is int and \
           (type(self.month) is not int or type(self.day) is not int):
            # convert from year,week,wday to year,month,day
            self.year, self.month, self.day = date_absdate_to_ymd(
              date_ywd_to_absdate(self.year, self.week, self.wday))
            # and discard the now-redundant week,wday
            self.week = self.wday = None


    def truncate(self, p):
        """Truncate this TimePoint object to the given precision."""
        if type(self.sec) is float: self.sec = int(self.sec)
        if p == U_SECOND: return
        self.sec = None
        if p == U_MINUTE: return
        self.min = None
        if p == U_HOUR: return
        self.hour = None
        self.tz = None
        if p == U_DAY: return
        if (p == U_WEEK) and (type(self.week) is not int) and \
           (type(self.year) is int) and (type(self.month) is int) and \
           (type(self.day) is int):
            # compute week number from y-m-d to preserve information
            (self.week, d) = date_ymd_to_ywd(self.year, self.month, self.day)
            self.day = self.wday = self.month = None
            return
        if (p == U_MONTH) and (type(self.month) is not int) and \
           (type(self.year) is int) and (type(self.week) is int) and \
           (type(self.wday) is int):
            # compute month number from week number to preserve information
            self.year, self.month, d = date_absdate_to_ymd(
              date_ywd_to_absdate(self.year, self.week, self.wday))
            self.week = None
        self.day = self.wday = None
        if p == U_WEEK: return
        self.week = None
        if p == U_MONTH: return
        if p == U_QUARTER:
            if type(self.month) is int:
                # compute quarter from month
                self.month = 'Q' + str((self.month + 2) // 3)
            elif (type(self.month) is not str) or (self.month != 'Q'):
                self.month = None
            return
        if p == U_HALFYEAR:
            if type(self.month) is int:
                # compute halfyear from month
                self.month = 'H' + str((self.month + 5) // 6)
            elif (type(self.month) is str) and \
                 self.month[0] == 'Q' and self.month[1:].isdigit():
                self.month = 'H' + str((int(self.month[1:]) + 1) // 2)
            elif (type(self.month) is not str) or self.month[0] != 'H':
                self.month = None
            return
        self.month = None
        if p == U_YEAR: return
        y = str(self.year)
        if y[:2] == 'BC':
            self.year = 'BC'
            return
        if p == U_DECADE:
            self.year = y[:3]
            return
        if p == U_CENTURY:
            self.year = y[:2]
            return
        if p == U_MILLENNIUM:
            self.year = y[:1]
            return
        if p == U_ERA:
            self.year = ''
            return
        assert False


    def extend_nonspecific(self, p):
        """Extend the self object to the given precision by appending placeholders."""
        if p == 0 or p == U_ERA: return
        if type(self.year) is str and self.year[:2] == 'BC':
            # we don't do arithmetic with BC years
            return
        if self.year is None: self.year = 'X'
        if type(self.year) is str:
            if p == U_MILLENNIUM: i = 1
            elif p == U_CENTURY: i = 2
            elif p == U_DECADE: i = 3
            else: i = 4
            if len(self.year) < i: self.year += 'X' * (i - len(self.year))
        if p in (U_MILLENNIUM, U_CENTURY, U_DECADE, U_YEAR): return
        if p in (U_QUARTER, U_HALFYEAR):
            if self.month is None: self.month = p
            return
        if p == U_MONTH:
            if self.month is None: self.month = 'XX'
            return
        if p == U_WEEK:
            if self.week is None: self.week = 'XX'
            if self.month == 'XX': self.month = None
            return
        if (type(self.week) is int and type(self.month) is not int) or \
           (type(self.wday) is int and type(self.day) is not int):
            # extend to y-w-d
            if self.week is None: self.week = 'XX'
            if self.wday is None: self.wday = 'X'
            if self.month == 'XX': self.month = None
            self.day = None
        else:
            # extend to y-m-d
            if self.month is None: self.month = 'XX'
            if self.day is None: self.day = 'XX'
            if self.wday == 'X': self.wday = None
            if not self.wday and self.week == 'XX': self.week = None
        if p == U_DAY: return
        if self.hour is None: self.hour = 'XX'
        if p == U_HOUR: return
        if self.min is None: self.min = 'XX'
        if p == U_MINUTE: return
        if self.sec is None: self.sec = 'XX'
        if p == U_SECOND: return
        assert False


    def fuzzy_month_range(self):
        """Return a range of possible month numbers for this date."""
        if type(self.month) == int:
            # use exact month number
            return (self.month, self.month)
        if type(self.week) == int:
            # calculate month range from exact week number
            minm = (7 * (self.week - 1)) // 30 + 1
            maxm = (7 * (self.week + 1)) // 30 + 1
            return (minm, maxm)
        # guess month range from fuzzy year part
        return _yearpart_month_range[self.month]


    def fuzzy_hour_range(self):
        """Return a range of possible hour numbers for this time value."""
        if type(self.hour) is int:
            # use exact hour
            return (self.hour, self.hour)
        if (type(self.hour) is str) and (self.hour != 'XX'):
            # guess hour range from daypart
            return _daypart_hour_range[self.hour]
        # anything is possible
        return (0, 23)


    def set_component_unknown(self, u):
        """Put a placeholder value in the given component."""
        if u == U_SECOND: self.sec = 'XX'
        elif u == U_MINUTE: self.min = 'XX'
        elif u == U_HOUR: self.hour = 'XX'
        elif u == U_DAY:
            if self.month and (self.week is None or self.week == 'XX'):
                self.day = 'XX'
                self.week = self.wday = None
            elif self.week:
                self.wday = 'X'
        elif u == U_WEEK:
            self.week = 'XX'
            self.day = None
        elif u == U_MONTH: self.month = 'XX'
        elif u in (U_QUARTER, U_HALFYEAR): self.month = u
        elif u == U_YEAR: self.year = 'XXXX'
        elif u in (U_DECADE, U_CENTURY, U_MILLENNIUM) and \
             (self.month or self.week):
            self.year = 'XXXX'
        elif u == U_DECADE: self.year = 'XXX'
        elif u == U_CENTURY: self.year = 'XX'
        elif u == U_MILLENNIUM: self.year = 'X'
        else: assert False


    def add_units(self, u, n):
        """Add a (possibly negative) number of units to the time value.
        The time value must already be fully specified and its precision
        must match the unit of the offset.
        The number of units must be an integer, unless the unit
        is U_HOUR, U_MINUTE or U_SECOND."""
        if u == U_SECOND:
            t = self.sec + n
            self.sec = t % 60
            n = int(t // 60)
            u = U_MINUTE
        if u == U_MINUTE:
            t = self.min + n
            self.min = t % 60
            n = int(t // 60)
            u = U_HOUR
        if u == U_HOUR:
            t = self.hour + n
            self.hour = t % 24
            n = int(t // 24)
            u = U_DAY
        assert int(n) == n
        if u == U_WEEK:
            if type(self.month) is int and type(self.day) is int:
                # we already know the month-based full date, so don't
                # bother maintaining a week-based date separately
                self.week = None
                n = 7 * n
                u = U_DAY
            else:
                # compute the year and iso-week
                wday = self.wday
                if type(wday) is not int: wday = 1
                t = date_ywd_to_absdate(self.year, self.week, wday)
                t += 7 * n
                self.year, self.week, wday = date_absdate_to_ywd(t)
                if self.year < 0 or self.year > 9999:
                    raise ValueError("Year overflow")
                u = None
                # we don't know anything about month and day now
                self.month = self.day = None
        if u == U_DAY:
            # compute days passed since 0000-01-01
            y, m, d = self.year, self.month, self.day
            if type(m) is not int or type(d) is not int:
                t = date_ywd_to_absdate(y, self.week, self.wday)
            else:
                t = date_ymd_to_absdate(y, m, d)
            # add day offset
            t += n
            if t < 0:
                raise ValueError("Year underflow")
            # compute y-m-d
            (self.year, self.month, self.day) = date_absdate_to_ymd(t)
            if self.year < 0 or self.year > 9999:
                raise ValueError("Year overflow")
            self.week = self.wday = None
            u = None
        if u == U_MONTH:
            t = self.month - 1 + n
            self.month = t % 12 + 1
            n = t // 12
            u = U_YEAR
        if u == U_QUARTER:
            assert self.month[0] == 'Q'
            t = int(self.month[1]) - 1 + n
            self.month = 'Q%d' % (t % 4 + 1)
            n = t // 4
            u = U_YEAR
        if u == U_HALFYEAR:
            assert self.month[0] == 'H'
            t = int(self.month[1]) - 1 + n
            self.month = 'H%d' % (t % 2 + 1)
            n = t // 2
            u = U_YEAR
        if u == U_YEAR:
            if type(self.year) != int:
                raise ValueError("Arithmetic on BC dates not supported")
            t = self.year + n
            if t > 9999:
                raise ValueError("Year overflow")
            if t < 0:
                self.year = 'BC%04d' % (-t)
            else:
                self.year = t
            u = None
        if u == U_DECADE:
            if self.year[:2] == 'BC':
                raise ValueError("Arithmetic on BC dates not supported")
            assert len(self.year) == 3
            t = int(self.year) + n
            if t < 0 or t > 999:
                raise ValueError("Decade overflow")
            self.year = '%03d' % t
            u = None
        if u == U_CENTURY:
            if self.year[:2] == 'BC':
                raise ValueError("Arithmetic on BC dates not supported")
            assert len(self.year) == 2
            t = int(self.year) + n
            if t < 0 or t > 99:
                raise ValueError("Century overflow")
            self.year = '%02d' % t
            u = None
        if u == U_MILLENNIUM:
            if self.year[:2] == 'BC':
                raise ValueError("Arithmetic on BC dates not supported")
            assert len(self.year) == 1
            t = int(self.year) + n
            if t < 0 or t > 9:
                raise ValueError("Millennium overflow")
            self.year = '%d' % t
            u = None
        assert u is None


# ========================================================
#   Date helper functions
# ========================================================

def date_ymd_to_ywd(y, m, d):
    """Compute week number and day-of-week from year,month,mday date."""
    (ty, wk, wd) = datetime.date(y, m, d).isocalendar()
    if ty == y - 1:
        # project to week 0 of the next year
        assert wk >= 52
        (ty, wk, wd) = datetime.date(y, m, d+7).isocalendar()
        wk -= 1
    elif ty == y + 1:
        # project to an extra week in the previous year
        assert wk == 1
        (ty, wk, wd) = datetime.date(y, m, d-7).isocalendar()
        wk += 1
    assert ty == y
    return wk, wd
    ## The following code also works, but using the datetime module is easier.
    ## Compute day-of-year (Jan 1 == 0)
    #yd = d - 1
    #for i in range(m-1): yd += _month_ndays[i]
    #if m > 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0): yd += 1
    ## Determine first day of the year (assuming Gregorian calendar)
    ## 0=mon .. 6=sun
    #t = (6 + y + (y-1) // 4 - (y-1) // 100 + (y-1) // 400) % 7
    ## Compute week number 0 .. 53
    #w = (t + yd) // 7
    #if t < 4: w += 1
    ## Compute day-of-week 1=mon .. 7=sun
    #d = (t + yd) % 7 + 1
    #return (w, d)


def date_ymd_to_absdate(y, m, d):
    """Compute the absolute day number of yyyy-mm-dd, where 0001-01-01
    has absolute day number 1 (assuming the Gregorian calendar)."""
    return datetime.date(y, m, d).toordinal()
    ## The following code also works, but using the datetime module is easier.
    ## Compute absolute day number of yyyy-01-01
    #t = 1 + (y-1) * 365 + (y-1) // 4 - (y-1) // 100 + (y-1) // 400
    ## Step to absolute day number of yyyy-mm-01
    #for i in range(m-1): t += _month_ndays[i]
    #if m > 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0): t += 1
    ## Step to absolute day number of yyyy-mm-dd
    #t += d - 1
    #return t


def date_absdate_to_ymd(t):
    """Compute year, month and day-of-month corresponding to the given
    absolute day number, where 0001-01-01 has absolute day number 1."""
    dt = datetime.date.fromordinal(t)
    return dt.year, dt.month, dt.day
    ## The following code also works, but using the datetime module is easier.
    ## Start from an underestimation of the year
    #y = t // 366
    ## Increase year while t is large enough to fit Jan 1 in year (y+1)
    #while t >= date_ymd_to_absdate(y+1, 1, 1):
    #    y += 1
    ## Compute remaining days since Jan 1
    #t -= date_ymd_to_absdate(y, 1, 1)
    ## Find the month
    #for m in range(12):
    #    md = _month_ndays[m]
    #    if m == 1 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0): md = 29
    #    if t < md: break
    #    t -= md
    ## Return year, month, day-of-month
    #return y, m + 1, t + 1


def date_ywd_to_absdate(y, w, d):
    """Compute the absolute day number for given year, week and day-of-week,
    where 0001-01-01 has absolute day number 1."""
    # Compute ISO week and day-of-week for some day in the input year
    dt = datetime.date(y, 6, 1)
    (ty, tw, td) = dt.isocalendar()
    assert ty == y
    # Add difference to input week and day-of-week
    return dt.toordinal() + 7 * (w - tw) + d - td
    ## The following code also works, but using the datetime module is easier.
    ## Compute absolute day number for yyyy-W01-1 (monday in week 1)
    #t = 1 + ((3 + (y-1)*365 + (y-1)//4 - (y-1)//100 + (y-1)//400) // 7) * 7
    ## Add week and day-of-week
    #t += 7 * (w - 1) + (d - 1)
    #return t


def date_absdate_to_ywd(t):
    """Compute year, week and day-of-week corresponding to the given
    absolute day number, where 0001-01-01 has absolute day number 1."""
    return datetime.date.fromordinal(t).isocalendar()
    ## The following code also works, but using the datetime module is easier
    ## Start from an underestimation of the year
    #y = t // 366
    ## Increase year while t is large enough for monday of week 1 year (y+1)
    #while t >= date_ywd_to_absdate(y+1, 1, 1):
    #    y += 1
    ## Compute remaining offset from monday of week 1
    #t -= date_ywd_to_absdate(y, 1, 1)
    ## Compute week number and day-of-week
    #w = t // 7 + 1
    #d = t % 7 + 1
    #return y, w, d

