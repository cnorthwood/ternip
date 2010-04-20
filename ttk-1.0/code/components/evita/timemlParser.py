#!/usr/bin/python

import sys
import re
import os
import xml.parsers.expat
from types import NoneType

from components.common_modules.chunks import Chunk, VerbChunk, NounChunk
from components.common_modules.tokens import Token, AdjectiveToken
from components.common_modules.document import Document
from components.common_modules.document import startElementString, endElementString
from components.common_modules.sentence import Sentence

DEBUG = False

SENTENCE = 's'
CHUNK = re.compile('NG|VG|NP|VP')
TOKEN = 'lex'
POS = 'pos'
CHUNKHEAD = 'HEAD'
CHUNKPOSS = 'POS'
MARKEDEVENT = 'isEvent'
LEMMA = 'lemma'

currentDoc = None
currentSentence = None
currentChunk = None
embeddingChunk = 0
currentToken = None
parser = None


def initialize():
    global currentDoc
    global currentSentence
    global currentChunk
    global embeddingChunk
    global currentToken
    global parser
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = charData
    parser.XmlDeclHandler = xmlDec
    parser.DefaultHandler = default
    currentDoc = None
    currentSentence = None
    currentChunk = None
    currentToken = None
    embeddingChunk = 0
    eventCounter = 0
    instanceCounter = 0

def parseFile(fileName):
    global currentDoc
    global parser
    initialize()
    currentDoc = Document(fileName)
    if os.path.exists(fileName):
        file = open(fileName, 'r')
    else:
        print "not a real path", fileName
    #print "File name:", fileName, file
    try:
        parser.ParseFile(file)
    except:
        print "ERROR: file is not XML compliant"
    file.close()
    return currentDoc

def start_element(name, attrs):
    debug('<' + name + '>' + str(attrs))
    if name == SENTENCE:
        procSentStart()
    elif CHUNK.match(name):
        procChunkStart(name)
    elif name == TOKEN:
        try:
            pos = attrs[POS]
        except:
            pos = "PUNCT"
        try:
            markedEvent = attrs[MARKEDEVENT]
        except:
            markedEvent = None
        try:
            lemma = attrs[LEMMA]
        except:
            lemma = None
        procTokStart(pos,markedEvent,lemma)
    elif name == CHUNKHEAD:
        procChunkHeadStart()
    elif name == CHUNKPOSS:
        procPOSStart()
    currentDoc.addDocNode(startElementString(name, attrs))
    
def end_element(name):
    debug('<\\' + name + '>')
    if name == SENTENCE:
        procSentEnd()
    elif CHUNK.match(name):
        procChunkEnd(name)
    elif name == TOKEN:
        procTokEnd()
    currentDoc.addDocNode(endElementString(name))

def charData(string):
    debug('\t\t'+string)
    if currentToken is not None:
        if currentToken.textIdx:
            currentDoc.nodeList[-1] = currentDoc.nodeList[-1] + string
        else:
            currentToken.setTextNode(currentDoc.nodeCounter)
            currentDoc.addDocNode(string)
    else:
        currentDoc.addDocNode(string)

def default(string):
    currentDoc.addDocNode(string)

def xmlDec(version, encoding, standalone):
    pass

def procSentStart():
    global currentSentence
    currentSentence = Sentence()

def procSentEnd():
    global currentSentence
    currentDoc.addSentence(currentSentence)
    currentSentence = None

def procTokStart(pos, markedEvent=None, lemma=None):
    global currentToken
    currentToken = newToken(currentDoc, pos, markedEvent, lemma)

def procTokEnd():
    global currentToken
    if currentSentence is not None:
        if currentChunk is not None:
            currentChunk.addToken(currentToken)
            currentToken = None
        elif currentToken is not None:
            currentSentence.add(currentToken)
            currentToken = None
    else:
        pass

def newToken(currentDoc,pos,markedEvent=None,lemma=None):
    if pos[0:2] == 'JJ':
        return AdjectiveToken(currentDoc,pos)
    else:
        newToken = Token(currentDoc,pos)
        if not markedEvent is None: newToken.markedEvent = markedEvent
        if not lemma is None: newToken.lemma = lemma
        return newToken

def procChunkStart(name):
    global currentChunk
    global embeddingChunk
    if currentChunk is not None:
        """Not dealing with embedded chunks.
        The only measure taken here: if the embedded chunk
        has the same name as the embedding one,
        keep track of it so that you don't delete currentChunk
        when finding </currentChunk> tag
        """
        if currentChunk.phraseType == name:
            embeddingChunk = 1
        else:
            pass
        '''
        if currentChunk.phraseType =="NGP" and name == "NG":
            #we have NG inside possessive.  Just treat NGP as the chunk
            pass
        elif currentChunk.phraseType =="NG" and name == "VG-VBG":
            #we have a present participle modifying a noun.
            #should generate a VerbChunk from prespart, put VG-VBG on stack
            pass
        else:
            raise Error("unexpected embedded chunk: "+name+" inside:
            "+currentChunk.__class__.__name__)
        '''
    else:
        currentChunk = newChunk(name)

def procChunkEnd(name):
    global currentChunk
    global embeddingChunk
    if currentChunk.phraseType == name:
        #print "Current chunk name:\t", name, currentSentence.positionCount
        if embeddingChunk == 0:
            """Proceed as follows only if not embedded within a chunk
            of the same name as you"""
            if type(currentSentence) is not NoneType:
                currentSentence.add(currentChunk)
                currentChunk = None
            else: pass
        else:
            """Finishing the embedding of two chunks of the same name """
            embeddingChunk = 0
    else:
        #not dealing with embedded chunks
        debug("WARNING: embedded chunk" + name)
        pass

def procChunkHeadStart():
    #print currentChunk;
    if type(currentChunk) is NoneType: pass
    else: currentChunk.startHead()

def procPOSStart():
    if currentChunk:  #R   #BK if we get a POS node with no current chunk, something is broken.
        currentChunk.startPOSS()   #we should probably raise an exception

def newChunk(name):
    if name.startswith("V"):     # use VG???
        return VerbChunk(name)
    elif name.startswith("N"):   # use NG???
        return NounChunk(name)
    else:
        return Chunk(name)

class Error(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

def debug(str):
    if DEBUG: print str
