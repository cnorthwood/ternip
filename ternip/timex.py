#!/usr/bin/env python

# Attribute     TIMEX2      TIMEX3
#---------------------------------
# ID            None        X tid ('t' + ID)
# value         val         value
# mod           mod         mod
# type          set         X type
#               (only if type=set)
# freq          periodicity freq
#               ('f' + freq)
# quant         None        quant
# granuality    granuality  None
# comment       comment     comment
# non_specific  non_specific None
# temporal_function None    temporalFunction
# role          None        functionInDocument
# begin_timex   None        beginPoint (ID of begin_timex)
# end_timex     None        endPoint (ID of end_timex)
# context       None        anchorTimeID (ID of context)

class timex:
    """ A temporal expression """
    
    def __init__(self,
                 type  = None,
                 value = None,
                 id    = None):
        """ Initialise a timex object with some optional values """
        self.type       = type
        self.value      = value
        self.id         = id
        self.mod        = None
        self.freq       = None
        self.quant      = None
        self.granuality = None
        self.comment    = None
        self.non_specific = False
        self.temporal_function = False
        self.document_role = None
        self.begin_timex = None
        self.end_timex  = None
        self.context    = None
        self.non_consuming = False
        

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