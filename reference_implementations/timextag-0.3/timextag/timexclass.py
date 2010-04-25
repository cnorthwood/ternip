"""Timex classification using SVM and parse based features.

This module implements annotator interfaces for timex type classification
and time direction classification. An annotator is initialized by
loading a pre-trained SVM model from files. New models can be trained by
presenting examples to the trainer interface.

Since "timex type" and "time direction" attributes are specific to this
particular annotation system, some method is needed to generate example
data for these attributes. The correct data for these attributes is
fully determined by the correct normalized timex value, the prenormalized
value that are system would produce, and the document timestamp.
Two additional annotator interfaces implement this procedure of inferring
example data from correct normalization results.
"""

import sys, re, time, os, inspect, cPickle
import svm
import timexwords, patternmatch
from timexval import TimePoint
from timexwords import getWordCategory, getWordInfo
from timexref import TimexReferenceTracker


######## Annotation interface ########

class TimexClassAnnotator:
    """Perform category classification on the document's timexes.

    Input:  timex span, sentence parses;
    Output: span.tmxclass"""

    def __init__(self, modelFile):
        self.model = loadModel(modelFile)
        a = self.model['classAttr']
        if a != 'tmxclass':
            raise TypeError(
              "Map file is for '%s' prediction instead of 'tmxclass'" % a)

    def annotateDocument(self, doc):
        for span in doc.timexSpans:
            span.tmxclass = None
        doc.fetchParses()
        params = self.model['params']
        instseq = getInstancesFromDocument(doc, doc.timexSpans, params)
        doc.freeParses()
        # annotate only spans that have nonzero features
        instseq = [ (span, f) for (span, f) in instseq if f ]
        ylist = runModel(instseq, self.model)
        for i in xrange(len(instseq)):
            (span, f) = instseq[i]
            span.tmxclass = ylist[i]


class DirClassAnnotator:
    """Perform direction classification on the document's point-like timexes.

    Input:  timex span, sentence parses, span.tmxclass, document timestamp;
    Output: span.dirclass"""

    def __init__(self, modelFile):
        self.model = loadModel(modelFile)
        a = self.model['classAttr']
        if a != 'dirclass':
            raise TypeError(
              "Map file is for '%s' prediction instead of 'dirclass'" % a)

    def annotateDocument(self, doc):
        if not doc.timestamp:
            #raise ValueError("Document without timestamp: " + repr(doc))
            # don't crash on this (special case for ACE2007)
            mesg('WARNING [class] no timestamp in document ' + doc.name + '\n')
        for span in doc.timexSpans:
            span.dirclass = None
        doc.fetchParses()
        params = self.model['params']
        instseq = getInstancesFromDocument(doc, doc.timexSpans, params)
        doc.freeParses()
        # annotate only point and genpoint timexes with nonzero features
        instseq = [ (span, f) for (span, f) in instseq
                    if f and (span.tmxclass in ('point', 'genpoint')) ]
        # run classifier and store output in dirclass attribute
        ylist = runModel(instseq, self.model)
        for i in xrange(len(instseq)):
            (span, f) = instseq[i]
            span.dirclass = ylist[i]


class TimexClassTrainer:
    """Train a new category classification model on a collection of
    classified documents.

    Input:  timex span, sentence parses, span.tmxclass"""

    def __init__(self, modelFile, params={}):
        self.modelFile = modelFile
        self.params = params
        self.instgroups = [ ]

    def addDocument(self, doc):
        a = filter(lambda span: span.tmxclass is None, doc.timexSpans)
        if a:
            raise ValueError("Timex without target tmxclass: " + repr(a[0]))
        doc.fetchParses()
        instseq = getInstancesFromDocument(doc, doc.timexSpans, self.params)
        doc.freeParses()
        # give an error if the example tmxclass is missing
        noclass = [ span for (span, f) in instseq if (span.tmxclass is None) ]
        if noclass:
            raise ValueError("Timex without tmxclass attribute: " +
                             repr(noclass[0]))
        # train only on spans that have nonzero features and an example class
        instseq = [ (span.tmxclass, f)
                    for (span, f) in instseq
                    if f and span.tmxclass is not None ]
        self.instgroups.append(instseq)

    def train(self):
        trainModel(self.instgroups, self.modelFile, 'tmxclass', self.params)


