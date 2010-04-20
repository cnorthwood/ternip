"""

Contains the Evita wrapper.

"""

import os

from library.tarsqi_constants import EVITA
from components.common_modules.component import ComponentWrapper
from components.evita.main import Evita


class EvitaWrapper(ComponentWrapper):

    """Wrapper for Evita. See ComponentWrapper for more details on how
    component wrappers work.

    Instance variables
       parser - an instance of the Evita parser
       see ComponentWrapper for other variables."""


    def __init__(self, tag, xmldoc, tarsqi_instance):
        """Calls __init__ of the base class and sets component_name,
        parser, CREATION_EXTENSION and RETRIEVAL_EXTENSION."""
        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = EVITA
        self.parser = Evita()
        self.CREATION_EXTENSION = 'evi.i'
        self.RETRIEVAL_EXTENSION = 'evi.o'

    def process_fragments(self):
        """Apply the Evita parser to each fragment. No arguments and no
        return value."""
        for fragment in self.fragments:
            base = fragment[0]
            infile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.CREATION_EXTENSION)
            outfile = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.RETRIEVAL_EXTENSION)
            self.parser.process(infile, outfile)

    
