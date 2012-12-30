from ternip.rule_engine.rule_block import RuleBlock

class RecognitionRuleBlock(RuleBlock):
    """
    A block of recognition rules
    """

    def apply(self, sent):
        """
        Apply rules in this block, in order, to this sentence, either until one
        rule is successful, or all rules have been applied.
        """

        block_success = False

        for rule in self._rules:
            (sent, success) = rule.apply(sent)
            if success:
                block_success = True
            if self._type == 'until-success' and success:
                break

        return sent, block_success
