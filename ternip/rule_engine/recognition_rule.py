#!/usr/bin/env python

import re
from ..timex import timex
import rule
import expressions

class recognition_rule(rule.rule):
    """ A class that represents identification rules """
    
    # If debug mode is enabled, then the comment in the TIMEX tag is set to
    # the ID of the rule which created it
    _DEBUG = False
    
    def __init__(self, match,
                       type,
                       id,
                       guards             = [],
                       after_guards       = [],
                       before_guards      = [],
                       after              = [],
                       squelch            = False,
                       case_sensitive     = False,
                       deliminate_numbers = False):
        """
        Create a recognition rule, with a number of optional arguments. All
        regex's are in the form to be used with nltk.TokenSearcher.findall
        (http://nltk.googlecode.com/svn/trunk/doc/api/nltk.text.TokenSearcher-class.html#findall)
        however with the amendment that the body of the tokens are actually in
        the form <token~POS>, e.g., <about~.+> would match about with any POS
        tag.
        
        match is a regex. The text that is matched by this regex is annotated as
            a timex. Compulsory.
        type can be date, time or duration (TIMEX3 annotation guidelines). This
            is a compulsory value.
        id is a unique value other rules can refer to in order to express an
            ordering.
        guards is a list of regexes which must be satisfied for this rule to be
            applied. Defauts to an empty list. If the first character in the
            regex is a !, then it means that it's a negative guard - the guard
            must NOT match for this rule to be applied.
        after_guards is a list of regexes, like normal guards, but is only
            matched against the string immediately proceeding a match to check
            if that is satisfied
        before_guards is like after_guards, but matches against the string
            immediately preceeding a match
        after is a list of IDs which must have preceeded the execution of this
            rule
        squelch is a Boolean. If true, then if the 'match' regex matches some
            stuff that's already been timex annotated, those timexes are removed
            and no timex is added to the match. Defaults to false.
        case_sensitive is a Boolean indicating whether or not this rule should
            be matched case sensitively or not.
        deliminate_numbers is a Boolean indicating whether or not this rule
            requires the sentence to have deliminated numbers
        """
        
        self.id                  = id
        self._type               = type
        if case_sensitive:
            self._match          = re.compile(self._prep_re(match))
        else:
            self._match          = re.compile(self._prep_re(match), re.IGNORECASE)
        self._squelch            = squelch
        self.after               = after
        self._deliminate_numbers = deliminate_numbers
        
        # Load guards
        self._guards = self._load_guards(guards)
        self._before_guards = self._load_guards(before_guards)
        self._after_guards = self._load_guards(after_guards)
    
    def apply(self, sent):
        """
        Applies this rule to the tokenised sentence. The 'after' ordering
        must be checked by the caller to ensure correct rule application.
        
        sent is a list of tuples (token, POS, [timexes])
        
        A tuple is returned where the first element is a list in the same form
        as sent, with additional timexes added to the 3rd element if need be,
        and the second element in the tuple is whether or not this rule matched
        anything
        """
        
        senttext = self._toks_to_str(sent)
        
        if self._deliminate_numbers:
            senttext = self._do_deliminate_numbers(senttext)
        
        success = False
        
        # Ensure the sentence-level guards are satisfied
        if not self._check_guards(senttext, self._guards):
            return (sent, success)
        
        # Now see if this rule actually matches anything
        for match in self._match.finditer(senttext):
            
            # Now check before guards
            if not self._check_guards(senttext[:match.start()], self._before_guards):
                continue
            
            # and after guards
            if not self._check_guards(senttext[match.end():], self._after_guards):
                continue
            
            # okay, first we need to find which tokens we matched, can do this
            # by using our token markers
            ti = senttext.count('<', 0, match.start())
            tj = senttext.count('<', 0, match.end())
            
            if not self._squelch:
                t = timex(self._type) # only create a new timex if not squelching
                if self._DEBUG:
                    t.comment = self.id
            else:
                t = None
            
            # Add TIMEX
            self._set_timex_extents(t, sent, ti, tj, self._squelch)
            #print self.id, "matched", match.group(), sent[ti:tj], senttext
            success = True
        
        return (sent, success)