#!/usr/bin/python

import sys, re, os
import xml.parsers.expat
from types import NoneType

from components.common_modules.chunks import Chunk, NounChunk, VerbChunk
from components.common_modules.tokens import Token, AdjectiveToken
from components.common_modules.document import Document
from components.common_modules.document import startElementString, endElementString
from components.common_modules.document import emptyContentString
from components.common_modules.sentence import Sentence
from components.common_modules.tags import EventTag, InstanceTag, TimexTag
from library.timeMLspec import *
from utilities import logger


currentDoc = None
currentSentence = None
currentChunk = None
currentEvent = None
currentToken = None
currentTimex = None
finishedEventInChunk = 0  #needed for VerbChunks conatining an EVENT followed by some other particle.
timexWithinChunk = 0
chunkWithinTimex = 0
parser = None



def readFileWithEvents(fileName):
    global currentDoc
    global parser

    initializeParsingEvents()

    currentDoc = Document(fileName)
    if os.path.exists(fileName):
        try:
            file = open(fileName, 'r')
            #logger.debug("\nFILE:",fileName)
            parser.ParseFile(file)
            file.close()
        except:
            print "WARNING: file could not be processed:", fileName
    #currentDoc.pretty_print()
    return currentDoc



def initializeParsingEvents():
    global currentDoc
    global currentSentence
    global currentChunk
    global currentToken
    global currentEvent
    global currentTimex
    global finishedEventInChunk
    global timexWithinChunk
    global chunkWithinTimex
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
    currentEvent = None
    currentTimex = None
    finishedEventInChunk = 0
    timexWithinChunk = 0
    chunkWithinTimex = 0

def start_element(name, attrs):
    #logger.debug("\n============\nNAME: "+str(name)+"\n============\n")
    #logger.debug("\nATTRS: "+str(attrs)+"\n")
    if name == SENTENCE:
        #print ">> SENTENCE"
        procSentStart()
    elif CHUNK.match(name):
        #print ">> CHUNK:", name
        procChunkStart(name)
    elif name == TOKEN:
        #print ">> TOKEN:", attrs
        if attrs.has_key(POS):
            pos = attrs[POS]
        else:
            pos = "PUNCT"
        procTokStart(pos)
    elif name == CHUNKHEAD:
        #print ">> CHUNKHEAD"
        procChunkHeadStart()
    elif CHUNKVERBAL.match(name):
        #print ">> CHUNKVERBAL:", name
        procChunkVerbalStart()
    elif name == CHUNKPOSS:
        #print ">> CHUNKPOSS"
        procPOSStart()
    elif name == EVENT:
        #print ">> EVENTS:", attrs
        procEventStart(attrs)
    elif name == INSTANCE:
        #print ">> INSTANCE:", attrs
        procInstanceStart(attrs)
    elif name == TIMEX:
        #print ">> TIMEX:", attrs
        procTimexStart(attrs)

    if name in EMPTY_TAGS:
        #print ">> EMPTY TAG:", name, attrs
        if name == 'MAKEINSTANCE':
            # to avoid confusion with the lex.pos attribute.
            # It is a bit hackish.    
            posVal = attrs[EPOS]
            del attrs[EPOS]
            attrs[POS] = posVal
        currentDoc.addDocNode(emptyContentString(name, attrs))
    elif name == TIMEML:
        pass
    else:
        #print "OTHER:", name, attrs
        currentDoc.addDocNode(startElementString(name, attrs))

def end_element(name):
    #logger.debug("\n============\n\tEND: "+str(name)+"\n============\n")
    if name == SENTENCE:
        #print ".......SENTENCE"
        procSentEnd()
    elif CHUNK.match(name):
        #print ".......CHUNK"
        procChunkEnd(name)
    elif name == TOKEN:
        #print ".......TOKEN"
        procTokEnd()
    elif CHUNKVERBAL.match(name):
        #print ".......CHUNKVERBAL"
        procChunkVerbalEnd()
    elif name == EVENT:
        #print ".......EVENT"
        procEventEnd()
    elif name == TIMEX:
        #print ".......TIMEX"
        procTimexEnd()
    elif name == CHUNKHEAD:
        #print ".......CHUNKHEAD"
        procChunkHeadEnd()

    if name in EMPTY_TAGS:    #Hacking, but anyway!
        pass
    elif name == TIMEML:
        pass 
    else:
        currentDoc.addDocNode(endElementString(name))

