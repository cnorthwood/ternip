import re

"""==============================================

Variables for TimeML tags, attributes and  values

Author: Roser
Last Modified: April 14, 2005
==============================================="""

# TimeBank chunking
# =================

SENTENCE = 's'
CHUNK = re.compile('NG|NP|NGP|ADJP|VG($|-)|VP|IN-MW')#('NG|NGP|VG($|-)|IN-MW')
NOUNCHUNK = 'NG'
VERBCHUNK = 'VG'
TOKEN = 'lex'
POS = 'pos'
CHUNKHEAD = 'HEAD'
CHUNKVERBAL = re.compile('VX|INF')
CHUNKPOSS = 'POS'
ENTITY = re.compile('(ENA|NU)MEX')

# POS Tags
# ========

POS_ADJ = 'JJ'
POS_CD = 'CD'


# TimeBank Processing
# ===================

# Classes declared in Chunk.py and used by ppParser.py, eventParser.py:
ConstituentClassNames = ['Constituent', 'Chunk', 'NounChunk', 'VerbChunk', 'Token', 'AdjectiveToken']
ChunkClassNames = ['Chunk', 'NounChunk', 'VerbChunk']
EventConstituentClassNames = ChunkClassNames + ['AdjectiveToken'] 

# Classes declared in Tag.py and used by timeMLparser.py, eventParser.py
TagClassNames = ['EventTag', 'InstanceTag', 'TimexTag', 'SignalTag', 'TlinkTag', 'SlinkTag', 'AlinkTag']

FORM = 'form'



# TimeML spec
# ===========

TIMEML = 'TimeML'

EVENT = 'EVENT'
EID = 'eid'
CLASS = 'class'
STEM = 'stem'

TIMEX = 'TIMEX3'
TID = 'tid'

SIGNAL = 'SIGNAL'

INSTANCE = 'MAKEINSTANCE'
EVENTID = 'eventID'
EIID = 'eiid'
EPOS = 'epos' #NF_MORPH = 'nf_morph'
TENSE = 'tense'
ASPECT = 'aspect'
MOD = 'modality'
POL = 'polarity'
NO_FINITE = ['PRESPART', 'PASTPART', 'INFINITIVE']
FINITE = ['PRESENT', 'PAST', 'FUTURE']

LINK = re.compile('(S|T|A)LINK')
TLINK = 'TLINK'
SLINK = 'SLINK'
ALINK = 'ALINK'

RELTYPE = 'relType'
EVENT_INSTANCE_ID = 'eventInstanceID'
TIME_ID = 'timeID'
RELATED_TO_EVENT_INSTANCE = 'relatedToEventInstance'
RELATED_TO_TIME = 'relatedToTime'
CONFIDENCE = 'confidence'

NOUN = 'NOUN'
ADJECTIVE = 'ADJECTIVE'
VERB = 'VERB'
NONE = 'NONE'

EMPTY_TAGS = ['MAKEINSTANCE', 'TLINK', 'SLINK', 'ALINK']

COUNTER_FACTIVE = 'COUNTER_FACTIVE'
FACTIVE = "FACTIVE"
MODAL = "MODAL"
CONDITIONAL = "CONDITIONAL"
EVIDENTIAL = "EVIDENTIAL"
NEG_EVIDENTIAL = "NEG_EVIDENTIAL"

INIT = 'INITIATES'
TERM = 'TERMINATES'
CULM = 'CULMINATES'
CONT = 'CONTINUES'
REINIT = 'REINITIATES'
