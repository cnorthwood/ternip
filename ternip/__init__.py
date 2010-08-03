import sys
import traceback

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