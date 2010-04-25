"""
Main module for the S2T component. 

Responsible for the top-level processing of S2T. It contains
Slink2Tlink, which inherits from TarsqiComponent as well as Slink, a
class that takes care of applying s2t-rules to each SLINK.

"""

#from components.s2t.Alinks import Alink

from docmodel.xml_parser import Parser
from utilities import logger
from utilities.converter import FragmentConverter
from components.common_modules.component import TarsqiComponent
from library.tarsqi_constants import S2T
from library.s2t.s2t_rule_loader import read_rules


class Slink2Tlink (TarsqiComponent):

    """Implements the S2T component of Tarsqi.
    S2T takes the output of the Slinket component and applies rules to the
    Slinks to create new Tlinks.

    Instance variables:
       NAME - a string
       rules - an S2TRuleDictionary"""

    def __init__(self):
        """Set component name and load rules into an S2TRuleDictionary object.
        This object knows where the rules are stored."""
        self.NAME = S2T
        self.rules = read_rules()

    def process(self, infile, outfile):
        """Apply all S2T rules to the input file.
        Parses the xml file with xml_parser.Parser and converts it to a shallow tree
        with converter.FragmentConverter.  Then calls createTLinksFromSlinks."""
        xmlfile = open(infile, "r")
        self.xmldoc = Parser().parse_file(xmlfile)
        self.doctree = FragmentConverter(self.xmldoc, infile).convert()
        #self.print_doctree(S2T)
        self.alinks = self.doctree.alink_list
        self.slinks = self.doctree.slink_list
        self.tlinks = self.doctree.tlink_list
        #self.createTLinksFromALinks()
        self.createTLinksFromSLinks()
        self.xmldoc.save_to_file(outfile)
            
    def createTLinksFromALinks(self):
        """Calls alink.lookForAtlinks to add Tlinks from Alinks. This is
        rather moronic unfortunately because it will never do anything
        because at the time of application there are no tlinks in the
        document. Needs to be separated out and apply at a later
        processing stage, after all other tlinking."""
        logger.debug("Number of ALINKs in file: "+str(len(self.alinks)))
        for alinkTag in self.alinks:
            try:
                alink = Alink(self.xmldoc, self.doctree, alinkTag)
                alink.lookForAtlinks()
            except:
                logger.error("Error processing ALINK")
                
    def createTLinksFromSLinks(self):
        """Calls lookForStlinks for a given Slink object."""
        logger.debug("Number of SLINKs in file: "+str(len(self.slinks)))
        for slinkTag in self.slinks:
            try:
                slink = Slink(self.xmldoc, self.doctree, slinkTag)
                slink.match_rules(self.rules)
            except:
                logger.error("Error processing SLINK")


class Slink:

    """Implements the Slink object. An Slink object consists of the
    attributes of the SLINK (relType, eventInstanceID, and
    subordinatedEventInstance) and the attributes of the specific
    event instances involved in the link.

    Instance variables:
       xmldoc - an XmlDocument
       attrs - adictionary containing the attributes of the slink
       eventInstance - an InstanceTag
       subEventInstance - an InstanceTag"""
    
    
    def __init__(self, xmldoc, doctree, slinkTag):
        """Initialize an Slink using an XMLDocument, a Document, and an SlinkTag."""
        self.xmldoc = xmldoc
        self.attrs = slinkTag.attrs
        self.eventInstance = doctree.instance_dict[self.attrs['eventInstanceID']]
        self.subEventInstance = doctree.instance_dict[self.attrs['subordinatedEventInstance']]
        
    def match_rules(self, rules):
        """Match all the rules in the rules argument to the SLINK. If a rule
        matches, this method creates a TLINK and returns. There is no
        return value."""
        for rule in rules:
            result = self.match(rule)
            if result:
                self.create_tlink(rule)
                break

    def match(self, rule):
        """ The match method applies an S2TRule object to an the Slink. It
        returns the rule if the Slink is a match, False otherwise."""
        for (attr, val) in rule.attrs.items():
            # relType must match
            if attr == 'reltype':
                if (val != self.attrs['relType']):
                    return False
            # relation is the rhs of the rule, so need not match
            elif attr == 'relation':
                continue
            # all other features are features on the events in the
            # SLINK, only consider those that are on event and
            # subevent.
            elif '.' in attr:
                (event_object, attribute) = attr.split('.')
                if event_object == 'event':
                    if (val != self.eventInstance.attrs.get(attribute)):
                        return False
                elif event_object == 'subevent':
                    if (val != self.subEventInstance.attrs.get(attribute)):
                        return False
        return rule

    def create_tlink(self, rule):
        """Takes an S2T rule object and calls the add_tlink method from xmldoc
        to create a new TLINK using the appropriate SLINK event
        instance IDs and the relation attribute of the S2T rule."""
        self.xmldoc.add_tlink(rule.attrs['relation'],
                              self.attrs['eventInstanceID'],
                              self.attrs['subordinatedEventInstance'],
                              'S2T Rule ' + rule.id)
