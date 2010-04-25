import forms

                     ########################                     
                     #                      #
                     # MULTI-CHUNK PATTERNS #
                     #                      #
                     ########################

                     
# Note: Patterns must be sorted from longest to shortest,
#       and from most to less specific.
#
#       Some combinations are 'more possible' than others. But that's not
#       a problems, since the list aims at a recognition task, not a
#       generation one.


# =======
# OBJECTS:
# =======

chunk_NounChunk = {'nodeType': 'NounChunk'}
chunk_AdjChunk = {'nodeType': 'AdjChunk'}

particlesInVChunk = {'nodeType':['Token', 'AdjectiveToken'], 'pos': forms.partInVChunks, 'text':('^', forms.det1)}
particlesInVChunk2 = {'nodeType':'Token', 'pos': forms.partInVChunks2, 'text':('^', forms.det1)}

token_AdjToken = {'nodeType':'AdjectiveToken'}
token_AdjPlain = {'nodeType':'AdjectiveToken', 'pos': 'JJ'}
token_AdjCompar = {'nodeType':'AdjectiveToken', 'pos': 'JJR'}

tokenHAVE_base = {'nodeType':'Token', 'text': 'have', 'pos': forms.verbsBase }
tokenHAD = {'nodeType':'Token', 'text': 'had'}
tokenHAVING = {'nodeType':'Token', 'text': 'having'}

tokenBE_base = {'nodeType':'Token', 'text': 'be', 'pos': forms.verbsBase }
tokenBEING = {'nodeType':'Token', 'text': 'being'}
tokenBEEN = {'nodeType':'Token', 'text': 'been'}

tokenGOING = {'nodeType':'Token', 'text':'going'}

tokenVMODAL1 = {'nodeType':'Token', 'text': forms.marginalMod1}
tokenVMODAL1_ger = {'nodeType':'Token', 'text': forms.marginalMod1_ger}
tokenVMODAL1_part = {'nodeType':'Token', 'text': forms.marginalMod1_part} 

tokenVMODAL2 = {'nodeType':'Token', 'text': forms.marginalMod2}

tokenV_base = {'nodeType':'Token', 'pos': forms.verbsBase }
tokenV_part = {'nodeType':'Token', 'pos': forms.verbsPart}
tokenV_ger = {'nodeType':'Token', 'pos': 'VBG'}

tokenTO = {'nodeType':'Token', 'text':'to'}
tokenNEG = {'nodeType': 'Token', 'text': forms.negative }

punct_COLON = {'nodeType': 'Token', 'text': ','}


# ======================
# RegEx OBJECT PATTERNS:
# ======================

# ;;;;;;;;;;;;;;;;
#  DO (auxiliar)
# ;;;;;;;;;;;;;;;;

doAux = [
    particlesInVChunk, '*',
    '(',
    tokenHAVE_base,
    tokenTO,
    tokenBE_base,
    tokenBEING,
    tokenV_part,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenHAVE_base,
    tokenBEEN,
    tokenV_part,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenHAVE_base,
    tokenBEEN,
    tokenV_ger,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenBE_base,
    tokenV_part,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenHAVE_base,
    tokenV_part,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenBE_base,
    tokenV_ger,
    '|',
    tokenHAVE_base,
    tokenTO,
    tokenV_base,
    '|',
    tokenV_base,
    ')'
    ]

# ;;;;;;;;;;;;;;;;
#  USED TO (past)
# ;;;;;;;;;;;;;;;;

usedTo = [
     particlesInVChunk, '*',
     tokenTO,
     particlesInVChunk, '*',
     tokenV_base,                     # Active, NONE: '[used to] eat'
    ]

# ;;;;;;;
#  MODAL
# ;;;;;;;

