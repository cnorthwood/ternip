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
    
    # check for valid refdate
    if len(v) > 0:
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
    
    elif offset >= 1:
        return 'FUTURE_REF'
    
    elif offset <= -1:
        return 'PAST_REF'
    
    else:
        return v
    
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
        
        y += offset
        
        # Python doesn't allow datetime objects to be created representing years
        # before 1970, so do this the old fashioned way
        if not exact:
            if gran == 'C':
                return ("%04d" % y)[:2]
            elif gran == 'E':
                return ("%04d" % y)[:3]
            else:
                return ("%04d" % y)
        else:
            if d == 29 and m == 2 and not calendar.isleap(y):
                # eugh, mucking about with a date that's not going to be in the
                # target year - fall back
                d = 28
            if really_d:
                return "%04d%02d%02d" % (y, m, d)
            else:
                return "%04d%02d" % (y, m)
    
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
    
    # If it's a partial date expression
    match = re.search(r'^XXXX(\d\d)(\d\d)', expression, re.I)
    if match != None:
        m = int(match.group(1))
        d = int(match.group(2))
        ref_m = int(ref_date[4:6])
        ref_d = int(ref_date[6:8])
        
        if (m < ref_m or (m == ref_m and d < ref_d)) and current_direction > 0:
            ref_date = offset_from_date(ref_date, 1, 'Y', True)
        elif (m > ref_m or (m == ref_m and d > ref_d)) and current_direction < 0:
            ref_date = offset_from_date(ref_date, -1, 'Y', True)
        
        return ref_date[:4] + expression[4:]
    
    # If it's a day...
    elif re.search(expressions.DAYS, expression, re.I) != None:
        match = re.search(expressions.DAYS, expression, re.I)
        day = string_conversions.day_to_num(match.group())
        t = day - date_functions.date_to_dow(int(ref_date[:4]), int(ref_date[4:6]), int(ref_date[6:8]))
        if t >= 0 and current_direction < 0:
            t -= 7
        if t <= 0 and current_direction > 0:
            t += 7
        return offset_from_date(ref_date, t)
    
    # if it's a month
    elif re.search('(' + expressions.MONTH_ABBRS + '|' + expressions.MONTHS + ')', expression, re.I) != None:
        match = re.search('(' + expressions.MONTH_ABBRS + '|' + expressions.MONTHS + ')', expression, re.I)
        m = date_functions.month_to_num(match.group()) - int(ref_date[4:6])
        if m >= 0 and current_direction < 0:
            m -= 12
        if m <= 0 and current_direction > 0:
            m += 12
        return offset_from_date(ref_date, m, 'M')
    
    # if it's a fixed holiday
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
    
    # if it's an nth dow holiday
    elif re.search(expressions.NTH_DOW_HOLIDAYS, expression, re.I) != None:
        match = re.search(expressions.NTH_DOW_HOLIDAYS, expression, re.I)
        
        # Get the date of the event this year and figure out if it's passed or
        # not
        ref_m = int(ref_date[4:6])
        ref_d = int(ref_date[6:8])
        hol_m = string_conversions.nth_dow_holiday_date(match.group(1))[0]
        hol_d = date_functions.nth_dow_to_day(string_conversions.nth_dow_holiday_date(match.group(1)), int(ref_date[:4]))
        
        if (hol_m < ref_m or (hol_m == ref_m and hol_d < ref_d)) and current_direction > 0:
            ref_date = offset_from_date(ref_date, 1, 'Y', True)
        elif (hol_m > ref_m or (hol_m == ref_m and hol_d > ref_d)) and current_direction < 0:
            ref_date = offset_from_date(ref_date, -1, 'Y', True)
        
        # Now figure out the date for that year
        return "%s%02d%02d" % (ref_date[:4], string_conversions.nth_dow_holiday_date(match.group(1))[0], date_functions.nth_dow_to_day(string_conversions.nth_dow_holiday_date(match.group(1)), int(ref_date[:4])))
    
    # if it's a lunar holiday
    elif re.search(expressions.LUNAR_HOLIDAYS, expression, re.I) != None:
        match = re.search(expressions.LUNAR_HOLIDAYS, expression, re.I)
        
        hol = match.group()
        hol = re.sub(r'<([^~]*)[^>]*>', r'\1', hol)
        hol = re.sub(r'\s', '', hol)
        hol = hol.lower()
        
        easter_offsets = {
            'goodfriday': -3,
            'shrovetuesday': -47,
            'ashwednesday': -46,
            'palmsunday': -7,
            'easter': 0
        }
        
        # Get the date of the event this year and figure out if it's passed or
        # not
        ref_m = int(ref_date[4:6])
        ref_d = int(ref_date[6:8])
        hol_date = offset_from_date(date_functions.easter_date(int(ref_date[:4])), easter_offsets[hol])
        hol_m = int(hol_date[4:6])
        hol_d = int(hol_date[6:8])
        
        if (hol_m < ref_m or (hol_m == ref_m and hol_d < ref_d)) and current_direction > 0:
            ref_date = offset_from_date(ref_date, 1, 'Y', True)
        elif (hol_m > ref_m or (hol_m == ref_m and hol_d > ref_d)) and current_direction < 0:
            ref_date = offset_from_date(ref_date, -1, 'Y', True)
        
        hol_y = int(ref_date[:4])
        return offset_from_date(date_functions.easter_date(hol_y), easter_offsets[hol])
    
    # Other expressions
    elif expression.lower().find('yesterday') > -1:
        return offset_from_date(ref_date, -1)
    elif expression.lower().find('tomorrow') > -1:
        return offset_from_date(ref_date, 1)
    
    # Couldn't figure out an offset
    else:
        return ref_date

