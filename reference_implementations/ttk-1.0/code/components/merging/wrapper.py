"""Python wrapper around the merging code"""


import os

from ttk_path import TTK_ROOT
from library.tarsqi_constants import LINK_MERGER
from library.timeMLspec import TLINK
from library.timeMLspec import RELTYPE, EVENT_INSTANCE_ID, TIME_ID
from library.timeMLspec import RELATED_TO_EVENT_INSTANCE, RELATED_TO_TIME, CONFIDENCE
from components.common_modules.component import ComponentWrapper
from utilities import logger
from docmodel.xml_parser import Parser


class MergerWrapper(ComponentWrapper):

    """Wraps the merging code, which includes Sputlinks temporal closure code.

    Instance variables

       DIR_LINK_MERGER - directory where the classifier executables live

    See ComponentWrapper for other instance variables."""


    def __init__(self, tag, xmldoc, tarsqi_instance):

        """Calls __init__ on the base class and initializes component_name,
        DIR_LINK_MERGER, CREATION_EXTENSION, TMP_EXTENSION and
        RETRIEVAL_EXTENSION."""

        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = LINK_MERGER
        self.DIR_LINK_MERGER = os.path.join(TTK_ROOT, 'components', 'merging')
        self.CREATION_EXTENSION = 'mer.i.xml'
        self.TMP_EXTENSION = 'mer.t.xml'
        self.RETRIEVAL_EXTENSION = 'mer.o.xml'

        
    def process_fragments(self):

        """Set fragment names, create the vectors for each fragment, run the
        classifier and add links from the classifier to the fragments."""

        os.chdir(self.DIR_LINK_MERGER + os.sep + 'sputlink')
        perl = '/usr/local/ActivePerl-5.8/bin/perl'
        perl = 'perl'
        perl = self.tarsqi_instance.getopt_perl()

        for fragment in self.fragments:
            # set fragment names
            base = fragment[0]
            in_fragment = os.path.join(self.DIR_DATA, base+'.'+self.CREATION_EXTENSION)
            tmp_fragment = os.path.join(self.DIR_DATA, base+'.'+self.TMP_EXTENSION)
            out_fragment = os.path.join(self.DIR_DATA, base+'.'+self.RETRIEVAL_EXTENSION)
            # process them
            command = "%s merge.pl %s %s" % (perl, in_fragment, tmp_fragment)
            (i, o, e) = os.popen3(command)
            for line in e:
                if line.lower().startswith('warn'):
                    logger.warn('MERGING: ' + line)
                else:
                    logger.error('MERGING: ' + line)
            for line in o:
                logger.debug('MERGING: ' + line)
            self._add_tlinks_to_fragment(in_fragment, tmp_fragment, out_fragment)
        os.chdir(TTK_ROOT)

        
    def _add_tlinks_to_fragment(self, in_fragment, tmp_fragment, out_fragment):

        """Take the links from the merged tlinks and add them into the
        fragment. Based on the method with the same name in the
        classifier wrapper."""

        xmldoc1 = Parser().parse_file(open(in_fragment,'r'))
        xmldoc2 = Parser().parse_file(open(tmp_fragment,'r'))

        xmldoc1.remove_tags(TLINK)
        
        for tlink in xmldoc2.get_tags(TLINK):
            reltype = tlink.attrs[RELTYPE]
            id1 = tlink.attrs.get(EVENT_INSTANCE_ID, None)
            if not id1:
                id1 = tlink.attrs.get(TIME_ID, None)
            if not id1:
                logger.warn("Could not find id1 in " + tlink.content)
            id2 = tlink.attrs.get(RELATED_TO_EVENT_INSTANCE, None)
            if not id2:
                id2 = tlink.attrs.get(RELATED_TO_TIME, None)
            if not id2:
                logger.warn("Could not find id2 in " + tlink.content)
            #origin = CLASSIFIER + ' ' + tlink.attrs.get(CONFIDENCE,'')
            origin = tlink.attrs.get('origin','')
            xmldoc1.add_tlink(reltype, id1, id2, origin)

        xmldoc1.save_to_file(out_fragment)
        