class DirClassTrainer:
    """Train a new direction classification model on a collection
    of classified documents.

    Input:  timex spans, sentence parses, span.tmxclass, span.dirclass,
            document timestamp"""

    def __init__(self, modelFile, params={}):
        self.modelFile = modelFile
        self.params = params
        self.instgroups = [ ]

    def addDocument(self, doc):
        if not doc.timestamp:
            raise ValueError("Document without timestamp: " + repr(doc))
        doc.fetchParses()
        instseq = getInstancesFromDocument(doc, doc.timexSpans, self.params)
        doc.freeParses()
        # give an error if the example dirclass is missing
        noclass = [ span for (span, f) in instseq
                    if (span.tmxclass == 'point' and not span.dirclass) ]
        if noclass:
            raise ValueError("Timex without dirclass attribute: " +
                             repr(noclass[0]))
        # train only on spans that have nonzero features and an example dirclass
        instseq = [ (span.dirclass, f) for (span, f) in instseq 
                    if f and span.dirclass ]
        self.instgroups.append(instseq)

    def train(self):
        trainModel(self.instgroups, self.modelFile, 'dirclass', self.params)


class InferredTimexClassAnnotator:
    """Assign timex class based on the val attribute.
    This is useful when training a new classifier."""

    def annotateDocument(self, doc):
        for span in doc.timexSpans:
#            if span.val is None:
#                raise ValueError("Timex without val attribute: " + repr(span))
            span.tmxclass = inferTimexClass(span.val, span.set)


class InferredDirClassAnnotator:
    """Assign direction class based on the val attribute, prenormalisation
    result and document timestamp.
    This is useful when training a new classifier."""

    def __init__(self, refmodel):
        if refmodel:
            self.refmodel = refmodel
        else:
            self.refmodel = None

    def annotateDocument(self, doc):
        if not doc.timestamp:
            raise ValueError("Document without timestamp: " + repr(doc))
        docstamp = TimePoint(doc.timestamp)
        ref_tracker = TimexReferenceTracker(docstamp, doc.timexSpans,
                                            refmodel=self.refmodel)
        for span in doc.timexSpans:
#            if span.val is None:
#                raise ValueError("Timex without val attribute: " + repr(span))
            # compare to document timestamp or local context depending
            # on prenorm result
            if span.prenormval:
                t = ref_tracker.resolve(span)
                if t is None: t = docstamp
            else:
                t = docstamp
            span.dirclass = inferDirClass(span.val, span.set, t)
            if span.dirclass is None and span.tmxclass == 'point':
                mesg("WARNING: [class] direction class inference failed: " +
                     "doc=%s val=%s span=%s" % (doc.name, span.val, repr(span.txt)))


######## Internal functions ########

def info(s):
    from timextool import info
    info(s)

def mesg(s):
    from timextool import mesg
    mesg(s)


def inferTimexClass(tmxval, tmxset):
    """Infer the target timex class from the val and set attributes."""

    # Detect not-normalizable timexes
    if not tmxval:
        return ''

    # Detect recurring timexes
    if tmxset:
        return 'recur'

    # Detect generic point-like timexes
    if tmxval in ('PRESENT_REF', 'PAST_REF', 'FUTURE_REF'):
        return 'genpoint'
    if tmxval[0] in 'TX':
        return 'genpoint'

    # Detect duration timexes
    if tmxval[:2] == 'PX' or tmxval[:3] == 'PTX':
        return 'gendur'
    if tmxval[0] == 'P':
        return 'duration'

    # Otherwise it must be a specific point
    return 'point'


def inferDirClass(tmxval, tmxset, reftime):
    """Infer the target direction class from val and reference time."""

    # Skip not-normalized timexes
    if not tmxval:
        return None

    # Skip recurring timexes
    if tmxset:
        return None

    # Handle generic points
    if tmxval == 'PRESENT_REF':
        return 'same'
    elif tmxval == 'PAST_REF':
        return 'before'
    elif tmxval == 'FUTURE_REF':
        return 'after'

    # Skip durations and other non-specific points
    if tmxval[0] in 'PTX':
        return None

    # Handle specific points
    t = TimePoint(tmxval)
    c = t.compare(reftime)
    if c < 0:
        return 'before'
    elif c > 0:
        return 'after'
    elif c == 0:
        return 'same'
    else:
        mesg("WARNING: [class] timex value comparison failed: '%s' vs '%s'" %
          tmxval, str(reftime))
        return None


