"""Timex recognition using SVM and parse based features.

This module implements an annotator interface for timex recognition.
The annotator is initialized by loading a pre-trained SVM model from files.
New models can be trained by presenting examples to the trainer interface.
"""

import sys, re, os, inspect, cPickle
import svm # this module is part of libSVM
from timexdoc import TimexSpan
import timexwords
from timexwords import getWordCategory
from interval_dict import IntervalDict


######## Annotation interface ########

class TimexRecognitionAnnotator:
    """Perform timex recognition on a document.

    Input:  document text, sentence parses;
    Output: timex spans"""

    def __init__(self, modelFile):
        self.model = loadModel(modelFile)

    def annotateDocument(self, doc):
        doc.fetchParses()
        instseq = getInstancesFromDocument(doc)
        doc.freeParses()
        ylist = runModel(instseq, self.model)
        doc.timexSpans = [ ]
        for i in xrange(len(instseq)):
            if ylist[i] > 0:
                (s, e, sentid, nodeid) = instseq[i][0]
                doc.timexSpans.append(
                  TimexSpan(start=s, end=e, document=doc,
                            txt=doc.txt[s:e], parseNodeId=(sentid, nodeid)))
        doc.timexSpans.sort()


class TimexRecognitionTrainer:
    """Train a new recognition model on a collection of annotated documents.

    Input:  sentence parses, timex spans"""

    def __init__(self, modelFile):
        self.modelFile = modelFile
        self.instgroups = [ ]

    def addDocument(self, doc):
        doc.fetchParses()
        instseq = getInstancesFromDocument(doc)
        doc.freeParses()
        textspanid = IntervalDict()
        for textspan in doc.textSpans:
            textspanid[textspan.start, textspan.end] = 1
        spanmap = { }
        inst_ct = len(instseq)
        timex_ct = 0
        for span in doc.timexSpans:
            spanmap[(span.start, span.end)] = 1
            if textspanid[span.start:span.end] != []:
                timex_ct += 1
        instseq = [ (spanmap.get(loc[0:2], 0), f) for (loc, f) in instseq ]
        aligned_ct = len(filter(lambda (cls, f): cls == 1, instseq))
        self.instgroups.append(instseq)
        return inst_ct, timex_ct, aligned_ct

    def train(self):
        trainModel(self.instgroups, self.modelFile)


######## Dummy annotator that filters parse-aligned spans ########

class TimexAlignmentFilter:
    """Filter already recognized timexes and keep just those
    spans that align perfectly with a parsed phrase/word of the right type.

    Input:  document text, timex spans, sentence parses;
    Output: filtered timex spans"""

    def annotateDocument(self, doc):
        doc.fetchParses()
        instseq = getInstancesFromDocument(doc)
        doc.freeParses()
        origSpans = doc.timexSpans
        spanmap = { }
        for (i, f) in instseq:
            spanmap[(i[0], i[1])] = 1
        doc.timexSpans = filter((
          lambda span:
            (span.start, span.end) in spanmap
          ), origSpans)
        info("keeping %d aligned timexes out of %d input timexes\n" %
          (len(doc.timexSpans), len(origSpans)) )


######## Internal functions ########

def mesg(s):
    import timextool
    timextool.mesg(s)

def info(s):
    import timextool
    timextool.info(s)


def fileStamp(fname):
    """Return MD5 hash of file contents."""
    import md5
    f = file(fname, 'rb')
    s = f.read()
    f.close()
    return md5.md5(s).hexdigest()


######## SVM classification and feature extraction ########

class FeatureMap:
    """Map features to integers and frequency-based features to real numbers."""

    def __init__(self):
        self.idCount = [ ]
        self.nameToId = { }
        self.freqCount = { }
        self.freqPosCount = { }
        self.totCount = 0
        self.totPosCount = 0

    def putFeature(self, s, w=1):
        """Count the occurrence of a feature, and allocate an index if
        it is a new feature. If w=-1, then uncount an occurrence of this
        feature."""
        if s in self.nameToId:
            i = self.nameToId[s]
            self.idCount[i-1] += w
            return i
        self.idCount.append(w)
        i = len(self.idCount)
        self.nameToId[s] = i
        return i

    def getFeature(self, s):
        """Return a positive integer index for a given feature,
        or return 0 if this is an unknown feature."""
        if s in self.nameToId:
            i = self.nameToId[s]
            if self.idCount[i-1] > 0:
                return i
        return 0

    def putFreqFeature(self, s, pos, w=1):
        """Count a positive/negative occurrence of a frequency based feature.
        If w=-1, then uncount an occurrence of this feature."""
        if s not in self.freqCount:
            self.freqCount[s] = 0
            self.freqPosCount[s] = 0
        self.freqCount[s] += w
        self.totCount += w
        if pos:
            self.freqPosCount[s] += w
            self.totPosCount += w

    def getFreqFeature(self, s):
        """Return the fraction of positive occurrences of a given
        frequecy-based feature."""
        if s not in self.freqCount or not self.freqCount[s]:
            return self.totPosCount / float(self.totCount)
        return self.freqPosCount[s] / float(self.freqCount[s])


