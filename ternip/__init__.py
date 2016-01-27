import os.path

VERSION = '1.1dev'

no_NLTK = False


def recogniser():
    """
    Returns the default recogniser, already configured.
    """
    from ternip.rule_engine.recognition_rule_engine import RecognitionRuleEngine
    r = RecognitionRuleEngine()
    r.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'recognition'))
    return r


def normaliser():
    """
    Returns default normaliser, already configured.
    """
    from ternip.rule_engine.normalisation_rule_engine import NormalisationRuleEngine
    n = NormalisationRuleEngine()
    n.load_rules(os.path.join(os.path.split(__file__)[0], 'rules', 'normalisation'))
    return n
