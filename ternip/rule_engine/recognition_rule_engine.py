#!/usr/bin/env python

from abstract_rule_engine import abstract_rule_engine, rule_load_error, rule_load_errors
from recognition_rule import recognition_rule
import os.path

class recognition_rule_engine(abstract_rule_engine):
    """
    A class which does recognition using a rule engine
    
    Complex rules must have a string member called 'id', which is used for
    after ordering, a list of strings called 'after' (which can be an empty
    list) which consists of IDs that must have run before this rule.
    Additionally, a function called 'apply' which takes a list of
    (token, pos, timexes) tuples and returns them in the same form with
    potentially modified timexes.
    """
    
    def _load_rule(self, filename, rulelines):
        """
        Load a 'simple' recognition rule
        """
        
        # get key/value dictionaries
        d = self._parse_rule(filename, rulelines)
        
        # 'Type' is a compulsory field
        if (len(d['type']) != 1):
            raise rule_load_error(filename, "There must be exactly 1 'Type' field")
        else:
            type = d['type'][0]
        
        # 'Match' is a compulsory field
        if (len(d['match']) != 1):
            raise rule_load_error(filename, "There must be exactly 1 'Match' field")
        else:
            match = d['match'][0]
        
        # ID is an optional field, which can only exist once
        if (len(d['id']) == 1):
            id = d['id'][0]
        elif (len(d['id']) > 1):
            raise rule_load_error(filename, "Too many 'ID' fields")
        else:
            id = filename
        
        # Squelch is an optional field, defaulting to False, which accepts
        # either true or false (case-insensitive) as values
        if (len(d['squelch']) == 1):
            squelch = d['squelch'][0].lower()
            if squelch == 'true':
                squelch = True
            elif squelch == 'false':
                squelch = False
            else:
                raise rule_load_error(filename, "Squelch must be either 'True' or 'False'")
        elif (len(d['squelch']) > 1):
            raise rule_load_error(filename, "Too many 'Squelch' fields")
        else:
            squelch = False
        
        # 'After' and 'Guards' are optional, possibly multi-valued, fields
        return recognition_rule(match, type, id, d['guard'], d['after'], squelch)
    
    def tag(self, sents):
        """
        This function actually does word recognition. It expects content to be
        split into tokenised, POS tagged, sentences. i.e., a list of lists of
        tuples ([[(token, pos-tag), ...], ...]). Rules are applied one at a
        time.
        
        What is returned is in the same form, except the token tuples contain a
        third element consisting of the set of timexes associated with that
        token.
        """
        
        # Apply rules on one sentence at a time
        r = []
        for sent in sents:
            
            # Add the element to hold Timexes
            sent = [(token, pos, set()) for (token, pos) in sent]
            
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