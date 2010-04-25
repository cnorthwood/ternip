"""

Added this so the treetaggerwrapper will run on my old Python. It
requires logging (with the warning, error and info functionality
below), which is new in version 2.3.

"""

def getLogger(string):
    return Logger()

class Logger:
    def warning(self,string,more=None): pass
    def info(self,string,more=None): pass
    def error(self,string,more=None): pass
