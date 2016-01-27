import os.path

from ternip.rule_engine.normalisation_rule_engine import NormalisationRuleEngine
from ternip.rule_engine.recognition_rule_engine import RecognitionRuleEngine


VERSION = '1.1dev'

no_NLTK = False


def recogniser():
    """
    Returns the default recogniser, already configured.
    """
    r = RecognitionRuleEngine()
    r.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'recognition'))
    return r


def normaliser():
    """
    Returns default normaliser, already configured.
    """
    n = NormalisationRuleEngine()
    n.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'normalisation'))
    return n
