#!/usr/bin/env python

from rule_engine import rule_engine, rule_load_error, rule_load_errors
from normalisation_rule import normalisation_rule
from normalisation_rule_block import normalisation_rule_block
import re

class normalisation_rule_engine(rule_engine):
    """
    A class which does normalisation using a rule engine
    
    Complex rules must have a string member called 'id', which is used for
    after ordering, a list of strings called 'after' (which can be an empty
    list) which consists of IDs that must have run before this rule.
    Additionally, a function called 'apply' which takes a list of
    (token, pos, timexes) tuples and returns them in the same form with
    potentially modified timexes.
    """
    
    _block_type = normalisation_rule_block
    
    def _load_rule(self, filename, rulelines):
        """
        Load a 'simple' normalisation rule
        """
        
        # get key/value dictionaries
        d = self._parse_rule(filename, rulelines)
        
        # Set defaults
        type          = None
        match         = None
        id            = filename
        value         = None
        guards        = []
        before_guards = []
        after_guards  = []
        after         = []
        tokenise      = True
        deliminate_numbers = False
        change_type   = None
        freq          = None
        quant         = None
        
        for key in d:
            
            # Only one 'Type' field allowed
            if key == 'type':
                if (len(d[key]) != 1):
                    raise rule_load_error(filename, "Too many 'Type' field")
                else:
                    type = d[key][0]
            
            # Only one 'Match' field allowed
            elif key == 'match':
                if (len(d[key]) != 1):
                    raise rule_load_error(filename, "There must be exactly 1 'Match' field")
                else:
                    match = d[key][0]
            
            # No more than one ID key allowed
            elif key == 'id':
                if (len(d[key]) == 1):
                    id = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'ID' fields")
            
            # No more than one Value key allowed
            elif key == 'value':
                if (len(d[key]) == 1):
                    value = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Value' fields")
            
            # No more than one Change-Type key allowed
            elif key == 'change-type':
                if (len(d[key]) == 1):
                    change_type = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Change-Type' fields")
            
            # No more than one Freq key allowed
            elif key == 'freq':
                if (len(d[key]) == 1):
                    freq = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Freq' fields")
            
            # No more than one Quant key allowed
            elif key == 'quant':
                if (len(d[key]) == 1):
                    quant = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Quant' fields")
            
            # set optional fields
            elif key == 'guard':
                guards = d[key]
            elif key == 'after':
                after = d[key]
            elif key == 'before-guard':
                before_guards = d[key]
            elif key == 'after-guard':
                after_guards = d[key]
            
            elif key == 'tokenise':
                if (len(d[key]) == 1):
                    tokenise = d[key][0].lower()
                    if tokenise == 'true':
                        tokenise = True
                    elif tokenise == 'space':
                        tokenise = ' '
                    elif tokenise == 'null':
                        tokenise = ''
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Tokenise' fields")
            
            # Deliminate-Numbers is an optional field, defaulting to False, which
            # accepts either true or false (case-insensitive) as values
            elif key == 'deliminate-numbers':
                if (len(d[key]) == 1):
                    deliminate_numbers = d[key][0].lower()
                    if deliminate_numbers == 'true':
                        deliminate_numbers = True
                    elif deliminate_numbers == 'false':
                        deliminate_numbers = False
                    else:
                        raise rule_load_error(filename, "Deliminate-Numbers must be either 'True' or 'False'")
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Deliminate-Numbers' fields")
            
            # error on unknown fields
            else:
                raise rule_load_error(filename, "Unknown field '" + key + "'")
        
        if match is None:
            raise rule_load_error(filename, "'Match' is a compulsory field")
        
        if deliminate_numbers and tokenise != True:
            raise rule_load_error(filename, "'Deliminate-Numbers' can not be set if Tokenise is")
        
        # Guard against any RE errors
        try:
            return normalisation_rule(match, type, id, value, change_type, freq, quant, guards, after_guards, before_guards, after, tokenise, deliminate_numbers)
        except re.error as e:
            raise rule_load_error(filename, "Malformed regular expression: " + str(e))
    
    def annotate(self, sents, dct):
        """
        This annotates all the timexes in the sents. dct means the document
        creation time (in the TIDES-modified ISO8601 format), which some rules
        may use to determine a context.
        """
        
        # Current context
        context_dt = dct
        
        # Timex's can't span sentence boundaries, but rules can alter the
        # text context for later sentences, so consider each sentence in turn,
        # updating the context if need be.
        for sent in sents:
            
            # Now collect all timexes in this sentence
            timexes = set()
            for (w, pos, ts) in sent:
                for t in ts:
                    timexes.add(t)
            
            # Now annotate each timex
            for timex in timexes:
                
                # First find the token extent of this timex
                tfound = False
                i = 0
                for (w, pos, ts) in sent:
                    if timex in ts:
                        if tfound == False:
                            tfound = True
                            ei = i
                        ej = i + 1
                    i += 1
                
                # Slice up into different extents
                before = sent[:ei]
                body = sent[ei:ej]
                after = sent[ej:]
                
                # Now run the rules
                rules_run = set()
                rules_to_run = set(self._rules)
                
                # Apply rules until all rules have been applied
                while rules_to_run:
                    for rule in rules_to_run.copy():
                        
                        # Check that if 'after' is defined, the rules we must run
                        # after have run
                        after_ok = True
                        for aid in rule.after:
                            if aid not in rules_run:
                                after_ok = False
                        
                        # Apply this rule, and update our states of rules waiting to
                        # run and rules that have been run
                        if after_ok:
                            (success, context_dt) = rule.apply(timex, context_dt, dct, body, before, after)
                            rules_run.add(rule.id)
                            rules_to_run.remove(rule)