import sys
import re
import itertools
import itertools
from patternmatch import *
from timexval import *
from timexwords import getWordInfo, getWordTypeList
from timexnorm import TimexTransducer_point, NumericTransducer
from timexprenormval import *

spaceRe = re.compile(r'''\s+''')
toAsciiRe = re.compile(r'''[^\s -~]''')

###########################

class DependencyParse(object):
    def __init__(self, parsesXml, parseOffsetMap, start, end, lookupFn):
        char2byteMap = invert_map(parseOffsetMap)
        start, end = char2byteMap.get(start, -1), char2byteMap.get(end, 0) - 1
        (self.headId, self.headPos, self.phraseType, self.ids, self.words, \
         xmlDependencyTriples) = extractDepInfo(parsesXml, start, end)
        # Force words to ASCII
        self.parseTokens = zip(
            self.ids,
            [ str(toAsciiRe.sub('*', w)).lower() for w in self.words ])
        # Tokenize words as patternmatch tokens and map to ids
        i = 0
        self.id2index_map = dict()
        self.index2id_map = dict()
        self.tokens = []
        for id, toks in [ (id, tokenize(pt)) for (id, pt) in self.parseTokens ]:
            for tok in toks:
                self.tokens.append(tok)
                self.id2index_map.setdefault(id, []).append(i)
                self.index2id_map[i] = id
                i += 1
        # Look up tokens as supertokens and map to ids
        self.supertokens = [ [] for tok in self.tokens ]
        self.id2supertoken_map = None
        for i in range(len(self.tokens)):
            tok = self.tokens[i]
            w = lookupFn(tok)
            if w:
                for (typ, val) in w:
                    self.supertokens[i].append(
                        SuperToken(start=i, end=i+1, name=typ, val=val,
                                   raw=tok))

        # Convert dependency triples to maps
        #self.id2rel_map = dict()
        #self.id2invrel_map = dict()
        #for t in xmlDependencyTriples:
            #label, head, dep = t.prop('label'), t.prop('head'), t.prop('dep')
            #self.id2rel_map.setdefault(head, []).append((dep, label))
            #self.id2invrel_map.setdefault(dep, []).append((head, label))
        # Convert XML dependency triples to tuples
        self.dependencyTriples = []
        for triple in xmlDependencyTriples:
            self.dependencyTriples.append(
                (triple.prop('label'), triple.prop('head'), triple.prop('dep')))

    def run_numbers(self):
        num_trans = NumericTransducer(self.tokens, self.supertokens,
                                      getWordTypeList())
        offsets = num_trans.num_offset()
        self.id2supertoken_map = dict()
        for sts in self.supertokens:
            for st in sts:
                for i in range(st.start, st.end):
                    self.id2supertoken_map.setdefault(
                        self.index2id_map[i],
                        []).append(st)

    def partition_tokens(self, id):
        num_pred = lambda st: st.name in ('NUMXX', 'NUMXXX', 'NUMXXX0',
                                          'NUM12', 'NUM24', 'NUM31', 'NUM60',
                                          'NUM', 'NUMWORD', 'RANKWORD',
                                          'NumberWords', 'SegmentedNumbers', 
                                          'Rank', 'Num31OrRank')
        indices = self.id2index_map[id]
        tok_pairs = zip([ self.tokens[i] for i in indices ],
                        [ self.supertokens[i] for i in indices ])
        num_tok_pairs, non_num_tok_pairs = \
            split_lst(lambda (t, st): st and all(num_pred, st), tok_pairs)
        word_tok_pairs, punc_tok_pairs = \
            split_lst(lambda(t, st): t.isalnum(), non_num_tok_pairs)
        if self.id2supertoken_map:
            cover_stoks = filter(lambda st: st.start not in indices,
                                 self.id2supertoken_map.get(id, []))
        else:
            cover_stoks = []
        return word_tok_pairs, num_tok_pairs, punc_tok_pairs, cover_stoks

    def get_deps(self, id):
        return filter(lambda (label, head, dep): head == id,
                      self.dependencyTriples)
    def get_label_deps(self, id, rel):
        return filter(lambda (label, head, dep): head == id and label == rel,
                      self.dependencyTriples)
    def get_heads(self, id):
        return filter(lambda (label, head, dep): dep == id,
                      self.dependencyTriples)
    def get_label_heads(self, id, rel):
        return filter(lambda (label, head, dep): dep == id and label == rel,
                      self.dependencyTriples)

    def triple2dep_tokens(self, (label, head, dep)):
        return [ self.tokens[i] for i in self.id2index_map[dep] ]
    def triple2dep_supertokens(self, (label, head, dep)):
        return flatten([ self.supertokens[i] for i
                         in self.id2supertokens_map[dep] ])

    def get_dep_tok(self, id, token):
        return filter(lambda tr: token in self.triple2dep_tokens(tr),
                      get_deps(id))
    def get_dep_stok(self, id, name):
        return filter(lambda tr: some(lambda st: st.name == name,
                                      self.triple2dep_supertokens(tr)),
                      dep_deps(id))

