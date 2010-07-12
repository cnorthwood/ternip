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

def add_timex_ids(ts):
    """
    Goes through all TIMEXs and adds IDs to the timexes, if they don't exist
    already. Each ID is an integer, and is guaranteed to be unique in this set
    of timexes.
    """
    # go through all timexes and collect current IDs
    ids = set([t.id for t in ts])
    
    # start an incrementing counter, then skip any IDs that already exist
    i = 1
    for t in ts:
        # Only add IDs to Timexes which currently have none
        if t.id is None:
            # Find next free ID
            while i in ids:
                i += 1
            t.id = i
            ids.add(i)