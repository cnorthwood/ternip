#!/usr/bin/env python

from rule_engine import rule_engine, rule_load_error, rule_load_errors
from recognition_rule import recognition_rule
from recognition_rule_block import recognition_rule_block
import re

class recognition_rule_engine(rule_engine):
    """
    A class which does recognition using a rule engine
    
    Complex rules must have a string member called 'id', which is used for
    after ordering, a list of strings called 'after' (which can be an empty
    list) which consists of IDs that must have run before this rule.
    Additionally, a function called 'apply' which takes a list of
    (token, pos, timexes) tuples and returns them in the same form with
    potentially modified timexes.
    """
    
    _block_type = recognition_rule_block
    
    def _load_rule(self, filename, rulelines):
        """
        Load a 'simple' recognition rule
        """
        
        # get key/value dictionaries
        d = self._parse_rule(filename, rulelines)
        
        # Set defaults
        type               = None
        match              = None
        id                 = filename
        squelch            = False
        guards             = []
        before_guards      = []
        after_guards       = []
        after              = []
        case_sensitive     = False
        deliminate_numbers = False
        
        for key in d:
            
            # Only one 'Type field allowed
            if key == 'type':
                if (len(d[key]) != 1):
                    raise rule_load_error(filename, "There must be exactly 1 'Type' field")
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
            
            # Squelch is an optional field, defaulting to False, which accepts
            # either true or false (case-insensitive) as values
            elif key == 'squelch':
                if (len(d[key]) == 1):
                    squelch = d[key][0].lower()
                    if squelch == 'true':
                        squelch = True
                    elif squelch == 'false':
                        squelch = False
                    else:
                        raise rule_load_error(filename, "Squelch must be either 'True' or 'False'")
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Squelch' fields")
            
            # Case-sensitive is an optional field, defaulting to False, which
            # accepts either true or false (case-insensitive) as values
            elif key == 'case-sensitive':
                if (len(d[key]) == 1):
                    case_sensitive = d[key][0].lower()
                    if case_sensitive == 'true':
                        case_sensitive = True
                    elif case_sensitive == 'false':
                        case_sensitive = False
                    else:
                        raise rule_load_error(filename, "Case-Sensitive must be either 'True' or 'False'")
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Case-Sensitive' fields")
            
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
            
            # set optional fields
            elif key == 'guard':
                guards = d[key]
            elif key == 'after':
                after = d[key]
            elif key == 'before-guard':
                before_guards = d[key]
            elif key == 'after-guard':
                after_guards = d[key]
            
            # error on unknown fields
            else:
                raise rule_load_error(filename, "Unknown field '" + key + "'")
        
        if type is None:
            raise rule_load_error(filename, "'Type' is a compulsory field")
        
        if match is None:
            raise rule_load_error(filename, "'Match' is a compulsory field")
        
        # Guard against any RE errors
        try:
            return recognition_rule(match, type, id, guards, after_guards, before_guards, after, squelch, case_sensitive, deliminate_numbers)
        except re.error as e:
            raise rule_load_error(filename, "Malformed regular expression: " + str(e))
        except (SyntaxError, ValueError) as e:
            raise rule_load_error(filename, "Malformed Python expression: " + str(e))
    
    def tag(self, sents):
        """
        This function actually does word recognition. It expects content to be
        split into tokenised, POS tagged, sentences. i.e., a list of lists of
        tuples ([[(token, pos-tag, timexes), ...], ...]). Rules are applied one
        at a time.
        
        What is returned is in the same form, except the token tuples contain a
        third element consisting of the set of timexes associated with that
        token.
        """
        
        # Apply rules on one sentence at a time
        r = []
        for sent in sents:
            
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
                        (sent, success) = rule.apply(sent)
                        rules_run.add(rule.id)
                        rules_to_run.remove(rule)
            
            r.append(sent)
        
        return r