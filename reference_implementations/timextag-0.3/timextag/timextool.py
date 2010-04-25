#!/usr/bin/env python
"""Timex recognition and normalization.

Usage: timextool.py options...
  --inputtxt path      File or dir containing plain text of input document
  --inputenc enc       Encoding for plain text input; defaults to ASCII
  --inputxml path      File or dir containing span markup as stand-off XML
  --inputlabels path   File containing span labels in MinorThird format
  --inputparses path   File or dir containing Charniak parses as stand-off XML
  --outputxml path     File or dir where output is written as stand-off XML
  --outputlabels path  File where output spans are written in MinorThird format
  --filelist file      Read document names from a file; default is to process
                       all documents specified under --inputtxt.
  --struct             Enable recognition/normalization of structured timexes
  --timestamp          Enable detection/normalization of document timestamp
  --recog              Enable timex recognition
  --tmxclass           Enable timex classification
  --dirclass           Enable direction classification
  --prenorm            Enable pre-normalization of timexes
  --parseprenorm       Enable parse-based pre-normalization of timexes
  --pattern            Enable pattern-based recognition for special cases
  --norm               Enable final normalization of timexes
  --all                Enable all of the above processing steps
  --infertmxclass      Determine timex class from normalized value
  --inferdirclass      Determine direction class from normalized value
  --basetmxclass       Run baseline timex classifier
  --basedirclass       Run baseline direction classifier
  --forcealign         Keep only parse-aligned spans from the input
  --trainrecog         Train a new recognition model
  --traintmxclass      Train a new timex classification model
  --traindirclass      Train a new direction classification model
  --recogmodel path    Filename prefix of recognition model
  --tmxclassmodel path Filename prefix of timex classification model
  --dirclassmodel path Filename prefix of direction classification model
  --reftracking model  Reference tracking: heuristic, timestamp, or recent
  --quiet              Don't talk so much
"""

import sys, getopt, os, os.path, traceback
import libxml2
import timexval, timexstruct, timexrecog, timexclass, timexnorm, timexpattern
import timexparsenorm
from timexdoc import *


# Default SVM classification models
defaultRecogModel = 'recog_tern_model'
defaultTmxClassModel = 'tmxclass_tern_model'
defaultDirClassModel = 'dirclass_tern_model'


def mesg(s):
    """Display a message to the user."""
    sys.stderr.write(s)
    sys.stderr.flush()

info = mesg


def findfile(fname):
    """Search for a file in the Python module search path."""
    if not os.path.dirname(fname) and not os.path.exists(fname):
        for d in sys.path:
            p = os.path.join(d, fname)
            if os.path.exists(p):
                return p
    return fname


def safediv(a, b):
    if a == 0:
        return 0
    else:
        return a / float(b)


class ClassificationEvaluator(object):
    """Measure classification accuracy."""

    def __init__(self, name):
        self.name = name
        self.nref = { }
        self.ntest = { }
        self.npair = { }
        self.ntotal = 0
        self.ngood = 0
        self.nskip = 0

    def add(self, test, ref):
        """Add a list of classified instances to the evaluation."""
        for (t, r) in zip(test, ref):
            if (t is None) or (r is None):
                self.nskip += 1
                continue
            self.ntotal += 1
            if t == r:
                self.ngood += 1
            if t not in self.ntest: self.ntest[t] = 0
            if t not in self.nref: self.nref[t] = 0
            if r not in self.ntest: self.ntest[r] = 0
            if r not in self.nref: self.nref[r] = 0
            self.ntest[t] += 1
            self.nref[r] += 1
            self.npair[(t, r)] = self.npair.get((t, r), 0) + 1
            

    def printResult(self, outf, showMatrix=1):
        """Print evaluation result."""
        classlist = self.nref.keys()
        classlist.sort()
        print >>outf
        print >>outf, "** Classification accuracy for '%s' **" % self.name
        if self.nskip:
            print >>outf, "Warning: not counting", self.nskip, \
                          "timexes with missing class label"
        if showMatrix:
            # Print the confusion matrix
            w = max(10, max(map(len, classlist)))
            s = " %*s " % (w, "ref \\ test")
            s += "| error  "
            for c in classlist:
                s += "| %*s " % (max(len(c), 6), (c or '_null'))
            print >>outf, s
            for c in classlist:
                nref = self.nref[c]
                ngood = self.npair.get((c, c), 0)
                s = " %*s " % (w, (c or '_null'))
                s += "| %.4f " % safediv(nref - ngood, nref)
                for cc in classlist:
                    n = self.npair.get((cc, c), 0)
                    p = safediv(n, nref)
                    s += "| %.4f%*s " % (p, max(0, len(cc)-6), '')
                print >>outf, s
        totalerr = safediv(self.ntotal - self.ngood, self.ntotal)
        print >>outf, "%s total error = %.4f" % (self.name, totalerr)
        expectgood = sum([ self.nref[c] * self.ntest[c] / float(self.ntotal)
                           for c in classlist ])
        kappa = safediv(self.ngood - expectgood, self.ntotal - expectgood)
        print >>outf, "%s kappa = %.4f" % (self.name, kappa)
        print >>outf, "ref class counts:", ' '.join(
          [ '%s:%d' % (c or '_null', self.nref[c]) for c in classlist ])
        print >>outf