def fileStamp(fname):
    """Return MD5 hash of file contents."""
    import md5
    f = file(fname, 'rb')
    s = f.read()
    f.close()
    return md5.md5(s).hexdigest()


######## SVM classification and feature extraction ########

class FeatureMap:
    """Map features to integers."""

    def __init__(self):
        self.idCount = [ 0 ]
        self.nameToId = { }

    def putFeature(self, s, w=1):
        if s in self.nameToId:
            i = self.nameToId[s]
            self.idCount[i] += w
            return i
        i = len(self.idCount)
        self.idCount.append(w)
        self.nameToId[s] = i
        return i

    def getFeature(self, s):
        if s in self.nameToId:
            i = self.nameToId[s]
            if self.idCount[i] > 0:
                return i
        return 0


def getInstancesFromDocument(doc, spanList, params):
    """Extract feature vectors for each of the listed spans in one document."""

    goodPhraseType = ('NP', 'ADVP', 'ADJP', 'PP')
    useDateFeatures = params.get('useDateFeatures', 0)
    useVerbFeatures = params.get('useVerbFeatures', 0)

    # Create the list of (initially empty) feature vectors;
    # index the list by (start, end) offset
    instseq = [ (span, [ ]) for span in spanList ]
    instmap = dict([ ( (inst[0].start, inst[0].end), inst )
                     for inst in instseq ])

    # Get document timestamp
    docstamp = None
    if doc.timestamp:
        m = re.match(r'([0-9]{4})-?([0-9]{2})-?([0-9]{2})', doc.timestamp)
        if m:
            docstamp = time.mktime((int(m.group(1)), int(m.group(2)),
                                    int(m.group(3)), 0, 0, 0, 0, 0, -1))
            docstamp = time.localtime(docstamp)
        else:
            print >>sys.stderr, \
              "WARNING: misformed document timestamp doc=%s" % doc.name

    # For each sentence
    for sent in doc.parsesXml.xpathEval('//sentence'):

        # Index words and POS tags
        wordList = [ ]
        wordText = { }
        wordPos = { }
        for xnode in sent.xpathEval('.//word'):
            id = xnode.prop('id')
            span = doc.getNodeSpan(xnode)
            wordList.append( (span.start, span.end, id) )
            w = re.sub(r'[^0-9A-Za-z]', '_', xnode.content).lower()
            wcat = getWordCategory(w)
            if wcat:
                wordText[id] = wcat
            else:
                wordText[id] = w
            wordPos[id] = xnode.prop('tag')
        wordList.sort()

        # Index dependency relations
        wordHead = { }
        wordArg = { }
        wordRel = { }
        for xnode in sent.xpathEval('.//rel'):
            id = xnode.prop('dep')
            hd = xnode.prop('head')
            wordHead[id] = hd
            if hd not in wordArg: wordArg[hd] = [ ]
            wordArg[hd].append(id)
            wordRel[id] = xnode.prop('label')

        def dateFeatures(txt):
            """Compare day name or month name to document timestamp."""
            if not docstamp:
                return [ ]
            txt = txt.lower()
            if len(txt) <= 5 and txt[-1:] == '.': txt = txt[:-1]
            winfo = getWordInfo(txt)
            if winfo and winfo[0][0] == 'DAYNAME':
                wday = winfo[0][1] % 7
                wdayStamp = (docstamp[6] + 1) % 7
                if wday == wdayStamp: return [ ('dayoff', 'same') ]
                if wday < wdayStamp: return [ ('dayoff', 'before') ]
                if wday > wdayStamp: return [ ('dayoff', 'after') ]
            elif winfo and winfo[0][0] == 'MONTHNAME':
                mon = winfo[0][1]
                monStamp = docstamp[1]
                if mon == monStamp: return [ ('monoff', 'same') ]
                if mon < monStamp: return [ ('monoff', 'before') ]
                if mon > monStamp: return [ ('monoff', 'after') ]
            elif txt.isdigit() and len(txt) == 4:
                year = int(txt)
                yearStamp = docstamp[0]
                if year == yearStamp: return [ ('yearoff', 'same') ]
                if year < yearStamp: return [ ('yearoff', 'before') ]
                if year > yearStamp: return [ ('yearoff', 'after') ]
            return [ ]

        def verbFeatures(id):
            """Find verbs related to this phrase."""
            verbTags = ('VB','VBP','VBZ','VBD','VBG','VBN','AUX','AUXG','MD')
            # walk up the dependency chain until we hit a verb
            id = wordHead.get(id)
            step = 0
            while id and wordPos[id] not in verbTags:
                if step > 5: return [ ]
                step += 1
                id = wordHead.get(id)
            if not id:
                return [ ]
            # collect this verb and all directly related verbs
            f = [ ('vb', wordPos[id]), ('vb', wordText[id]) ]
            if id in wordHead:
                t = wordHead[id]
                if wordPos[t] in verbTags:
                    f += [ ('vb', wordPos[t]), ('vb', wordText[t]) ]
            if id in wordArg:
                for t in wordArg[id]:
                    if wordPos[t] in verbTags:
                        f += [ ('vb', wordPos[t]), ('vb', wordText[t]) ]
            return f

        # Consider phrases
        for xnode in sent.xpathEval('.//phrase'):
            span = doc.getNodeSpan(xnode)
            ts, te = span.start, span.end
            if (ts, te) not in instmap:
                continue # not a timex span
            ptype = xnode.prop('type')
            hd = xnode.prop('head')
            if ptype not in goodPhraseType:
                continue # not a good phrase type
            (span, f) = instmap[(ts, te)]
            if f:
                continue # already got features (from enclosing phrase?)
            # features: phrase type and phrase head word
            f += [ ('type', ptype),
                   ('head', wordText[hd]),
                   ('headpos', wordPos[hd]) ]
            # features: external head and dependency relation
            if hd in wordHead:
                f += [ ('dep', wordText[wordHead[hd]]),
                       ('deppos', wordPos[wordHead[hd]]),
                       ('deprel', wordRel[hd]) ]
            # features: words inside the phrase
            j = 0
            for i in range(len(wordList)):
                if wordList[i][0] >= ts and wordList[i][1] <= te:
                    id = wordList[i][2]
                    f += [ ('w', wordText[id]) ]
                    if j == 0:
                        phraseFirstWord = wordText[id]
                        f += [ ('w1', wordText[id]),
                               ('w1pos', wordPos[id]) ]
                        # features: left context
                        if i > 0:
                            f += [ ('p1', wordText[wordList[i-1][2]]) ]
                        else:
                            f += [ ('p1', False) ]
                        if i > 1:
                            f += [ ('p2', wordText[wordList[i-2][2]]) ]
                    elif j == 1:
                        f += [ ('w2', wordText[id]) ]
                    j += 1
            if j < 2:
                f += [ ('w2', False) ]
            # extra features
            if useVerbFeatures:
                f += verbFeatures(hd)
            if useDateFeatures:
                f += dateFeatures(span.__str__())

        # Consider single words
        for i in range(len(wordList)):
            ts, te, id = wordList[i]
            if (ts, te) not in instmap:
                continue # not a timex span
            span, f = instmap[(ts, te)]
            if f:
                continue # already got features from phrase
            # features: word itself, POS tag
            f += [ ('w', wordText[id]),
                   ('w1', wordText[id]),
                   ('w1pos', wordPos[id]),
                   ('w2', False) ]
            # features: left context
            if i > 0:
                f += [ ('p1', wordText[wordList[i-1][2]]) ]
            else:
                f += [ ('p1', False) ]
            if i > 1:
                f += [ ('p2', wordText[wordList[i-2][2]]) ]
            # features: external head and dependency relation
            if id in wordHead:
                f += [ ('dep', wordText[wordHead[id]]),
                       ('deppos', wordPos[wordHead[id]]),
                       ('deprel', wordRel[id]) ]
            # extra features
            if useVerbFeatures:
                f += verbFeatures(id)
            if useDateFeatures:
                f += dateFeatures(span.__str__())

    # Return only instances that have features
    return [ (span, f) for (span, f) in instseq if f ]


