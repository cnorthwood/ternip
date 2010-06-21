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
        be a class called 'rule'
        """
        
        rules = []
        
        # First load simple rules
        for file in glob(os.path.join(path, '*.rule')):
            rules.append(self._load_rule(file))
        
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
        
        for line in lines:
            [key, value] = line.split(':', 1)
            d[key].append(value.strip())
        
        return d