import sys
import traceback
import rule_engine
import os.path

# Avoid messy imports
from timex import *

no_NLTK = False

def recogniser():
    """
    Returns the default recogniser, already configured.
    """
    r = rule_engine.recognition_rule_engine()
    r.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'recognition'))
    return r

def normaliser():
    """
    Returns default normaliser, already configured.
    """
    n = rule_engine.normalisation_rule_engine()
    n.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'normalisation'))
    return n