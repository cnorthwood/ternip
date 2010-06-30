#!/usr/bin/env python

class timex:
    """ A temporal expression """
    
    def __init__(self,
                 type  = None,
                 value = None,
                 id    = None):
        """ Initialise a timex object with some optional values """
        self.type = type
        self.value = value
        self.id = id

def add_timex_ids(sents):
    """
    Goes through all TIMEXs and adds IDs to the timexes, if they don't exist
    already. Each ID is an integer, and is guaranteed to be unique in this set
    of timexes.
    """
    pass
    # go through all timexes and collect current IDs
    # start an incrementing counter, then skip any IDs already existing