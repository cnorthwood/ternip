#!/usr/bin/env python

# predef re's for replacing
ORDINAL_WORDS = r'(tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|twenty-first|twenty-second|twenty-third|twenty-fourth|twenty-fifth|twenty-sixth|twenty-seventh|twenty-eighth|twenty-ninth|thirtieth|thirty-first|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)'
ORDINAL_NUMS = r'([23]?1-?st|11-?th|[23]?2-?nd|12-?th|[12]?3-?rd|13-?th|[12]?[4-90]-?th|30-?th)'
DAYS = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
MONTHS = r'(january|february|march|april|may|june|july|august|september|october|november|december)'
MONTH_ABBRS = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)'
RELATIVE_DAYS = r'(today|yesterday|tomorrow|tonight|tonite)'
DAY_HOLIDAYS = r'(election|memorial|C?Hanukk?ah|Rosh|Kippur|tet|diwali|halloween)'
NTH_DOW_HOLIDAYS = r'(mlk|king|president|canberra|mother|father|labor|columbus|thanksgiving)'
FIXED_HOLIDAYS = r'(<new~.+><year~.+>|<inauguration~.+>|<valentine~.+>|<ground~.+>|<candlemas~.+>|<patrick~.+>|<fool~.+>|<(saint|st\.)~.+><george~.+>|<walpurgisnacht~.+>|<may~.+><day~.+>|<beltane~.+>|<cinco~.+>|<flag~.+>|<baptiste~.+>|<canada~.+>|<dominion~.+>|<independence~.+>|<bastille~.+>|<halloween~.+>|<allhallow~.+>|<all~.+><(saint|soul)s~.+>|<day~.+><of~.+><the~.+><dead~.+>|<fawkes~.+>|<veteran~.+>|<christmas~.+>|<xmas~.+>|<boxing~.+>)'
LUNAR_HOLIDAYS = r'(<easter~.+>|<palm~.+><sunday~.+>|<good~.+><friday~.+>|<ash~.+><wednesday~.+>|<shrove~.+><tuesday~.+>|<mardis~.+><gras~.+>)'
NUMBER_TERM = r'(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|trillion|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|hundreth|thousandth|millionth|billionth|trillionth)'
ORD_UNIT_NUMS = r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)'
ORD_OTHER_NUMS = r'(tenth|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth|hundreth|thousandth|millionth|billionth|trillionth)'
HIGHER_NUMS = r'(hundred|thousand|million|billion|trillion)'
UNIT_NUMS = r'(one|two|three|four|five|six|seven|eight|nine)'
UNIQUE_NUMS = r'(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)'
TENS_NUMS = r'(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)'

# Mappings
month_to_num = {
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

ordinal_to_num = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "twenty-first": 21,
    "twenty-second": 22,
    "twenty-third": 23,
    "twenty-fourth": 24,
    "twenty-fifth": 25,
    "twenty-sixth": 26,
    "twenty-seventh": 27,
    "twenty-eighth": 28,
    "twenty-ninth": 29,
    "thirtieth": 30,
    "thirty-first": 31
}

timezones = {
    "E": -5,
    "C": -6,
    "M": -7,
    "P": -8
}

word_to_num = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000
}

decade_nums = {
    "twen": 2,
    "thir": 3,
    "for": 4,
    "fif": 5,
    "six": 6,
    "seven": 7,
    "eigh": 8,
    "nine": 9
}