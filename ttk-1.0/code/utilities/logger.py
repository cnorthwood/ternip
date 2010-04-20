"""Simple logging code that write messages to a log file. It uses five
levels:

   Level 0: no messages 
   Level 1: errors 
   Level 2: errors and warnings
   Level 3: errors and warnings and info
   Level 4: errors and warnings and info and debugging

Initialize the logger, typically from the main script, as follows

   import utilities.logger as logger
   logger.initialize_logger(<filename>, <level>)

This will open for writing a file <filename>.html. The <level>
argument is optional, the default is to print info, errors and warnings 
(level 3). After initialization, the logger can be used from any
module by importing it and using its methods:

   from utilities import logger
   logger.info(<string>)
   logger.debug(<string>)
   logger.warn(<string>)
   logger.error(<string>)

In addition, there is one method that writes to the lo no matter what
the level:
    
   logger.write(<string>)

Finally, it provides two convenience method that print directly to the
standard output:

   logger.out(*args)
   logger.outnl()

The first one writes the string representation of all arguments to the
standard output and the second writes a white line. Printing to the standard output can be turned on and off with

   set_stdout_printing(Boolean)

"""

# TODO:
# - use a list of strings rather that one string, so we can avoid using
#   string concatenation in the call to the logging methods
# - sometimes the string is created using rather expensive operations,
#   slowing down the program even if logging is barely used; may want to
#   send an object with a print operation instead
   

import os
import sys
import inspect

logger = None

STDOUT_PRINTING = True

class Logger:

    """The Logger class, has no other function than to store the logging
    level and the log file."""
    
    def __init__(self, filename, level=3):
        """Set logging level and the log file."""
        self.level = level
        self.html_file = open(filename + '.html', 'w')
        self.html_file.write("<html>\n<body>\n\n<table cellpadding=5>\n\n")
        
def initialize_logger(filename, level=3):
    """Initialize the logger on <filename>, default logging level is 2.
    Only initialize if logger has not been initialized yet."""
    global logger
    if not logger:
        logger = Logger(filename, level)

def debug(string):
    """Print a debugging message to the log file."""
    if logger.level > 3:
        _log('DEBUG', string)

def info(string):
    """Print an info string to the log file."""
    if logger.level > 2:
        _log('INFO', string)

def warn(string):
    """Print a warning to the log file."""
    if logger.level > 1:
        _log('WARNING', string)

def error(string):
    """Print an error to the log file, also print it to standard error."""
    if logger.level > 0:
        sys.stderr.write('ERROR: ' + string + "\n")
        _log('ERROR', string)

def write(string):
    """Print a string to the log file, no matter what the logging
    level. This will be printed as an INFO string"""
    _log('INFO', string)

def _log(message_type, log_string):
    """Inspect the stack to find the execution level and the calling
    function, then write the message to the log."""
    stack = inspect.stack()
    depth = len(stack) - 3
    frame = stack[2]
    path = frame[1]
    path_elements = path.split(os.sep)
    file = path_elements[-1]
    file = file.replace('.py','')
    line = str(frame[2])
    indent_string = '.'
    trace = depth * indent_string + file + '.' + frame[3] + '(' + line + ')'
    log_string = log_string.replace("<",'&lt;')
    log_string = log_string.replace(">",'&gt;')
    log_string = log_string.replace("\n",'<br/>')
    log_string = log_string.replace("\t",'&nbsp;&nbsp;&nbsp;')
    if message_type == 'ERROR':
        message_type = '<font color=red>' + message_type + '</font>'
    elif message_type == 'WARNING':
        message_type = '<font color=green>' + message_type + '</font>'
    elif message_type == 'INFO':
        message_type = '<font color=blue>' + message_type + '</font>'
    #if message_type == 'DEBUG':
    #    message_type = '<font color=green>' + message_type + '</font>'
    logger.html_file.write("\n<tr>\n")
    logger.html_file.write("  <td valign=top>%s\n" % (message_type))
    logger.html_file.write("  <td valign=top>%s\n" % (trace))
    logger.html_file.write("  <td valign=top>%s\n" % (log_string))
    logger.html_file.flush()


def set_stdout_printing(Boolean):
    """When this function is called, the out and outnl methods will
    not print to the output. """
    
    global STDOUT_PRINTING
    STDOUT_PRINTING = Boolean

    
def out(*args):
    """Method to write to standard output rather than the html
    file. Intended for quick and dirty debugging that should not be
    left in the code. Using this method makes it easier to later
    remove the debugging code (as opposed to using print statements
    right in the text). Works well only for one-liners."""
    if not STDOUT_PRINTING:
        return
    stack = inspect.stack()
    depth = len(stack) - 3
    frame = stack[1]
    path = frame[1]
    function = frame[3]
    path_elements = path.split(os.sep)
    file = path_elements[-1]
    file = file.replace('.py','')
    #line = str(frame[2])
    prefix = 'LOG (' + str(depth) + ') [' + file + '.' + function + ']'
    print prefix + ' ',
    for arg in args:
        print arg,
    print
    
def outnl():
    if not STDOUT_PRINTING:
        return
    print
