#!/usr/bin/env python

import re
import rule
import expressions

class normalisation_rule(rule.rule):
    """ A class that represents normalisation rules """
    
    # If debug mode is enabled, then the comment in the TIMEX tag is set to
    # the ID of the rule which normalised it
    _DEBUG = False
    
    def __init__(self, match,
                       type,
                       id,
                       value         = None,
                       guards        = [],
                       after_guards  = [],
                       before_guards = [],
                       after         = [],
                       tokenise      = True):
        """
        Create a normalisation rule, with a number of optional arguments. If
        tokenise is set to true, then regex's are in the form to be used with
        nltk.TokenSearcher.findall (http://nltk.googlecode.com/svn/trunk/doc/api/nltk.text.TokenSearcher-class.html#findall)
        however with the amendment that the body of the tokens are actually in
        the form <token~POS>, e.g., <about~.+> would match about with any POS
        tag.
        
        match is a regex which the body of the timex must match to run this
            rule. Subgroups of this expression are available to later
            expressions.
        type means the type of TIMEX which this rule applies to
        id is a unique value other rules can refer to in order to express an
            ordering.
        value is a Python expression which returns a value (in ISO 8601 format,
            as modified in TimeML). Subgroups from the match expression are
            available in the form {#[0-9]+}
        guard is a list of regexes which must be satisfied for this rule to be
            applied. Defauts to an empty list. If the first character in the
            regex is a !, then it means that it's a negative guard - the guard
            must NOT match for this rule to be applied.
        after_guards are like guards, but match against the text proceeding the
            annotation in the sentence
        before_guards are like after_guards, but match against preceeding text.
        after is a list of IDs which must have preceeded the execution of this
            rule
        tokenise is whether or not the regular expressions to be matched against
            care about token boundaries/POS tags. If it is not true, it is
            considered to be the separator for tokens.
        """
        
        if tokenise == True:
            match = self._prep_re(match)
        
        self.id               = id
        self._type            = type
        self._match           = re.compile(match, re.IGNORECASE)
        self.after            = after
        self._tokenise        = tokenise
        
        # replace our group short form, e.g., {#6} with actual Python code
        # it would be nice to support named groups, but this'll do for now
        self._value_exp = compile(re.sub(r'\{#(\d)+\}', r'match.group(\1)', value), id + ':value', 'eval')
        
        # Load guards
        self._guards = self._load_guards(guards)
        self._before_guards = self._load_guards(before_guards)
        self._after_guards = self._load_guards(after_guards)
    
    def apply(self, timex, cur_context, dct, body, before, after):
        """
        Applies this rule to this timex, where body is the full extent covered
        by this timex, before is the preceeding text in the sentence, and after
        is the proceeding text in the sentence, in the [(token, POS), ...] form
        
        A boolean indicating whether or not application was successful is
        returned. The timex may also be modified, so should be passed in by
        reference.
        """
        
        # Check this rule type matches the timex type
        if timex.type != self._type:
            return (False, cur_context)
        
        # Check before, after and whole sentence guards
        if not self._check_guards(self._toks_to_str(before), self._before_guards):
            return (False, cur_context)
        
        if not self._check_guards(self._toks_to_str(after), self._after_guards):
            return (False, cur_context)
        
        if not self._check_guards(self._toks_to_str(before + body + after), self._guards):
            return (False, cur_context)
        
        # Now, check if we match:
        if self._tokenise == True:
            senttext = self._toks_to_str(body)
        else:
            senttext = self._tokenise.join([tok for (tok, pos, ts) in body])
        
        match = self._match.search(senttext)
        
        # If we do, then calculate attributes for the timex
        if match:
            
            if self._DEBUG:
                timex.comment = self.id
            
            if self._value_exp != None:
                timex.value = eval(self._value_exp)
            
            # Need to update current time context, if necessary
            return (True, cur_context)
        else:
            # Rule did not match
            return (False, cur_context)

