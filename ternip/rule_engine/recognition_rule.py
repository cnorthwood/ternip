#!/usr/bin/env python

import re
import ternip.timex
import rule

class recognition_rule(rule.rule):
    """ A class that represents identification rules """
    
    def __init__(self, match,
                       type,
                       id,
                       guards        = [],
                       after_guards  = [],
                       before_guards = [],
                       after         = [],
                       squelch       = False):
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
        """
        
        self.id               = id
        self._type            = type
        self._match           = re.compile(self._prep_re(match), re.IGNORECASE)
        self._squelch         = squelch
        self.after            = after
        
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
        
        success = False
        
        # Ensure the sentence-level guards are satisfied
        if not self._check_guards(senttext, self._guards):
            return (sent, success)
        
        # Now see if this rule actually matches anything
        for match in self._match.finditer(senttext):
            
            guard_sat = True
            
            # Now check before guards
            if not self._check_guards(senttext[:match.start()], self._before_guards):
                guard_sat = False
            
            # and after guards
            if not self._check_guards(senttext[match.end():], self._after_guards):
                guard_sat = False
            
            if guard_sat:
                # okay, first we need to find which tokens we matched, can do this
                # by using our token markers
                ti = senttext.count('<', 0, match.start())
                tj = senttext.count('<', 0, match.end())
                
                if not self._squelch:
                    t = ternip.timex(self._type) # only create a new timex if not squelching
                
                for i in range(len(sent)):
                    # now get all tokens in the range and add the new timex if needed
                    (token, pos, ts) = sent[i]
                    if i >= ti and i < tj:
                        if self._squelch:
                            # in the case of this being a squelch rule, remove the
                            # timexes
                            ts = set()
                        else:
                            # otherwise add the new timex to the list of timexes
                            # associated with this token
                            ts.add(t)
                    
                    sent[i] = (token, pos, ts)
                    success = True
        
        return (sent, success)