def _extract_verbs(s):
    """
    Given a sentence, extract the verbs and their POS tags from it.
    """
    verb = None
    verb2 = None
    vpos = None
    vpos2 = None
    pos_found = False
    for (tok, pos, ts) in s:
        if (pos.upper() == 'VBP' or \
            pos.upper() == 'VBZ' or \
            pos.upper() == 'VBD' or \
            pos.upper() == 'MD') and \
            not pos_found:
            verb = tok.lower()
            vpos = pos.upper()
        elif pos_found and tok[:2].upper() == 'VB':
                verb2 = tok.lower()
                vpos2 = pos.upper()
                break
    
    if vpos == 'VBP' or vpos == 'VBZ' or vpos == 'MD' and \
        re.search(r'going\s+to', ' '.join([tok for (tok, pos, ts) in s]), re.I) != None:
        vpos = 'MD'
        verb = 'going_to'
    
    return (verb, vpos, verb2, vpos2)

def relative_direction_heuristic(before, after):
    """
    Given what preceeds and proceeds a TIMEX, then use heuristics to use tense
    to compute which direction a relative expression is in.
    Converted from GUTime.
    """
    
    # Get the bit after the last TIMEX and before this one
    lead = before
    for i in range(-1, -1 * len(before), -1):
        if len(before[i][2]) > 0:
            lead = before[i:]
            break
    
    # Okay, now extract the verbs
    (verb, pos, verb2, pos2) = _extract_verbs(lead)
    if verb is None:
        (verb, pos, verb2, pos2) = _extract_verbs(after)
    if verb is None:
        (verb, pos, verb2, pos2) = _extract_verbs(before)
    if verb is None:
        return 0
    
    # Now try and figure out a relative direction based on the verb information
    if pos == 'VBD':
        return -1
    
    elif pos == 'MD':
        if re.search(r'(will|\'ll|going_to)', verb, re.I) != None:
            return 1
        elif verb2 == 'have':
            return -1
        elif re.search(r'((w|c|sh)ould|\'d)', verb, re.I) != None and pos2 == 'VB':
            return 1
    
    # Use other linguistic cues to determine tense
    if before[-1][0].lower() == 'since':
        return -1
    elif before[-1][0].lower() == 'until':
        return 1
    
    return 0