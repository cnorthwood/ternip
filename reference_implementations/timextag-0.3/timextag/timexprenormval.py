import sys
from timexval import TimePoint

# Here's how I'm going to make this work:
#
# A separate class for every head type:
# - class instance contains attributes for possible data
# - class instance also has a method that processes dependencies
#
# What belongs in the superclass?  What belongs in the subclass?
#
# In the top-level superclass:
# - repr
#
# In the timex-class-level class:
# - functions to handle each of the dependency relations
#
# In the head-level subclass:
# - override dependency relation functions, when necessary
#
# The timex-class-level is useful just for type information; if I later
# find that I'm doing the same thing over and over again, I can move it
# up a level.

class PreNormVal(object):
    v = None
    mod = anchor = None
    def __init__(self, **kw):
        for n in kw:
            getattr(self, n)
            setattr(self, n, kw[n])
    def __repr__(self):
        attrs = ' '.join([ '%s=%s' % (k, v) for (k, v) in self.__dict__.items()
                           if v ])
        typ = str(type(self))
        if 'PreNormVal_' in typ:
            subclass = typ[typ.index('PreNormVal_') + 11:-2]
            return 'PreNormVal_%s(%s)' % (subclass, attrs)
        else:
            return 'PreNormVal(%s)' % attrs

class PreNormVal_recur(PreNormVal):
    pass

class PreNormVal_gendur(PreNormVal):
    pass

class PreNormVal_genpoint(PreNormVal):
    pass

class PreNormVal_duration(PreNormVal):
    pass

class PreNormVal_point(PreNormVal):
    unit = None
    ref_unit = None
    ref_type = None
    offset = None
    def __init__(self, **kw):
        init_fn = getattr(PreNormVal, '__init__', lambda x: None)
        init_fn(self, **kw)
        if len(self.v) == 2:
            self.ref_type, self.datestr = self.v
            self.unit = TimePoint(self.datestr).specific_precision()
        elif len(self.v) == 3:
            self.ref_type, self.ref_unit, self.datestr = self.v
        elif len(self.v) == 4:
            self.ref_type, self.unit, self.n, self.datestr = self.v
            self.ref_unit = self.unit

    def process_deps(self):
        dp = self.dp
        headId = dp.headId
        for label, head, dep in dp.get_deps(headId):
            label_fn_name = label.lower().replace('|', '_')
            label_fn = getattr(self, label_fn_name, lambda x: None)
            label_fn(dep)
    def np_dt(self, depId):
        # 282 NP|DT
        # 141 this
        # 133 the
        #   5 a
        #   3 that
        #   0 an, these, those
        det_toks = [ self.dp.tokens[i] for i in self.dp.id2index_map[depId] ]
        assert len(det_toks) == 1
        det = det_toks[0]
        self.ref_type = {
            'the' : 'ana',
            'this' : 'dex',
            'that' : 'dem',
            'these' : 'dex',
            'those' : 'dem',
            'a' : 'indef',
            'an' : 'indef'
            }.get(det, det)
    def np_jj(self, depId):
        # 233 NP|JJ
        # 129 last
        #  50 next
        #  16 late
        #   9 early
        #   8 third
        #   7 new
        #   4 same
        #   4 past
        #   1 previous
        #   1 later
        #   1 following
        # Do check for Rank first...
        jj_toks = [ self.dp.tokens[i] for i in self.dp.id2index_map[depId] ]
        assert len(jj_toks) == 1
        jj = jj_toks[0]
        ref_type, offset, mod = {
            'last' : ('dex', '-1', None),
            'next' : ('dex', '1', None),
            'late' : (None, None, 'END'),
            'early' : (None, None, 'START'),
            'same' : ('dem', None, None),
            'past' : ('dex', '-1', None),
            'previous' : ('ana', '-1', None),
            'later' : (None, None, None),
            'following' : ('ana', '1', None)
            }.get(jj, (None, None, None))
        if jj == ' later': self.jj = jj
    def np_cd(self, depId):
        # 119 NP|CD
        self.cd = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_nnp(self, depId):
        # 52 NP|NNP
        # 10 saturday
        #  9 monday
        #  8 thursday
        #  7 wednesday
        #  7 tuesday
        #  6 sunday
        #  5 friday
        self.nnp = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_pp(self, depId):
        # 32 NP|PP
        # 18 of
        #  7 after
        #  4 before
        #  2 in
        #  1 for
        self.pp = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_rbr(self, depId):
        # 16 NP|RBR
        # 16 earlier
        self.rbr = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_rb(self, depId):
        # 16 NP|RB
        # 7 later
        # 5 early
        # 3 late
        # 1 earlier
        self.rb = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_nn(self, depId):
        # 7 NP|NN
        # 2 yesterday
        # 2 tomorrow
        # 2 past
        # 1 afternoon
        self.nn = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_sbar(self, depId):
        # 6 NP|SBAR
        # 3 after
        # 1 that
        # 1 began
        # 1 became
        self.sbar = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_qp(self, depId):
        # 2 NP|QP
        # 1 three
        # 1 six
        self.qp = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_np(self, depId):
        # 2 NP|NP
        # 1 year
        # 1 '
        self.np = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_vp(self, depId):
        # 1 NP|VP
        # 1 called
        self.vp = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_vbg(self, depId):
        # 1 NP|VBG
        # 1 coming
        self.vbg = self.dp.tokens[self.dp.id2index_map[depId][0]]
    def np_jjr(self, depId):
        # 1 NP|JJR
        # 1 earlier
        self.jjr = self.dp.tokens[self.dp.id2index_map[depId][0]]

class PreNormVal_point_MONTHNAME(PreNormVal_point):
    def __init__(self, monthname, dp):
        self.monthname = monthname
        self.dp = dp

class PreNormVal_point_DAYNAME(PreNormVal_point):
    def __init__(self, dayname, dp):
        self.dayname = dayname
        self.dp = dp

class PreNormVal_point_SEASON(PreNormVal_point):
    def __init__(self, season, dp):
        self.season = season
        self.dp = dp

class PreNormVal_point_DAYPART(PreNormVal_point):
    def __init__(self, daypart, dp):
        self.daypart = daypart
        self.dp = dp

class PreNormVal_point_deictic_day(PreNormVal_point):
    def __init__(self, offset, dp):
        self.offset = offset
        self.dp = dp

class PreNormVal_point_UNIT(PreNormVal_point):
    def __init__(self, unit, dp):
        self.unit = unit
        self.dp = dp

class PreNormVal_point_UNITS(PreNormVal_point):
    def __init__(self, unit, dp):
        self.unit = unit
        self.dp = dp

class PreNormVal_point_Rank(PreNormVal_point):
    def __init__(self, rank, dp):
        self.rank = rank
        self.dp = dp

class PreNormVal_point_OffsetDir(PreNormVal_point):
    def __init__(self, offset, dp):
        self.offset = offset
        self.dp = dp

class PreNormVal_point_Mod(PreNormVal_point):
    def __init__(self, mod, dp):
        self.mod = mod
        self.dp = dp
