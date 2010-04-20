from utilities import logger


class Alink:
    
    def __init__(self, xmldoc, doctree, alinkTag):
        self.xmldoc = xmldoc
        self.doctree = doctree
        self.attrs = alinkTag.attrs
        
    def lookForAtlinks(self):
        """Examine whether the Alink can generate a Tlink."""
        if self.is_a2t_candidate():
            logger.debug("A2T Alink candidate " + self.attrs['lid'] + " " + self.attrs['relType'])
            apply_patterns(self)
        else:
            logger.debug("A2T Alink not a candidate " + self.attrs['lid'] + " " + self.attrs['relType'])

    def is_a2t_candidate(self):
        if a2tCandidate.attrs['relType'] in ('INITIATES', 'CULMINATES', 'TERMINATES'):
            return True
        else:
            return False


def apply_patterns(alink):
    """Loop through TLINKs to match A2T pattern"""
    logger.debug("ALINK Properties:")
    logger.debug(alink.attrs['lid'] + " " + alink.attrs['eventInstanceID']
                 + " " + alink.attrs['relatedToEventInstance']
                 + " " + alink.attrs['relType'])

    for tlink in self.doctree.alink_list:
        logger.debug("Current TLINK ID: " + tlink.attrs['lid'])
        if 'relatedToTime' not in tlink.attrs and 'timeID' not in tlink.attrs:
            if alink.attrs['eventInstanceID'] == tlink.attrs['eventInstanceID']:
                logger.debug("Matched TLINK Properties:")
                logger.debug(tlink.attrs['lid']
                             + " " + tlink.attrs['eventInstanceID']
                             + " " + tlink.attrs['relatedToEventInstance']
                             + " " + tlink.attrs['relType'])
                createTlink(alink, tlink, 1)
            elif alink.attrs['eventInstanceID'] == tlink.attrs['relatedToEventInstance']:
                logger.debug("Matched TLINK Properties:")
                logger.debug(tlink.attrs['lid']
                             + " " + tlink.attrs['eventInstanceID']
                             + " " + tlink.attrs['relatedToEventInstance']
                             + " " + tlink.attrs['relType'])
                createTlink(alink, tlink, 2)
            else:
                logger.debug("No TLINK match")
        else:
            logger.debug("TLINK with Time, no match")


def createTlink(alink, tlink, patternNum):

    if patternNum == 1:
        logger.debug("Pattern Number: " + str(patternNum))
        alink.xmldoc.add_tlink(tlink.attrs['relType'],
                               alink.attrs['relatedToEventInstance'],
                               tlink.attrs['relatedToEventInstance'],
                               'A2T_rule_' + str(patternNum))
    elif patternNum == 2:
        logger.debug("Pattern Number: " + str(patternNum))
        alink.xmldoc.add_tlink(tlink.attrs['relType'],
                               tlink.attrs['eventInstanceID'],
                               alink.attrs['relatedToEventInstance'],
                               'A2T_rule_' + str(patternNum))