def charData(string):
    """If string is event expression (i.e., within EVENT tag),
    add form into currentDoc.taggedEventDict"""
    if currentEvent is not None and currentToken is not None:
        eid = currentEvent.attrs[EID]
        logger.debug("Storing Event Values - charData: "+string)
        """To avoid storing the form of adverbs or other particles
        following the lexical item tagged as EVENT"""
        if currentDoc.hasEventWithAttribute(eid, FORM):
            logger.debug("FORM already there. Hence, not storing: "+str(string))
        else:
            logger.debug("STORING: "+str(string))
            currentDoc.storeEventValues({EID:eid, FORM: string})
    
    """Regardless whether the string is an event expression,
       add it into the Document object """
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

def procEventStart(attrs):
    global currentEvent
    #print "Current Timex:", currentTimex, "||", "Current Event:", currentEvent
    if currentTimex is not None or currentEvent is not None:
        logger.warn("<EVENT> within <TIMEX3> or another <EVENT> tag")
        currentSentence.trackEmbedding(EVENT)
    else:
        currentEvent = EventTag(attrs)
        
def getEventLocation():
    """Return the position of the event in the consituent it is embedded
    in. This method may be wrong (MV)."""
    global currentToken
    global currentChunk
    global currentSentence
    if currentSentence is not None:
        if currentToken is not None and currentToken.isAdjToken(): #if not currentChunk
            position = currentToken.position
            logger.debug("Event position obtained from AdkToken: "+str(position))
        else:
            position = currentChunk.position
            logger.debug("Event position obtained from Chunk: "+str(position))
        return position
    else:
        debug.error("No position for current Event")

def procEventEnd():
    global currentEvent
    global finishedEventInChunk

    """Not setting currentEvent to None here,
    but in procChunkEnd or procAdjTokenEnd instead, since:
    a) EVENT is always within a Chunk or an AdjToken,
    ##NOT VALID ANYMORE: b) there should be no more than ONE EVENT tag per chunk,
    c) EventTag object needs info of chunk or token location,
    which is only available once Chunk or AdjToken
    is added to its Sentence object

    NEW CONCERN: What to do with CHunks containing more than 1 EVENT???"""

    if currentSentence.hasEmbedded(EVENT):
        currentSentence.removeEmbedded(EVENT)
    else:
        if currentChunk is not None:
            #logger.debug("\n\nCurrent Event 1:"+currentEvent.__class__.__name__)
            currentChunk.addToken(currentEvent) 
            #logger.debug("\n\tsuccessss")
        elif currentToken is not None and currentToken.isAdjToken():
            pass
        else:
            #logger.debug("\n\nCurrent Event 2:"+currentEvent.__class__.__name__)
            currentSentence.add(currentEvent) 
    finishedEventInChunk = 1

def procInstanceStart(attrs):
    # to avoid confusion with the lex.pos attribute.
    # It is a bit hackish.    
    eposVal = attrs[POS]
    del attrs[POS]
    attrs[EPOS] = eposVal
    
    currentInstance = InstanceTag(attrs)
    #logger.debug("\n\t\t\tStoring Event Values - Instance: "+str(attrs))
    currentDoc.storeEventValues(currentInstance.attrs)
    
def procTimexStart(attrs):
    global currentSentence
    global currentTimex
    global currentChunk
    global timexWithinChunk

    if currentTimex is not None or currentEvent is not None:
        logger.warn("<TIMEX3> tag within <EVENT> or another <TIMEX3> tag")
        currentSentence.trackEmbedding(TIMEX)
    else:
        currentTimex = TimexTag(attrs)
    
def procTimexEnd():
    global currentTimex
    global currentChunk
    global currentSentence
    global currentDoc

    if currentSentence is not None and currentSentence.hasEmbedded(TIMEX):
        currentSentence.removeEmbedded(TIMEX)
    else:
        if currentChunk is not None:
            # timex is in chunk
            currentChunk.addToken(currentTimex)
        elif currentSentence is not None:
            # timex is in sentence
            currentSentence.add(currentTimex)
        else:
            # times is in document, ie, the timex is the DCT
            currentDoc.addTimex(currentTimex)
        currentTimex = None
    
def procTokStart(pos):
    global currentSentence
    global currentToken
    
    #logger.debug("\n\nSTARTING token")
    if currentToken is not None:
        raise "ERROR: currentToken is not None"
    currentToken = newToken(currentDoc, pos)

