from string import lower

from library.timeMLspec import EIID, TENSE, ASPECT, EPOS, POL, MOD, CLASS, POS, FORM, STEM
from library.timeMLspec import VERB, NOUN, ADJECTIVE
from library.slinket.main import SLINKET_DICTS
from utilities import logger


class EventExpression:

    """Class that wraps an event in a way that's convenient for
    Slinket.

    Instance variables:

       dict
       eid
       eiid
       tense
       aspect
       nf_morph
       polarity
       modality
       evClass
       pos
       form

       locInSent - idx of node bearing event tag in the document, wrt to its
                   sentence parent node.
       eventNum - position of event in sentence.eventList (needed for
                  potential slinking w/ previous or next events in list)
       isSlinking - an integer, set to 0 at initialization, does not seem to
                    be used
       
    """
    
    def __init__(self, eid, locInSent, eventNum, dict):
        """Set all attributes, using default values if appropriate.
        Arguments:
           eid - a string
           locInSent - an integer
           eventNum - an integer
           dict - a dictionary with event attributes"""
        self.isSlinking = 0
        self.dict = dict
        logger.debug("DICT VALUE:"+str(self.dict))
        self.eid = eid
        self.eiid = self.get_event_attribute(EIID)
        self.tense = self.get_event_attribute(TENSE)
        self.aspect = self.get_event_attribute(ASPECT)
        self.nf_morph = self.get_event_attribute(EPOS)
        self.polarity = self.get_event_attribute(POL, optional=True)
        self.modality = self.get_event_attribute(MOD, optional=True)
        self.evClass = self.get_event_attribute(CLASS)
        self.pos = self.get_event_attribute(POS)
        self.form = self.get_event_attribute(FORM)
        self.locInSent = locInSent
        self.eventNum = eventNum 

    def get_event_attribute(self, attr, optional=False):
        """Return the value of an attribute from self.dict. If the attribute
        is not in the dictionary, then (i) return a default value, and
        (ii) write an error if the attribute is not optinal.
        Arguments:
           attr - a string
           optional - a boolean"""
        try:
            return self.dict[attr]
        except KeyError:
            if not optional:
                logger.error("No %s attribute for current event" % attr)
            if attr == POL: return 'POS'
            return None
        
    def pretty_print(self):
        """Print all attributes to the log file."""
        logger.debug(str(self))
        logger.debug("eid: "+self.eid)
        logger.debug("eiid: "+self.eiid)
        logger.debug("tense: "+self.tense)
        logger.debug("aspect: "+self.aspect)
        logger.debug("epos: "+self.nf_morph) #("nf_morph: "+self.nf_morph)
        logger.debug("polarity: "+str(self.polarity))
        logger.debug("modality: "+str(self.modality))
        logger.debug("evClass: "+self.evClass)
        logger.debug("pos: "+self.pos)
        logger.debug("form: "+self.form)
        logger.debug("locInSent: "+str(self.locInSent))
        logger.debug("eventNum: "+str(self.eventNum))

    def can_introduce_alink(self):
        """Returns True if the EventExpression instance can introduce an
        Alink, False otherwise. This ability is determined by a
        dictionary lookup."""
        if self.nf_morph == VERB and lower(self.form) in SLINKET_DICTS.alinkVerbsDict.keys():
            return True
        if self.nf_morph == NOUN and lower(self.form) in SLINKET_DICTS.alinkNounsDict.keys():
            return True
        return False

    def can_introduce_slink(self):
        """Returns True if the EventExpression instance can introduce an
        Slink, False otherwise. This ability is determined by a
        dictionary lookup."""
        if self.nf_morph == VERB and lower(self.form) in SLINKET_DICTS.slinkVerbsDict.keys():
            return True
        if self.nf_morph == NOUN and lower(self.form) in SLINKET_DICTS.slinkNounsDict.keys():
            return True
        if self.nf_morph == ADJECTIVE and lower(self.form) in SLINKET_DICTS.slinkAdjsDict.keys():
            return True
        return False

    def alinkingContexts(self, key):
        """Returns the list of alink patterns from the dictionary."""
        form = lower(self.form)
        if self.nf_morph == VERB:
            pattern_dictionary = SLINKET_DICTS.alinkVerbsDict
        elif self.nf_morph == NOUN:
            pattern_dictionary = SLINKET_DICTS.alinkNounsDict
        else:
            logger.warn("SLINKS of type "+str(key)+" for EVENT form "+str(form)+" should be in the dict")
            return []
        return pattern_dictionary.get(form,{}).get(key,[])
        #if pattern_dictionary.has_key(form):
        #    return pattern_dictionary[form].get(key,[])
        #else:
        #    return []
        
    def slinkingContexts(self, key):
        """Returns the list of slink patterns from the dictionary."""
        form = lower(self.form)
        if self.nf_morph == VERB:
            pattern_dictionary = SLINKET_DICTS.slinkVerbsDict
        elif self.nf_morph == NOUN:
            pattern_dictionary = SLINKET_DICTS.slinkNounsDict
        elif self.nf_morph == ADJECTIVE:
            pattern_dictionary = SLINKET_DICTS.slinkAdjsDict
        else:
            logger.warn("SLINKS of type "+str(key)+" for EVENT form "+str(form)+" should be in the dict")
            return []
        return pattern_dictionary.get(form,{}).get(key,[])
        #if pattern_dictionary.has_key(form):
        #    return pattern_dictionary[form].get(key,[])
        #else:
        #    return []
