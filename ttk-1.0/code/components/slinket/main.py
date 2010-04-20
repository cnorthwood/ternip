"""

Main module for the Slinket component.

Responsible for the top-level processing of Slinket.

"""

import eventParser
from EventExpression import EventExpression

from components.common_modules.component import TarsqiComponent
from library.slinket.main import SLINKET_DICTS
from library.tarsqi_constants import SLINKET
from utilities import logger

from docmodel.xml_parser import Parser
from utilities.converter import FragmentConverter

class Slinket (TarsqiComponent):

    """Class that implements the Slinket SLINK and ALINK parser.

    Instance variables:
       NAME - a string
       doctree - a Document"""
    
    def __init__(self):
        """Load the Slinket dictionaries if they have not been loaded yet."""
        self.NAME = SLINKET
        self.doctree = None
        SLINKET_DICTS.load()

    def process(self, infile, outfile):
        """Run Slinket on the input file and write the results to the output
        file. Both input an doutput file are fragments. Uses the xml
        parser as well as the fragment converter to prepare the input
        and create the shallow tree that Slinket requires.
        Arguments:
           infile - an absolute path
           outfile - an absolute path"""
        use_old = True
        use_old = False
        if use_old:
            self.doctree = eventParser.readFileWithEvents(infile)
        else:
            xmldoc = Parser().parse_file(open(infile,'r'))
            self.doctree = FragmentConverter(xmldoc, infile).convert(user=SLINKET)
        #self.print_doctree(SLINKET)
        #logger.debug("Number of sentences in file: " + str(len(self.doctree))) 
        for sentence in self.doctree:
            self._find_links(self.doctree, sentence)
        self.doctree.printOut(outfile)

    def _find_links(self, doc, sentence):
        """For each event in the sentence, check whether an Alink or Slink can
        be created for it."""
        self.currSent = sentence
        #print; print "SENTENCE\n"; sentence.pretty_print(); print
        #logger.out("ELIST", self.currSent.eventList)
        eventNum = -1
        for (eLocation, eId) in self.currSent.eventList:
            eventNum += 1
            #logger.out("< %d %d %s >" % (eventNum, eLocation, eId))
            event_expr = EventExpression(eId, eLocation, eventNum, doc.taggedEventsDict[eId])
            # alinks
            if event_expr.can_introduce_alink():
                logger.debug("EVENT: '"+event_expr.form+"' is candidate to Alinking")
                self._find_alinks(event_expr)
            # lexical slinks
            if event_expr.can_introduce_slink() :
                logger.debug("EVENT: '"+event_expr.form+"' is candidate to Slinking")
                self._find_lexically_based_slinks(event_expr)
            # syntactic slinks
            self._find_purpose_clause_slinks(event_expr)
            self._find_conditional_slinks(event_expr)

    def _find_alinks(self, event_expr):
        evNode = self.currSent[event_expr.locInSent]
        if evNode is None:
            logger.warning("No event node found at locInSent")
        forwardFSAs = event_expr.alinkingContexts('forward')
        if forwardFSAs:
            logger.debug("PROCESS for FORWARD alinks")
            evNode.createForwardAlink(forwardFSAs)
            if evNode.createdAlink:
                evNode.createdAlink = 0
                return 
        backwardFSAs = event_expr.alinkingContexts('backwards')
        if backwardFSAs:
            logger.debug("PROCESS for BACKWARD alinks")
            evNode.createBackwardAlink(backwardFSAs)
            if evNode.createdAlink:
                evNode.createdAlink = 0

                
    def _find_lexically_based_slinks(self, event_expr):

        """Try to find lexically based Slinks using forward, backward and
        reporting FSA paterns. No return value, if an Slink is found,
        it will be created by the chunk that embeds the Slink
        triggering event.
        Arguments:
           event_expr - an EventExpression"""

        evNode = self.currSent[event_expr.locInSent]
        #logger.out('trying slink')
        if evNode is None:
            logger.error("No event node found at locInSent")
            
        forwardFSAs = event_expr.slinkingContexts('forward')
        if forwardFSAs:
            #logger.out('found', len(forwardFSAs[0]), 'groups of forwardFSAs')
            evNode.find_forward_slink(forwardFSAs)
            if evNode.createdLexicalSlink:
                #logger.out('created slink')
                evNode.createdLexicalSlink = 0
                return
            
        backwardFSAs = event_expr.slinkingContexts('backwards')
        if backwardFSAs:
            #logger.out('found', len(backwardFSAs[0]), 'groups of backwardFSAs')
            logger.debug("PROCESS for BACKWARD slinks")
            evNode.find_backward_slink(backwardFSAs)
            if evNode.createdLexicalSlink:
                evNode.createdLexicalSlink = 0
                return
            
        reportingFSAs = event_expr.slinkingContexts('reporting')
        if reportingFSAs:
            #logger.out('found', len(reportingFSAs[0]), 'groups of reportingFSAs')
            logger.debug("PROCESS for REPORTING slinks")
            evNode.find_reporting_slink(reportingFSAs)
            if evNode.createdLexicalSlink:
                evNode.createdLexicalSlink = 0

                
    def _find_purpose_clause_slinks(self, event_expr):
        """Not yet implemented. But note that some purpose clause SLINKS are
        already introduced in the lexically-triggered process. This is
        so for those events that discoursively tend to appear modified
        by a Purpose Clause (e.g., 'address').  The data are based on
        TimeBank."""
        pass

    def _find_conditional_slinks(self, event_expr):
        """Not yet implemented."""
        pass
    





            
