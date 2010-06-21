#!/usr/bin/env python

class timex:
    """ A temporal expression """
    
    def __init__(self,
                 type  = None,
                 value = None):
        """ Initialise a timex object with some optional values """
        self.type = type
        self.value = value