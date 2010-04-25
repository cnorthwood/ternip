"""

Python wrapper around the MaxEnt Classifier

CLASSES
   ClassifierWrapper

"""


import os

from ttk_path import TTK_ROOT
from library.tarsqi_constants import CLASSIFIER
from library.timeMLspec import TLINK
from library.timeMLspec import RELTYPE, EVENT_INSTANCE_ID, TIME_ID
from library.timeMLspec import RELATED_TO_EVENT_INSTANCE, RELATED_TO_TIME, CONFIDENCE
from components.common_modules.component import ComponentWrapper
from utilities import logger
from docmodel.xml_parser import Parser


class ClassifierWrapper(ComponentWrapper):

    """Wraps the maxent link classifier. See ComponentWrapper for details
    on how wrappers work.

    Instance variables

       DIR_CLASSIFIER - directory where the classifier executables live

    See ComponentWrapper for other instance variables."""


    def __init__(self, tag, xmldoc, tarsqi_instance):

        """Calls __init__ on the base class and initializes component_name,
        DIR_CLASSIFIER, CREATION_EXTENSION, TMP_EXTENSION and
        RETRIEVAL_EXTENSION."""

        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = CLASSIFIER
        self.DIR_CLASSIFIER = os.path.join(TTK_ROOT, 'components', 'classifier')
        self.CREATION_EXTENSION = 'cla.i.xml'
        self.TMP_EXTENSION = 'cla.t.xml'
        self.RETRIEVAL_EXTENSION = 'cla.o.xml'

        
    def process_fragments(self):

        """Set fragment names, create the vectors for each fragment, run the
        classifier and add links from the classifier to the fragments."""

        os.chdir(self.DIR_CLASSIFIER)
        perl = self.tarsqi_instance.getopt_perl()

        for fragment in self.fragments:

            # set fragment names
            base = fragment[0]
            fin = os.path.join(self.DIR_DATA, base+'.'+self.CREATION_EXTENSION)
            ftmp = os.path.join(self.DIR_DATA, base+'.'+self.TMP_EXTENSION)
            fout = os.path.join(self.DIR_DATA, base+'.'+self.RETRIEVAL_EXTENSION)

            # process them
            #self._create_vectors(in, in+'.EE2', in+'.ET2', fragment)

            fin_ee = fin + '.EE'
            fin_et = fin + '.ET'
            ee_model = 'data/op.e-e.model'
            et_model = 'data/op.e-t.model'
            commands = [
                "%s prepareClassifier.pl %s %s %s" % (perl, fin, fin_ee, fin_et),
                "./mxtest.opt -input %s -model %s -output %s.REL >> class.log" % (fin_ee, ee_model, fin_ee),
                "./mxtest.opt -input %s -model %s -output %s.REL >> class.log" % (fin_et, et_model, fin_et),
                "%s collectClassifier.pl %s %s %s" % (perl, fin_ee, fin_et, ftmp) ]

            for command in commands:
                logger.info(command)
                os.system(command)
                
            self._add_tlinks_to_fragment(fin, ftmp, fout)

        os.chdir(TTK_ROOT)
        

    def _create_vectors(self, in_fragment, ee_fragment, et_fragment, fragment):

        """New method that takes over the functionality of the old
        Perl script named prepareClassifier.

        UNDER CONSTRUCTION"""

        #print in_fragment
        ee_file = open(ee_fragment, 'w') 
        et_file = open(et_fragment, 'w') 
        #print fragment
        frag = Parser().parse_file(open(in_fragment,'r'))

        # collect objects from the fragment
        events = frag.tags['EVENT']
        instances = frag.tags['MAKEINSTANCE']
        times = frag.tags['TIMEX3']

        # add instance information to events
        eid2inst = {}
        for inst in instances:
            eid = inst.attrs.get('eventID', None)
            eid2inst[eid] = inst
        for event in events:
            eid = event.attrs.get('eid', None)
            inst = eid2inst[eid]
            for (key, val) in inst.attrs.items():
                event.attrs[key] = val
            #event.attrs['instance'] = eid2inst[eid]
            #print event.attrs
            
        objects = times + events
        objects.sort(lambda a,b: cmp(a.id, b.id))

        #print
        #for x in objects:
        #    print x
            
        #for time in times: print time
        #for event in events: print event
        #for instance in instances: print instance
        
        
    def _add_tlinks_to_fragment(self, in_fragment, tmp_fragment, out_fragment):

        """Takes the links created by the classifier and merges them into the
        input fragment."""

        xmldoc1 = Parser().parse_file(open(in_fragment,'r'))
        xmldoc2 = Parser().parse_file(open(tmp_fragment,'r'))

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
            origin = CLASSIFIER + ' ' + tlink.attrs.get(CONFIDENCE,'')
            xmldoc1.add_tlink(reltype, id1, id2, origin)

        xmldoc1.save_to_file(out_fragment)
        

 
