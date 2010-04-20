"""Rules to set event features.

These rules apply to chunks that contain an event and determine the
tense and aspect features. They also create part of speech values, but
with a tagger these are obsolute.

"""

# LISTS of WORDS and POS:
# ======================

from library.forms import *  


# RULES:
# =====

# GRAMMAR Rules:
# -------------
  
# VERBAL CHUNKS RULES:
#
# Info contained in each position:
#    row 1.a) node.name            None or 2-place tuple (operator, 2nd elem)
#    row 2.a) node.items[0].word   None or 2-place tuple (operator, 2nd elem)
#          b) node.items[0].pos    None or 2-place tuple (operator, 2nd elem)
#    row 3.a) node.items[1].word None or 2-place tuple (operator, 2nd elem)
#          b) node.items[1].pos  None or 2-place tuple (operator, 2nd elem)
#    row 4.a) node.items[2].word None or 2-place tuple (operator, 2nd elem)
#          b) node.items[2].pos  None or 2-place tuple (operator, 2nd elem)
#    row 5.a) node.items[3].word   None or 2-place tuple (operator, 2nd elem)
#          b) node.items[3].pos    None or 2-place tuple (operator, 2nd elem)
#    row 6.Grammar feature to return: TENSE, ASPECT, NF_MORPH

# Length 1 rules:
grammarRules1 = [
    [None,                                     # Active, simple past    ('asked')
     None, ('in', verbsPast),
     ('PAST', 'NONE', 'VERB')],    
    [None,                                     # Active, simple present ('asks') 
     None, ('in', verbsPresent),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                     # infinitive             ('(to) ask') 
     None, ('==', 'VB'),
     ('INFINITIVE', 'NONE', 'VERB')],
    [None,                                     # past participle        ('asked')
     None, ('==', 'VBN'),
     ('PASTPART', 'NONE', 'VERB')],
    [None,                                     # present participle     ('asking')
     None, ('==', 'VBG'),
     ('PRESPART', 'NONE', 'VERB')],
    ]