class UsageError(Exception):
    """Report invalid invocation."""
    def __init__(self, s=None):
        self.msg = s


def readLabels(fname):
    """Read a MinorThird style label file."""
    labels = dict()
    f = file(fname)
    for s in f:
        w = s.strip().split()
        if w[0] in ('addToType', 'closeType'):
            fname = w[1]
            if fname not in labels:
                labels[fname] = [ ]
            if w[0] == 'addToType':
                labels[fname].append((int(w[2]), int(w[3]), w[4]))
    f.close()
    return labels


def writeLabels(f, fname, spans):
    """Write labels in MinorThird format."""
    for (p, n, t) in spans:
        f.write('addToType %s %d %d %s\n' % (fname, p, n, t))


def fixIsoValue(s):
    """Correct impossible annotated values."""
    if s is None: return
    if s[-8:] == '20:28:75': s = s[:-8] + '20:31:28'
    if s[-9:] == '101:09.96': s = s[:-9] + '01:09.96'
    if s == '2003-06-1': s = '2003-06-XX'
    if s == '2003-06-10T1:58': s = '2003-06-10T13:58'
    if s == '2003-W1': s = '2003-W01'
    if s == 'MA20': s = ''
    if s == '04-03-03T02:16:00-05': s = '2004-03-03T02:16:00-05'
    if s == '2004-11-XXT2:30': s = '2004-11-XXT02:30'
    if s == '2005-01-28 T01:23:42Z': s = '2005-01-28T01:23:42Z'
    return s


def mergeSpans(basespans, newspans,
               prefernew=0, keepnestedbase=0, keepnestednew=1):
    """Merge new spans into the base span set.
    If a new span partly overlaps a base span with improper nesting,
    the new span is removed.
    If a new span and base span have identical extent and only one of them
    has a normalized value, the span that has a value is kept and the span
    without a value is removed.
    If a new span and abse span have identical extent and none or both of
    them have a normalized value, the new span is removed if prefernew=0
    or the base span is removed if prefernew=1.
    If a base span is properly nested inside a new span, the base span
    is removed if keepnestedbase=0, otherwise both spans are kept.
    If a new span is properly nested inside a base span, the new span
    is removed if keepnestednew=0, otherwise both spans are kept."""

    # Decide which new spans to keep
    nspans = [ ]
    for nspan in newspans:
        keep = 1
        for bspan in basespans:
            if ( nspan.start == bspan.start and
                 nspan.end == bspan.end ):
                # identical extent
                forcebase = (bspan.val and not nspan.val)
                forcenew = (nspan.val and not bspan.val)
                if forcebase or ((not prefernew) and (not forcenew)):
                    keep = 0
            elif ( nspan.start >= bspan.start and
                   nspan.end <= bspan.end ):
                # properly nested
                keep = keep and keepnestednew
            elif ( ( nspan.start > bspan.start and
                     nspan.start < bspan.end and
                     nspan.end > bspan.end ) or
                   ( nspan.start < bspan.start and
                     nspan.end > bspan.start and
                     nspan.end < bspan.end ) ):
                # improper overlap
                keep = 0
        if keep:
            nspans.append(nspan)

    # Decide which base spans to keep
    outspans = [ ]
    for bspan in basespans:
        keep = 1
        for nspan in nspans:
            if ( bspan.start == nspan.start and
                 bspan.end == nspan.end ):
                # identical extent
                forcebase = (bspan.val and not nspan.val)
                forcenew = (nspan.val and not bspan.val)
                if forcenew or (prefernew and (not forcebase)):
                    keep = 0
            elif ( bspan.start >= nspan.start and
                   bspan.end <= nspan.end ):
                # properly nested
                keep = keep and keepnestedbase
        if keep:
            outspans.append(bspan)

    # Merge sets and sort
    outspans += nspans
    outspans.sort()

    return outspans