def getInstances(baseDir, labelFile):
    """Read data and make classification instances."""

    # Read input labels
    fileNames = [ ]
    goodSpan = { }
    f = file(labelFile)
    for line in f:
        w = line.strip().split(' ')
        if w[0] in ('addToType', 'setSpanProp') and w[4].upper() == labelType:
            fname = w[1]
            ts = int(w[2])
            te = ts + int(w[3])
            if fname not in goodSpan:
                fileNames.append(fname)
                goodSpan[fname] = { }
            if w[0] == 'addToType' and (ts, te) not in goodSpan[fname]:
                goodSpan[fname][(ts, te)] = '_'
            else:
                goodSpan[fname][(ts, te)] = w[5]
    f.close()

    # Generate classification instances
    inst = { }
    for fname in fileNames:
        print >>sys.stderr, fname
        inst[fname] = getFileInstances(fname, baseDir, goodSpan[fname])

    return fileNames, inst


def analyzeInstances(fmap, inst, w=1):
    """Analyze instances from a document."""
    for (c, f) in inst:
        for ff in f:
            fmap.putFeature(ff, w)


def featuresToSvm(fmap, f):
    """Map a list of features to an SVM feature vector (dictionary)."""
    return dict([ (fmap.getFeature(ff), 1.0) for ff in f ])


