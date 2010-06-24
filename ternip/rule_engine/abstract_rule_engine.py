#!/usr/bin/env python

from collections import defaultdict
from glob import glob
import imp
import os.path

class abstract_rule_engine:
    
    def __init__(self):
        self.rules = []
    
    def load_rules(self, path):
        """
        Do rule loading. Loads all files ending in .py as 'complex' rules
        (direct Python code), other rules are loaded using the documented rule
        format. For direct Python code, the rule must be a class called 'rule'.
        """
        
        errors = []
        
        # First load simple rules
        for file in glob(os.path.join(path, '*.rule')):
            # don't bail out after one load failure, load them all and report
            # all at once
            try:
                self.rules.append(self._load_rule(file))
            except rule_load_error as e:
                errors.append(e)
        
        # Then complex rules
        for file in glob(os.path.join(path, '*.pyrule')):
            (dir, modname) = os.path.split(file)
            modname = modname[:-7]
            self.rules.append(imp.load_source(modname, file).rule())
        
        # Now, check the rule's we've just loaded for consistency
        # First, get all rule IDs and then all IDs mentioned as after IDs
        rule_ids = dict()
        for rule in self.rules:
            if rule.id in rule_ids:
                errors.append(rule_load_error(rule.id, 'Duplicate ID!'))
            else:
                rule_ids[rule.id] = rule
        
        # Now check each referred to after ID exists
        for rule in self.rules:
            circular_check = True
            for after in rule.after:
                if after not in rule_ids:
                    errors.append(rule_load_error(rule.id, 'Reference made to non-existant rule'))
                    # If this happens, don't check for circular references, as
                    # there are dangling references and it causes errors
                    circular_check = False
            
            # and check each rule for any circular references
            if circular_check and self._circular_check(rule.id, rule, rule_ids):
                errors.append(rule_load_error(rule.id, 'Circular dependency - rule must run after itself'))
        
        # Bulk raise any errors that occurred
        if len(errors) > 0:
            raise rule_load_errors(errors)
    
    def _parse_rule(self, rulelines):
        """
        Private function that takes the lines of a 'simple' rule file, parses
        the key/value pairs, and then returns them as a dictionary. Does no kind
        of type or validity checking, and assumes that everything can have
        multiple values. It's then the caller's responsibility to check what
        gets returned.
        """
        
        d = defaultdict(list)
        
        for line in rulelines:
            [key, value] = line.split(':', 1)
            d[key.lower()].append(value.strip())
        
        return d
    
    def _circular_check(self, search_for, rule, rule_ids):
        """ Check for any circular references """
        if search_for in rule.after:
            return True
        else:
            for after in rule.after:
                res = self._circular_check(search_for, rule_ids[after], rule_ids)
                if res:
                    return True
            return False

class rule_load_error(Exception):
    """
    Error for when a rule fails to load
    """
    
    def __init__(self, filename, errorstr):
        self._filename = filename
        self._errorstr = errorstr
    
    def __str__(self):
        return 'Error when loading rule ' + self._filename + ': ' + self._errorstr

class rule_load_errors(Exception):
    """
    Error which bundles multiple RuleLoadError's together. Allows for delayed
    exit on multiple load errors
    """
    
    def __init__(self, errors):
        self.errors = errors
    
    def __str__(self):
        return '\n'.join([str(error) for error in self.errors])