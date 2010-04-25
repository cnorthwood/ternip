import os
import sys
import string
import re
import shelve
import pickle

from ttk_path import TTK_ROOT

def group(*choices):
    return '(' + string.join(choices, '|') + ')'



# EVITA DICTIONARIES & FILES:
# ===========================

DictDIR = os.path.join(TTK_ROOT, 'library', 'evita', 'dictionaries')

DictSemcorEventPickleFilename = os.path.join(DictDIR, 'semcorNomEvent.pickle')
DictSemcorContextPickleFilename = os.path.join(DictDIR, 'semcorNomEventContextProb.pickle')
DictVerbStemPickleFileName = os.path.join(DictDIR, 'verbStems.pickle')

STEM_EXCEPTIONS_FILE = os.path.join(DictDIR, 'stems_exceptions.txt')

WORDNET_NOUNS_FILE = os.path.join(DictDIR, 'index.noun')

wnPrimSenseIsEvent_DBM = os.path.join(DictDIR, 'wnPrimSenseIsEvent.dbm')
wnPrimSenseIsEvent_TXT = os.path.join(DictDIR, 'wnPrimSenseIsEvent.txt')
wnAllSensesAreEvents_DBM = os.path.join(DictDIR, 'wnAllSensesAreEvents.dbm')
wnAllSensesAreEvents_TXT = os.path.join(DictDIR, 'wnAllSensesAreEvents.txt')
wnSomeSensesAreEvents_DBM = os.path.join(DictDIR, 'wnSomeSensesAreEvents.dbm')
wnSomeSensesAreEvents_TXT = os.path.join(DictDIR, 'wnSomeSensesAreEvents.txt')



# WORD LISTS
# ==========

# VERBS:

futureMod = ['will', 'shall', 'wo', "'ll"]
presentMod = ['may','can','ca', 'must']
pastMod = ['might', 'could', 'should', 'would', "'d"]
allMod = ['may','can','ca', 'must','might', 'could', 'should', 'would', "'d", 'ought']
# Future modals excluded
wholeMod = ['may','can','must','might', 'could', 'should', 'would', 'ought']
marginalMod1 = ['dare', 'need'] # when followed by an NP, treated as main events
marginalMod1_ger = ['daring', 'needing']
marginalMod1_part =['dared', 'needed']
marginalMod2 = ['ought', 'used'] # need to be followed by TO + V_base
abbrevMod = ['ca', "'d"]
semiAuxVerbs = ['bound', 'going', 'meant', 'obliged', 'supposed']  # pos: VBN, VBG
semiAuxAdjs = ['able', 'apt', 'bound', 'due', 'likely', 'unlikely', 'unwilling',
'willing'] # pos: JJ
semiAuxPreps = ['about', 'due']   # pos: IN; also accepting RB
semiAux = semiAuxVerbs + semiAuxAdjs + semiAuxPreps
do = ['do', 'does', 'did', 'done']
have = ['has', 'have','had', "'s", "s", "'ve", "'d", 'having']
wholeHave = ['has', 'have','had', 'having']
be = ['is','was','were','am','be',"'s", 'are', "'re","'m",'been', 'being']
beFin = ['is','was','were','am',"'s", 'are', "'re","'m"]
beNotFin = ['be', 'been', 'being']
auxVerbs = be + have + do + allMod + ["s", "re", "m", "ve", "d"]
spuriousVerb = ['_', '-', "'", '"', ')', '(', 'uh']


# VERB types:

perception = group('^see$', '^watch$', '^hear$', '^overhear$', '^listen$', '^view$', '^glimpse$')
report = group('^say$', '^assert$', '^repeat$', '^inform$', '^insist$', '^tell$', '^report$', '^deny''recognize$', '^recognise$', '^confirm$', '^affirm$', '^explain$', '^state$')
iaction = group('^attempt$', '^try$', '^seek$', '^avoid$', '^agree$', '^delay$', '^promise$', '^offer$', '^assure$', '^propose$', '^accept$', '^request$', '^ask$',
'^order$', '^persuade$', '^beg$', '^command$', '^authorize$', '^investigate$', '^postpone$', '^prevent$', '^cancel$', '^claim$', '^allege$', '^urge$', '^indicate$')
istate = group('^wish$', '^believe$', '^expect$', '^want$', '^desire$', '^think$', '^consider$', '^suppose$', '^imagine$', '^reckon$', '^guess$', '^hope$', '^expect$',
'^plan$', '^fear$', '^need$', '^seem$')
aspect1 = group('^begin$', 'began$', '^start$', '^commence$', '^set out$', '^set about$', '^lead off$', '^originate$', '^initiate$')
aspect2 = group('^restart$', '^reinitiate$', '^reignite$')
aspect3 = group('^stop$', '^end$', '^halt$', '^terminate$', '^cease$', '^discontinue$', '^interrupt$', '^quit$', '^abandon$')
aspect4 = group('^continue$', '^keep$', '^proceed$')
aspect5 = group('^finish$', '^complete$')
state = group('^remain$', '^love$', '^be$', '^belong$', '^is$', '^are$', '^was$', '^were$', '^being$')

