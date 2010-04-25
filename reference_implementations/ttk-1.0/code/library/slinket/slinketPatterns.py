import forms
from timeMLspec import *
from FSA import compileOP




                     ########################                     
                     #                      #
                     # MULTI-CHUNK PATTERNS #
                     #                      #
                     ########################

                     
# Note: Patterns must be sorted from shortest to longest,
#       and from most to less specific.
#
#       Some combinations are 'more possible' than others. But that's not
#       a problems, since the list aims at a recognition task, not a
#       generation one.
#
#
# This module could eventually be conflated with patterns.py, from EVITA.


# =======
# OBJECTS:
# =======

chunk_EVENT_finite = {'nodeType': EventConstituentClassNames, TENSE: ['PAST', 'PRESENT', 'FUTURE']}
chunk_EVENT_finite_NOT_report = {'nodeType': EventConstituentClassNames, TENSE: ['PAST', 'PRESENT', 'FUTURE'], CLASS: ('^', 'REPORTING')}
chunk_EVENT_modal = {'nodeType': EventConstituentClassNames, MOD: forms.wholeMod+['have to'] }
chunk_EVENT_modal_NOT_report = {'nodeType': EventConstituentClassNames, MOD: forms.wholeMod+['have to'], CLASS: ('^', 'REPORTING') }
chunk_EVENT_infinite = {'nodeType': 'VerbChunk', TENSE: 'INFINITIVE' } 
chunk_EVENT_verbal = {'nodeType': 'VerbChunk', 'eventStatus': '1'}
chunk_EVENT_nominal = {'nodeType': 'NounChunk', 'eventStatus': '1'}
chunk_EVENT_adj = {'nodeType': 'AdjectiveToken', 'eventStatus': '1'}
chunk_EVENT_pastPart = {'nodeType': 'VerbChunk', 'eventStatus': '1', 'pos': 'VBN'}
chunk_EVENT_presPart = {'nodeType': 'VerbChunk', 'eventStatus': '1', 'pos': 'VBG'}
chunk_EVENT_participial = {'nodeType': 'VerbChunk', 'eventStatus': '1', 'pos': ['VBG', 'VBN']}
#chunk_EVENT_base = {'nodeType': 'VerbChunk', 'eventStatus': '1', 'pos': 'VB'}
chunk_EVENT_nonfinite = {'nodeType': 'VerbChunk', 'eventStatus': '1', TENSE: 'INFINITIVE', 'pos': 'VB'}
chunk_EVENT_perfective = {'eventStatus': '1', ASPECT: 'PERFECTIVE'} 
chunk_EVENT_perfective_infinitive = {'eventStatus': '1', ASPECT: 'PERFECTIVE', TENSE: 'INFINITIVE'} 
chunk_EVENT_perfective_neg = {'eventStatus': '1', ASPECT: 'PERFECTIVE', POL: 'NEG'} 
chunk_EVENT_past = {'eventStatus': '1', TENSE: 'PAST'} 
chunk_EVENT_present = {'eventStatus': '1', TENSE: 'PRESENT'} 
chunk_EVENT_future = {'eventStatus': '1', TENSE: 'FUTURE'} 

chunk_Participle = {'nodeType': 'VerbChunk', 'pos' : ['VGB', 'VBN']}
chunk_NounChunk = {'nodeType': 'NounChunk'}#, 'eventStatus': ('^', '1')}
chunk_VerbChunk = {'nodeType': 'VerbChunk', 'eventStatus': ('^', '1')}
chunk_VerbChunk_BE = {'nodeType': 'VerbChunk', 'text': forms.be }


