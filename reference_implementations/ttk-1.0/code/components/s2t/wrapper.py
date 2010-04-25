import os

from ttk_path import TTK_ROOT
from library.tarsqi_constants import S2T
from components.common_modules.component import ComponentWrapper
from components.s2t.main import Slink2Tlink

s2tParser = Slink2Tlink()

class S2tWrapper(ComponentWrapper):

    """Wraps the S2T components. See ComponentWrapper for the instance variables."""

    def __init__(self, tag, xmldoc, tarsqi_instance):

        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = S2T
        self.CREATION_EXTENSION = 's2t.i'
        self.RETRIEVAL_EXTENSION = 's2t.o'

    def process_fragments(self):
        for fragment in self.fragments:
            base = fragment[0]
            infile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.CREATION_EXTENSION)
            outfile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.RETRIEVAL_EXTENSION)
            s2tParser.process(infile, outfile)

    
