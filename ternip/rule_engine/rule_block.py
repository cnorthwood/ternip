from ternip.rule_engine.rule_engine import RuleLoadError

class RuleBlock(object):
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
            self._type = type
        else:
            raise RuleLoadError(id, "Invalid type, must be either 'until-success' or 'all'")