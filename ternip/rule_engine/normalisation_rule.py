#!/usr/bin/env python

import re
import calendar

import rule
from expressions import *
from normalisation_functions import *
import ternip

class normalisation_rule(rule.rule):
    """ A class that represents normalisation rules """
    
    # If debug mode is enabled, then the comment in the TIMEX tag is set to
    # the ID of the rule which normalised it
    _DEBUG = True
    
    def __init__(self, match,
                       type          = None,
                       id            = '',
                       value         = None,
                       change_type   = None,
                       freq          = None,
                       quant         = None,
                       guards        = [],
                       after_guards  = [],
                       before_guards = [],
                       after         = [],
                       tokenise      = True,
                       deliminate_numbers = False):
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
        id is a unique string other rules can refer to in order to express an
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
        
        self.id                  = id
        self._type               = type
        self._match              = re.compile(self._prep_re(match, tokenise), re.IGNORECASE)
        self.after               = after
        self._tokenise           = tokenise
        self._deliminate_numbers = deliminate_numbers
        self._value_exp          = self._compile_exp(value, 'value')
        self._type_exp           = self._compile_exp(change_type, 'change-type')
        self._freq_exp           = self._compile_exp(freq, 'freq')
        self._quant_exp          = self._compile_exp(quant, 'quant')
        
        # Load guards
        self._guards = self._load_guards(guards, tokenise)
        self._before_guards = self._load_guards(before_guards, tokenise)
        self._after_guards = self._load_guards(after_guards, tokenise)
    
    def _compile_exp(self, exp, type):
        """
        Replace our group short form in value expressions, e.g., {#6} with
        actual Python code so that matched regular expressions get subbed in
        """
        # it would be nice to support named groups, but this'll do for now
        if exp != None:
            return compile(re.sub(r'\{#(\d)+\}', r'match.group(\1)', exp), self.id + ':' + type, 'eval')
        else:
            return None
    
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
        if timex.type != self._type and self._type != None:
            return (False, cur_context)
        
        # Check before, after and whole sentence guards
        if not self._check_guards(self._toks_to_str(before), self._before_guards):
            return (False, cur_context)
        
        if not self._check_guards(self._toks_to_str(after), self._after_guards):
            return (False, cur_context)
        
        if not self._check_guards(self._toks_to_str(body), self._guards):
            return (False, cur_context)
        
        # Now, check if we match:
        if self._tokenise == True:
            senttext = self._toks_to_str(body)
            if self._deliminate_numbers:
                senttext = self._do_deliminate_numbers(senttext)
        else:
            senttext = self._tokenise.join([tok for (tok, pos, ts) in body])
        
        match = self._match.search(senttext)
        
        # If we do, then calculate attributes for the timex
        if match:
            
            if self._DEBUG:
                timex.comment = self.id
            
            try:
                if self._value_exp != None:
                    timex.value = eval(self._value_exp)
                
                if self._type_exp != None:
                    timex.type = eval(self._type_exp)
                
                if self._freq_exp != None:
                    timex.freq = eval(self._freq_exp)
                
                if self._quant_exp != None:
                    timex.quant = eval(self._quant_exp)
            
            except Exception as e:
                ternip.warn('Malformed rule expression', e)
            
            # Need to update current time context, if necessary
            return (True, cur_context)
        else:
            # Rule did not match
            return (False, cur_context)