###################
#
###################

def extractDepInfo(parsesXml, start, end):
    words = parsesXml.xpathEval('//word[@rstart="%s" and @rend="%s"]' %
                                (start, end))
    if words:
        headId = words[0].prop('id')
        headPos = words[0].prop('tag')
        phraseType = 'word'
        ids = [ word.prop('id') for word in words ]
        words = [ word.get_content() for word in words ]
        return headId, headPos, phraseType, ids, words, []
    phrases = parsesXml.xpathEval('//phrase[@rstart="%s" and @rend="%s"]' %
                                  (start, end))
    if phrases:
        phrase = phrases[0]
        phraseType = phrase.prop('type')
        sentId = phrase.xpathEval('ancestor::sentence')[0].prop('id')
        headId = phrase.prop('head')
        headPos = phrase.xpathEval('.//word[@id="%s"]' % headId)[0].prop('tag')
        words = phrase.xpathEval('.//word')
        ids = [ word.prop('id') for word in words ]
        words = [ word.get_content() for word in words ]
        dependencyTriples = filter(
            lambda t: t.prop('head') in ids and t.prop('dep') in ids,
            parsesXml.xpathEval('//sentence[@id="%s"]/rel' % sentId))
        return headId, headPos, phraseType, ids, words, dependencyTriples
    return None, None, None, [], [], []

#############################
# Pre-normalization annotator
#############################

class ParsePreNormAnnotator:
    """Perform pre-normalization on the document's timex spans,
    using parse information rather than regexps.

    Input: span.tmxclass, span.txt, doc.parsesXml
    Output: span.prenorm, span.mod, span.anchorDir"""

    def annotateDocument(self, doc):
        # For each timex span
        for span in doc.timexSpans:
            span.prenorm = span.mod = span.anchorDir = None

            # Skip span if it has no tmxclass attribute
            if span.tmxclass is None:
                continue

            v = None
            if span.tmxclass == '':
                span.tmxclass = 'unknown'
            if span.tmxclass == '':
                # Negative class (not-normalizable timex)
                #print >>sys.stderr, spaceRe.sub(' ', span.txt), '\n'
                v = None
            else:
                # Get dependency triples within timex span
                start, end = span.start, span.end
                span.dp = DependencyParse(doc.parsesXml, doc.parseOffsetMap,
                                          start, end, getWordInfo)
                # Run pre-normalization patterns
                #(v, mod, anchor) = parseTimex(span.dp, span.tmxclass)
                v = parseTimex(span.__str__(), span.dp, span.tmxclass)
                if isinstance(v, tuple):
                    pass
                    #print >>sys.stderr, v
                elif isinstance(v, PreNormVal_point):
                    #print >>sys.stderr, \
                        #'\t'.join((spaceRe.sub(' ', span.txt), span.tmxclass,
                                   #v.__repr__()))
                    #for att in ('dt', 'jj', 'cd', 'nnp', 'pp', 'rbr', 'rb',
                                #'nn', 'sbar', 'qp', 'np', 'vp', 'vbg', 'jjr'):
                        #val = getattr(v, att, None)
                        #if val:
                            #print '%s\t%s' % (att, val)
                    if hasattr(v, 'jj'):
                        print span.txt, v.jj
                else:
                    pass
                    #print >>sys.stderr, \
                        #'\t'.join((spaceRe.sub(' ', span.txt), span.tmxclass))
                #raw_input()

            # Store results in attributes
            #if v is None:
                #span.prenorm = ''
            #else:
                #if type(v) is tuple:
                    #v = encodeTuple(v)
                #span.prenorm = v
                #span.mod = mod
                #span.anchorDir = anchor


