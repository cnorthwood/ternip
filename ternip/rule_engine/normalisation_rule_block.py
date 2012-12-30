from ternip.rule_engine.rule_block import RuleBlock

class NormalisationRuleBlock(RuleBlock):
    """
    A block of normalisation rules
    """

    def apply(self, timex, cur_context, dct, body, before, after):
        """
        Apply rules in this block, in order, to this sentence, either until one
        rule is successful, or all rules have been applied.
        """

        block_success = False

        for rule in self._rules:
            (success, cur_context) = rule.apply(timex, cur_context, dct, body, before, after)
            if success:
                block_success = True
            if self._type == 'until-success' and success:
                break

        return block_success, cur_context