modal = [
     particlesInVChunk, '*', 
     '(',
        tokenBE_base,                    # [may] BE GOING to                
        particlesInVChunk, '*',
        tokenGOING,
        tokenTO,
#     '|',
#        tokenBE_base,                    # [may] BE to                     
#        tokenTO,
     '|',
        tokenNEG,
     '|',
        tokenHAVE_base,
        tokenHAD, '?',
        tokenTO,
     '|',
        punct_COLON,
        '.',
        '.',
        '.', '?',
        '.', '?',        
        punct_COLON,
     ')', '*',
     particlesInVChunk, '*',
     '(',
        tokenHAVE_base,                  # Passive, PERFECTIVE_PROGRESSIVE          
        particlesInVChunk, '*',          # '[may] have been being eaten' 
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,
     '|',
        tokenBE_base,                    # Passive, PROGRESSIVE
        particlesInVChunk, '*',          # '[may] be being eaten'
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Passive, PERFECTIVE
        particlesInVChunk, '*',          # '[may] have been eaten'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',          # '[may] have been eating'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_ger,        
     '|',
        tokenBE_base,                    # Passive, NONE
        particlesInVChunk, '*',          # '[may] be eaten'
        tokenV_part,        
     '|',
        tokenBE_base,                    # Active, PROGRESSIVE
        particlesInVChunk, '*',          # '[may] be eating'
        tokenV_ger, 
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE
        particlesInVChunk, '*',          # '[may] have eaten'
        tokenV_part,
     '|',
        tokenV_base,                     # Active, NONE: '[may] eat'
    ')'
     ]



# ;;;;;;;;;;;;;;;;;;;;
#   GOING TO (future)
# ;;;;;;;;;;;;;;;;;;;;

goingTo = [
     particlesInVChunk, '*',
     tokenTO,
     particlesInVChunk, '*',
     '(',
        tokenHAVE_base,                  # Passive, PERFECTIVE
        particlesInVChunk, '*',          # '[be going to] have been eaten'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',          # '[be going to] have been eating'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_ger,        
     '|',
        tokenBE_base,                    # Passive, NONE
        particlesInVChunk, '*',          # '[be going to] be eaten'
        tokenV_part,        
     '|',
        tokenBE_base,                    # Active, PROGRESSIVE
        particlesInVChunk, '*',          # '[be going to] be eating'
        tokenV_ger, 
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE
        particlesInVChunk, '*',          # '[be going to] have eaten'
        tokenV_part,
     '|',
        tokenV_base,                     # Active, NONE: '[be going to] eat'
    ')'
    ]


# ;;;;;;;;
#  TO BE:
# ;;;;;;;;


# BE + Nominal predicative Complement

beNomPredCompl = [
    particlesInVChunk, '*',
    chunk_NounChunk
    ]

# BE + Adjectival predicative complement

beAdjPredCompl1 = [
    particlesInVChunk2, '*',
    token_AdjCompar, '*',
    token_AdjPlain
#     '|',
#     token_AdjCompar
    ]

beAdjPredCompl2 = [
    particlesInVChunk2, '*',
    token_AdjCompar
    ]


# BE going to:

beGoingTo = [
     particlesInVChunk, '*',
     tokenGOING,
     tokenTO,
     particlesInVChunk, '*',
     '(',
        tokenHAVE_base,                  # Passive, PERFECTIVE
        particlesInVChunk, '*',          # '[be going to] have been eaten'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',          # '[be going to] have been eating'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_ger,        
     '|',
        tokenBE_base,                    # Passive, NONE
        particlesInVChunk, '*',          # '[be going to] be eaten'
        tokenV_part,        
     '|',
        tokenBE_base,                    # Active, PROGRESSIVE
        particlesInVChunk, '*',          # '[be going to] be eating'
        tokenV_ger, 
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE
        particlesInVChunk, '*',          # '[be going to] have eaten'
        tokenV_part,
     '|',
        tokenV_base,                     # Active, NONE: '[be going to] eat'
    ')'
    ]

# BE (auxiliar), preceding a regular verb:

beAux_RegVerb = [
    particlesInVChunk, '*',
     '(',
        tokenBEING,                      # Passive, PROGRESSIVE 
        particlesInVChunk, '*',           # '[is] being eaten' 
        tokenV_part,
     '|',
        tokenV_ger,                      # Active, PROGRESSIVE (infinitive): '[be] eating'
     '|',
        tokenV_part,                     # Passive, NONE: '[is] eaten'
    ')'
    ]

