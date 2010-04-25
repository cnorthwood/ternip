#!/usr/bin/python

import os
import sys
import string
import re
import pickle

import evitaTimemlParser
import forms

contentPos = re.compile(r'(NN$|NNS|VB|JJ)')
featureFuncs = [lambda x: x.pos, lambda x: definiteness(x)]
valueList = ["NN", "NNS", "DEF", "INDEF"]
priors = {}
context = {}

def processFile(dirName, fileName):
    doc = evitaTimemlParser.parseFile(dirName+os.sep+fileName)
    for sentence in doc:
        for token in sentence.getTokens():
            form = getLemma(token)
            try:
                isEvent = token.markedEvent
            except:
                isEvent = ''
            if (token.pos == 'NN' or token.pos == 'NNS') and form:
                try:
                    isEvent = int(isEvent)
                except:
                    isEvent = 0
                try:
                    priors[form][isEvent] += float(1)
                except:
                    priors[form] = [0,0]
                    priors[form][isEvent] += float(1)
                featureList = [f(token) for f in featureFuncs]
                try:
                    #dictionary of context words and countpairs
                    lentry = context[form]
                    for feature in featureList:
                        try:
                            #countpair associated with context form
                            centry = lentry[feature]
                            if isEvent: centry[1] += 1
                            else: centry[0] += 1
                        except KeyError:
                            #new context word
                            if isEvent: centry = [0,1]
                            else: centry = [1,0]
                        lentry[feature] = centry
                except KeyError:
                    #new nominal lemmata
                    lentry = {}
                    if isEvent:
                        for feature in featureList:
                            lentry[feature] = [0,1]
                    else:
                        for feature in featureList:
                            lentry[feature] = [1,0]
                context[form] = lentry


def getLemma(token):
    try:
        return str(token.lemma)
    except:
        return str(token.getText()).lower()

def definiteness(token):
    try:
        if token.parent.isDefinite():
            return "DEF"
        else:
            return "INDEF"
    except AttributeError:
        tokens = token.parent.getTokens()
        position = token.position
        while True:
            position = position - 1
            try:
                checkToken = tokens[position]
            except IndexError:
                return "INDEF"
            checkPos = checkToken.pos
            if checkPos[0:2] == 'NN': 
                if position == token.position -1:
                    pass
                else:
                    return "INDEF"
            else:
                if checkPos == 'POS' or checkPos == 'PRP$':
                    return "DEF"
                elif checkPos == 'DET' and checkToken.getText() in ['the', 'this', 'that', 'these', 'those']:
                    return "DEF"



if __name__ == '__main__':
    for dirName in sys.argv[1:]:
        if os.path.isdir(dirName):
            dirName = os.path.abspath(dirName)
            fileList = os.listdir(dirName)
            for fileName in fileList:
                processFile(dirName, fileName)
    keepPriors = dict([item for item in priors.items() if item[1][1]])
    keepContext = dict([[item[0], context[item[0]]] for item in keepPriors.items()])
    for item in keepPriors.items():
        nonEventCount = float(item[1][0])
        eventCount = float(item[1][1])
        instances = nonEventCount + eventCount
        try:
            cdict = keepContext[item[0]]
        except KeyError:
            cdict = {}
        cdictProb = {}        
        for contextForm in cdict.items():
            noCount, yesCount = contextForm[1]
            probNo = float(noCount + .25)/((nonEventCount) +.5)
            probYes = float(yesCount + .25)/(eventCount +.5)
            cdictProb[contextForm[0]] = (probNo, probYes)
        zeroData = (.25/((nonEventCount) +.5), .25/(eventCount+.5))
        for value in valueList:
            if value not in cdictProb.keys():
                cdictProb[value] = zeroData
        keepContext[item[0]] = cdictProb
    f = open(forms.DictSemcorEventPickleFilename, 'w')
    pickle.dump(keepPriors, f)
    f.close()
    f = open(forms.DictSemcorContextPickleFilename, 'w')
    pickle.dump(keepContext, f)
    f.close()


