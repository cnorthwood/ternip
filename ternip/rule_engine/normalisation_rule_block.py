#!/usr/bin/env python

import rule_block

class normalisation_rule_block(rule_block.rule_block):
    """
    A block of normalisation rules
    """
    
    def apply(self, timex, body, before, after):
        """
        Apply rules in this block, in order, to this sentence, either until one
        rule is successful, or all rules have been applied.
        """
        
        block_success = False
        
        for rule in self._rules:
            success = rule.apply(timex, body, before, after)
            if success:
                block_success = True
            if self._type == 'until-success' and success:
                break
        
        return block_success