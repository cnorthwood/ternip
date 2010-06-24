#!/usr/bin/env python

from abstract_rule_engine import rule_load_error

class rule_block:
    
    def __init__(self, id, after, type, rules):
        """
        Create a rule block, with some ID, some restrictions on ordering, type
        (which is either 'until-success' or 'all', which means apply rules until
        one is successful, or apply all the rules regardless) and an initial
        ordered list of rules.
        
        For rules in blocks, ID and after are meaningless, they are run in
        sequence anyway. Blocks can be ordered like normal rules.
        """
        
        self.id = id
        self.after = after
        self._rules = rules
        if type == 'until-success' or type == 'all':
            self.type = type
        else:
            raise rule_load_error(id, "Invalid type, must be either 'until-success' or 'all'")
    
    def apply(self, thing):
        """
        Apply rules in this block, in order, to this 'thing', either until one
        rule is successful, or all rules have been applied.
        
        For recognition rules, 'thing' is the list of (token, POS, timexes), one
        sentence at a time (as per regular rules), and for normalisation rules,
        it is the tuple (before, inside, after, timex) tuple, one timex at a
        time.
        """
        
        block_success = False
        
        for rule in self._rules:
            (thing, success) = rule.apply(thing)
            if success:
                block_success = True
            if self.type == 'until-success' and success:
                break
        
        return (thing, block_success)