# Functions for normalisation rules to use
def date_to_iso(string):
    """
    A translation of GUTime's Date2ISO function
    """
    
    # disregard tokenisation, if it's there, to make this an easier conversion for GUTime
    string = re.sub(r'<([^~]*)~.+?>', r'\1 ', string)
    
    # Defaults
    d = None
    m = None
    y = None
    h = None
    min = None
    s = None
    fs = None
    zone = None
    
    # Already in ISO format
    match = re.search(r'(\d\d\d\d-?\d\d-?\d\d)(-?(T\d\d(:?\d\d)?(:?\d\d)?([+-]\d{1,4})?))?', re.sub('\s', '', string))
    if match != None:
        d = match.group(1)
        d = re.sub(r'-', r'', d)
        h = match.group(3)
        if h != None:
            h = re.sub(r':', r'', h)
            return d + h
        else:
            return d
    
    # ACE format
    match = re.search(r'(\d\d\d\d\d\d\d\d:\d\d\d\d)', re.sub('\s', '', string))
    if match != None:
        d = match.group(1)
        d = re.sub(r':', r'T', d)
        return d
    
    # some pre-processing
    match = re.search('T\d\d(:?\d\d)?(:?\d\d)?([+-]\d{1,4})?', re.sub('\s', '', string))
    if match != None:
        return re.sub(r':', r'', re.sub('\s', '', string))
    
    # extract date
    if re.search(r'(\d\d?)\s+(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\s*\.?)\s*,?\s+(\d\d(\s|\Z)|\d{4}\b)', string, re.I) != None:
        match = re.search(r'(\d\d?)\s+(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\s*\.?)\s*,?\s+(\d\d(\s|\Z)|\d{4}\b)', string, re.I)
        d = match.group(1)
        m = expressions.month_to_num[match.group(2)[:3].lower()]
        y = match.group(5)
        
    elif re.search(r'(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\s*\.?)\s+(\d\d?|' + expressions.ORDINAL_WORDS + r')\b,?\s*(\d\d(\s|\Z)|\d{4}\b)', string, re.I) != None:
        match = re.search(r'(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\s*\.?)\s+(\d\d?|' + expressions.ORDINAL_WORDS + r')\b,?\s*(\d\d(\s|\Z)|\d{4}\b)', string, re.I)
        d = match.group(4)
        dm = re.search(expressions.ORDINAL_WORDS, d)
        if dm != None:
            d = expressions.ordinal_to_num[dm.group()]
        m = expressions.month_to_num[match.group(1)[:3].lower()]
        y = match.group(6)
    
    elif re.search(r'(\d\d\d\d)(\/|\-)(\d\d?)\2(\d\d?)', re.sub('\s', '', string)) != None:
        match = re.search(r'(\d\d\d\d)(\/|\-)(\d\d?)\2(\d\d?)', re.sub('\s', '', string))
        m = match.group(3)
        d = match.group(4)
        y = match.group(1)
    
    elif re.search(r'(\d\d?)(\/|\-|\.)(\d\d?)\2(\d\d(\d\d)?)', re.sub('\s', '', string)) != None:
        match = re.search(r'(\d\d?)(\/|\-|\.)(\d\d?)\2(\d\d(\d\d)?', re.sub('\s', '', string))
        m = match.group(1)
        d = match.group(3)
        y = match.group(4)
    
    elif re.search(r'(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\.?)\s+(\d\d?).+(\d\d\d\d)\b', string) != None:
        match = re.search(r'(' + expressions.MONTHS + r'|' + expressions.MONTH_ABBRS + r'\.?)\s+(\d\d?).+(\d\d\d\d)\b', string)
        d = match.group(4)
        m = expressions.month_to_num[match.group(2)[:3].lower()]
        y = match.group(5)
        if int(y) > 2100 or int(y) < 1900:
            y = None
    
    if y != None:
        # check for European style date
        if int(m) > 12 and int(m) < 31 and int(d) < 12:
            new_d = m
            m = d
            d = new_d
        
        # check for 2 digit year
        if int(y) < 39:
            y = str(int(y) + 2000)
        elif int(y) < 100:
            y = str(int(y) + 1900)
        
        iso = "%4d%02d%02d" % (int(y), int(m), int(d))
    
    else:
        iso = "XXXXXXXX"
    
    # Extract time
    match = re.search(r'(\d?\d):(\d\d)(:(\d\d)(\.\d+)?)?(([AP])\.?M\.?)?(([+\-]\d+|[A-Z][SD]T|GMT([+\-]\d+)?))?', re.sub('\s', '', string), re.I)
    if match != None:
        h = match.group(1)
        min = match.group(2)
        s = match.group(4)
        fs = match.group(5)
        ampm = match.group(7)
        zone = match.group(9)
        
        if ampm != None and ampm[0].lower() == 'p':
            h = str(int(h) + 12)
        
        if zone != None:
            zm = re.search(r'(GMT)([+\-]\d+)', zone)
            if zm != None:
                zone = zm.group(2)
            elif zone.lower().contains('gmt'):
                zone = 'Z'
            elif re.search(r'([A-Z])([SD])T', zone) != None:
                zm = re.search(r'([A-Z])([SD])T', zone)
                if zm.group(1) in expressions.timezones:
                    zone = expressions.timezones[zone]
                    if zm.group(2) == 'd':
                        zone += 1
                    if zone < 0:
                        zone = '-%02d' % (-1 * zone)
                    else:
                        zone = '+%02d' % zone
    elif re.search(r'(\d\d)(\d\d)\s+(h(ou)?r|(on\s+)?\d\d?\/\d)', string, re.I) != None:
        match = re.search(r'(\d\d)(\d\d)\s+(h(ou)?r|(on\s+)?\d\d?\/\d)', string, re.I)
        h = match.group(1)
        min = match.group(2)
    
    if h != None:
        if fs != None:
            fs = re.sub(r'\.', r'', fs)
            iso += 'T%02d:%02d:%02d.%02d' % (int(h), int(min), int(s), int(fs))
        elif s != None:
            iso += 'T%02d:%02d:%02d' % (int(h), int(min), int(s))
        elif min != None:
            iso += 'T%02d:%02d' % (int(h), int(min))
        else:
            iso += 'T%02d' % (int(h))
        
        if zone != None:
            iso += zone.lstrip()
    
    return iso