def trainModel(instgroups, modelFile, classAttr, params):
    """Train an SVM model on the given classification instances.
    Store parameters, features and trained SVM model in files."""

    info("[class] Training model for attribute %s\n" % classAttr)

    # Construct class map
    info("[class] Analyzing target classes ...\n")
    classmap = { }
    for instseq in instgroups:
        for (c, f) in instseq:
            if type(c) is not str:
                raise ValueError("Missing timex " + classAttr + " attribute")
            classmap[c] = 1
    classlist = classmap.keys()
    classlist.sort()
    classmap = dict(zip(classlist, range(len(classlist))))
    info("[class] %d classes\n" % len(classlist))

    # Construct feature map
    info("[class] Analyzing features ...\n")
    fmap = FeatureMap()
    for instseq in instgroups:
        analyzeInstances(fmap, instseq, 1)
    info("[class] %d features\n" % len(fmap.idCount))

    # Save parameters and feature map
    info("[class] Saving feature map ...\n")
    f = file(modelFile + '.map', 'wb')
    cPickle.dump("timexclass_FeatureMap", f, 2)
    cPickle.dump(fileStamp(inspect.getsourcefile(trainModel)), f, 2)
    cPickle.dump(fileStamp(inspect.getsourcefile(timexwords)), f, 2)
    cPickle.dump(classAttr, f, 2)
    cPickle.dump(params, f, 2)
    cPickle.dump(fmap, f, 2)
    cPickle.dump(classlist, f, 2)
    f.close()

    # Construct SVM problem
    info("[class] Constructing SVM problem ...\n")

    # xlist is the list of feature vectors
    # ylist is the list of target classes
    xlist = [ ]
    ylist = [ ]
#    metalist = [ ]
    for instseq in instgroups:
        # un-analyze this document
        analyzeInstances(fmap, instseq, -1)
        # compute feature vectors for this document;
#        metalist.append([ (classmap[c], featuresToSvm(fmap, f))
#                          for (c, f) in instseq ])
        xlist += [ featuresToSvm(fmap, f) for (c, f) in instseq ]
        ylist += [ classmap[c] for (c, f) in instseq ]
        # re-analyze this document
        analyzeInstances(fmap, instseq, 1)

#    featlist = dict()
#    for (n, i) in fmap.nameToId.iteritems():
#        if n[0] not in featlist:
#            featlist[n[0]] = [ i ]
#        else:
#            featlist[n[0]].append(i)
#    featlist = featlist.items()
#    f = file(modelFile + '.meta', 'wb')
#    cPickle.dump(featlist, f, 2)
#    cPickle.dump(metalist, f, 2)
#    f.close()

    info("[class] %d instances from %d documents\n" %
         (len(xlist), len(instgroups)))

    # Train SVM model
    info("[class] Training SVM model (kernel=LINEAR, C=1) ...\n")
    svmParam = svm.svm_parameter(kernel_type=svm.LINEAR, C=1)
    svmProblem = svm.svm_problem(ylist, xlist)
    del ylist, xlist
    svmModel = svm.svm_model(svmProblem, svmParam)

    # Save SVM model
    info("[class] Saving SVM model ...\n")
    svmModel.save(modelFile + '.svm')