# BE (auxiliar), preceding regular verb in a chunk that contains an embedded comment
#                 (e.g., 'she has, I think, to walk faster')
#                 The embedded comment has to extent between 2 and 3 items (excluding the colons).

beAux_RegVerb_EmbedComment = [
        particlesInVChunk, '*',
    punct_COLON,
    '.',
    '.',
    '.', '?',
    punct_COLON,
     '(',
        tokenBEING,                      # Passive, PROGRESSIVE 
        particlesInVChunk, '*',           # '[is] being eaten' 
        tokenV_part,
     '|',
        tokenV_ger,                      # Active, PROGRESSIVE (infinitive): '[be] eating'
     '|',
        tokenV_part,                     # Passive, NONE: '[is] eaten'
    ')'
    ]


# ;;;;;;;;
# TO HAVE:
# ;;;;;;;;

# HAVE TO, preceding:          # TENSE = none/past (depending on morphology of 'have')    
haveTo = [                     # =================
     particlesInVChunk, '*', 
     '(',
         tokenHAD,             # Possibly  presence of 'have' aux.: [have had to]   TENSE = pres./past      
     '|',                      #                                                    ASPECT = perfective
         tokenBEEN,            # Possibly  presence of 'have' aux.: [have been having to]  TENSE = pres./past
         tokenHAVING,          #                                                    ASPECT = perfective_progressive
     ')', '?',
     particlesInVChunk, '*', 
     tokenTO,
     particlesInVChunk, '*',                                                 
     '(',
        tokenBE_base,                    # [have to] BE GOING to                
        tokenGOING,
        tokenTO,
     '|',
        tokenVMODAL2,                    # [have to] OUGHT to, *[have to] USED to 
        tokenTO,
     '|',
        tokenBE_base,                    # [have to] BE to                     
        tokenTO,
     ')', '*',
     particlesInVChunk, '*',
     '(',
        tokenHAVE_base,                  # Passive, PERFECTIVE_PROGRESSIVE          
        particlesInVChunk, '*',          # '[have to] have been being eaten' 
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,
     '|',
        tokenBE_base,                    # Passive, PROGRESSIVE
        particlesInVChunk, '*',          # '[has to] be being eaten'
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Passive, PERFECTIVE
        particlesInVChunk, '*',          # '[have to] have been eaten'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',          # '[have to] have been eating'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_ger,        
     '|',
        tokenBE_base,                    # Passive, NONE
        particlesInVChunk, '*',          # '[has to] be eaten'
        tokenV_part,        
     '|',
        tokenBE_base,                    # Active, PROGRESSIVE
        particlesInVChunk, '*',          # '[has to] be eating'
        tokenV_ger, 
     '|',
        tokenHAVE_base,                  # Active, PERFECTIVE
        particlesInVChunk, '*',          # '[have to] have eaten'
        tokenV_part,
     '|',
        tokenV_base,                     # Active, NONE: '[have to] eat'
    ')', '+']

"""# HAVE (auxiliar), preceding BE going to:
haveAux_BeGoingTo = [                            # TENSE = none/past (depending on morphology of 'have') 
    particlesInVChunk, '*',                      # =================
    tokenBEEN,                            
    tokenGOING,
    tokenTO,
    particlesInVChunk, '*',
     '(',
        tokenHAVE_base,                           # Passive, PERFECTIVE
        particlesInVChunk, '*',                   # '[have been going to] have been eaten'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_part,        
     '|',
        tokenHAVE_base,                           # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',                   # '[have been going to] have been eating'
        tokenBEEN,
        particlesInVChunk, '*', 
        tokenV_ger,        
     '|',
        tokenBE_base,                             # Passive, NONE
        particlesInVChunk, '*',                   # '[has been going to] be eaten'
        tokenV_part,        
     '|',
        tokenBE_base,                             # Active, PROGRESSIVE
        particlesInVChunk, '*',                   # '[has been going to] be eating'
        tokenV_ger, 
     '|',
        tokenHAVE_base,                           # Active, PERFECTIVE
        particlesInVChunk, '*',                   # '[have been going to] have eaten'
        tokenV_part,
     '|',
        tokenV_base,                              # Active, NONE: '[have been going to] eat'
    ')'
    ]"""
    

