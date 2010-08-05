import sys
import traceback
import rule_engine

# Avoid messy imports
from timex import *

# Set up non-fatal error reporting

def _warn(message, e):
    """
    A default warning function, which prints the error information to stdout
    """
    
    print >>sys.stderr, "TERNIP: WARNING:", message
    traceback.print_exc(file=sys.stderr)
    print >>sys.stderr

warn = _warn
"""
Warning handler. Change me to have warnings handled by your own function.

e.g., ternip.warn = my_error_handler
"""

def recogniser():
    """
    Returns the default recogniser, already configured.
    """
    r = rule_engine.recognition_rule_engine()
    r.load_rules('rules/recognition/')
    return r

def normaliser():
    """
    Returns default normaliser, already configured.
    """
    n = rule_engine.normalisation_rule_engine()
    n.load_rules('rules/normalisation/')
    return n