token_PARTICIPLE = {'pos' : ['VGB', 'VBN']}
token_PRON = {'nodeType': 'Token', 'pos': ['PP', 'PP$', 'PRP$', 'PRP']} 
token_PREDET = {'nodeType': 'Token', 'pos': 'PDT'}
token_DEMONSTRATIVE = {'nodeType': 'Token', 'text': ['this', 'that', 'these', 'those']}
token_DETERMINER = {'nodeType': 'Token', 'pos': 'DT'}
token_NUMBER = {'nodeType': 'Token', 'pos': 'CD'}
token_ADJECTIVE = {'nodeType': 'Token', 'pos': ['JJ', 'JJR', 'JJS']}
token_ADJ_or_ADV = {'nodeType': 'Token', 'pos': ['JJ', 'RB']}
token_NOUNCHUNK_PARTICLES= {'nodeType': 'Token', 'pos': ['JJ', 'JJR', 'JJS', 'DT', 'PDT', 'POS', 'CD', 'SYM']}
token_POSSESSIVE = {'nodeType': 'Token', 'pos': 'POS'}
token_PREPOSITION = {'nodeType': 'Token', 'pos': 'IN'}
token_AT = {'nodeType': 'Token', 'text':'at'}
token_ABOUT = {'nodeType': 'Token', 'text':'about'}
token_AGAINST = {'text':'against'}
token_FOR = {'text':'for'}
token_FROM = {'text':'from'}
token_IN = {'text':'in'}
token_OF = {'text':'of'}
token_ON = {'text':'on'}
token_OUT = {'text':'out'}
token_OVER = {'text':'over'}
token_TO = {'text':'to', 'pos': 'TO'}
token_WITH = {'text':'with'}
token_WITHOUT = {'text':'without'}
token_ADV_or_similar = {'pos' : ['RB', 'RBR', 'RBS', 'RP', 'JJR']}
token_COMPLEMENTIZER = {'nodeType':'Token', 'text':['that', 'if', 'whether'], 'pos': 'IN'}
token_IF_WHETHER = {'nodeType':'Token', 'text':['if', 'whether']}
token_WH = {'nodeType':'Token', 'text':['who', 'what', 'when', 'which', 'how', 'where', 'why']}
token_WHICH = {'nodeType':'Token', 'text':'which'}
token_THAT = {'nodeType':'Token', 'text':'that'}
token_RelPron = {'nodeType':'Token', 'pos': ['WP', 'WDT', 'WRB']}
token_COORDCONJ = {'nodeType': 'Token', 'pos': 'CC', 'text':['and', 'or']}
token_PUNCT =  {'text': [';', '.', '!', '?', '...']}
token_NOT_CONJ = {'pos': ('^', 'CC')}
token_NOT_PUNCT  = {'text': ('^', [';', '.', '!', '?', '...', '"', '``'])}
token_NOT_PUNCT_or_RelPron = {'text': ('^', [';', '.', '!', '?', '...', '"', '``']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''", "``"])}
token_NOT_PUNCT_or_RelPron_or_VerbChunk = {'text': ('^', [';', '.', '!', '?', '...', '"', '``']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''", "``", 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'])}
token_NOT_PUNCT_or_RelPron_or_THAT = {'text': ('^', [';', '.', '!', '?', '...', '"', '``', 'that']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''", "``"])}
token_NOT_PUNCT_or_RelPron_or_ReportV = {'text': ('^', [';', '.', '!', '?', '...', '"', '``']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''", "``"]), TENSE: ['PAST', 'PRESENT', 'FUTURE'], CLASS: ('^', 'REPORTING')}
#PUNCT2 does not include opening quotes: ``
token_NOT_PUNCT2  = {'text': ('^', [';', '.', '!', '?', '...', '"'])}
token_NOT_PUNCT2_or_RelPron = {'text': ('^', [';', '.', '!', '?', '...', '"']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''"])}
token_NOT_PUNCT2_or_RelPron_or_VerbChunk = {'text': ('^', [';', '.', '!', '?', '...', '"']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''",'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'])}
token_NOT_PUNCT2_or_RelPron_or_THAT = {'text': ('^', [';', '.', '!', '?', '...', '"', 'that']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''"])}
token_NOT_PUNCT2_or_RelPron_or_ReportV = {'text': ('^', [';', '.', '!', '?', '...', '"']), 'pos': ('^', ['WP', 'WDT', 'WRB', '"', "''"]), TENSE: ['PAST', 'PRESENT', 'FUTURE'], CLASS: ('^', 'REPORTING')}
token_COMMA = {'text': ','} 
token_COLON = {'text': ':'} 
token_NOT_COMMA = {'text':('^', [','])} 
token_QUOTES = {'text': ['"', '``', "''"]}
token_SYM = {'pos': 'SYM'}
token_UH = {'pos': 'UH'}


# ======================
# RegEx OBJECT PATTERNS 
# ======================




# FORWARD PATTERNS:
# =================
# =================

# ;;;;;;;;;;;;;;;;
#   THAT clause
# ;;;;;;;;;;;;;;;;

thatClause_that = [
    '(',
         token_COMPLEMENTIZER,
    '|',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,'|',token_QUOTES,')','+', 
         token_COMPLEMENTIZER,
    '|',
         token_NOT_COMMA, '?',
         token_NOT_PUNCT_or_RelPron, '?', 
         token_NOT_PUNCT_or_RelPron, '?', 
         token_COMPLEMENTIZER,
    '|',
         token_COMMA,
         token_COMPLEMENTIZER,
    ')',
    token_NOT_PUNCT_or_RelPron, '?',
    '(',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,')','+',
        '(', chunk_EVENT_finite, '|', chunk_EVENT_modal,')',
   
    '|',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         '(', chunk_EVENT_finite, '|', chunk_EVENT_modal,')',
    '|',
         chunk_VerbChunk_BE,
         token_PREPOSITION, '?',
         chunk_EVENT_nominal,
    ')',
    ]


thatClausePAST_that = [                   #for cases: "I wish *that he came*"
    '(', token_NOT_COMMA, '?',
         token_NOT_PUNCT_or_RelPron, '?', 
         token_NOT_PUNCT_or_RelPron, '?', 
    '|',
         token_COMMA,
    ')',
    token_COMPLEMENTIZER,
    token_NOT_PUNCT_or_RelPron, '?',
    '(',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,')','+',
        chunk_EVENT_past, 
   
    '|',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         chunk_EVENT_past,
    ')',
    ]

thatClausePERFECTIVE_NEG_that = [ #for cases: "I wish *that he had not come*"
    '(', token_NOT_COMMA, '?',
         token_NOT_PUNCT_or_RelPron, '?', 
         token_NOT_PUNCT_or_RelPron, '?', 
    '|',
         token_COMMA,
    ')',
    token_COMPLEMENTIZER,
    token_NOT_PUNCT_or_RelPron, '?',
    '(',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,')','+',
        chunk_EVENT_perfective_neg,
   
    '|',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         chunk_EVENT_perfective_neg,
    ')',
    ]


thatClause_NOT_that = [
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT2_or_RelPron, '?', 
    '(',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         '(', chunk_EVENT_finite, '|', chunk_EVENT_modal,')',
    '|',
         chunk_VerbChunk_BE,
         token_PREPOSITION, '?',
         chunk_EVENT_nominal,
    ')',
    ]

thatClausePAST_NOT_that = [   #for cases: "I wish *he came*"
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    chunk_EVENT_past,
    ]

thatClausePERFECTIVE_NEG_NOT_that = [   #for cases: "I wish *he had not come*"
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    chunk_EVENT_perfective_neg, 
    ]

thatClause_that_QUOTES = [
    '(',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,'|',token_QUOTES,')','?', 
    '|',
        token_COMMA,
    '|',
        token_COLON,
    ')', '?',
    token_COMPLEMENTIZER, 
    token_QUOTES,
    token_NOT_PUNCT_or_RelPron, '?',
    '(',
        '(',chunk_NounChunk,'|',token_PREPOSITION,'|',token_NOUNCHUNK_PARTICLES,')','+',
        '(', chunk_EVENT_finite, '|', chunk_EVENT_modal,')',
   
    '|',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         token_NOT_PUNCT_or_RelPron, '?',
         '(', chunk_EVENT_finite, '|', chunk_EVENT_modal,')',
    '|',
         chunk_VerbChunk_BE,
         token_PREPOSITION, '?',
         chunk_EVENT_nominal,
    ')',
    ]

thatClause_NOT_that_QUOTES = [
    '(',
        token_COMMA,
    '|',
        token_COLON,
    ')', '?',
    token_QUOTES,
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')',
    ]


thatClause_that_NOT_report = [
    # To avoid duplication of Reporting EVENT expressions in the same context.
    # E.g., 'CITING government sources, the official SAID that..."
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_COMPLEMENTIZER, 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?',
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite_NOT_report,'|',chunk_EVENT_modal_NOT_report,')', 
    ]

thatClause_NOT_that_NOT_report = [
    # To avoid duplication of Reporting EVENT expressions in the same context.
    # E.g., 'CITING government sources, the official SAID ..."
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
    token_NOT_PUNCT_or_RelPron_or_ReportV, '?', 
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite_NOT_report,'|',chunk_EVENT_modal_NOT_report,')', 
    ]


thatClause_SIMPLE = [
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')'
    ]


thatClause_NOT_tensed = [
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
#    token_NOT_CONJ,
    chunk_EVENT_nonfinite, #chunk_EVENT_base, 
    ]


thatClause_if = [
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron, '?', 
    token_NOT_PUNCT_or_RelPron, '?', 
    token_IF_WHETHER, 
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')', 
    ]

indirectInterrog = [
#    token_NOT_COMMA, #'?',
    token_WH, 
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')', 
    ]

of_indirectInterrog = [
    token_OF,
#    token_NOT_COMMA, #'?',
    token_WH, 
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
    token_NOT_PUNCT_or_RelPron, '?',
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')', 
    ]



# ;;;;;;;;;;;;;;;;
#   TO clauses
# ;;;;;;;;;;;;;;;;

# TO IMPROVE PERFORMANCE TIME:
# Try merging patterns numbered 1-2, 3-4, 5-6.

# 'to' clause is chunked as a Verb Chunk.
toClause1 = [
    token_ADV_or_similar, '?',
    '(',
       chunk_EVENT_infinite,    # This is the default case.
    '|',
       token_TO,           # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',      # --to overcome chunker errors.
       '(',          
           chunk_EVENT_verbal,
           '|',
           chunk_EVENT_nominal,
       ')',
    ')'
    ]

toClause1_PERFECTIVE = [
    token_ADV_or_similar, '?',
    '(',
       chunk_EVENT_perfective_infinitive,    # This is the default case.
    '|',
       token_TO,           # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',      # --to overcome chunker errors.
       chunk_EVENT_perfective,
    ')'
    ]

# 'to' clause is preceeded by a NounChunk
# or a nominal group of different sort:
# e.g., 'expected you to do it'.
toClause3 = [
    '(', token_PREDET, '|', token_DETERMINER, token_PREPOSITION, ')', '?',
    '(',
        chunk_NounChunk,
        '(',token_PREPOSITION, '|', token_COORDCONJ, ')', 
        chunk_NounChunk,
        '(',  token_PREPOSITION,
              chunk_NounChunk,
        ')', '?',
        '|',
        '(', token_PRON, '|', chunk_NounChunk, ')',
        '|',
        token_DEMONSTRATIVE,
        '|',
            token_DETERMINER,
            '(',token_ADJECTIVE,'|',token_SYM,')','*',
            token_NUMBER, '*',
            '(',
                 chunk_NounChunk,
                 '|',
                 chunk_NounChunk,
                  '(', token_PREPOSITION, '|', token_COORDCONJ, ')',
                 chunk_NounChunk,
            ')', 
    ')',
    '(',
       chunk_EVENT_infinite,    # This is the default case.
    '|',
       token_TO,           # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',      # --to overcome chunker errors.
       '(',          
           chunk_EVENT_verbal,
           '|',
           chunk_EVENT_nominal,
       ')',
    ')'
    ]

toClause3_PERFECTIVE = [
    '(', token_PREDET, '|', token_DETERMINER, token_PREPOSITION, ')', '?',
    '(',
        chunk_NounChunk,
        '(',token_PREPOSITION, '|', token_COORDCONJ, ')', 
        chunk_NounChunk,
        '(',  token_PREPOSITION,
              chunk_NounChunk,
        ')', '?',
        '|',
        '(', token_PRON, '|', chunk_NounChunk, ')',
        '|',
        token_DEMONSTRATIVE,
        '|',
            token_DETERMINER,
            '(',token_ADJECTIVE,'|',token_SYM,')','*',
            token_NUMBER, '*',
            '(',
                 chunk_NounChunk,
                 '|',
                 chunk_NounChunk,
                  '(', token_PREPOSITION, '|', token_COORDCONJ, ')',
                 chunk_NounChunk,
            ')', 
    ')',
    '(',
       chunk_EVENT_perfective_infinitive,    # This is the default case.
    '|',
       token_TO,           # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',      # --to overcome chunker errors.
       chunk_EVENT_perfective,
    ')'
    ]


# 'to' clause is preceeded by a PP
# a PREP + a NounChunk:
toClause5 = [
    token_PREPOSITION,
    token_PREDET, '?',
    chunk_NounChunk,
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    '(',
       chunk_EVENT_infinite,   # This is the default case.
    '|',
       token_TO,               # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',          # --to overcome chunker errors.
       '(',          
           chunk_EVENT_verbal,
           '|',
           chunk_EVENT_nominal,
       ')',
    ')'
    ]

toClause5_PERFECTIVE = [
    token_PREPOSITION,
    token_PREDET, '?',
    chunk_NounChunk,
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    '(',
       chunk_EVENT_perfective_infinitive,   # This is the default case.
    '|',
       token_TO,               # 'to' clause is split into a token TO, and a VerbChunk 
       token_UH, '?',          # --to overcome chunker errors.
       chunk_EVENT_perfective,
    ')'
    ]



# 'to' clause is not tagged as event,
# because its verb is TO BE.
# Instead, the event is a following
# adj or noun
toClause7 = [
    chunk_VerbChunk,
    '(', chunk_EVENT_adj, '|', chunk_EVENT_nominal, ')'
    ]




#
indirectInterrog_nonfinite = [
    token_WH,
    '(', 
        chunk_EVENT_infinite,
    '|',
        token_TO,
        token_UH, '?',
        '(',
            chunk_EVENT_verbal,
        '|',
            chunk_EVENT_nominal,
        ')',
    ')'
    ]

of_indirectInterrog_nonfinite = [
    token_OF,
    token_WH,
    '(', 
        chunk_EVENT_infinite,
    '|',
        token_TO,
        token_UH, '?',
        '(',
            chunk_EVENT_verbal,
        '|',
            chunk_EVENT_nominal,
        ')',
    ')'
    ]


# ;;;;;;;;;;;;;;;;
#   ING clauses
# ;;;;;;;;;;;;;;;;


IngClause = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    chunk_EVENT_presPart
    ]

aboutING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_ABOUT,
    chunk_EVENT_verbal
    ]

atING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_AT,
    chunk_EVENT_verbal
    ]

againstING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_AGAINST,
    chunk_EVENT_verbal
    ]

forING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_FOR,
    chunk_EVENT_verbal
    ]

fromING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk,'?',
    token_FROM,
    chunk_EVENT_verbal
    ]

inING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_IN,
    chunk_EVENT_verbal
    ]

ofING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_OF,
    chunk_EVENT_verbal
    ]

onING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_ON,
    chunk_EVENT_verbal
    ]

toING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_TO,
    chunk_EVENT_verbal
    ]

withING_clause = [
    token_PREPOSITION, '?',
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_WITH,
    chunk_EVENT_verbal
    ]

# ;;;;;;;;;;;;;;;;;;;;;
#   NPs event-denoting
# ;;;;;;;;;;;;;;;;;;;;;

NP_event1 = [
    token_PREDET, '?',
    token_QUOTES, '?',
    '(',token_NOUNCHUNK_PARTICLES,'*',
        chunk_NounChunk,
        token_OF,')','*',
    chunk_EVENT_nominal
    ]

NP_event2 = [
    token_PREDET, '?',
    token_QUOTES, '?',
    token_DETERMINER, '?',
    token_QUOTES, '?',
    '(',token_ADJECTIVE, '|', chunk_Participle, '|',token_SYM,')','*',
    token_QUOTES, '?',
    token_NUMBER, '*',
    token_QUOTES, '?',
    chunk_EVENT_nominal
    ]


# ;;;;;;;;;;;;;;;;;;;;;
#   PPs event-denoting
# ;;;;;;;;;;;;;;;;;;;;;

PP_about = [
    token_PREDET, '?',
    chunk_NounChunk, '+',
    token_ABOUT,
    chunk_EVENT_presPart
    ]

at_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_AT,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle, '|',  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

about_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_ABOUT,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle, '|',  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

for_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_FOR,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle, '|',  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

from_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_FROM,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle, '|',  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

in_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_IN,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

of_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_OF,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

on_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_ON,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

over_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_OVER,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

to_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_TO,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

with_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_WITH,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

without_NPev = [
    token_PREDET, '?',
    chunk_NounChunk, '?',
    token_WITHOUT,
    token_PREDET, '?',
    '(',    chunk_EVENT_nominal,
         '|',
            token_DETERMINER,
            '(',token_ADJECTIVE, '|', chunk_Participle,  '|',token_SYM,')','*',
            token_NUMBER, '*',
            chunk_NounChunk,
    ')',     
    ]

# ;;;;;;;;;;;;;;;;;;;;;;;;
#   Object Complement
# ;;;;;;;;;;;;;;;;;;;;;;;;

# TO BE + event + PastPart
# e.g., 'was expected killed'b
objectCompl_pastPart = [
    '(', token_PREDET, '|', token_DETERMINER, token_PREPOSITION, ')', '?',
    '(',
        chunk_NounChunk,
        '(',token_PREPOSITION, '|', token_COORDCONJ, ')', 
        chunk_NounChunk,
        '(',  token_PREPOSITION,
              chunk_NounChunk,
        ')', '?',
        '|',
        '(', token_PRON, '|', chunk_NounChunk, ')',
        '|',
        token_DEMONSTRATIVE,
        '|',
            token_DETERMINER,
            '(',token_ADJECTIVE,'|',token_SYM,')','*',
            token_NUMBER, '*',
            '(',
                 chunk_NounChunk,
                 '|',
                 chunk_NounChunk,
                 '(', token_PREPOSITION, '|', token_COORDCONJ, ')',
                 chunk_NounChunk,
            ')', 
    ')', '?',
    chunk_EVENT_pastPart
    ]

#e.g., left the children unattended.
objectCompl_adj = [
    '(', token_PREDET, '|', token_DETERMINER, token_PREPOSITION, ')', '?',
    '(',
        chunk_NounChunk,
        '(',token_PREPOSITION, '|', token_COORDCONJ, ')', 
        chunk_NounChunk,
        '(',  token_PREPOSITION,
              chunk_NounChunk,
        ')', '?',
        '|',
        '(', token_PRON, '|', chunk_NounChunk, ')',
        '|',
        token_DEMONSTRATIVE,
        '|',
            token_DETERMINER,
            '(',token_ADJECTIVE,'|',token_SYM,')','*',
            token_NUMBER, '*',
            '(',
                 chunk_NounChunk,
                 '|',
                 chunk_NounChunk,
                 '(', token_PREPOSITION, '|', token_COORDCONJ, ')',
                 chunk_NounChunk,
            ')', 
    ')', '?',
    chunk_EVENT_adj
    ]



# BACKWARD PATTERNS:
# =================
# =================

"""VERY IMPORTANT NOTES on BACKWARD PATTERNS:

   (1) Backward patterns are written assuming that the sentence has been
       reversed. Thus, to look for the slink triggered by 'approved' in
       the sentence '<NG>the <EVENT>transaction</EVENT></NG>
       <VG>has been <EVENT>approved</EVENT></VG>,
       the pattern will be as follows:
       [EVENT, aspect=perfective] + [EVENT, NounChunk]
   
   (2) Backward patterns do also include info about the slinking or alinking
       predicate, so that we can specify info such as its tense and aspect.
       This is particularly necessary for backward s-/a-linking, given that
       the grammatical structure of the clauses is less 'graspable' when
       starting from the end."""



# NP constructions
# ;;;;;;;;;;;;;;;;;


NP_eventAsSubj1 = [   # Backwards pattern: "Trading opened yesterday"
    chunk_EVENT_verbal,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_nominal
    ]

NP_eventAsSubj2 = [   # Backwards pattern: "Trading opened yesterday"
    chunk_EVENT_verbal,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_presPart
    ]

NP_eventAsSubj1_PAST = [   # Backwards pattern: "Trading opened yesterday"
    chunk_EVENT_past,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_nominal
    ]

NP_eventAsSubj2_PAST = [   # Backwards pattern: "Trading opened yesterday"
    chunk_EVENT_past,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_presPart
    ]

NP_eventAsSubj1_PRESENT = [   # Backwards pattern: "Trading opens today"
    chunk_EVENT_present,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_nominal
    ]

NP_eventAsSubj2_PRESENT = [   # Backwards pattern: "Trading opens today"
    chunk_EVENT_present,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_presPart
    ]

NP_eventAsSubj1_FUTURE = [   # Backwards pattern: "Trading will open today"
    chunk_EVENT_future,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_nominal
    ]

NP_eventAsSubj2_FUTURE = [   # Backwards pattern: "Trading will open today"
    chunk_EVENT_future,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_presPart
    ]

NP_eventAsSubj3 = [   # Backwards pattern: "Another accident is inconceivable"
    '(',              #                    SLINK: inconceivable -> accident
        chunk_EVENT_adj,
    '|',
        chunk_EVENT_participial,
    ')',
    chunk_VerbChunk,
    token_ADJ_or_ADV, '?',
#    '(',chunk_NounChunk,'|',token_OF,'|',token_NOUNCHUNK_PARTICLES,')','*', 
    chunk_EVENT_nominal
    ]


# PASSIVE constructions:
# ;;;;;;;;;;;;;;;;;;;;;;

# e.g., <NG>the <EV>transaction</EV></NG> <VG>has been <EV>approved</EV></VG>
passive1 = [
    chunk_EVENT_pastPart,   #<VG>has been <EV>approved</EV></VG>
    chunk_EVENT_nominal       #<NG>the <EV>transaction</EV></NG>
    ]


# RELATIVE CLAUSES:
# ;;;;;;;;;;;;;;;;

# e.g., The *sales*, which is *expected*
relClauseExplicative = [
    chunk_EVENT_pastPart,  # is expected
    token_WHICH,           # which
    token_COMMA,           # ,
    chunk_EVENT_nominal    # the sales   
    ]

# e.g., The *sales*, which had been *expected*
relClauseExplicativePerfective = [
    chunk_EVENT_perfective, # had been expected
    token_WHICH,            # which
    token_COMMA,            # ,
    chunk_EVENT_nominal     # the sales       
    ]

# e.g., The *sales* which is *expected*
relClauseRestrictive = [
    chunk_EVENT_verbal,  # is expected
    token_RelPron,         # which
    chunk_EVENT_nominal    # the sales   
    ]

# e.g., The *sales* which had been *expected*
relClauseRestrictivePerfective = [
    chunk_EVENT_perfective, # had been expected
    token_RelPron,          # which
    chunk_EVENT_nominal     # the sales       
    ]


# REPORTING PATTERNS:
# ===================
# ===================

# ;;;;;;;;;;;;;;;;
#   MAIN SENTENCE
# ;;;;;;;;;;;;;;;;

mainSentence = [
    token_NOT_COMMA, #'?',
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
    token_NOT_PUNCT_or_RelPron_or_THAT, '?', 
#    token_NOT_CONJ,
    '(',chunk_EVENT_finite,'|',chunk_EVENT_modal,')', 
    ]


# ========================
# FSA from Object Patterns:
# ========================


# FORWARD PATTERNS:
# =================
# =================


#  THAT clauses
# ;;;;;;;;;;;;;;

#THAT_clause = compileOP(thatClause, name='thatClause')
THAT_clause_that = compileOP(thatClause_that, name='thatClause_that')
#THAT_clause_that_BE = compileOP(thatClause_that_BE, name='thatClause_that_BE')
THAT_clause_NOT_that = compileOP(thatClause_NOT_that, name='thatClause_NOT_that')
THAT_clausePAST_that = compileOP(thatClausePAST_that, name='thatClausePAST_that')
THAT_clausePERFECTIVE_NEG_that = compileOP(thatClausePERFECTIVE_NEG_that, name='thatClausePERFECTIVE_NEG_that')
THAT_clausePAST_NOT_that = compileOP(thatClausePAST_NOT_that, name='thatClausePAST_NOT_that')
THAT_clausePERFECTIVE_NEG_NOT_that = compileOP(thatClausePERFECTIVE_NEG_NOT_that, name='thatClausePERFECTIVE_NEG_NOT_that')

THAT_clause_that_QUOTES = compileOP(thatClause_that_QUOTES, name='thatClause_that_QUOTES')
THAT_clause_NOT_that_QUOTES = compileOP(thatClause_NOT_that_QUOTES, name='thatClause_NOT_that_QUOTES')
THAT_clause_that_NOT_report = compileOP(thatClause_that_NOT_report, name='thatClause_that_NOT_report')
THAT_clause_N_that_N_report = compileOP(thatClause_NOT_that_NOT_report, name='thatClause_NOT_that_NOT_report')
THAT_clause_SIMPLE = compileOP(thatClause_SIMPLE, name='thatClause_SIMPLE')
THAT_clause_NOT_tensed = compileOP(thatClause_NOT_tensed, name='thatClause_NOT_tensed')

THAT_clause_if = compileOP(thatClause_if, name='thatClause_if')

IND_INTERROG = compileOP(indirectInterrog, name='indirectInterrog')
OF_IND_INTERROG = compileOP(of_indirectInterrog, name='of_indirectInterrog')

#  TO clauses
# ;;;;;;;;;;;;;;

TO_clause1 = compileOP(toClause1, name='toClause1')
TO_clause1_PERFECTIVE = compileOP(toClause1_PERFECTIVE, name='toClause1_PERFECTIVE')
#TO_clause2 = compileOP(toClause2, name='toClause2')
TO_clause3 = compileOP(toClause3, name='toClause3')
TO_clause3_PERFECTIVE = compileOP(toClause3_PERFECTIVE, name='toClause3_PERFECTIVE')
#TO_clause4 = compileOP(toClause4, name='toClause4')
TO_clause5 = compileOP(toClause5, name='toClause5')
TO_clause5_PERFECTIVE = compileOP(toClause5_PERFECTIVE, name='toClause5_PERFECTIVE')
#TO_clause6 = compileOP(toClause6, name='toClause6')
TO_clause7 = compileOP(toClause7, name='toClause7')

IND_INTERROG_nonfin = compileOP(indirectInterrog_nonfinite, name='indirectInterrog_nonfinite')
OF_IND_INTERROG_nonfin = compileOP(of_indirectInterrog_nonfinite, name='of_indirectInterrog_nonfinite')


#  ING clauses
# ;;;;;;;;;;;;;;

ING_clause = compileOP(IngClause, name='IngClause')
#ING_clause2 = compileOP(IngClause2, name='IngClause2')

ABOUT_ING_clause = compileOP(aboutING_clause, name='aboutING_clause')
AT_ING_clause = compileOP(atING_clause, name='atING_clause')
AGAINST_ING_clause = compileOP(againstING_clause, name='againstING_clause')
FOR_ING_clause = compileOP(forING_clause, name='forING_clause')
FROM_ING_clause = compileOP(fromING_clause, name='fromING_clause')
IN_ING_clause = compileOP(inING_clause, name='inING_clause')
OF_ING_clause = compileOP(ofING_clause, name='ofING_clause')
ON_ING_clause = compileOP(onING_clause, name='onING_clause')
TO_ING_clause = compileOP(toING_clause, name='toING_clause')
WITH_ING_clause = compileOP(withING_clause, name='withING_clause')

#  NPs event-denoting
# ;;;;;;;;;;;;;;;;;;;

NP_ev1 = compileOP(NP_event1, name='NP_event1')
NP_ev2 = compileOP(NP_event2, name='NP_event2')

#  PPs event-denoting
# ;;;;;;;;;;;;;;;;;;;

PP_ABOUT = compileOP(PP_about, name='PP_about')

AT_NPev = compileOP(at_NPev, name='at_NPev')
ABOUT_NPev = compileOP(about_NPev, name='about_NPev')
FOR_NPev = compileOP(for_NPev, name='for_NPev')
FROM_NPev = compileOP(from_NPev, name='from_NPev')
IN_NPev = compileOP(in_NPev, name='in_NPev')
OF_NPev = compileOP(of_NPev, name='of_NPev')
ON_NPev = compileOP(on_NPev, name='on_NPev')
OVER_NPev = compileOP(over_NPev, name='over_NPev')
TO_NPev = compileOP(to_NPev, name='to_NPev')
WITH_NPev = compileOP(with_NPev, name='with_NPev')
WITHOUT_NPev = compileOP(without_NPev, name='without_NPev')

#  OBJ COMPLEMENT constructions
# ;;;;;;;;;;;;;;;;;;;;;;

OBJCOMPL_pastPart = compileOP(objectCompl_pastPart, name='objectCompl_pastPart')
OBJCOMPL_adj = compileOP(objectCompl_adj, name='objectCompl_adj')



# BACKWARD PATTERNS:
# =================
# =================

# NP constructions:
# ;;;;;;;;;;;;;;;;;

NP_evAsSubj1 = compileOP(NP_eventAsSubj1, name='NP_eventAsSubj1')
NP_evAsSubj2 = compileOP(NP_eventAsSubj2, name='NP_eventAsSubj2')
NP_evAsSubj1_PAST = compileOP(NP_eventAsSubj1_PAST, name='NP_eventAsSubj1_PAST')
NP_evAsSubj2_PAST = compileOP(NP_eventAsSubj2_PAST, name='NP_eventAsSubj2_PAST')
NP_evAsSubj1_PRESENT = compileOP(NP_eventAsSubj1_PRESENT, name='NP_eventAsSubj1_PRESENT')
NP_evAsSubj2_PRESENT = compileOP(NP_eventAsSubj2_PRESENT, name='NP_eventAsSubj2_PRESENT')
NP_evAsSubj1_FUTURE = compileOP(NP_eventAsSubj1_FUTURE, name='NP_eventAsSubj1_FUTURE')
NP_evAsSubj2_FUTURE = compileOP(NP_eventAsSubj2_FUTURE, name='NP_eventAsSubj2_FUTURE')
NP_evAsSubj3 = compileOP(NP_eventAsSubj3, name='NP_eventAsSubj3')

# PASSIVE constructions:
# ;;;;;;;;;;;;;;;;;;;;;;

# the *transaction* has been *approved*
Passive1 = compileOP(passive1, name='passive1')

# RELATIVE CLAUSES:
# ;;;;;;;;;;;;;;;;

# The *sales*, which had been *expected*
RelClauseExplic = compileOP(relClauseExplicative, name='relClauseExplicative')
RelClauseExplicPerfect = compileOP(relClauseExplicativePerfective, name='relClauseExplicativePerfective')
RelClauseRestric = compileOP(relClauseRestrictive, name='relClauseRestrictive')
RelClauseRestricPerfect = compileOP(relClauseRestrictivePerfective, name='relClauseRestrictivePerfective')

# REPORTING PATTERNS:
# ===================
# ===================

#   MAIN SENTENCE
# ;;;;;;;;;;;;;;;;


MAINsentence = compileOP(mainSentence, name='mainSentence')
