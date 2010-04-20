import os
import cPickle

from ttk_path import TTK_ROOT


# EVITA PATTERNS

DIR_PATTERNS = os.path.join(TTK_ROOT, 'library', 'evita', 'patterns')

HAVE_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "HAVE_FSAs.pickle")))
MODAL_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "MODAL_FSAs.pickle")))
BE_N_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "BE_N_FSAs.pickle")))
BE_A_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "BE_A_FSAs.pickle")))
BE_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "BE_FSAs.pickle")))
GOINGto_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "GOINGto_FSAs.pickle")))
USEDto_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "USEDto_FSAs.pickle")))
DO_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "DO_FSAs.pickle")))
BECOME_A_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "BECOME_A_FSAs.pickle")))
CONTINUE_A_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "CONTINUE_A_FSAs.pickle")))
KEEP_A_FSAs = cPickle.load(open(os.path.join(DIR_PATTERNS, "KEEP_A_FSAs.pickle")))

