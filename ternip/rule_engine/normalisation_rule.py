#!/usr/bin/env python

import re
import rule

class normalisation_rule(rule.rule):
    """ A class that represents normalisation rules """
    
    def __init__(self, match,
                       type,
                       id,
                       value         = None,
                       guards        = [],
                       after_guards  = [],
                       before_guards = [],
                       after         = []):
        """
        Create a normalisation rule, with a number of optional arguments. All
        regex's are in the form to be used with nltk.TokenSearcher.findall
        (http://nltk.googlecode.com/svn/trunk/doc/api/nltk.text.TokenSearcher-class.html#findall)
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
            available in the form {#[0-9]}
        guard is a list of regexes which must be satisfied for this rule to be
            applied. Defauts to an empty list. If the first character in the
            regex is a !, then it means that it's a negative guard - the guard
            must NOT match for this rule to be applied.
        after_guards are like guards, but match against the text proceeding the
            annotation in the sentence
        before_guards are like after_guards, but match against preceeding text.
        after is a list of IDs which must have preceeded the execution of this
            rule
        """
        
        self.id               = id
        self._type            = type
        self._match           = re.compile(self._prep_re(match), re.IGNORECASE)
        self.after            = after
        
        # replace our group short form, e.g., {#6} with actual Python code
        # it would be nice to support named groups, but this'll do for now
        self._value_exp = re.sub(r'{#(\d)+}', r'match.group(\1)', value)
        
        # Load guards
        self._guards = self._load_guards(guards)
        self._before_guards = self._load_guards(before_guards)
        self._after_guards = self._load_guards(after_guards)