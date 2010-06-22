#!/usr/bin/env python

from collections import defaultdict
from glob import glob
import imp
import os.path

class abstract_rule_engine:
    
    def __init__(self):
        raise NotImplementedError
    
    def _load_rules(self, path):
        """
        Private function to actually do rule loading. Loads all files ending in
        .py as 'complex' rules (direct Python code), other rules are loaded
        using the documented rule format. For direct Python code, the rule must
        be a class called 'rule'.
        """
        
        rules = []
        errors = []
        
        # First load simple rules
        for file in glob(os.path.join(path, '*.rule')):
            # don't bail out after one load failure, load them all and report
            # all at once
            try:
                rules.append(self._load_rule(file))
            except rule_load_error as e:
                errors.append(e)
        
        # now bail out
        if len(errors) > 0:
            raise rule_load_errors(errors)
        
        # Then complex rules
        for file in glob(os.path.join(path, '*.pyrule')):
            (dir, modname) = os.path.split(file)
            modname = modname[:-7]
            rules.append(imp.load_source(modname, file).rule())
        
        self._rules = rules
    
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
        self._errors = errors
    
    def __str__(self):
        return '\n'.join([str(error) for error in self._errors])