def cutEmbeddedSpans(doc):
    """Eliminate some cases of embedded timex predictions."""

    # Eliminate spans that are a left extension of an embedded span,
    # unless the containing span has a value and the embedded span hasn't
    spans = doc.timexSpans
    keepspans = [ ]
    for ispan in spans:
        keep = 1
        for jspan in spans:
            if ( ispan.end == jspan.end and
                 ispan.start < jspan.start and
                 (jspan.val or not ispan.val) ):
                keep = 0
                break
        if keep:
            keepspans.append(ispan)

    # Eliminate spans that are a right extension of an embedded span,
    # unless the containing span has a value and the embedded span hasn't
    spans = keepspans
    keepspans = [ ]
    for ispan in spans:
        keep = 1
        for jspan in spans:
            if ( ispan.start == jspan.start and
                 ispan.end > jspan.end and
                 (jspan.val or not ispan.val) ):
                keep = 0
                break
        if keep:
            keepspans.append(ispan)

    doc.timexSpans = keepspans


def main(args):
    global info

    # Parse command line
    opts, args = getopt.getopt(args, "", [
      'inputtxt=', 'inputenc=', 'inputxml=', 'inputlabels=', 'inputparses=',
      'outputxml=', 'outputlabels=', 'filelist=',
      'struct', 'timestamp', 'recog', 'tmxclass', 'dirclass',
      'prenorm', 'parseprenorm', 'pattern', 'norm', 'all', 'forcealign',
      'infertmxclass', 'inferdirclass', 'basetmxclass', 'basedirclass',
      'trainrecog', 'traintmxclass', 'traindirclass',
      'recogmodel=', 'tmxclassmodel=', 'dirclassmodel=',
      'reftracking=', 'quiet' ])
    if args:
        raise UsageError("Unknown option '%s'" % args[0])

    optmap = { }
    for (opt, val) in opts:
        assert opt.startswith('--')
        if opt[2:] in optmap:
            raise UsageError("Duplicate option '%s'" % opt)
        optmap[opt[2:]] = val

    if 'quiet' in optmap:
        # Suppress verbose messages
        def info(s):
            """Don't bother the user with this message."""
            pass

    # Get run mode from command line options
    doStruct = ('struct' in optmap) or ('all' in optmap)
    doTimestamp = ('timestamp' in optmap) or ('all' in optmap)
    doRecog = ('recog' in optmap) or ('all' in optmap)
    doTmxClass = ('tmxclass' in optmap) or ('all' in optmap) or ('basetmxclass' in optmap)
    doDirClass = ('dirclass' in optmap) or ('all' in optmap) or ('basedirclass' in optmap)
    doPreNorm = ('prenorm' in optmap) or ('all' in optmap)
    doParsePreNorm = ('parseprenorm' in optmap)
    doNorm = ('norm' in optmap) or ('all' in optmap)
    doPatternBased = ('pattern' in optmap)
    inferTmxClass = 'infertmxclass' in optmap
    inferDirClass = 'inferdirclass' in optmap
    trainRecog = 'trainrecog' in optmap
    trainTmxClass = 'traintmxclass' in optmap
    trainDirClass = 'traindirclass' in optmap
    forceAlign = 'forcealign' in optmap

    # Check valid combination of options
    if 'inputtxt' not in optmap:
        raise UsageError("Required option --inputtxt missing")
    if (doStruct or doRecog) and trainRecog:
        raise UsageError("Cannot run and train recognition at the same time")
    if doTimestamp and not doStruct:
        raise UsageError(
          "Cannot detect document timestamp without structured recognition")
    if (doTmxClass and trainTmxClass) or (doDirClass and trainDirClass):
        raise UsageError("Cannot train and run a model at the same time")
    if trainRecog and 'recogmodel' not in optmap:
        raise UsageError("Required option --recogmodel missing")
    if trainTmxClass and 'tmxclassmodel' not in optmap:
        raise UsageError("Required option --tmxclassmodel missing")
    if trainDirClass and 'dirclassmodel' not in optmap:
        raise UsageError("Required option --dirclassmodel missing")
    if ( (doRecog or doTmxClass or doDirClass or
          trainRecog or trainTmxClass or trainDirClass or forceAlign) and
         ('inputparses' not in optmap) ):
        raise UsageError("Need sentence parses for recognition/classification")
    if ( trainRecog and
         ('inputxml' not in optmap) and ('inputlabels' not in optmap) ):
        raise UsageError("Need example spans to train a recognition model")
    if (trainTmxClass or trainDirClass) and ('inputxml' not in optmap):
        raise UsageError("Need example classes to train a classification model")

    # Make a list of input documents
    t = optmap['inputtxt']
    if os.path.isfile(t):
        if 'filelist' in optmap:
            raise UsageError(
            "--filelist can only be used when --inputtxt specifies a directory")
        documents = [ TimexDocument(name=os.path.basename(t),
                                    encoding=optmap.get('inputenc'),
                                    loadFn=loadDocFromPlainTxt,
                                    srcTxtFile=t) ]
    elif os.path.isdir(t):
        if 'filelist' in optmap:
            f = file(optmap['filelist'], 'r')
            fnames = [ s.strip('\n') for s in f.readlines() ]
            f.close()
            if not fnames:
                raise UsageError("No files found in '%s'" % optmap['filelist'])
        else:
            fnames = os.listdir(t)
            if not fnames:
                raise UsageError("No files found in '%s'" % t)
        documents = [ TimexDocument(name=f,
                                    encoding=optmap.get('inputenc'),
                                    loadFn=loadDocFromPlainTxt,
                                    srcTxtFile=os.path.join(t, f))
                      for f in fnames ]
    else:
        raise UsageError("Invalid path '%s'" % t)

    if 'inputxml' in optmap:
        t = optmap['inputxml']
        if os.path.isfile(t):
            if len(documents) != 1:
                raise UsageError("Can not use single XML file with multiple TXT files")
            documents[0].loadFn = loadDocFromTernSoXml
            documents[0].srcXmlFile = t
        elif os.path.isdir(t):
            for doc in documents:
                doc.loadFn = loadDocFromTernSoXml
                doc.srcXmlFile = os.path.join(t, doc.name)
        else:
            raise UsageError("Invalid path '%s'" % t)

    if 'inputlabels' in optmap:
        if 'inputxml' in optmap:
            raise UsageError("Can not mix --inputxml with --inputlabels")
        labels = readLabels(optmap['inputlabels'])
        for doc in documents:
            doc.loadFn = loadDocFromLabels
            if doc.name in labels:
                doc.srcLabels = labels[doc.name]
            else:
                doc.srcLabels = [ ]
                mesg("WARNING: no input labels for file '%s'\n" % doc.name)
        del labels

    if 'inputparses' in optmap:
        t = optmap['inputparses']
        if os.path.isfile(t):
            if len(documents) != 1:
                raise UsageError("Can not use single parse file with multiple TXT files")
            documents[0].srcParseFile = t
        elif os.path.isdir(t):
            for doc in documents:
                doc.srcParseFile = os.path.join(t, doc.name)
        else:
            raise UsageError("Invalid path '%s'" % t)

    # Verify output options
    outputXml = optmap.get('outputxml')
    if outputXml:
        if not os.path.isdir(outputXml) and len(documents) != 1:
            raise UsageError("Can not write single output file for multiple input files")

    # Create annotator/trainer objects
    if doStruct:
        info("[init] Structured timex recognition/normalization\n")
        annStruct = timexstruct.StructuredTimexAnnotator()
    if doRecog:
        mfile = optmap.get('recogmodel', defaultRecogModel)
        mfile = findfile(mfile + '.map')[:-4]
        info("[init] Timex recognition model '%s'\n" % mfile)
        annRecog= timexrecog.TimexRecognitionAnnotator(mfile)
    if forceAlign:
        info("[init] Keep only timexes that align with a parsed constituent of good type\n")
        annAlign = timexrecog.TimexAlignmentFilter()
    if trainRecog:
        mfile = optmap.get('recogmodel', defaultRecogModel)
        info("[init] Train timex recognition model '%s'\n" % mfile)
        modRecog = timexrecog.TimexRecognitionTrainer(mfile)
        inst_ct, timex_ct, aligned_ct = 0, 0, 0

    if inferTmxClass:
        info("[init] Timex class inference from input val\n")
        annInferredTmxClass = timexclass.InferredTimexClassAnnotator()
    if 'basetmxclass' in optmap:
        info("[init] Baseline timex classification\n")
        annTmxClass = timexclass.BaselineTimexClassAnnotator(useHead=1)  
    elif doTmxClass:
        mfile = optmap.get('tmxclassmodel', defaultTmxClassModel)
        mfile = findfile(mfile + '.map')[:-4]
        info("[init] Timex classification model '%s'\n" % mfile)
        annTmxClass = timexclass.TimexClassAnnotator(mfile)
    if inferTmxClass and doTmxClass:
        info("[init] Evaluate timex classification against inferred class\n")
        tmxClassEval = ClassificationEvaluator('tmxclass')
        
    if trainTmxClass:
        mfile = optmap['tmxclassmodel']
        info("[init] Train timex classification model '%s'\n" % mfile)
        modTmxClass = timexclass.TimexClassTrainer(mfile)

    if inferDirClass:
        info("[init] Direction class inference from input val\n")
        refmodel = optmap.get('reftracking')
        annInferredDirClass = timexclass.InferredDirClassAnnotator(refmodel)
    if 'basedirclass' in optmap:
        info("[init] Baseline direction classification\n")
        annDirClass = timexclass.BaselineDirClassAnnotator()
    elif doDirClass:
        mfile = optmap.get('dirclassmodel', defaultDirClassModel)
        mfile = findfile(mfile + '.map')[:-4]
        info("[init] Direction classification model '%s'\n" % mfile)
        annDirClass = timexclass.DirClassAnnotator(mfile)
    if inferDirClass and doDirClass:
        info("[init] Evaluate direction classification against inferred class\n")
        dirClassEval = ClassificationEvaluator('dirclass')
    if trainDirClass:
        mfile = optmap['dirclassmodel']
        mparam = { 'useVerbFeatures': 1, 'useDateFeatures': 1 }
        info("[init] Train direction classification model '%s' param=%s\n" %
             (mfile, repr(mparam.keys())))
        modDirClass = timexclass.DirClassTrainer(mfile, mparam)

    if doPreNorm:
        info("[init] Pre-normalization\n")
        annPreNorm = timexnorm.PreNormAnnotator()
    if doNorm:
        info("[init] Final normalization\n")
        refmodel = optmap.get('reftracking')
        annNorm = timexnorm.FinalNormAnnotator(refmodel)

    if doParsePreNorm:
        info("[init] Parse-based pre-normalization\n")
        annPreNorm = timexparsenorm.ParsePreNormAnnotator()

    if doPatternBased:
        info("[init] Pattern-based recognition\n")
        annPatternBased = timexpattern.PatternBasedAnnotator()

    # Open output label file
    outputLabels = None
    if 'outputlabels' in optmap:
        outputLabels = file(optmap['outputlabels'], 'w')

    # Run the annotation pipeline on each document
    faileddocs = [ ]
    for doc in documents:

        try:
            info("Processing document '%s'\n" % doc.name)

            # Load document
            doc.fetchDoc()

            # Fix broken ISO strings
            doc.timestamp = fixIsoValue(doc.timestamp)
            if doc.timexSpans:
                for span in doc.timexSpans:
                    span.val = fixIsoValue(span.val)

            # Load sentence parses if needed
            needParses = ( doRecog or doTmxClass or doDirClass or
                           trainRecog or trainTmxClass or trainDirClass or
                           doParsePreNorm )
            if needParses:
                doc.fetchParses()

            # Step 0: rule-based recognition and timestamp detection
            if doStruct:
                ts = doc.timestamp
                annStruct.annotateDocument(doc)
                if not doTimestamp:
                    # Use the input timestamp instead of the detected timestamp
                    doc.timestamp = ts
                doc.structTimexSpans = doc.timexSpans
                doc.timexSpans = None

            # Step 1: model-based recognition
            if doRecog:
                annRecog.annotateDocument(doc)
            if forceAlign:
                annAlign.annotateDocument(doc)
            if trainRecog:
                i_ct, t_ct, a_ct = modRecog.addDocument(doc)
                info('\t%s instances\t%s timexes (%.3f)\t%s aligned timexes (%.3f, %.3f)\n' % (i_ct, t_ct, safediv(t_ct, i_ct), a_ct, safediv(a_ct, i_ct), safediv(a_ct, t_ct)))
                inst_ct += i_ct
                timex_ct += t_ct
                aligned_ct += a_ct

            # Step 2: classification
            if inferTmxClass:
                annInferredTmxClass.annotateDocument(doc)
            if doTmxClass:
                if inferTmxClass:
                    refclass = [ span.tmxclass for span in doc.timexSpans ]
                annTmxClass.annotateDocument(doc)
                if inferTmxClass:
                    testclass = [ span.tmxclass for span in doc.timexSpans ]
                    tmxClassEval.add(testclass, refclass)
            if trainTmxClass:
                modTmxClass.addDocument(doc)

            # Step 3: pre-normalization
            if doPreNorm:
                annPreNorm.annotateDocument(doc)

            if doParsePreNorm:
                annPreNorm.annotateDocument(doc)

            # Step 4: direction classification
            if inferDirClass:
                annInferredDirClass.annotateDocument(doc)
            if doDirClass:
                if inferDirClass:
                    refclass = [ span.dirclass for span in doc.timexSpans ]
                annDirClass.annotateDocument(doc)
                if inferDirClass:
                    testclass = [ span.dirclass for span in doc.timexSpans ]
                    dirClassEval.add(testclass, refclass)
            if trainDirClass:
                modDirClass.addDocument(doc)

            # Step 5: final normalization
            if doNorm:
                annNorm.annotateDocument(doc)

            # Pattern-based recognition
            if doPatternBased:
                annPatternBased.annotateDocument(doc)

            # Improvised rule to reduce our errors with embedded predictions
            cutEmbeddedSpans(doc)

            # Merge rule-based and model-based recognition results
            if doStruct:
                if doc.timexSpans:
                    doc.timexSpans = mergeSpans(doc.timexSpans, doc.structTimexSpans)
                else:
                    doc.timexSpans = doc.structTimexSpans
                del doc.structTimexSpans

            # Write output
            if outputXml:
                fname = outputXml
                if os.path.isdir(outputXml):
                    fname = os.path.join(outputXml, doc.name)
                writeDocAsTernSoXml(doc, fname)
            if outputLabels:
                writeLabels(outputLabels, doc.name, getLabelsFromDoc(doc))

            # Release document data
            if needParses:
                doc.freeParses()
            doc.freeDoc()

        except:
            if issubclass(sys.exc_info()[0], KeyboardInterrupt):
                raise
            print >>sys.stderr, "Exception while processing", doc.name
            print >>sys.stderr, '-'*60
            traceback.print_exc(file=sys.stderr)
            print >>sys.stderr, '-'*60
            faileddocs.append(doc.name)

    # Close output label file
    if outputLabels:
        outputLabels.close()

    # Report classification results
    if inferTmxClass and doTmxClass:
        tmxClassEval.printResult(sys.stderr)
    if inferDirClass and doDirClass:
        dirClassEval.printResult(sys.stderr)

    # Train models on the instances collected from documents
    if trainRecog:
        info('%s instances\t%s timexes (%.3f)\t%s aligned timexes (%.3f, %.3f)\n' % (inst_ct, timex_ct, safediv(timex_ct, inst_ct), aligned_ct, safediv(aligned_ct, inst_ct), safediv(aligned_ct, timex_ct)))
        modRecog.train()
    if trainTmxClass:
        modTmxClass.train()
    if trainDirClass:
        modDirClass.train()

    # All done
    if faileddocs:
        print >>sys.stderr, \
          "WARNING: Errors occurred in the following documents:", faileddocs


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (getopt.GetoptError, UsageError), e:
        print __doc__
        if e and e.msg:
            print >>sys.stderr, "ERROR:", e.msg
        sys.exit(1)

# End

