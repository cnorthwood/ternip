#!/usr/bin/env python

from operator import itemgetter

import re


_word_to_num = {
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


def words_to_num(words):
    """
    Converted from GUTime. Given a string of number words, attempts to derive
    the numerical value of those words. Returns an integer.
    """

    # Get out quickly if we're passed in a group that doesn't match
    if words is None:
        return 0

    # If this comes from deliminated numbers
    words = re.sub(r'NUM_START', r'', words).strip()
    words = re.sub(r'NUM_END', r'', words).strip()

    # Clean up our input
    words = words.lower()

    # Get rid of tokens
    words = re.sub(r'<([^~]*)[^>]*>', r'\1 ', words).strip()

    # Superfluous white space
    words = words.strip()

    # Hyphenated number words
    words = re.sub(r'-', '', words)

    # Number word separators
    words = re.sub(r',', '', words)
    words = re.sub(r'\sand', '', words)

    # "a" and "the" mean one, really
    words = re.sub(r'^a', 'one', words)
    words = re.sub(r'^the', 'one', words)

    # convert to list
    words = words.split()

    # now attempt to convert each word to it's numerical equivalent
    for i in range(len(words)):
        if words[i] in _word_to_num:
            words[i] = _word_to_num[words[i]]
        elif words[i] in _ordinal_to_num and len(words) - 1 == i:
            # only allow ordinal words in the last position
            words[i] = ordinal_to_num(words[i])
        else:
            # Hope it's a number. If not, we error out
            try:
                words[i] = int(words[i])
            except ValueError:
                return 0

    # Now recursively break down these
    return _words_to_num(words)


def _words_to_num(nums):
    """
    Recursively break down a number string into individual number components,
    compute the value of those components (basically, the bit before the largest
    number, and the bit after) and then put it all back together.
    """

    # base case
    if len(nums) == 1:
        return nums[0]

    # find highest number in string
    (highest_num, highest_num_i) = max(zip(nums, range(len(nums))), key=itemgetter(0))
    before = nums[:highest_num_i]
    after = nums[highest_num_i + 1:]

    # If there are no numbers before the biggest term, then assume it means 1 of
    # those units
    if len(before) > 0:
        before = _words_to_num(before)
    else:
        before = 1

    # if there are no numbers after, then append 0 to it
    if len(after) > 0:
        after = _words_to_num(after)
    else:
        after = 0

    return (before * highest_num) + after

# Mapping of ordinals to numbers
_ordinal_to_num = {
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


def ordinal_to_num(o):
    """
    Given an ordinal (i.e., thirty-first or second) in the range 1st-31st (both
    numbers and words accepted), return the number value of that ordinal.
    Unrecognised data gets 1. Returns an integer
    """
    match = re.search(r'\d+', o)
    if match is not None:
        return int(match.group())
    elif o.lower() in _ordinal_to_num:
        return _ordinal_to_num[o.lower()]
    else:
        return 1