def loadModel(modelFile):
    """Load a pre-trained classification model and return it."""
    info("[class] Loading feature map ...\n")
    f = file(modelFile + '.map', 'rb')
    if cPickle.load(f) != "timexclass_FeatureMap":
        raise TypeError("Invalid feature map file")
    if cPickle.load(f) != fileStamp(inspect.getsourcefile(loadModel)):
        mesg("WARNING: [class] map file does not correspond to current program version\n")
    if cPickle.load(f) != fileStamp(inspect.getsourcefile(timexwords)):
        mesg("WARNING: [class] map file does not correspond to word lookup module\n")
    model = dict()
    model['classAttr'] = cPickle.load(f)
    model['params'] = cPickle.load(f)
    model['fmap'] = cPickle.load(f)
    model['classlist'] = cPickle.load(f)
    f.close()
    info("[class] Loading SVM model ...\n")
    model['svm'] = svm.svm_model(modelFile + '.svm')
    return model


def runModel(instseq, model):
    """Classify instances using a classification model."""

    fmap = model['fmap']
    classlist = model['classlist']
    svmModel = model['svm']

    ylist = len(instseq) * [ None ]
    for i in xrange(len(instseq)):
        (span, f) = instseq[i]
        fdict = featuresToSvm(fmap, f)
        y = svmModel.predict(fdict)
        assert y == int(y)
        ylist[i] = classlist[int(y)]

    return ylist


######## Baseline classifiers ########

class BaselineTimexClassAnnotator:
    """Baseline classifier for semantic class."""

    def __init__(self, useHead=1):
        self.useHead = useHead

    def annotateDocument(self, doc):
        if self.useHead:
            doc.fetchParses()
            phraseHead = { }
            for xnode in doc.parsesXml.xpathEval('//phrase'):
                # This condition on phrase type is not strictly required;
                # we do it so that the baseline classifier processes
                # the same set of timexes as the SVM classifier.
                if xnode.prop('type') not in ('NP', 'ADVP', 'ADJP', 'PP'):
                    continue
                span = doc.getNodeSpan(xnode)
                phraseHead[(span.start, span.end)] = \
                  xnode.prop('headword').decode('utf8').lower()
            for xnode in doc.parsesXml.xpathEval('//word'):
                span = doc.getNodeSpan(xnode)
                phraseHead[(span.start, span.end)] = \
                  xnode.content.decode('utf8').lower()
            doc.freeParses()
            for span in doc.timexSpans:
                headWord = phraseHead.get((span.start, span.end))
                if headWord:
                    span.tmxclass = self.classifySpan(span, headWord=headWord)
                else:
                    # drop non-parse-aligned timex
                    span.tmxclass = None
        else:
            for span in doc.timexSpans:
                span.tmxclass = self.classifySpan(span, headWord=None)
            parseInfo = None

    def classifySpan(self, span, headWord):

        tokens = patternmatch.tokenize(span.txt.lower())

        # Find a unit-like word
        unitWord = None
        if headWord:
            if getWordCategory(headWord) in ('UNIT', 'UNITS', 'UNITLY'):
                unitWord = headWord
        else:
            for tok in tokens:
                c = getWordCategory(tok)
                if (c == 'UNITLY') or \
                   (unitWord is None) and (c in ('UNIT', 'UNITS')):
                    unitWord = tok

        # UNITLY -> RECUR
        if unitWord and getWordCategory(unitWord) == 'UNITLY':
            return 'recur'

        # UNITS -> DURATION (or GENDUR)
        if unitWord and getWordCategory(unitWord) == 'UNITS':
            for tok in tokens:
                if tok == unitWord:
                    break
                if tok.isdigit() or getWordCategory(tok) == 'NUMWORD':
                    return 'duration'
            return 'gendur'

        if unitWord:

            # 'every' or 'per' occurs before unit -> RECUR
            for tok in tokens:
                if tok == unitWord:
                    break
                if tok in ('every', 'per'):
                    return 'recur'

            # a deictic word occurs before unit -> POINT
            for tok in tokens:
                if tok == unitWord:
                    break
                if tok in ('this', 'next', 'last', 'coming', 'past'):
                    return 'point'

            # an offset indication follows the unit -> POINT
            for i in range(len(tokens),0,-1):
                if tokens[i-1] == unitWord:
                    break
                if tokens[i-1] in ('ago', 'later', 'earlier',
                                   'before', 'after'):
                    return 'point'
                if tokens[i-1] == 'now' and tokens[i-2] == 'from':
                    return 'point'

            # timex directly preceded by 'in' -> POINT
            #if span.document.txt[:span.start].strip().lower().endswith('in'):
                #return 'point'

            # otherwise -> DURATION
            return 'duration'

        # x-UNIT or x-UNIT-old
        elif '-' in headWord:
            headToks = headWord.split('-')
            if len(headToks) > 1:
                if getWordCategory(headToks[-1]):
                    return 'duration'
                elif headToks[-1] == 'old' and \
                        getWordCategory(headToks[-2]) == 'UNIT':
                    return 'duration'
            return 'point'

        else:

            # non-unit, but contains number or name or unit -> POINT
            for tok in tokens:
                if (tok in ('yesterday', 'today', 'tomorrow')) or \
                   tok.isdigit() or \
                   (getWordCategory(tok) in
                    ('UNIT', 'UNITS',
                     'NUMWORD', 'RANKWORD', 'YYs', 'YYYYs', 'DECADE',
                     'DAYNAME', 'DAYNAMES', 'MONTHNAME', 'SEASON', 'SEASONS',
                     'DAYPART', 'DAYPARTS')):
                    return 'point' 

            # otherwise -> GENPOINT
            return 'genpoint'


