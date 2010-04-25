import os
import re

from ttk_path import TTK_ROOT
#TTK_ROOT = '/home/j/llc/arum/projects/timeml/blinker/ttk/code'

DIR_SYNTACTIC_RULES = os.path.join(TTK_ROOT, 'library', 'blinker', 'syntactic_rules')
DIR_LEXICAL_RULES = os.path.join(TTK_ROOT, 'library', 'blinker', 'lexical_rules')

SYNTACTIC_RULES_FILE_1 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.1.txt')
SYNTACTIC_RULES_FILE_2 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.2.txt')
SYNTACTIC_RULES_FILE_3 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.3.txt')
SYNTACTIC_RULES_FILE_4 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.4.txt')
SYNTACTIC_RULES_FILE_5 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.5.txt')
SYNTACTIC_RULES_FILE_6 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.6.txt')
SYNTACTIC_RULES_FILE_7 = os.path.join(DIR_SYNTACTIC_RULES, 'syntactic.rules.7.txt')

re_rule_header = re.compile('ruleNum=(\d+)-(\d+)')
re_attribute = re.compile('(.*)=(.*)')


class BlinkerRuleDictionary:

    """Convenience class to store the Blinker rules. Doesn't do a
    lot more than that at this point."""

    def __init__(self):
        self.rules = {}
        self.rules[1] = read_syntactic_rules(SYNTACTIC_RULES_FILE_1)
        self.rules[2] = read_syntactic_rules(SYNTACTIC_RULES_FILE_2)
        self.rules[3] = read_syntactic_rules(SYNTACTIC_RULES_FILE_3)
        self.rules[4] = read_syntactic_rules(SYNTACTIC_RULES_FILE_4)
        self.rules[5] = read_syntactic_rules(SYNTACTIC_RULES_FILE_5)
        self.rules[6] = read_syntactic_rules(SYNTACTIC_RULES_FILE_6)
        self.rules[7] = read_syntactic_rules(SYNTACTIC_RULES_FILE_7)

    def __getitem__(self, key):
        return self.rules[key]

    def pp(self):
        for i in range(1,7):
            print "\nBLINKER RULES TYPE %d:\n\n" % i
            for rule in self.rules[i]:
                rule.pp()

    def pp_ruletype(self, i):
        for rule in self.rules[i]:
            rule.pp()
        
                    
    
class BlinkerRule:

    """Implements the Blinker rule object."""
    
    def __init__(self, rule_type, rule_number):
        self.type = rule_type
        self.rule_number = rule_number
        self.id = "%s-%s" % (rule_type, rule_number)
        self.attrs = {}
        
    def set_attribute(self, attr, val):
        self.attrs[attr] = val

    def get_attribute(self, attr):
        return self.attrs.get(attr)

    def __str__(self):
        return '<BlinkerRule ' + self.id + '>'
    
    def pp(self):
        print "<BlinkerRule %s>" % self.id
        for attr, val in self.attrs.items():
            print "  %s=\"%s\"" % (attr, val)



def read_syntactic_rules(rule_file):
    
    """Read and return all the rules in the given rule file. All
    syntactic rule files need to adhere to the same syntax."""

    rules = []
    current_rule = None
    file = open(rule_file,'r')

    for line in file.readlines():
        # skip comments and empty lines
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        # find rule header
        match = re_rule_header.search(line)
        if match:
            if current_rule:
                # store previous rule and reset it
                rules.append(current_rule)
                current_rule = None
            (rule_type, rule_number) = match.group(1,2)
            current_rule = BlinkerRule(rule_type, rule_number)
            continue
        # find attributes
        match = re_attribute.search(line)
        if match:
            (att, val) = match.group(1,2)
            att = att.strip()
            val = val.strip()
            # value is now always a list of strings
            if val[0] != '(':
                val = [val]
            else:
                val = str.split(val[1:-1], '|')
            current_rule.set_attribute(att, val)
            continue

    # do not forget the very last rule
    if current_rule:
        rules.append(current_rule)

    return rules