# HAVE (auxiliar), preceding regular verb:
haveAux_RegVerb = [
    particlesInVChunk, '*',
     '(',
        tokenBEEN,                                                     # Passive, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',                                        # '[have] been being eaten'
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,
     '|',
        tokenBEEN,                                                     # Passive, PERFECTIVE
        particlesInVChunk, '*',                                        # '[have] been eaten'
        tokenV_part,        
     '|',
        tokenBEEN,                                                     # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',                                        # '[have] been eating'
        tokenV_ger,        
     '|',
        tokenV_part,                                                   # Active, PERFECTIVE: '[have] eaten'
    ')'     
    ]

# HAVE (auxiliar), preceding regular verb in a chunk that contains an embedded comment
#                 (e.g., 'she has, I think, to walk faster')
#                 The embedded comment has to extent between 2 and 3 items (excluding the colons).
haveAux_RegVerb_EmbedComment = [
    particlesInVChunk, '*',
    punct_COLON,
    '.',
    '.',
    '.', '?',
    punct_COLON,
     '(',
        tokenBEEN,                                                     # Passive, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',                                        # '[have], I think, been being eaten'
        tokenBEING,
        particlesInVChunk, '*', 
        tokenV_part,
     '|',
        tokenBEEN,                                                     # Passive, PERFECTIVE
        particlesInVChunk, '*',                                        # '[have], I think,  been eaten'
        tokenV_part,        
     '|',
        tokenBEEN,                                                     # Active, PERFECTIVE_PROGRESSIVE
        particlesInVChunk, '*',                                        # '[have], I think,  been eating'
        tokenV_ger,        
     '|',
        tokenV_part,                                                   # Active, PERFECTIVE: '[have], I think,  eaten'
    ')'     
    ]


# ;;;;;;;;
# BECOME
# ;;;;;;;;

# BECOME adj (e.g., "He became famous at the age of 21")

becomeAdj1 = [
     particlesInVChunk2, '*',
     token_AdjCompar, '*',
     token_AdjPlain
     ]

becomeAdj2 = [
     particlesInVChunk2, '*',
     token_AdjCompar
     ]

# ;;;;;;;;
# CONTINUE
# ;;;;;;;;

# CONTINUE adj (e.g., "rate interests continue low this week")

continueAdj1 = [
     particlesInVChunk2, '*',
     token_AdjCompar, '*',
     token_AdjPlain
     ]

continueAdj2 = [
     particlesInVChunk2, '*',
     token_AdjCompar
     ]

# ;;;;;;;;
#   KEEP
# ;;;;;;;;

# KEEP NChunk adj (e.g., "It kept interest rates unchanged")

keepAdj1 = [
     particlesInVChunk2, '*',
     chunk_NounChunk,
#     particlesInVChunk2, '*',
     token_AdjCompar, '*',
     token_AdjPlain
     ]

keepAdj2 = [
     particlesInVChunk2, '*',
     chunk_NounChunk,
#     particlesInVChunk2, '*',
     token_AdjCompar
     ]


# ========================
#  List patterns:
# ========================

patternsGroups = [
    ('BE_FSAs', [beGoingTo, beAux_RegVerb, beAux_RegVerb_EmbedComment]),
    ('BE_N_FSAs', [beNomPredCompl]),
    ('BE_A_FSAs', [beAdjPredCompl1, beAdjPredCompl2]),
    ('BECOME_A_FSAs', [becomeAdj1, becomeAdj2]),
    ('CONTINUE_A_FSAs', [continueAdj1, continueAdj2]),
    ('DO_FSAs', [doAux]),
    ('HAVE_FSAs', [haveTo, haveAux_RegVerb, haveAux_RegVerb_EmbedComment]),
    ('GOINGto_FSAs', [goingTo]),
    ('KEEP_A_FSAs', [keepAdj1, keepAdj2]),
    ('MODAL_FSAs', [modal]),
    ('USEDto_FSAs', [usedTo])
    ]

