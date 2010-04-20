"""Main module for Evita, the event recognition  component.

Responsible for the top-level processing of Evita.

"""

import time

from components.evita.timemlParser import parseFile
from components.evita.gramChunk import getWordList, getPOSList

from components.common_modules.component import TarsqiComponent
from docmodel.xml_parser import Parser
from library.tarsqi_constants import EVITA
from utilities import logger
from utilities.converter import FragmentConverter



class Evita (TarsqiComponent):

    """Class that implements Evita's event recognizer.

    Instance variables:
       NAME - a string
       doctree - a Document instance """
    
    def __init__(self):
        """Set the NAME instance variable."""
        self.NAME = EVITA
    
    def process(self, infile, outfile):
        """Process a fragment file and write a file with EVENT tags.
        Arguments:
           infile - an absolute path
           outfile - an absolute path"""
        use_old = True
        use_old = False
        if use_old:
            #logger.out('start event parser ', time.time())
            self.doctree = parseFile(infile)
            #logger.out('end event parser   ', time.time())
        else:
            xmldoc = Parser().parse_file(open(infile,'r'))
            # creating the document tree takes way too long, needs
            # to be optimized
            self.doctree = FragmentConverter(xmldoc, infile).convert()
        #xmldoc.pretty_print()
        #self.print_doctree(EVITA)
        self.extractEvents()
        self.doctree.printOut(outfile)

    def extractEvents(self):
        """Loop through all sentences in self.doctree and through all nodes in
        each sentence and determine if the node contains an event."""
        for sentence in self.doctree:
            logger.debug("> SENTENCE:" + str(getWordList(sentence)))
            for node in sentence:
                #print
                #node.pretty_print()
                wordlist = str(getWordList(node))
                poslist = str(getPOSList(node))
                #logger.debug("> NODE:" + wordlist + poslist + " checked=" +
                #             str(node.flagCheckedForEvents))
                if not node.flagCheckedForEvents:
                    #logger.out(node.__class__.__name__)
                    node.createEvent()
                else:
                    logger.debug("PASSING, already checked!")