def getInstancesFromDocument(doc):
    """Extract classification instances from one document; return
    a list of instances. Each classification instance is a tuple
      ( (startpos, endpos, sentid, nodeid), [ features... ] )"""

    # Single words with these POS tags are considered as candidate timex
    goodWordPos = ('JJ', 'NN', 'NNP', 'CD', 'RB')

    # Phrases with these types are considered as candidate timex
    goodPhraseType = ('NP', 'ADVP', 'ADJP', 'PP')

    # Start with an empty list of instances
    instseq = [ ]

    if doc.parsesXml.getRootElement().name != 'charniak-deps':
        raise ValueError("Expected root element 'charniak-deps'")

    # For each sentence
    for sent in doc.parsesXml.xpathEval('//sentence'):
        sentid = sent.prop('id')

        # map span (startpos, endpos) to index in instseq
        instmap = { }

        # Index words and POS tags
        wordList = [ ]
        wordText = { }
        wordPos = { }
        for xnode in sent.xpathEval('.//word'):
            id = xnode.prop('id')
            span = doc.getNodeSpan(xnode)
            ts, te = span.start, span.end
            wordList.append( (ts, te, id) )
            w = xnode.content.lower()
            wcat = getWordCategory(w)
            if wcat:
                wordText[id] = wordText[id] = wcat
            else:
                wordText[id] = w
            wordPos[id] = xnode.prop('tag')
        wordList.sort()

        # Index dependency relations
        wordHead = { }
        wordRel = { }
        for xnode in sent.xpathEval('.//rel'):
            id = xnode.prop('dep')
            wordHead[id] = xnode.prop('head')
            wordRel[id] = xnode.prop('label')

        # Consider single words
        for i in range(len(wordList)):
            ts, te, id = wordList[i]
            # has the word a good POS tag?
            if wordPos[id] not in goodWordPos:
                continue
            # features: word itself
            w1 = wordText[id]
            f = [ ('w', w1),
                  ('w1', w1),
                  ('w1pos', wordPos[id]),
                  ('w2', False) ]
            # features: left context
            wp1 = (i > 0) and wordText[wordList[i-1][2]]
            wp2 = (i > 1) and wordText[wordList[i-2][2]]
            f += [ ('p1', wp1),
                   ('p2', wp2) ]
            # frequency features: first 2-gram and 2-gram crossing start
            f += [ ('f1', (w1, False)),
                   ('f2', (wp1, w1)) ]
            # features: external head and dependency relation
            if id in wordHead:
                f += [ ('dep', wordText[wordHead[id]]),
                       ('deppos', wordPos[wordHead[id]]),
                       ('deprel', wordRel[id]) ]
            # store span features
            if (ts, te) not in instmap:
                instmap[(ts, te)] = len(instseq)
                instseq.append(None)
            instseq[instmap[(ts, te)]] = ((ts, te, sentid, id), f)

        # Consider phrases
        for xnode in sent.xpathEval('.//phrase'):
            phraseid = xnode.prop('id')
            span = doc.getNodeSpan(xnode)
            ts, te = span.start, span.end
            ptype = xnode.prop('type')
            hd = xnode.prop('head')
            # has this phrase a good phrase type ?
            if ptype not in goodPhraseType:
                continue
            # features: phrase type and phrase head word
            f = [ ('type', ptype),
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
                    # features: all words inside the phrase
                    f += [ ('w', wordText[id]) ]
                    if j == 0:
                        # features: first word
                        w1 = wordText[id]
                        f += [ ('w1', w1),
                               ('w1pos', wordPos[id]) ]
                        # features: left context
                        wp1 = (i > 0) and wordText[wordList[i-1][2]]
                        wp2 = (i > 1) and wordText[wordList[i-2][2]]
                        f += [ ('p1', wp1),
                               ('p2', wp2) ]
                        # frequency features: 2-gram crossing start
                        f += [ ('f2', (wp1, w1)) ]
                    elif j == 1:
                        # features: second word
                        w2 = wordText[id]
                        f += [ ('w2', w2) ]
                        # frequency-features: first 2-gram
                        f += [ ('f1', (w1, w2)) ]
                    j += 1
            if j < 2:
                f += [ ('w2', False),
                       ('f1', (w1, False)) ]
            # store span features
            if (ts, te) not in instmap:
                instmap[(ts, te)] = len(instseq)
                instseq.append(None)
            instseq[instmap[(ts, te)]] = ((ts, te, sentid, phraseid), f)

    return instseq


def analyzeInstances(fmap, inst, w=1):
    """Analyze a list of classification instances and update
    the feature map. This is done during training.
    Set w=-1 to untrain a document."""
    for (y, f) in inst:
        for ff in f:
            if ff[0] == 'f1' or ff[0] == 'f2':
                fmap.putFreqFeature(ff, y > 0, w)
                fmap.putFeature(ff[0], w)
            else:
                fmap.putFeature(ff, w)


def featuresToSvm(fmap, f):
    """Map a list of features to an SVM feature vector (dictionary)."""
    fvec = dict()
    for ff in f:
        if ff[0].startswith('f'):
            # frequency based feature
            i = fmap.getFeature(ff[0])
            fvec[i] = fmap.getFreqFeature(ff)
        else:
            # binary feature
            i = fmap.getFeature(ff)
            fvec[i] = 1.0
    return fvec


def trainModel(instgroups, modelFile):
    """Train an SVM model on the given classification instances
    and store the feature map and trained SVM model in files."""

    info("[recog] Training recognition model\n")

    # Construct feature map
    info("[recog] Analyzing features ...\n")
    fmap = FeatureMap()
    for instseq in instgroups:
        analyzeInstances(fmap, instseq, 1)
    info("[recog] %d features\n" % len(fmap.idCount))

    # Save feature map
    info("[recog] Saving feature map ...\n")
    f = file(modelFile + '.map', 'wb')
    cPickle.dump("timexrecog_FeatureMap", f, 2)
    cPickle.dump(fileStamp(inspect.getsourcefile(trainModel)), f, 2)
    cPickle.dump(fileStamp(inspect.getsourcefile(timexwords)), f, 2)
    cPickle.dump(fmap, f, 2)
    f.close()

    # Construct SVM problem
    info("[recog] Constructing SVM problem ...\n")

    # xlist is the list of feature vectors
    # ylist is the list of target classes
    xlist = [ ]
    ylist = [ ]
#    metalist = [ ]
    for instseq in instgroups:
        # un-analyze this document
        analyzeInstances(fmap, instseq, -1)
        # compute feature vectors for this document
#        metalist.append([ (y, featuresToSvm(fmap, f)) for (y, f) in instseq ])
        xlist += [ featuresToSvm(fmap, f) for (y, f) in instseq ]
        ylist += [ y for (y, f) in instseq ]
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

    info("[recog] %d instances from %d documents\n" %
         (len(xlist), len(instgroups)))

    # Train SVM model
    info("[recog] Training SVM model (kernel=LINEAR, C=1) ...\n")
    svmParam = svm.svm_parameter(kernel_type=svm.LINEAR, C=1)
    svmProblem = svm.svm_problem(ylist, xlist)
    del ylist, xlist
    svmModel = svm.svm_model(svmProblem, svmParam)

    # Save SVM model
    info("[recog] Saving SVM model ...\n")
    svmModel.save(modelFile + ".svm")


def loadModel(modelFile):
    """Load a pre-trained classification model and return it."""
    info("[recog] Loading recognition model ...\n");
    f = file(modelFile + '.map', 'rb')
    if cPickle.load(f) != 'timexrecog_FeatureMap':
        raise TypeError("Invalid feature map file")
    if cPickle.load(f) != fileStamp(inspect.getsourcefile(loadModel)):
        mesg("WARNING: [recog] map file does not correspond to current program version\n")
    if cPickle.load(f) != fileStamp(inspect.getsourcefile(timexwords)): 
        mesg("WARNING: [recog] map file does not correspond to word lookup module\n")
    model = dict()
    model['fmap'] = cPickle.load(f)
    f.close()
    model['svm'] = svm.svm_model(modelFile + '.svm')
    return model


def runModel(instseq, model):
    """Classify candidate spans into positive/negative spans using
    a classification model."""

    fmap = model['fmap']
    svmModel = model['svm']

    ylist = len(instseq) * [ None ]
    for i in xrange(len(instseq)):
        (q, f) = instseq[i]
        fdict = featuresToSvm(fmap, f)
        ylist[i] = svmModel.predict(fdict)

    return ylist

# End
