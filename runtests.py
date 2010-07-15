#!/usr/bin/env python

import unittest

from tests.rule_engine.recognition_rule import *
from tests.rule_engine.recognition_rule_engine import *
from tests.rule_engine.recognition_rule_block import *
from tests.rule_engine.normalisation_rule import *
from tests.rule_engine.normalisation_rule_block import *
from tests.rule_engine.normalisation_rule_engine import *

from tests.formats.xml_doc import *
from tests.formats.timex2 import *
from tests.formats.timex3 import *
from tests.formats.timeml import *
from tests.formats.tern import *

from tests.timex import *

def main():
    unittest.main()

if __name__ == '__main__':
    main()