class BaselineDirClassAnnotator:
    """Baseline classifier for time direction."""

    class Word:
        __slots__ = [ 'txt', 'tag', 'head', 'firstverb', 'next' ]

    verbTags = [ 'VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN', 'AUX', 'AUXG', 'MD' ]

    reOffsetDirBefore = re.compile(r'.* (before|ago|earlier) ')
    reOffsetDirAfter =  re.compile(r'.* (after|later|from now) ')
    reRefBefore =       re.compile(r'.* (last|past|previous) ')
    reRefAfter =        re.compile(r'.* (next|coming|following) ')
    reRefSame =         re.compile(r'.* (this|same) ')
    reToday =           re.compile(r'.* (today|now) ')
    reYesterday =       re.compile(r'.* (yesterday) ')
    reTomorrow =        re.compile(r'.* (tomorrow) ')
    reThen =            re.compile(r'.* (then) ')
    rePast =            re.compile(r'.* (past|former) ')
    rePresent =         re.compile(r'.* (present) ')
    reFuture =          re.compile(r'.* (future) ')

    def annotateDocument(self, doc):
        # Get document timestamp
        docstamp = None
        if doc.timestamp:
            m = re.match(r'([0-9]{4})-?([0-9]{2})-?([0-9]{2})', doc.timestamp)
            if m:
                docstamp = time.mktime((int(m.group(1)), int(m.group(2)),
                                        int(m.group(3)), 0, 0, 0, 0, 0, -1))
                docstamp = time.localtime(docstamp)
            else:
                print >>sys.stderr, \
                  "WARNING: misformed document timestamp doc=%s" % doc.name

        doc.fetchParses()
        parseInfo = self.extractParseInfo(doc)
        doc.freeParses()
        for span in doc.timexSpans:
            headNode = parseInfo.get((span.start, span.end))
            if headNode is not None:
                span.dirclass = self.classifySpan(span, headNode, docstamp)
            else:
                # drop non-parse-aligned timex
                span.dirclass = None

    def extractParseInfo(self, doc):
        verbTags = self.verbTags
        parseInfo = { }
        for sent in doc.parsesXml.xpathEval('//sentence'):
            wordById = { }
            firstverb = None
            lastw = None
            for xnode in sent.xpathEval('.//word'):
                w = BaselineDirClassAnnotator.Word()
                w.txt = xnode.content.decode('utf8').lower()
                w.tag = xnode.prop('tag')
                w.head = None
                w.next = None
                if w.tag in verbTags:
                    if not firstverb: firstverb = w
                    w.firstverb = firstverb
                else:
                    firstverb = None
                    w.firstverb = None
                if lastw:
                    lastw.next = w
                wordById[xnode.prop('id')] = w
                span = doc.getNodeSpan(xnode)
                parseInfo[(span.start, span.end)] = w
                lastw = w
            for xnode in sent.xpathEval('.//phrase'):
                if xnode.prop('type') not in ('NP', 'ADVP', 'ADJP', 'PP'):
                    continue
                span = doc.getNodeSpan(xnode)
                parseInfo[(span.start,span.end)] = wordById[xnode.prop('head')]
            for xnode in sent.xpathEval('.//rel'):
                wordById[xnode.prop('dep')].head = wordById[xnode.prop('head')]
        return parseInfo

    def classifySpan(self, span, headNode, docstamp):

        tokens = patternmatch.tokenize(span.txt.lower())
        tokenized = ' ' + u' '.join(tokens) + ' '

        # Try to match word patterns
        if self.reOffsetDirBefore.match(tokenized): return 'before'
        if self.reOffsetDirAfter.match(tokenized):  return 'after'
        if self.reRefBefore.match(tokenized): return 'before'
        if self.reRefAfter.match(tokenized):  return 'after'
        if self.reRefSame.match(tokenized):   return 'same'
        if self.reToday.match(tokenized):     return 'same'
        if self.reYesterday.match(tokenized): return 'before'
        if self.reTomorrow.match(tokenized):  return 'after'
        # Experimental below:
        if self.rePast.match(tokenized): return 'before'
        if self.rePresent.match(tokenized): return 'before'
        if self.reFuture.match(tokenized): return 'before'
        if self.reThen.match(tokenized): return 'before'

        # Use date feature
        dateFeatureMap = dict(self.dateFeatures(span.txt.lower(), docstamp))
        if 'yearoff' in dateFeatureMap:
            return dateFeatureMap['yearoff']
        elif 'monoff' in dateFeatureMap and dateFeatureMap['monoff'] == 'same':
            return 'same'
        elif 'dayoff' in dateFeatureMap and dateFeatureMap['dayoff'] == 'same':
            return 'same'

        # Use tense of closest verb: move up through the dependency chain
        w = headNode
        i = 0
        while w and (i < 10):
            if w.firstverb:
                # reached a verb cluster
                w = w.firstverb
                # (may|might|must) (not)? have VBN -> past
                if w.txt in ('may', 'might', 'must'):
                    if w.next and w.next.txt == 'have' and \
                       w.next.next and w.next.next.tag == 'VBN':
                        return 'before'
                    if w.next and w.next.txt == 'not' and \
                       w.next.next and w.next.next.txt == 'have' and \
                       w.next.next.next and w.next.next.next.tag == 'VBN':
                        return 'before'
                # MD -> future
                if w.tag == 'MD':
                    return 'after'
                # (have|had) (not)? VBN -> past
                if w.txt in ('have', 'had'):
                    if w.next and w.next.tag == 'VBN':
                        return 'before'
                    if w.next and w.next.txt == 'not' and \
                       w.next.next and w.next.next.tag == 'VBN':
                        return 'before'
                # VBD|VBN|was|were|had|did -> past
                if w.tag in ('VBD', 'VBN') or \
                   w.txt in ('was', 'were', 'had', 'did'):
                    return 'before'
                # VBP|VBZ|is|am|are|has|have|do|does -> present
                if w.tag in ('VBP', 'VBZ') or \
                   w.txt in ('is', 'am', 'are', 'has', 'have', 'do', 'does'):
                    return 'same'
                # VB -> future
                if w.tag == 'VB':
                    return 'after'
            w = w.head
            i += 1

        # We have no idea; guess 'before'
        return 'before'

    def dateFeatures(self, txt, docstamp):
        """Compare day name or month name to document timestamp."""
        if not docstamp:
            return [ ]
        txt = txt.lower()
        if len(txt) <= 5 and txt[-1:] == '.': txt = txt[:-1]
        winfo = getWordInfo(txt)
        if winfo and winfo[0][0] == 'DAYNAME':
            wday = winfo[0][1] % 7
            wdayStamp = (docstamp[6] + 1) % 7
            if wday == wdayStamp: return [ ('dayoff', 'same') ]
            if wday < wdayStamp: return [ ('dayoff', 'before') ]
            if wday > wdayStamp: return [ ('dayoff', 'after') ]
        elif winfo and winfo[0][0] == 'MONTHNAME':
            mon = winfo[0][1]
            monStamp = docstamp[1]
            if mon == monStamp: return [ ('monoff', 'same') ]
            if mon < monStamp: return [ ('monoff', 'before') ]
            if mon > monStamp: return [ ('monoff', 'after') ]
        elif txt.isdigit() and len(txt) == 4:
            year = int(txt)
            yearStamp = docstamp[0]
            if year == yearStamp: return [ ('yearoff', 'same') ]
            if year < yearStamp: return [ ('yearoff', 'before') ]
            if year > yearStamp: return [ ('yearoff', 'after') ]
        return [ ]

# End
