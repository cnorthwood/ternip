"""Small module that provides patches to GUTime."""


import re

from docmodel.xml_parser import Parser
from library.tarsqi_constants import BTIME
from library.timeMLspec import POS_CD
from utilities import logger
from utilities.converter import FragmentConverter
from components.common_modules.component import TarsqiComponent
from components.common_modules.tags import TimexTag



    
class BTime(TarsqiComponent):

    """Fledgling component to add Timex tags to a document. It now
    only serves to fill in some timexes that GUTime does not get,
    doing it this way is easier than modifiying GUTime.

    Instance variables:
       name - a string
       xmldoc - an XmlDocument
       doctree - a Document"""

    
    def __init__(self):
        """Set the NAME instance variable."""
        self.NAME = BTIME


    def process(self, infile, outfile):
        """Process a fragment file and add TIMEX3 tags that were
        missed by Tempex.
        Arguments:
           infile - an absolute path
           outfile - an absolute path"""
        xmldoc = Parser().parse_file(open(infile,'r'))
        self.doctree = FragmentConverter(xmldoc, infile).convert()
        #self.print_doctree(BTIME)
        self.find_timexes()
        self.doctree.printOut(outfile)

    def find_timexes(self):
        """Loop through all sentences in self.doctree and through all nodes in
        each sentence and search for missed timexes in noun groups."""
        for sentence in self.doctree:
            for node in sentence:
                if node.isNounChunk():
                    self.find_timex_in_noungroup(node)

    def find_timex_in_noungroup(self, noungroup):
        """Find missing timexes in noun groups. Searches for
        years. Assumes that the noun group is not contained in a
        Timex tag."""
        idx = 0
        for node in noungroup:
            if node.isToken() and node.pos == POS_CD:
                text = node.getText()
                if text.isdigit() and len(text) == 4:
                    attrs = { 'TYPE': 'DATE', 'VAL': text }
                    timex = TimexTag(attrs)
                    timex.dtrs = [node]
                    # this changes doctree.sentenceList
                    noungroup[idx] = timex
                    # and this changes doctree.nodeList
                    self.doctree.addTimexTag(timex)
            idx += 1

                    

