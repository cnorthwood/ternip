import string

class FeatureRule:

    def __init__(self, rule, chunk): 
        self.rule = rule
        self.chunk = chunk

        """Info contained in each RULE position:
           ------------------------------------
        row 1.a) node.name               None or 2-place tuple (operator, 2nd elem)
        row 2.a) node.items[0].word   None or 2-place tuple (operator, 2nd elem)
              b) node.items[0].pos    None or 2-place tuple (operator, 2nd elem)
        row 3.a) node.items[1].word None or 2-place tuple (operator, 2nd elem)
              b) node.items[1].pos  None or 2-place tuple (operator, 2nd elem)
        row 4.a) node.items[2].word None or 2-place tuple (operator, 2nd elem)
              b) node.items[2].pos  None or 2-place tuple (operator, 2nd elem)
        row 5.a) node.items[3].word   None or 2-place tuple (operator, 2nd elem)
              b) node.items[3].pos    None or 2-place tuple (operator, 2nd elem)
        row 6.Grammar feature to return
           """

    def applyRule1pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0)):
            return self.rule[-1]
        else: return 0

    def applyRule2pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1)):
            return self.rule[-1]
        else: return 0

    def applyRule3pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1) and
            self.matchWord(self.rule[5], 2) and
            self.matchPos(self.rule[6], 2)):
            return self.rule[-1]
        else: return 0

    def applyRule4pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1) and
            self.matchWord(self.rule[5], 2) and
            self.matchPos(self.rule[6], 2) and
            self.matchWord(self.rule[7], 3) and
            self.matchPos(self.rule[8], 3)):
            return self.rule[-1]
        else: return 0

    def applyRule5pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1) and
            self.matchWord(self.rule[5], 2) and
            self.matchPos(self.rule[6], 2) and
            self.matchWord(self.rule[7], 3) and
            self.matchPos(self.rule[8], 3) and
            self.matchWord(self.rule[9], 4) and
            self.matchPos(self.rule[10], 4)):
            return self.rule[-1]
        else: return 0

    def applyRule6pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1) and
            self.matchWord(self.rule[5], 2) and
            self.matchPos(self.rule[6], 2) and
            self.matchWord(self.rule[7], 3) and
            self.matchPos(self.rule[8], 3) and
            self.matchWord(self.rule[9], 4) and
            self.matchPos(self.rule[10], 4) and
            self.matchWord(self.rule[11], 5) and
            self.matchPos(self.rule[12], 5)):
            return self.rule[-1]
        else: return 0

    def applyRule7pos(self):
        if (self.matchWord(self.rule[1], 0) and
            self.matchPos(self.rule[2], 0) and
            self.matchWord(self.rule[3], 1) and
            self.matchPos(self.rule[4], 1) and
            self.matchWord(self.rule[5], 2) and
            self.matchPos(self.rule[6], 2) and
            self.matchWord(self.rule[7], 3) and
            self.matchPos(self.rule[8], 3) and
            self.matchWord(self.rule[9], 4) and
            self.matchPos(self.rule[10], 4) and
            self.matchWord(self.rule[11], 5) and
            self.matchPos(self.rule[12], 5) and
            self.matchWord(self.rule[13], 6) and
            self.matchPos(self.rule[14], 6)):
            return self.rule[-1]
        else: return 0

#    def matchNodeName(self):
#        # if no info in self.rule[0], consider the rule match
#        if not self.rule[0]: return 1
#        else: return self.checkItem(self.chunkName, self.rule[0])

    def matchWord(self, ruleInfo, i):
        # if no ruleInfo, consider the rule match
        if not ruleInfo: return 1
        else: return self.checkItem(self.chunk[i].getText(), ruleInfo)

    def matchPos(self, ruleInfo, i):
        # if no ruleInfo, consider the rule match
        if not ruleInfo: return 1
        else: return self.checkItem(self.chunk[i].pos, ruleInfo)

    def checkItem(self, elem, tuple):
        op = " " + string.strip(tuple[0]) + " "
        elem2 = tuple[1]
        if op == " == " and elem2 == 'None':
            if not elem: return 1
            else: return 0
        elif op == " != " and elem2 == 'None':
            if not elem: return 0
            else: return 1
        else: return eval(string.lower('elem') + op + 'elem2')



