#!/usr/bin/env python

from gate import *

# Allow disabling classes which rely on the NLTK, allows for quicker loading if
# we're using a class which never needs the NLTK
if not ternip.no_NLTK:
    from timeml import *
    from tern import *
    from tempeval2 import *
    from timex2 import *
    from timex3 import *
