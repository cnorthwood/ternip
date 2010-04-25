import os
import cPickle

from ttk_path import TTK_ROOT

DIR_DICTS = os.path.join(TTK_ROOT, 'library', 'slinket', 'dictionaries')


class SlinketDicts:

    def __init__(self):
        self.slinkVerbsDict = None
        self.slinkNounsDict = None
        self.slinkAdjsDict = None
        self.alinkVerbsDict = None
        self.alinkNounsDict = None

    def load(self):
        """Load the Slinket dictionaries if they have not been loaded yet."""
        if not self.slinkVerbsDict:
            self.slinkVerbsDict = cPickle.load(open(os.path.join(DIR_DICTS, "slinkVerbs.pickle")))
            self.slinkNounsDict = cPickle.load(open(os.path.join(DIR_DICTS, "slinkNouns.pickle")))
            self.slinkAdjsDict = cPickle.load(open(os.path.join(DIR_DICTS, "slinkAdjs.pickle")))
            self.alinkVerbsDict = cPickle.load(open(os.path.join(DIR_DICTS, "alinkVerbs.pickle")))
            self.alinkNounsDict = cPickle.load(open(os.path.join(DIR_DICTS, "alinkNouns.pickle")))
        
SLINKET_DICTS = SlinketDicts()