def parseTimex(timexString, depParse, timexClass):
    # Find pre-normalizer class for this timex class
    handlerName = 'PreNormDepParse_' + timexClass
    handler = parseTimex.func_globals[handlerName]

    # Invoke pre-normalizer
    prenorm = handler(timexString, depParse)
    v = prenorm.go()
    return v

#############################################
# Pre-normalization classes for timex classes
#############################################

class PreNormDepParse_unknown:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def go(self):
        dp = self.depParse
        if dp.phraseType == 'word':
            return 'word:%s' % dp.headPos
        else:
            return dp.phraseType

class PreNormDepParse_recur:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def go(self):
        dp = self.depParse
        if dp.phraseType == 'word':
            return 'word:%s' % dp.headPos
        else:
            return dp.phraseType

class PreNormDepParse_gendur:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def go(self):
        dp = self.depParse
        if dp.phraseType == 'word':
            return 'word:%s' % dp.headPos
        else:
            return dp.phraseType

class PreNormDepParse_duration:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def go(self):
        dp = self.depParse
        if dp.phraseType == 'word':
            return 'word:%s' % dp.headPos
        else:
            return dp.phraseType

class PreNormDepParse_genpoint:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def go(self):
        dp = self.depParse
        if dp.phraseType == 'word':
            return 'word:%s' % dp.headPos
        else:
            return dp.phraseType

