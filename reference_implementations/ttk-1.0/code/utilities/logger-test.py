"""

components.common_modules.logger.py
===================================

Simple logging code that write messages to a log file. It uses five
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
argument is optional, the default is to print errors and warnings only
(level 2). After initialization, the logger can be used from any
module by importing it and using its methods

   from utilities import logger
   logger.info(<string>)
   logger.debug(<string>)
   logger.warn(<string>)
   logger.error(<string>)

TODO:
- use a list of strings rather that one string, so we can avoid using
  string concatenation in the call to the logging methods
- sometimes the string is created using rather expensive operations,
  slowing down the program even if logging is barely used; may want to
  send an object with a print operation instead
   
"""

import os
import inspect

logger = None



class Logger:
    def __init__(self, filename, level=3):
        self.level = level
        self.html_file = open(filename + '.html', 'w')
        self.html_file.write("<html>\n<body>\n\n<table cellpadding=5>\n\n")
        
    def debug(self, string):
        if self.level > 3:
            self.log('DEBUG', string)

    def info(self, string):
        if self.level > 2:
            self.log('INFO', string)

    def warn(self, string):
        if self.level > 1:
            self.log('WARNING', string)

    def error(self, string):
        if self.level > 0:
            self.log('ERROR', string)

    def log(self, message_type, log_string):
        stack = inspect.stack()
        depth = len(stack) - 3
        frame = stack[2]
        path = frame[1]
        path_elements = path.split(os.sep)
        file = path_elements[-1]
        file = file.replace('.py','')
        line = str(frame[2])
        indent_string = '&nbsp;&nbsp;'
        indent_string = '&gt;'
        indent_string = '.'
        trace = depth * indent_string + file + '.' + frame[3] + '(' + line + ')'
        log_string = log_string.replace("<",'&lt;')
        log_string = log_string.replace(">",'&gt;')
        log_string = log_string.replace("\n",'<br/>')
        log_string = log_string.replace("\t",'&nbsp;&nbsp;&nbsp;')
        if message_type == 'WARNING' or message_type == 'ERROR':
            message_type = '<font color=red>' + message_type + '</font>'
        if message_type == 'INFO':
            message_type = '<font color=blue>' + message_type + '</font>'
        if message_type == 'DEBUG':
            message_type = '<font color=green>' + message_type + '</font>'
        self.html_file.write("\n<tr>\n")
        self.html_file.write("  <td valign=top>%s\n" % (message_type))
        self.html_file.write("  <td valign=top>%s\n" % (trace))
        self.html_file.write("  <td valign=top>%s\n" % (log_string))
        self.html_file.flush()


def initialize_logger(filename, level=3):
    """Initialize the logger on <filename>, default logging level is 2.
    Only initialize if logger has not been initialized yet."""
    global logger
    if not logger:
        logger = Logger(filename, level)#

