#!/usr/bin/env python

"""
Functions which convert strings to some number index
"""

import re

# Mapping of month abbreviations to month index
_month_to_num = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}

def month_to_num(m):
    """
    Given a name of a month, get the number of that month. Invalid data gets 0.
    Returned as an integer.
    """
    if m[:3].lower() in _month_to_num:
        return _month_to_num[m[:3].lower()]
    else:
        return 0

# Mapping of days to day index
_day_to_num = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6
}

def day_to_num(day):
    """
    Given the name of a day, the number of that day. Sunday is 0. Invalid data
    gets 7. All returned as integers.
    """
    if day.lower() in _day_to_num:
        return _day_to_num[day.lower()]
    else:
        return 7

# The decade number that a year component (-ty) refers to
_decade_nums = {
    "twen": 2,
    "thir": 3,
    "for": 4,
    "fif": 5,
    "six": 6,
    "seven": 7,
    "eigh": 8,
    "nine": 9
}

def decade_nums(dec):
    """
    Given the decade component (less the ty suffix) of a year, the number of
    that year as an integer.
    """
    if dec.lower() in _decade_nums:
        return _decade_nums[dec.lower()]
    else:
        return 1

# Season to TIDES identifiers
_season = {
    "spring": "SP",
    "summer": "SU",
    "autumn": "FA",
    "fall":   "FA",
    "winter": "WI"
}

def season(s):
    """
    Transforms a season name into an identifer from TIDES. Invalid data gets
    returned as is
    """
    if s.lower() in _season:
        return _season[s.lower()]
    else:
        return s

_season_to_month = {
    'SP': 'april',
    'SU': 'june',
    'FA': 'september',
    'WI': 'december'
}

def season_to_month(s):
    """
    Convert seasons to months (roughly), returns an int
    """
    s = season(s)
    if s in _season_to_month:
        return _season_to_month[s]
    else:
        return ''

# Words (or parts of words) and then unit identifier
_units_to_gran = {
    'dai': 'D',
    'night': 'D',
    'day': 'D',
    'week': 'W',
    'fortnight': 'F',
    'month': 'M',
    'year': 'Y',
    'annual': 'Y',
    'decade': 'E',
    'century': 'C',
    'centurie': 'C'
}

def units_to_gran(unit):
    """
    Given a word, or part of a word, that represents a unit of time, return the
    single character representing the granuality of that unit of time
    """
    if unit.lower() in _units_to_gran:
        return _units_to_gran[unit.lower()]
    else:
        return unit

# Dates of holidays which are on the same date every year MMDD. Keys have spaces
# removed
_fixed_holiday_dates = {
    "newyear":          "0101",
    "inauguration":     "0120",
    "valentine":        "0214",
    "ground":           "0202",
    "candlemas":        "0202",
    "patrick":          "0317",
    "fool":             "0401",
    "st\.george":       "0423",
    "saintgeorge":      "0423",
    "walpurgisnacht":   "0430",
    "mayday":           "0501",
    "beltane":          "0501",
    "cinco":            "0505",
    "flag":             "0614",
    "baptiste":         "0624",
    "dominion":         "0701",
    "canada":           "0701",
    "independence":     "0704",
    "bastille":         "0714",
    "halloween":        "1031",
    "allhallow":        "1101",
    "allsaints":        "1101",
    "allsouls":         "1102",
    "dayofthedead":     "1102",
    "fawkes":           "1105",
    "veteran":          "1111",
    "christmas":        "1225",
    "xmas":             "1225"
}

def fixed_holiday_date(hol):
    """
    Get the date string MMDD of a holiday
    """
    hol = re.sub(r'<([^~]*)~[^>]*>', r'\1', hol).lower()
    if hol in _fixed_holiday_dates:
        return _fixed_holiday_dates[hol]
    else:
        return ''

# Mapping of holidays which always occur on the Nth X of some month, where X is
# day of week. Mapping is of tuples of the form (month, dow, n)
_nth_dow_holiday_date = {
    "mlk":          (1, 1, 3),
    "king":         (1, 1, 3),
    "president":    (2, 1, 3),
    "canberra":     (3, 1, 3),
    "mother":       (5, 7, 2),
    "father":       (6, 7, 3),
    "labor":        (9, 1, 1),
    "columbus":     (10, 1, 2),
    "thanksgiving": (11, 4, 4)
}

def nth_dow_holiday_date(hol):
    """
    Given the name of a holiday which always occur on the Nth X of some month,
    where X is day of week, returns tuples of the form (month, dow, n)
    representing the information about that holiday.
    """
    if hol.lower() in _nth_dow_holiday_date:
        return _nth_dow_holiday_date[hol.lower()]
    else:
        return (0,0,0)