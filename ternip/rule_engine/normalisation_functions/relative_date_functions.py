#!/usr/bin/env python

import re
import datetime
import calendar

import string_conversions
import date_functions
from .. import expressions

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
    
    if len(v) >= 13:
        min = int(v[11:13])
    else:
        min = None
        if h != None:
            dt = datetime.datetime(y, m, d, h)
    
    if len(v) >= 15:
        s = int(v[13:15])
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
            y += int(m/12)
            m = m % 12
        elif m < 0:
            y += int(m/12)
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
    
    elif offset >= 1:
        return 'FUTURE_REF'
    
    elif offset <= -1:
        return 'PAST_REF'
    
    else:
        return v

def compute_offset_base(ref_date, expression, current_direction):
    """
    Given a reference date, some simple expression (yesterday/tomorrow or a
    day of week) and the direction of the relative expression, the base date
    with which to compute the offset from as a date string
    """
    
    # No expression or empty match object, do no computation
    if expression is None:
        return ref_date
    
    # If it's a day...
    match = re.search(expressions.DAYS, expression, re.I)
    if match != None:
        day = string_conversions.day_to_num(match.group())
        t = day - date_functions.date_to_dow(int(ref_date[:4]), int(ref_date[4:6]), int(ref_date[6:8]))
        if t > 0 and current_direction < 0:
            t -= 7
        if t < 0 and current_direction > 0:
            t += 7
        return offset_from_date(ref_date, t)
    
    # if it's a month
    elif re.search('(' + expressions.MONTH_ABBRS + '|' + expressions.MONTHS + ')', expression, re.I) != None:
        match = re.search('(' + expressions.MONTH_ABBRS + '|' + expressions.MONTHS + ')', expression, re.I)
        m = date_functions.month_to_num(match.group()) - int(ref_date[4:6])
        if m > 0 and current_direction < 0:
            m -= 12
        if m < 0 and current_direction > 0:
            m += 12
        return offset_from_date(ref_date, m, 'M')
    
    # if it's a holiday
    elif re.search(expressions.FIXED_HOLIDAYS, expression, re.I) != None:
        match = re.search(expressions.FIXED_HOLIDAYS, expression, re.I)
        ref_m = int(ref_date[4:6])
        ref_d = int(ref_date[6:8])
        holdate = string_conversions.fixed_holiday_date(match.group())
        hol_m = int(holdate[:2])
        hol_d = int(holdate[2:4])
        
        if (hol_m < ref_m or (hol_m == ref_m and hol_d < ref_d)) and current_direction > 0:
            ref_date = offset_from_date(ref_date, 1, 'Y', True)
        elif (hol_m > ref_m or (hol_m == ref_m and hol_d > ref_d)) and current_direction < 0:
            ref_date = offset_from_date(ref_date, -1, 'Y', True)
        
        return ref_date[:4] + holdate
    
    # Other expressions
    elif expression.lower().find('yesterday') > -1:
        return offset_from_date(ref_date, -1)
    elif expression.lower().find('tomorrow') > -1:
        return offset_from_date(ref_date, 1)
    
    # Couldn't figure out an offset
    else:
        return ref_date
    