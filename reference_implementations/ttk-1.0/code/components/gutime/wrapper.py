"""

Contains the GUTime wrapper.

"""

import os

from ttk_path import TTK_ROOT
from library.tarsqi_constants import GUTIME
from utilities.xml_utils import merge_tags
from utilities import logger
from components.common_modules.component import ComponentWrapper
from components.gutime.btime import BTime


class GUTimeWrapper(ComponentWrapper):

    """Wrapper for GUTime. See ComponentWrapper for more details on how
    component wrappers work.

    Instance variables
       DIR_GUTIME - directry where the GUTime code lives
       see ComponentWrapper for other variables."""


    def __init__(self, tag, xmldoc, tarsqi_instance):
        """Calls __init__ of the base class and sets component_name,
        DIR_GUTIME, CREATION_EXTENSION and RETRIEVAL_EXTENSION."""
        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = GUTIME
        self.btime = BTime()
        self.DIR_GUTIME = TTK_ROOT + os.sep + 'components' + os.sep + 'gutime'
        self.CREATION_EXTENSION = 'gut.i.xml'
        self.TMP1_EXTENSION = 'gut.t1.xml'
        self.TMP2_EXTENSION = 'gut.t2.xml'
        self.RETRIEVAL_EXTENSION = 'gut.o.xml'
        
    def process_fragments(self):
        """Calls, for each fragment, the Perl scripts that implement GUTime
        and merges the results back into the fragment."""
        os.chdir(self.DIR_GUTIME)
        self.dct = self.tarsqi_instance.metadata['dct']
        for fragment in self.fragments:
            # set fragment names
            base = fragment[0]
            in_file = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.CREATION_EXTENSION)
            tmp1_file = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.TMP1_EXTENSION)
            tmp2_file = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.TMP2_EXTENSION)
            out_file = "%s%s%s.%s" % (self.DIR_DATA, os.sep, base, self.RETRIEVAL_EXTENSION)
            # process them
            command = "perl gutime.pl -dct %s -t fragment %s %s" % (self.dct, in_file, tmp1_file)
            (fh_in, fh_out, fh_errors) = os.popen3(command)
            for line in fh_errors:
                logger.warn(line)
            merge_tags(in_file, tmp1_file, tmp2_file)
            self.btime.process(tmp2_file, out_file)
        os.chdir(TTK_ROOT)