percepprog = re.compile(perception)
reportprog = re.compile(report)
iactionprog = re.compile(iaction)
istateprog = re.compile(istate)
aspect1prog = re.compile(aspect1)
aspect2prog = re.compile(aspect2)
aspect3prog = re.compile(aspect3)
aspect4prog = re.compile(aspect4)
aspect5prog = re.compile(aspect5)
stateprog = re.compile(state)

# NOUNS:

nounfilter = group('^debt$', '^share$', '^restructure$', '^lease$', '^including$', '^results$', '^times$')
filterprog = re.compile(nounfilter)

# ADJECTIVES:

# Seleceted only those adjs which:
# a) appear in TimeBank
# b) Select for an object
# c) seem to strongly require a complement when heading a predicative complement (e.g., *'She is able' vs. 'She is pleased/ready/available') 
istateAdj = ['able', 'afraid', 'aware', 'confident', 'due', 'eager', 'eligible', 'likely', 'subject', 'sure', 'unable', 'unaware', 'uneager', 'unlikely', 'unsure', 'unwilling', 'willing', 'worth']

# Other candidates to I_STATE:
# 'available', 'careful', 'clear'/'unclear', 'conditional', 'dependent', 'early', 'glad', 'happy', 'moved', 'necessary', 'open', 'optimistic', 'pleased', 'ready', 'receptive', 'responsible', 'safe', 'secret', 'troubled', 'terrible', 'unaffected', 'unavailable', 'unfair', 'unmoved', 'unnecessary'

# SIGNALS:

signals = ['after', 'around', 'at', 'before', 'between', 'during', 'from', 'in', 'into', 'on', 'since', 'through', 'till', 'until']
absoluteSignals = ['after', 'before', 'during', 'every', 'if', 'no', 'none', 'prior', 'till','until', 'when', 'while']

# TIMEX:

timexClues = ['earlier', 'early', 'late', 'later', 'latest', 'last', 'next']

# NEGATION:

negative = ["not","n't", "neither"]

# DETERMINERS:

det1 = ['a', 'an', 'the', 'as']


# POS LISTS:
# ----------

partAdv = ['RB', 'RP', 'RBR']
partInVChunks = ['RB', 'WDT', 'DT', 'JJ', 'PRP']  # particle POS that may be found within verbal chunks
partInVChunks2 = ['RB', 'RBR', 'RBS', 'WDT', 'DT', 'PRP', 'RP', 'IN']  # particle POS that may be found within verbal chunks
verbsPresent = ['VBZ', 'VBP']
verbsPast = ['VBD']
verbsPart = ['VBD', 'VBN']
verbsBase = ['VB', 'VBP']  # Bad POS tagging may assign VBP instead of VB
verbsNoFin = ['VB', 'VBG', 'VBN']
vChunksNoFin = ['VG-INF', 'VG-VBG', 'VG-VBN']
nounsProper = ['NNP', 'NNPS']
nounsCommon = ['NN ', 'NNS','NN']
quotations = ["''", "``"]

nomCommonGroup = group('NN ','NNS','NN$')
nomcomprog = re.compile(nomCommonGroup)

contentPos = re.compile('(NN|JJ|VB)')



# MORPHOLOGY:
# ----------

nomsuf = group('[a-zA-Z]{3,}ations?$','[a-zA-Z]{3,}ptions?$','[a-zA-Z]{3,}ages?$', '[a-zA-Z]{3,}ctions?$','[a-zA-Z]{3,}sions?$') #'al$','als$',
#BK: added requirement for more tokens before 'suffix';
#BK: combined singular and plural into one pattern

nomsufprog = re.compile(nomsuf)




