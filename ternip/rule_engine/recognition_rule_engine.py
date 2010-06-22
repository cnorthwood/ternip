#!/usr/bin/env python

from abstract_rule_engine import abstract_rule_engine, rule_load_error, rule_load_errors
import recognition_rule
import os.path

class recognition_rule_engine(abstract_rule_engine):
    """
    A class which does recognition using a rule engine
    """
    
    def __init__(self, rule_location = 'rules/recognition/'):
        """
        Initialises this rule engine. Uses the rules located in the supplied
        rule location, which defaults to what is distributed with TERNIP.
        """
        
        # Load rules
        self._load_rules(os.path.normpath(rule_location))
        
        # Check that all the IDs specified in 'After' keys actually exist
        errors = []
        
        # First, get all rule IDs and then all IDs mentioned as after IDs
        rule_ids = set([rule.id for rule in self._rules])
        after_ids = set()
        for rule in self._rules:
            after_ids |= rule.after
        
        # Now check each referred to after ID exists
        for id in after_ids:
            if id not in rule_ids:
                errors.append(rule_load_error(rule.filename, 'Unknown ID specified in after'))
        
        # Bulk raise errors
        if len(errors) > 0:
            raise rule_load_errors(errors)
    
    def _load_rule(self, filename):
        """
        Load a 'simple' recognition rule
        """
        
        # get key/value dictionaries
        with open(filename) as fd:
            d = self._parse_rule(fd.readlines())
        
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
            id = None
        
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
        else:
            squelch = False
        
        # 'After' and 'Guards' are optional, possibly multi-valued, fields
        return recognition_rule(match, type, d['guards'], id, d['after'], squelch)
    
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
            rules_to_run = set([self._rules])
            
            # Apply rules until all rules have been applied
            while rules_to_run:
                for rule in rules_to_run.copy():
                    
                    # Check that if 'after' is defined, the rules we must run
                    # after have run
                    after_ok = True
                    for aid in rule.after:
                        if aid not in rules_run:
                            after_ok = False
                    
                    # Apply this rule, and update our rules to run and run rules
                    # states
                    if after_ok:
                        sent = rule.apply(sent)
                        rules_run.add(rule.id)
                        rules_to_run.remove(rule)
            
            r.append(sent)
        
        return r