def procTokEnd():
    global currentSentence
    global currentToken
    global currentChunk
    global currentEvent
    global currentTimex
    global currentSentence
    global finishedEventInChunk

    if currentToken.isAdjToken():
        if currentChunk is not None:
            """For docs preprocessed using a chunker
               where Adj tokens are part of a chunk"""
            #logger.debug("\n\nLEAVING ADJ token 1")
            if currentEvent is not None: # and finishedEventInChunk:
                #logger.debug("\nSETTING form (Adj - Event 1)")             
                currentEvent.addTokenInfo(currentToken)
            elif currentTimex is not None:
                currentTimex.add(currentToken)
            elif currentChunk is not None:
                #logger.debug("\nSETTING form (Adj - Chunk)")             
                currentChunk.addToken(currentToken)
            elif currentSentence is not None:
                #logger.debug("\nSETTING form (Adj - Sentence)")                         
                currentSentence.add(currentToken)
            #logger.debug("\tPASSING now!")
            #pass
        else:
            """For docs preprocessed using an Alembic-like chunker
               where Adj tokens are NOT part of a chunk"""
            #logger.debug("\n\nLEAVING ADJ token 2")
            ##NO!! if currentSentence is not None:                 
            ##NO!!      currentSentence.add(currentToken)             
            if currentEvent is not None:# and finishedEventInChunk:
                """EVENT tag always within chunk or adjToken"""
                #logger.debug("\n\tSETTING form (Adj - Event 2)")              
                currentSentence.add(currentToken) 
                currentEvent.addTokenInfo(currentToken)  
                #logger.debug("\n\tEEventLocation from AdjToken - Event")
                """The following part needs to take place after
                having inserted the chunk within the Sentence""" 
                eventLoc = getEventLocation()
                currentSentence.storeEventLocation(eventLoc, currentEvent.attrs[EID])
                #logger.debug("\n\t\t\tStoring Event Values - Tok: "+str(currentEvent.attrs))            
                currentDoc.storeEventValues(currentEvent.attrs)
                currentToken.setEventInfo(currentEvent.attrs[EID])
                currentEvent = None
                finishedEventInChunk = 0
            else:                                          
                #logger.debug("\n\tSETTING form (Adj - Not event)")              
                if currentTimex is not None:
                    currentTimex.add(currentToken)         
                elif currentChunk is not None:         
                    currentChunk.addToken(currentToken)      
                elif currentSentence is not None:         
                    currentSentence.add(currentToken)     
    else:
        #logger.debug("\n\nLEAVING normal token")
        if currentEvent is not None: #R and not finishedEventInChunk:
            #logger.debug("\nSETTING form (Tok - Event)")             
            currentEvent.addTokenInfo(currentToken)
        elif currentTimex is not None:
            currentTimex.add(currentToken)
        elif currentChunk is not None:
            #logger.debug("\nSETTING form (Tok - Chunk)")             
            currentChunk.addToken(currentToken)
        elif currentSentence is not None:
            #logger.debug("\nSETTING form (Tok - Sentence)")                         
            currentSentence.add(currentToken)
    currentToken = None
        
def newToken(currentDoc,pos):
    if pos == 'JJ':
        #logger.debug("\nFOUND ADJ token")
        return AdjectiveToken(currentDoc,pos)
    else:
        #logger.debug("\nFOUND normal token")
        return Token(currentDoc, pos)

def procChunkStart(name):
    global currentSentence
    global currentTimex
    global currentChunk

    if currentEvent is not None:
        logger.warn("Chunk is contained within an <EVENT>")
        currentSentence.trackEmbedding(name)
    elif currentTimex is not None:
        currentSentence.trackEmbedding(name)
    elif currentChunk is not None:
        currentSentence.trackEmbedding(name)
    else:
        currentChunk = newChunk(name)
    
def procChunkEnd(name):
    global currentSentence
    global currentChunk
    global currentEvent
    global chunkWithinTimex
    global finishedEventInChunk

    if currentSentence.hasEmbedded(name):
        currentSentence.removeEmbedded(name)
    else:
        currentSentence.add(currentChunk)
        """The following part needs to take place after
        having inserted the chunk within the Sentence""" 
        if currentEvent is not None and finishedEventInChunk:
            """EVENT tag always within chunk """
            #logger.debug("EEventLocation from Chunk")
            eventLoc = getEventLocation()
            currentSentence.storeEventLocation(eventLoc, currentEvent.attrs[EID])
            #logger.debug("\t\t\tStoring Event Values - Chunk: "+str(currentEvent.attrs))                        
            currentDoc.storeEventValues(currentEvent.attrs)
            currentChunk.setEventInfo(currentEvent.attrs[EID])
            currentEvent = None
            finishedEventInChunk = 0
        currentChunk = None

def procChunkHeadStart():
    if type(currentChunk) is NoneType:
        pass
    else:
        currentChunk.startHead()

def procChunkHeadEnd():
    pass

    
def procChunkVerbalStart():
    if type(currentChunk) is NoneType:
        pass
    else:
        currentChunk.startVerbs()

def procChunkVerbalEnd():
    if type(currentChunk) is NoneType:
        pass
    else:
        currentChunk.endVerbs()

def procPOSStart():
    if currentChunk is not None:   #BK if we get a POS node with no current chunk, something is broken.
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
