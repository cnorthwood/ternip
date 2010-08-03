#!/usr/bin/env python

import re
import datetime
import string_conversions

def offset_from_date(v, offset, gran='D', exact=False):
    """
    Given a date string and some numeric offset, as well as a unit, then compute
    the offset from that value by offset gran's. Gran defaults to D. If exact
    is set to true, then the exact date is figured out, otherwise the level of
    granuality given by gran is used. Returns a date string.
    """
    
    gran = string_conversions.units_to_gran(gran)
    
    # Extract date components into a datetime object for manipulation
    y = int(v[:4])
    m = int(v[4:6])
    
    if len(v) >= 8:
        d = int(v[6:8])
        really_d = True
    else:
        really_d = False
        d = 1
    
    if len(v) >= 11:
        h = int(v[9:11])
    else:
        h = None
        dt = datetime.datetime(y, m, d)
    
    if len(v) >= 14:
        min = int(v[12:14])
    else:
        min = None
        if h != None:
            dt = datetime.datetime(y, m, d, h)
    
    if len(v) >= 17:
        s = int(v[15:17])
        dt = datetime.datetime(y, m, d, h, min, s)
    else:
        s = None
        if min != None:
            dt = datetime.datetime(y, m, d, h, min)
    
    # Do manipulations
    if gran == 'TM':
        # minutes
        dt += datetime.timedelta(minutes=offset)
        return dt.strftime('%Y%m%dT%H%M')
    
    elif gran == 'TH':
        # hours
        dt += datetime.timedelta(hours=offset)
        if exact:
            return dt.strftime('%Y%m%dT%H%M')
        else:
            return dt.strftime('%Y%m%dT%H')
    
    elif gran == 'D':
        # days
        dt += datetime.timedelta(days=offset)
        if exact and min != None:
            return dt.strftime('%Y%m%dT%H%M')
        elif exact and h != None:
            return dt.strftime('%Y%m%dT%H')
        else:
            return dt.strftime('%Y%m%d')
    
    elif gran == 'W' or gran == 'F':
        # weeks/fortnights
        if gran == 'F':
            offset *= 2
        dt += datetime.timedelta(weeks=offset)
        if exact:
            return dt.strftime('%Y%m%d')
        else:
            return dt.strftime('%YW%W')
    
    elif gran == 'M':
        # months - timedelta rather annoyingly doesn't support months, so we
        # need to do a bit more work here
        m += offset
        if m > 12:
            year += int(m/12)
            m = m % 12
        elif m < 0:
            y += int(m/12) - 1
            m = m % 12
        
        if m == 0:
            m = 12
            y -= 1
        
        # avoid bad days
        dt = None
        while dt == None and d > 0:
            try:
                dt = datetime.datetime(y, m, d)
            except ValueError:
                d -= 1
        
        if exact:
            return dt.strftime('%Y%m%d')
        else:
            return dt.strftime('%Y%m')
    
    elif gran == 'Y' or gran == 'E' or gran == 'C':
        # years/decades/centuries - again, need to do a bit more work
        if gran == 'C':
            offset *= 100
        if gran == 'E':
            offset *= 10
        if d == 29 and m == 2 and not calendar.isleap(y + offset):
            # eugh, mucking about with a date that's not going to be in the
            # target year - fall back
            d = 28
        y += offset
        dt = datetime.datetime(y, m, d)
        if not exact and gran == 'C':
            return dt.strftime('%Y')[:2]
        elif not exact and gran == 'E':
            return dt.strftime('%Y')[:3]
        elif exact and really_d:
            return dt.strftime('%Y%m%d')
        elif exact and not really_d:
            return dt.strftime('%Y%m')
        else:
            return dt.strftime('%Y')
    
    elif offset > 1:
        return 'FUTURE_REF'
    
    elif offset < 1:
        return 'PAST_REF'
    
    elif min != None:
        return dt.strftime('%Y%m%dT%H%M')
        
    elif h != None:
        return dt.strftime('%Y%m%dT%H')
        
    elif really_d:
        return dt.strftime('%Y%m%d')
        
    else:
        return dt.strftime('%Y%m')

def compute_relative_date(ref_date, expression, current_direction):
    """
    Given a reference date, some expression and the current direction of the
    expression (e.g., if talking in the past tense, then the definition of
    "Friday" might mean the previous rather than preceeding Friday).
    Returns string.
    """
    
    # No expression or empty match object, do no computation
    if expression is None:
        return ref_date
    
    # If it's a day...
    match = re.search(expressions.DAYS, expression, re.I)
    if match != None:
        day = day_to_num(match.group())
        t = day - date_to_dow(int(ref_date[:4]), int(ref_date[4:6]), int(ref_date[6:8]))
        if t > 0 and current_direction < 0:
            t -= 7
        if t < 0 and current_direction > 0:
            t += 7
        return offset_from_date(ref_date, t)
    
    # Other expressions
    elif expression.lower().contains('yesterday'):
        return offset_from_date(ref_date, -1)
    elif expression.lower().contains('tomorrow'):
        return offset_from_date(ref_date, 1)
    
    # Couldn't figure out an offset
    else:
        return ref_date