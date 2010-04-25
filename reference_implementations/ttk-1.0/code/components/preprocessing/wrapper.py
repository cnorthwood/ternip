"""

Contains the wrapper for all preprocessing components.

"""

import os

from treetaggerwrapper import TreeTagger
from formatConversor import Tokenizer2treeTagger
from formatConversor import ChunkerMarc2tarsqi
from formatConversor import normalizeXML
from formatConversor import normalizePOS

from ttk_path import TTK_ROOT
from library.tarsqi_constants import PREPROCESSOR
from components.common_modules.component import ComponentWrapper
from components.preprocessing.tokenizer import Tokenize_File

treetagger_dir = os.path.join(TTK_ROOT, 'components', 'preprocessing', 'treetagger')
treetagger = TreeTagger(TAGLANG='en', TAGDIR=treetagger_dir)


class PreprocessorWrapper(ComponentWrapper):
    
    """Wrapper for the preprocessing components. See ComponentWrapper for
    more details on how component wrappers work.

    Instance variables
       DIR_PRE - directry where the preprocessor code lives
       see ComponentWrapper for other variables."""

    def __init__(self, tag, xmldoc, tarsqi_instance):
        """Calls __init__ of the base class and sets component_name,
        DIR_PRE, CREATION_EXTENSION and RETRIEVAL_EXTENSION."""
        ComponentWrapper.__init__(self, tag, xmldoc, tarsqi_instance)
        self.component_name = PREPROCESSOR
        self.DIR_PRE = os.path.join(TTK_ROOT, 'components', 'preprocessing')
        # may need a better way to do this, too hard-wired and only works if the
        # entire pre-processing chain is used (which may be okay actually)
        self.CREATION_EXTENSION = 'txt'
        self.RETRIEVAL_EXTENSION = 'cnk2'

    def process(self):
        """This is one of the few components that overwrites the base class's
        process method. The reason for this is that there is no need to wrap
        the fragment in a <fragment> tag, in fact, it would disturb some of
        the preprocessing components."""
        self.create_fragments(self.tag, remove_tags=True)
        self.process_fragments()
        self.retrieve_fragments()
        
    def process_fragments(self):
        """ Method that takes care of calling the perl tokenizer, the TreeTagger,
        the perl chunker and various glue scripts."""
        os.chdir(self.DIR_PRE)
        for fragment in self.fragments:
            # set fragment names
            base = fragment[0]
            in_file = "%s/%s.txt" % (self.DIR_DATA, base)
            tok1_file = "%s/%s.tok1" % (self.DIR_DATA, base)
            tok2_file = "%s/%s.tok2" % (self.DIR_DATA, base)
            tag1_file = "%s/%s.tag1" % (self.DIR_DATA, base)
            tag2_file = "%s/%s.tag2" % (self.DIR_DATA, base)
            cnk1_file = "%s/%s.cnk1" % (self.DIR_DATA, base)
            cnk2_file = "%s/%s.cnk2" % (self.DIR_DATA, base)
            # process them
            self.tokenize_fragment(in_file, tok1_file, tok2_file)
            self.tag_fragment(tok2_file, tag1_file, tag2_file)
            self.chunk_fragment(tag2_file, cnk1_file, cnk2_file)
        os.chdir(TTK_ROOT)

    def tokenize_fragment(self, in_file, tok1_file, tok2_file):
        """Tokenize a file fragment and convert it to the format required by
        the tagger. The arguments are three absolute paths: in_file,
        tok1_file (tokenized file) and tok2_file (converted file)."""
        # NOTE: new Python tokenizer introduces some bad sentence
        # tags, still using perl version
        os.system("perl tokenize.pl %s %s" % (in_file, tok1_file))
        #Tokenize_File(in_file, tok1_file)
        conversor = Tokenizer2treeTagger(tok1_file, tok2_file)
        conversor.convert()
        conversor.closeFiles()

    def tag_fragment(self, tok2_file, tag1_file, tag2_file):
        """Tag a file fragment with the tree tagger and run aperl script to
        fix an output quirk of the tagger. The arguments are three
        absolute paths: tok2_file (converted tokenized file),
        tag1_file (output of tagger) and tag2_file (fixed output of
        tagger."""
        infile = open(tok2_file, 'r')
        outfile = open(tag1_file, 'w')
        text = infile.read() 
        taggedItems = treetagger.TagText(text)
        for item in taggedItems:
            if item == '<s>':
                outfile.write("\n")
            elif item[0] == '<' and item[-1] == '>':
                outfile.write(item)
            else:
                (tok, pos, stem) = item.split("\t")
                pos = normalizePOS(pos)
                tok = normalizeXML(tok)
                outfile.write(tok + "/" + pos + ' ')
        infile.close()
        outfile.close()
        os.system("perl fix_tag.pl %s > %s" % (tag1_file, tag2_file))
        
    def chunk_fragment(self, tag2_file, cnk1_file, cnk2_file):
        """Chunk a file fragment and convert tokens in the putput from
        'TOKEN/TAG' into '<lex tag="TAG">TOKEN</lex>'. The arguments
        are three absolute paths: tag2_file (converted tagged file),
        cnk1_file (chunked file) and cnk2_file (converted chunked
        file)."""
        os.system("perl chunk.pl %s > %s" % (tag2_file, cnk1_file))
        conversor = ChunkerMarc2tarsqi(cnk1_file, cnk2_file)
        conversor.convert()
        conversor.closeFiles()