# Length 2 rules:
grammarRules2 = [    
    [None,                                       # Active, future simple   ('will ask')
     ('in', futureMod), ('==', 'MD'),
     None, ('in', verbsPresent+['VB']),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Active, modal + base form  ('would ask')
     ('in', allMod), ('==', 'MD'),
     None, ('in', verbsPresent+['VB']),
     ('NONE', 'NONE', 'VERB')],
    [None,                                       # Active, 'do' form in present + base form  ('do ask')
     ('in', do), ('in', verbsPresent),
     None, ('in', ['VB', 'VBP']),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                       # Active, 'do' form in past + base form  ('did ask')
     ('in', do), ('in', verbsPast),
     None, ('in', ['VB', 'VBP']),
     ('PAST', 'NONE', 'VERB')],
    [None,                                       # Active, present progressive ('is V_ing')  
     ('in', be), ('in', verbsPresent),
     None, ('==', 'VBG'),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, past progressive ('was V_ing')  
     ('in', be), ('in', verbsPast),
     None, ('==', 'VBG'),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, infinitive progressive ('be V_ing')  
     ('==', 'be'), ('==', 'VB'),
     None, ('==', 'VBG'),
     ('INFINITIVE', 'PROGRESSIVE', 'VERB')],    
    [None,                                       # Active, past. participle progressive ('been V_ing')  
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PASTPART', 'PROGRESSIVE', 'VERB')],    
    [None,                                       # Active, pres. participle progressive ('being V_ing')  
     ('==', 'being'), None,
     None, ('==', 'VBG'),
     ('PRESPART', 'PROGRESSIVE', 'VERB')],    

    [None,                                       # Active, present perfective ('has V_en')  
     ('in', have), ('in', verbsPresent+['VB']) ,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, past perfective ('had V_en')  
     ('in', have), ('in', verbsPast) ,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, infinitive perfective ('have V_en')  
     ('==', 'have'), ('==', 'VB'),
     None, ('==', 'VBN'),
     ('INFINITIVE', 'PERFECTIVE', 'VERB')],    
    [None,                                       # Active, present participle perfective  ('having V_en')
     ('==', 'having'), ('==', 'VBG'),
     None, ('in', verbsPart),
     ('PRESPART', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, simple past ('was V_en')
     ('in', be), ('in', verbsPast),
     None, ('in', verbsPart),
     ('PAST', 'NONE', 'VERB')],   
    [None,                                       # Passive, simple present ('is V_en')
     ('in', be), ('in', verbsPresent),
     None, ('in', verbsPart),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                       # Passive, infinitive   ('be V_en': 'for a wish to be fulfilled...')
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('INFINITIVE', 'NONE', 'VERB')],
    [None,                                       # Passive, present participle  ('being V_en')
     ('==', 'being'), ('==', 'VBG'),
     None, ('in', verbsPart),
     ('PRESPART', 'NONE', 'VERB')],    
    [None,                                       # Passive, past participle   ('been V_en')
     ('==', 'been'), ('==', 'VBN'),
     None, ('in', verbsPart),
     ('PASTPART', 'NONE', 'VERB')]
    ]

# Lenght 3 rules:
grammarRules3 = [    
    [None,                                       # Active, modal "have to" Present + base form  ('has to ask')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                       # Active, modal "had to" Past + base form  ('had to ask')
     ('in', have), ('in', verbsPast), 
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PAST', 'NONE', 'VERB')],
    [None,                                       # Active, modal "have to" infinitive + base form  ('(to) have to ask')
     ('==', 'have'), ('==', 'VB'), 
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('INFINITIVE', 'NONE', 'VERB')],
    [None,                                       # Active, modal "have to" presPart + base form  ('having to ask')
     ('==', 'having'), None, 
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PRESPART', 'NONE', 'VERB')],
    [None,                                       # Active, fut. progressive ('will be V_ing')   
     ('in', futureMod), None,
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, modal progressive ('must be V_ing')   
     ('in', allMod), None,
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('NONE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, fut. perfective ('will have V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, modal perfective ('must have V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, present perfective-progressive ('has been V_ing')  
     ('in', have), ('in', verbsPresent+['VB']),
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PRESENT', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, past perfective-progressive ('had been V_ing')  
     ('in', have), ('in', verbsPresent),
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PAST', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, infinitive perfective-progressive ('(to) have been V_ing')  
     ('in', have), ('==', 'VB'),
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('INFINITIVE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Passive, modal  ('should be V_en')   
     ('in', allMod), None,
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('NONE', 'NONE', 'VERB')],
    [None,                                       # Passive, future ('will be V_en')   
     ('in', futureMod), None,
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],    
    [None,                                       # Passive, present progr. ('is being V_en')   
     ('in', beFin), ('in', verbsPresent),
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Passive, past progr. ('was being V_en')   
     ('in', beFin), ('in', verbsPast),
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Passive, infinitive, progr. ('be being V_en')   
     ('==', 'be'), ('==', 'VB'),
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('INFINITIVE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Passive, present perf. ('has been V_en')   
     ('in', have),('in', verbsPresent+['VB']),
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, past perf. ('had been V_en')   
     ('in', have),('in', verbsPast),
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, infinitive perf. ('(to) have been V_en')   
     ('==', 'have'),('==', 'VB'),
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('INFINITIVE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, present participle perfective ('having been V_en')   
     ('==', 'having'), None,
     ('==', 'been'), None,
     None, ('==', 'VBN'),
     ('PRESPART', 'PERFECTIVE', 'VERB')]    
    ]

# Lenght 4 rules:
grammarRules4 = [
    [None,                                       # Active, Aux. "DO" pres., modal "have to" + base form  ('does have to ask')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), ('==', 'VB'), 
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PPRESENT', 'NONE', 'VERB')],
    [None,                                       # Active, Aux. "DO" past, modal "have to" + base form  ('did have to ask')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), ('==', 'VB'), 
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PAST', 'NONE', 'VERB')],
    [None,                                       # Passive, present perfective-progressive ('has been being V_en')  
     ('in', have), ('in', verbsPresent+['VB']),
     ('==', 'been'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Passive, past perfective-progressive ('had been being V_en')  
     ('in', have), ('in', verbsPresent),
     ('==', 'been'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, pres. fut. "is GOING TO" + base form  ('is going to ask')
     ('in', be), ('in', verbsPresent),
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Active, past. fut. "was GOING TO" + base form  ('was going to ask')
     ('in', be), ('in', verbsPast),              # Loosing information here (PAST component of 'was going to') which 
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Active, infin., fut. "be GOING TO" + base form  ('be going to ask')
     ('==', 'be'), ('==', 'VB'),                 # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Active, pres. progr., modal "HAVE TO" + be V_ing  ('has to be asking')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, past. progr., modal "HAD TO" + be V_en  ('had to be asking')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, pres., perf., modal "HAVE TO" + have V_en  ('has to have asked')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, past., perf., modal "HAD TO" + have V_en  ('had to have asked')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, pres., modal "HAVE TO" + be V_en  ('has to be asked')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                       # Passive, past., modal "HAD TO" + be V_en  ('had to be asked')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('PAST', 'NONE', 'VERB')],
    [None,                                       # Active, pres., perf., modal "HAVE TO" ('has had to eat')
     ('in', have), ('in', verbsPresent),
     ('==', 'had'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, past., perf., modal "HAD TO" ('had had to eat')
     ('in', have), ('in', verbsPast),
     ('==', 'had'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, infinitive, perf., modal "HAVE TO" ('(to) have had to eat')
     ('==', 'have'), ('==', 'VB'),
     ('==', 'had'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('INFINITIVE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active, fut. modal "HAVE TO": ('will have to V')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                      #  Active, modal + modal "HAVE TO": ('may have to V')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),    
    ('NONE', 'NONE', 'VERB')],
    [None,                                      # Passive, fut. perfective ('will have been V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Passive, modal perfective ('must have been V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),    
    ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active, fut. perfective-progressive ('will have been V_ing')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                      # Active, modal perfective-progressive ('must have been V_ing')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('NONE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                      # Passive, fut. progressive ('will be being V_en')   
     ('in', futureMod), None,                   # Not very productive if at all, but anyway...
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                      # Passive, modal progressive ('must be being V_en')   
     ('in', allMod), None,                      # Not very productive if at all, but anyway...
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('NONE', 'PROGRESSIVE', 'VERB')],
    
    ]

# Lenght 5 rules:
grammarRules5 = [
    [None,                                       # Active, pres., perf_progr., modal "HAVE TO" ('has been having to eat')
     ('in', have), ('in', verbsPresent),
     ('==', 'been'), None,
     ('==', 'having'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PRESENT', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, past., perf_progr., modal "HAVE TO" ('had been having to eat')
     ('in', have), ('in', verbsPast),
     ('==', 'been'), None,
     ('==', 'having'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('PAST', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, infin., perf_progr., modal "HAVE TO" ('(to) have been having to eat')
     ('==', 'have'), ('==', 'VB'),
     ('==', 'been'), None,
     ('==', 'having'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('INFINITIVE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                       # Active, pres. progr., modal "HAVE TO" + be V_ing  ('does have to be asking')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, past. progr., modal "HAD TO" + be V_en  ('did have to be asking')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, pres., perf., modal "HAVE TO" + have V_en  ('does have to have asked')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, past., perf., modal "HAD TO" + have V_en  ('did have to have asked')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, pres., modal "HAVE TO" + be V_en  ('does have to be asked')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'NONE', 'VERB')],
    [None,                                       # Passive, past., modal "HAD TO" + be V_en  ('did have to be asked')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('PAST', 'NONE', 'VERB')],
    [None,                                  # Active, pres., perf_progr., modal "HAVE TO" + have been V_ing  ('has to have been asking')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PRESENT', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                   # Active, past., perf_progr., modal "HAD TO" + have been V_ing ('had to have been asking')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PAST', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                  # Passive, pres., perf., modal "HAVE TO" + have been V_en  ('has to have been asked')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                                   # Passive, past., perf., modal "HAD TO" + have been V_en ('had to have been asked')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                                  # Passive, pres., progr., modal "HAVE TO" + be being V_en  ('has to be being asked')
     ('in', have), ('in', verbsPresent),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                                   # Passive, past., progr., modal "HAD TO" + be being V_en ('had to be being asked')
     ('in', have), ('in', verbsPast),
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, progr., pres. fut. "is GOING TO"  ('is going to be asking')
     ('in', be), ('in', verbsPresent),
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, progr., past. fut. "was GOING TO"  ('was going to be eating')
     ('in', be), ('in', verbsPast),              # Loosing information here (PAST component of 'was going to') which 
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, progr., infin., fut. "be GOING TO"  ('be going to be eating')
     ('==', 'be'), ('==', 'VB'),                 # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                       # Active, perf., pres. fut. "is GOING TO"  ('is going to have asked')
     ('in', be), ('in', verbsPresent),
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, perf., past. fut. "was GOING TO"  ('was going to have asked')
     ('in', be), ('in', verbsPast),              # Loosing information here (PAST component of 'was going to') which 
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Active, perf., infin., fut. "be GOING TO"  ('be going to have asked')
     ('==', 'be'), ('==', 'VB'),                 # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                       # Passive, pres. fut. "is GOING TO"  ('is going to be asked')
     ('in', be), ('in', verbsPresent),
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Passive, past. fut. "was GOING TO"  ('was going to be eaten')
     ('in', be), ('in', verbsPast),              # Loosing information here (PAST component of 'was going to') which 
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                       # Passive, infin., fut. "be GOING TO"  ('be going to be eaten')
     ('==', 'be'), ('==', 'VB'),                 # Loosing information here (INFINITIVE component of 'be going to') which            
     ('==', 'going'), None,                      # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                      # Active, perf., fut. modal "HAVE TO": ('will have had to V')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      #  Active, perf., modal + modal "HAVE TO": ('may have had to V')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsPart),    
    ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active, perf, fut., modal "HAVE TO": ('will have to have V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      #  Active, perf, modal + modal "HAVE TO": ('may have to have V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),    
    ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active, prog., fut., modal "HAVE TO": ('will have to be V_ing')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                      #  Active, prog., modal + modal "HAVE TO": ('may have to be V_ing')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
    ('NONE', 'PROGRESSIVE', 'VERB')],
    [None,                                      # Passive, fut., modal "HAVE TO": ('will have to be V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                      #  Passive, modal + modal "HAVE TO": ('may have to be V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
    ('NONE', 'NONE', 'VERB')],
    [None,                                    # Active, fut., "will be going to"   ('will be going to ask')
     ('in', futureMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, fut. modal "may be going to ask" ('may be going to ask')
     ('in', allMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, fut. progr., modal "will have to" + be V_ing  ('will have to be asking')
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBN'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                    # Passive, fut. modal "will have to be" + V_en  ('will have to be asked')
     ('in', futureMod), None,
     ('==', have), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, progr., modal "may + have to" + be V_ing  ('may have to be asking')
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBN'),
     ('NONE', 'PROGRESSIVE', 'VERB')],
    [None,                                    # Passive, modal "may + have to be" + V_en  ('may have to be asked')
     ('in', futureMod), None,
     ('==', have), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('NONE', 'NONE', 'VERB')],
    [None,                                    # Passive, fut. perf_progr. ('will have been being asked')
     ('in', futureMod), None,                 # Not very productive, if at all
     ('==', 'have'), None,
     ('==', 'been'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                    # Passive, modal  perf_progr. ('may have been being asked')
     ('in', allMod), None,                    # Not very productive if at all.
     ('==', 'have'), None,
     ('==', 'been'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('NONE', 'PERFECTIVE_PROGRESSIVE', 'VERB')]
    ]

# Lenght 6 rules:
grammarRules6 = [
    [None,                           # Active, pres., perf_progr., modal "HAVE TO" + have been V_ing  ('does have to have been asking')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PRESENT', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                            # Active, past., perf_progr., modal "HAD TO" + have been V_ing ('did have to have been asking')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('PAST', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                             # Passive, pres., perf., modal "HAVE TO" + have been V_en  ('does have to have been asked')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PERFECTIVE', 'VERB')],
    [None,                             # Passive, past., perf., modal "HAD TO" + have been V_en ('did have to have been asked')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('PAST', 'PERFECTIVE', 'VERB')],
    [None,                             # Passive, pres., progr., modal "HAVE TO" + be being V_en  ('does have to be being asked')
     ('in', do), ('in', verbsPresent),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PRESENT', 'PROGRESSIVE', 'VERB')],
    [None,                              # Passive, past., progr., modal "HAD TO" + be being V_en ('did have to be being asked')
     ('in', do), ('in', verbsPast),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('PAST', 'PROGRESSIVE', 'VERB')],
    [None,                                    # Active, pres. fut., perf_progr., "is going to have been V_ing" 
     ('in', be), ('in', verbsPresent),        # Not very productive if at all.
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                    # Active, past fut., perf_progr., "was going to have been V_ing" 
     ('in', be), ('in', verbsPast),           # Not very productive if at all.
     ('==', 'going'), None,                   # Loosing information here (PAST component of 'was going to') which 
     ('==', 'to'), ('==', 'TO'),              # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                    # Active, infin., fut., perf_progr., "BE going to have been V_ing" 
     ('in', be), ('==', 'VB'),                # productive?
     ('==', 'going'), None,                   # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'to'), ('==', 'TO'),              # should be encoded in "tense", the same attribute as FUTURE 
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                    # Active, pres. fut., modal "HAVE TO":  "is going to have to V" 
     ('in', be), ('in', verbsPresent),        
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, past fut., modal "HAVE TO":  "was going to have to V" 
     ('in', be), ('in', verbsPast),           # Loosing information here (PAST component of 'was going to') which            
     ('==', 'going'), None,                   # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, infin. fut., modal "HAVE TO":  "(to) be going to have to V" 
     ('in', be), ('==', 'VB'),                # productive?
     ('==', 'going'), None,                   # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'to'), ('==', 'TO'),              # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Passive, pres. fut., perf., "is going to have been V_en" 
     ('in', be), ('in', verbsPresent),        # Not very productive if at all.
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                    # Passive, past fut., perf., "was going to have been V_en" 
     ('in', be), ('in', verbsPast),           # Not very productive if at all.
     ('==', 'going'), None,                   # Loosing information here (PAST component of 'was going to') which 
     ('==', 'to'), ('==', 'TO'),              # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                    # Passive, infin., fut., perf., "BE going to have been V_en" 
     ('in', be), ('==', 'VB'),                # Not very productive if at all.
     ('==', 'going'), None,                   # Loosing information here (INFINITIVE component of 'be going to') which
     ('==', 'to'), ('==', 'TO'),              # should be encoded in "tense", the same attribute as FUTURE
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active, perf, fut., modal "HAVE TO": ('will have had to have V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      #  Active, perf, modal + modal "HAVE TO": ('may have had to have V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),    
    ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                      # Active,perf_ prog., fut., modal "HAVE TO": ('will have had to be V_ing')   
     ('in', futureMod), None,                   # is ASPECT corrent? 
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                      #  Active, perf_prog., modal + modal "HAVE TO": ('may have had to be V_ing')   
     ('in', allMod), None,                      # is ASPECT corrent?
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
    ('NONE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                                      # Passive, perf, fut., modal "HAVE TO": ('will have had to be V_en')   
     ('in', futureMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                      #  Passive, perf, modal + modal "HAVE TO": ('may have had to be V_en')   
     ('in', allMod), None,
     ('==', 'have'), None,
     ('==', 'had'), None, 
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
    ('NONE', 'PERFECTIVE', 'VERB')],
    [None,                                    # Active, perf., fut., "will be going to have V_en" ('will be going to have asked')
     ('in', futureMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                    # Active, perf., modal "may be going to have V_en" ('may be going to have asked')
     ('in', allMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                                    # Active, progr., fut., "will be going to be V_ing" ('will be going to be asking')
     ('in', futureMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                    # Active, progr., fut., modal "may be going to be V_ing" ('may be going to be asking')
     ('in', allMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                                    # Passive, fut., "will be going to be V_en" ('will be going to be asked')
     ('in', futureMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Passive, fut., modal "may be going to be V_en" ('may be going to be asked')
     ('in', allMod), None,
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'NONE', 'VERB')],
    ]

# Lenght 7 rules:
grammarRules7 = [
    [None,                                    # Active, fut., modal + modal "HAVE TO":  "may be going to have to V" 
     ('in', allMod), None, 
     ('in', be), ('in', verbsPresent),        
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'to'), ('==', 'TO'),
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                                    # Active, fut., modal future + modal "HAVE TO":  "will be going to have to V" 
     ('in', futureMod), None,
     ('in', be), ('in', verbsPast),           
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     None, ('in', verbsBase),
     ('FUTURE', 'NONE', 'VERB')],
    [None,                   # Active, perf_progr., fut., "will be going to have been V_ing" ('will be going to have been asking')
     ('in', futureMod), None,      # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                  # Active, perf_progr.,fut.  modal, "may be going to have been V_ing" ('may be going to have been asking') 
     ('in', allMod), None,         # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,     
     None, ('==', 'VBG'),
     ('FUTURE', 'PERFECTIVE_PROGRESSIVE', 'VERB')],
    [None,                  # Passive, perf., fut., "will be going to have been V_en" ('will be going to have been asked')
     ('in', futureMod), None,      # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
    [None,                  # Passive, perf., fut. modal, "may be going to have been V_en" ('may be going to have been asked')
     ('in', allMod), None,         # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'have'), None,
     ('==', 'been'), None,     
     None, ('in', verbsPart),
     ('FUTURE', 'PERFECTIVE', 'VERB')],
   [None,                  # Passive, progr., fut., "will be going to be being V_en" ('will be going to be being asked')
     ('in', futureMod), None,      # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],
    [None,                  # Passive, progr., fut. modal, "may be going to be being V_en" ('may be going to be being asked')
     ('in', allMod), None,         # Any productive?
     ('==', 'be'), None,
     ('==', 'going'), None,
     ('==', 'to'), ('==', 'TO'),
     ('==', 'be'), None,
     ('==', 'being'), None,
     None, ('in', verbsPart),
     ('FUTURE', 'PROGRESSIVE', 'VERB')],        
    ]

