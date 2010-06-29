#!/usr/bin/env python

from abstract_rule_engine import abstract_rule_engine, rule_load_error, rule_load_errors
from normalisation_rule import normalisation_rule
from normalisation_rule_block import normalisation_rule_block
import re

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
            
            # No more than one Value key allowed
            elif key == 'value':
                if (len(d[key]) == 1):
                    value = d[key][0]
                elif (len(d[key]) > 1):
                    raise rule_load_error(filename, "Too many 'Value' fields")
            
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
            return normalisation_rule(match, type, id, value, guards, after_guards, before_guards, after)
        except re.error as e:
            raise rule_load_error(filename, "Malformed regular expression: " + str(e))
    
    def annotate(self, sents):
        """
        This annotates all the timexes 
        """
        
        pass