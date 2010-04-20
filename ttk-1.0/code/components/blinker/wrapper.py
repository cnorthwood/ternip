"""

Contains the Blinker wrapper.

"""

import os

from library.tarsqi_constants import BLINKER
from components.common_modules.component import ComponentWrapper
from components.blinker.main import Blinker

blinkerParser = Blinker()

class BlinkerWrapper(ComponentWrapper):

    """Wrapper for Blinker. See ComponentWrapper for more details on how
    component wrappers work and on the instance variables."""

    def __init__(self, tag, xmldoc, tarsqi_instance):
        """Calls __init__ of the base class and sets component_name,
        CREATION_EXTENSION and RETRIEVAL_EXTENSION."""
        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = BLINKER
        self.CREATION_EXTENSION = 'bli.i'
        self.RETRIEVAL_EXTENSION = 'bli.o'

    def process_fragments(self):
        """Apply the Blinker parser to each fragment. No arguments and no
        return value."""
        for fragment in self.fragments:
            base = fragment[0]
            infile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.CREATION_EXTENSION)
            outfile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.RETRIEVAL_EXTENSION)
            dct = self.tarsqi_instance.metadata['dct']
            blinkerParser.process(infile, outfile, dct)

    