class PreNormDepParse_point:
    def __init__(self, timexString, depParse):
        self.timexString = timexString
        self.depParse = depParse
    def np(self):
        dp = self.depParse
        headId = dp.headId
        tok_pairs = self.wordTokens(headId)
        assert len(tok_pairs) == 1
        token, stoks = tok_pairs[0]
        if stoks:
            # This ignores the possibility of 'the 30th of March'
            assert len(stoks) == 1
            stok = stoks[0]
            name = stok.name
        else:
            stok = None
            name = token
        head_val = {
            'MONTHNAME' : lambda stok, dp: PreNormVal_point_MONTHNAME(stok.val, dp),
            'DAYNAME' : lambda stok, dp: PreNormVal_point_DAYNAME(stok.val, dp),
            'SEASON' : lambda stok, dp: PreNormVal_point_SEASON(stok.val, dp),
            'DAYPART' : lambda stok, dp: PreNormVal_point_DAYPART(stok.val, dp),
            'UNIT' : lambda stok, dp: PreNormVal_point_UNIT(stok.val, dp),
            'UNITS' : lambda stok, dp: PreNormVal_point_UNITS(stok.val, dp),
            'today' : lambda stok, dp: PreNormVal_point_deictic_day(0, dp),
            'tomorrow' : lambda stok, dp: PreNormVal_point_deictic_day(1, dp),
            'yesterday' : lambda stok, dp: PreNormVal_point_deictic_day(-1, dp),
            'weekend' : lambda stok, dp: PreNormVal_point_UNIT('WE', dp),
            'weekends' : lambda stok, dp: PreNormVal_point_UNITS('WE', dp),
            'beginning' : lambda stok, dp: PreNormVal_point_Mod('START', dp),
            'start' : lambda stok, dp: PreNormVal_point_Mod('START', dp),
            'end' : lambda stok, dp: PreNormVal_point_Mod('END', dp),
            }.get(name, lambda stok, dp: None)(stok, dp)
        if head_val: head_val.process_deps()
        return head_val
    def advp(self):
        # ADVP
        return 'ADVP'
    def nac(self):
        # NAC
        return 'NAC'
    def pp(self):
        # PP
        return 'PP'
    def adjp(self):
        # ADJP
        return 'ADJP'
    def word(self):
        dp = self.depParse
        # Process head
        headId = dp.headId
        tok_pairs = self.wordTokens(headId)
        assert len(tok_pairs) > 0
        if len(tok_pairs) > 1:
            mid_pair, word_pair = split_lst(lambda (t, s): t == 'mid',
                                            tok_pairs)
            assert len(mid_pair) == 1 and len(word_pair) == 1
            token, stoks = word_pair[0]
        else:
            token, stoks = tok_pairs[0]
        if stoks:
            stoken = stoks[0]
            v = {
                'MONTHNAME' : (U_YEAR, stoken.val),
                'SEASON' : (U_YEAR, stoken.val),
                'DAYNAME' : (U_WEEK, stoken.val),
                'DAYPART' : (U_WEEK, stoken.val)
                }[stoken.name]
        else:
            v = {
                'today' : (U_DAY, ''),
                'tomorrow' : (U_DAY, '1'),
                'yesterday' : (U_DAY, '-1'),
                'tonight' : (U_DAY, 'TNI'),
                'overnight' : (U_DAY, 'TNI')
                }[token]
        return v
    def wordTokens(self, id):
        wtps, ntps, ptp, csts = self.depParse.partition_tokens(id)
        return wtps
    def go(self):
        # Force string to pure ASCII
        s = re.sub(r'[^\s -~]', '*', self.timexString)
        timexString = str(s)
        # Split string into tokens
        rawTokens = tokenize(timexString)
        # Do lookup on the tokens
        tokens, supertok = lookupTokens(rawTokens)
        # Run FQ point patterns on tokenized string
        trans = TimexTransducer_point(tokens, supertok, getWordTypeList())
        v, mod, anchor = trans.fq()
        if v != None:
            return v
        # If not FQ:
        dp = self.depParse
        if dp is None:
            return None
        dp.run_numbers()
        v = {
            'word' : self.word,
            'NP' : self.np,
            'ADVP' : self.advp,
            'NAC': self.nac,
            'PP': self.pp,
            'ADJP' : self.adjp,
            None : lambda: v
            }[dp.phraseType]()
        return v

def lookupTokens(tokens):
    """Convert tokens to lower case, look up each token against a list
    of special words and patterns and create a SuperToken for each match."""
    tokens = [ tok.lower() for tok in tokens ]
    supertok = [ [ ] for tok in tokens ]
    for i in range(len(tokens)):
        s = tokens[i]
        # look up the token against a list of special words
        w = getWordInfo(s)
        if w:
            for (typ, val) in w:
                supertok[i].append(
                  SuperToken(start=i, end=i+1, name=typ, val=val, raw=s))
    return tokens, supertok

###################
# Utility functions
###################

def all(pred, lst):
    if lst:
        return reduce(lambda x, y: x and y, [ pred(el) for el in lst ])
    else:
        return True

def some(pred, lst):
    if lst:
        return reduce(lambda x, y: x or y, [ pred(el) for el in lst ])
    else:
        return False

def split_lst(pred, lst):
    pos, neg = [], []
    for el in lst:
        if pred(el):
            pos.append(el)
        else:
            neg.append(el)
    return pos, neg

def flatten(listOfLists):
    return list(itertools.chain(*listOfLists))

def invert_map(mapping):
    newMap = dict()
    for key, val in mapping.items():
        if val in newMap:
            raise KeyError
        newMap[val] = key
    return newMap

