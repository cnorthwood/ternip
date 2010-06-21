#!/usr/bin/env python

import abstract_rule_engine
import recognition_rule
import os.path

class recognition_rule_engine(ternip.rule_engine.abstract_rule_engine.abstract_rule_engine):
    """
    A class which does recognition using a rule engine
    """
    
    def __init__(self, rule_location = 'rules/recognition/'):
        """
        Initialises this rule engine. Uses the rules located in the supplied
        rule location, which defaults to what is distributed with TERNIP.
        """
        self._load_rules(os.path.normpath(rule_location))
    
    def _load_rule(self, filename):
        """
        Load a 'simple' recognition rule
        """
        with open(filename) as fd:
            d = self._parse_rule(fd.readlines())
        
        if (len(d['type']) != 1):
            # do some error here
            pass
        else:
            type = d['type'][0]
        
        if (len(d['match']) != 1):
            # do some error here
            pass
        else:
            match = d['match'][0]
        
        if (len(d['id']) == 1):
            id = d['id'][0]
        else:
            id = None
        
        if (len(d['after']) == 1):
            after = d['after'][0]
        else:
            after = None
        
        if (len(d['squelch']) == 1):
            squelch = d['squelch'][0].lower()
            if squelch == 'true':
                squelch = True
            elif squelch == 'false':
                squelch = False
            else:
                # throw some error
                pass
        else:
            # throw some error
            pass
        
        return recognition_rule(match, type, d['guards'], id, after, squelch)