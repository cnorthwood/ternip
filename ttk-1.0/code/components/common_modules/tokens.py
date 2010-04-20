"""NOT YET PROPERLY DOCUMENTED"""

from library import forms
from library.timeMLspec import FORM, STEM, POS, TENSE, ASPECT, EPOS, MOD, POL, EVENTID, EIID, CLASS
from library.timeMLspec import ALINK, SLINK
from utilities import logger
from components.evita.event import Event
from components.evita.gramChunk import GramNChunk, GramAChunk, GramVChunkList
from components.common_modules.constituent import Constituent


class Token(Constituent):

    def __init__(self, document, pos):
        self.pos = pos
        self.event = None
        self.textIdx = []          # should be None?
        self.document = document
        self.position = None
        self.parent = None
        self.cachedGramChunk = 0
        self.flagCheckedForEvents = 0
        # added this one to provide a pointer to the XmlDocElement instance
        self.lex_tag = None

    def __getitem__(self, index):
        if index == 0:
            return self
        else:
            raise IndexError("list index out of range")

    def __len__(self):
        return 1

    def __getattr__(self, name):
        """Used by Sentence._match. Needs cases for all instance
        variables used in the pattern matching phase."""
        if name == 'nodeType':
            return self.__class__.__name__
        elif name == 'text':
            return self.getText()
        elif name == 'pos':
            return self.pos
        elif name in ['eventStatus', FORM, STEM, TENSE, ASPECT, EPOS, MOD, POL, EVENTID, EIID, CLASS]:
            return None
        else:
            raise AttributeError, name

    def _processEventInToken(self, gramChunk):
        doc = self.document
        if (gramChunk.head and
            gramChunk.head.getText() not in forms.be and
            gramChunk.evClass):
            doc.addEvent(Event(gramChunk))

    def setTextNode(self, docLoc):
        self.textIdx = docLoc

    def getText(self):
        return self.document.nodeList[self.textIdx]

    def document(self):
        """For some reason, tokens have a document variable. Use this
        variable and avoid looking all the way up the tree"""
        return self.document

    def isToken(self):
        return 1

    def isPreposition(self):
        """Perhaps needs a non-hard-coded value."""
        return self.pos == 'IN'
    
    def createEvent(self):
        pass

    def debug_string(self):
        try:
            event_val = self.event
        except AttributeError:
            event_val = None
        return self.__class__.__name__ +": "+self.getText()+" "+self.pos+" Event:"+str(event_val)

    def pretty_print(self, indent=0):
        event_string = ''
        if self.event:
            event_string = ' event="' + str(self.event_tag.attrs) + '"'
        print "%s<lex pos=\"%s\" text=\"%s\"%s>" % \
              (indent * ' ', self.pos, self.getText(), event_string)

        
class AdjectiveToken(Token):

    def __init__(self, document, pos):
        Token.__init__(self, document, pos)
        #self.pos = pos
        self.event = None
        self.eid = None
        self.createdLexicalSlink = 0
        self.createdAlink = 0

    def _createGramChunk(self):
        self.cachedGramChunk = GramAChunk(self)

    def __getattr__(self, name):
        """(Slinket method) Used by Sentence._match. Needs cases for all instance
        variables used in the pattern matching phase."""
        if name == 'nodeType':
            return self.__class__.__name__

        # restored from Token
        elif name == 'text':
            return self.getText()
        elif name == 'pos':
            return self.pos
        
        elif name == 'nodeName':
            return self.pos

        # this is used by slinket/s2t in case there is event
        # information available
        elif name in ['eventStatus', 'text', FORM, STEM, POS, TENSE, ASPECT, EPOS, MOD, POL, EVENTID, EIID, CLASS]:
            if not self.event:
                return None
            else:
                doc = self.parent.document()
                if name == 'eventStatus':
                    return '1'
                elif name == TENSE:
                    return doc.taggedEventsDict[self.eid][TENSE]
                elif name == ASPECT:
                    return doc.taggedEventsDict[self.eid][ASPECT]
                elif name == EPOS: #NF_MORPH:
                    return doc.taggedEventsDict[self.eid][EPOS]#[NF_MORPH]
                elif name == MOD:
                    try: mod = doc.taggedEventsDict[self.eid][MOD]
                    except: mod = 'NONE'
                    return mod
                elif name == POL:
                    try: pol = doc.taggedEventsDict[self.eid][POL]
                    except: pol = 'POS'
                    return pol
                elif name == EVENTID:
                    return doc.taggedEventsDict[self.eid][EVENTID]
                elif name == EIID:
                    return doc.taggedEventsDict[self.eid][EIID]
                elif name == CLASS:
                    return doc.taggedEventsDict[self.eid][CLASS]
                elif name == 'text' or name == FORM:
                    return doc.taggedEventsDict[self.eid][FORM] 
                elif name == STEM:
                    return doc.taggedEventsDict[self.eid][STEM] 
                elif name == POS:
                    try:
                        return doc.taggedEventsDict[self.eid][POS] #self.token.pos
                    except:
                        return 'NONE'
        else:
            raise AttributeError, name

    def createEvent(self):
        """Arriving here adjs passed through the main loop
        for createEvent"""
        logger.debug("createEvent in AdjToken")
        pass

    def createAdjEvent(self, verbGramFeat='nil'):
        """(Evita method) only for tokens that are not in a chunk"""
        logger.debug("createAdjEvent in AdjToken")
        if not self.parent.__class__.__name__ == 'Sentence':
            return
        else:
            GramACh = self.gramChunk()
            if verbGramFeat !='nil':
                """ Percolating gram features from copular verb"""
                GramACh.tense = verbGramFeat['tense']
                GramACh.aspect = verbGramFeat['aspect']
                GramACh.modality = verbGramFeat['modality']
                GramACh.polarity = verbGramFeat['polarity']
                logger.debug("Accepted Adjective")
                logger.debug("[A_APC] " + GramACh.as_extended_string())
            else: 
                logger.debug("[A_2Ev] " + GramACh.as_extended_string())
            self._processEventInToken(GramACh)            

    def isAdjToken(self):
        return 1

    def doc(self):
        logger.debug("RETURNING document")
        return self.parent.document()
    
    def setEventInfo(self, eid):
        self.event = 1
        self.eid = eid

        
    def createForwardAlink(self, forwardAlinks):
        alinkedEventContext = self.parent[self.position+1:] # chunks following the currEvent
        self.createAlink(alinkedEventContext, forwardAlinks[0], forwardAlinks[1]) # forwardSlinks[0]:pattern name, forwardSlinks[1]: relType
        if self.createdAlink:
            logger.debug("FORWARD ALINK CREATED")

    def createBackwardAlink(self, backwardAlinks):
        """Backward Alinks also check for the adequacy (e.g., in terms of TENSE
        or ASPECT) of the Subordinating Event. For cases such as
        'the <EVENT>transaction</EVENT> has been <EVENT>initiated</EVENT>'
        """
        logger.debug("TRYING backward alink")
        alinkedEventContext = self.parent[:self.position+1]
        alinkedEventContext.reverse()
        self.createAlink(alinkedEventContext, backwardAlinks[0], backwardAlinks[1])
        if self.createdAlink:
            logger.debug("BACKWARD ALINK CREATED")

        
    def createAlink(self, alinkedEventContext, syntaxPatternLists, relTypeList):
        for i in range(len(syntaxPatternLists)):
            #self._printSequence(alinkedEventContext, 1)
            substring = self._lookForLink(alinkedEventContext, syntaxPatternLists[i])
            if substring:
                #log("substring\n"+str(substring)+"\n")
                substringLength = substring[0]
                subpatternNum = substring[1]
                relType = relTypeList[i]
                patternName = syntaxPatternLists[i][subpatternNum]
                logger.debug(21*"."+"ACCEPTED ALINK!!! LENGTH: "+str(substringLength)+" "+
                             str(relType)+" || FSA: "+str(i)+"."+str(subpatternNum)+
                             " PatternName: "+patternName.fsaname)
                alinkAttrs = {
                    'eventInstanceID': self.eiid, 
                    'relatedToEventInstance': alinkedEventContext[substringLength-1].eiid,
                    'relType': relType,
                    'syntax': patternName.fsaname }
                self.document().addLink(alinkAttrs, ALINK)
                self.createdAlink = 1
                break    
            else:
                logger.debug(".....................REJECTED ALINK by FSA: "+str(i)+".?")

    def createForwardSlink(self, forwardSlinks):
        """Only used if doc is chunked with Alembic;
        that is, Adj tokens do not belong to any chunk"""
        slinkedEventContext = self.parent[self.position+1:] # chunks following the currEvent
        self.createSlink(slinkedEventContext, forwardSlinks[0], forwardSlinks[1]) # forwardSlinks[0]:pattern name, forwardSlinks[1]: relType
        if self.createdLexicalSlink:
            logger.debug("FORWARD SLINK CREATED")

    def createBackwardSlink(self, backwardSlinks):
        """Backward Slinks also check for the adequacy (e.g., in terms of TENSE
        or ASPECT) of the Subordinating Event. For cases such as
        'the <EVENT>transaction</EVENT> has been <EVENT>approved</EVENT>'
        Only used if doc is chunked with Alembic;
        that is, Adj tokens do not belong to any chunk"""
        
        logger.debug("TRYING backward slink")
        slinkedEventContext = self.parent[:self.position+1]
        slinkedEventContext.reverse()
        self.createSlink(slinkedEventContext, backwardSlinks[0], backwardSlinks[1]) 
        if self.createdLexicalSlink:
            logger.debug("BACKWARD SLINK CREATED")
        
    def createReportingSlink(self, reportingSlink):
        """Reporting Slinks are applied to reporting predicates ('say', 'told', etc)
        that link an event in a preceeding quoted sentence which is
        separated from the clause of the reporting event by a comma; e.g.,
            ``I <EVENT>want</EVENT> a referendum,'' Howard <EVENT class='REPORTING'>said</EVENT>.
        Slinket assumes that these quoted clauses always initiate the main sentence.
        Therefore, the first item in the sentence are quotation marks.
        Only used if doc is chunked with Alembic;
        that is, Adj tokens do not belong to any chunk
        """
        sentenceBeginning = self.parent[:self.position]
        if len(sentenceBeginning) > 0 and sentenceBeginning[0].getText() == "``":
            """quotation does not contain quotation marks"""
            quotation = self._extractQuotation(sentenceBeginning)
            if quotation is not None:
                logger.debug("TRYING reporting slink")
                self.createSlink(quotation, reportingSlink[0], reportingSlink[1])
        
    def createSlink(self, slinkedEventContext, syntaxPatternLists, relTypeList):
       """Only used if doc is chunked with Alembic;
       that is, Adj tokens do not belong to any chunk
       """
       for i in range(len(syntaxPatternLists)):
            self._printSequence(slinkedEventContext, 1)   # DEBUGGING method
            substring = self._lookForLink(slinkedEventContext, syntaxPatternLists[i])
            if substring:
                #log("substring\n"+str(substring)+"\n")
                substringLength = substring[0]
                subpatternNum = substring[1]
                relType = relTypeList[i]
                #patterns = syntaxPatternLists[i]  # should be ith nested list in syntaxPatternLists
                #patternName = patterns[subpatternNum] # should be subpatternNumth item in the list
                patternName = syntaxPatternLists[i][subpatternNum]
                logger.debug(21*"."+"ACCEPTED SLINK!!! LENGTH: "+str(substringLength)+" "+
                             str(relType)+" || FSA: "+str(i)+"."+str(subpatternNum)+
                             " PatternName: "+patternName.fsaname)
                slinkAttrs = {
                    'eventInstanceID': self.eiid, 
                    'subordinatedEventInstance': slinkedEventContext[substringLength-1].eiid,
                    'relType': relType,
                    'syntax': patternName.fsaname }
                self.doc().addLink(slinkAttrs, SLINK)
                self.createdLexicalSlink = 1
                break    
            else:
                logger.debug(".....................REJECTED SLINK by FSA: "+str(i)+".?")

    def _printSequence(self, sequence, depth):
        """Given a sentence or a piece of it, print the list of chunks and
        tokens it contains.  'depth' establishes the number of tabs to
        be printed for each item, in order to display it in a
        hierarchical manner.  """

        try:
            for item in sequence:
                if item.nodeType[-14:] == 'AdjectiveToken':
                    logger.debug(depth*"\t"+"ADJ TOKEN: "+item.getText()+"\t"+item.pos+"\t\tEvent:"+str(item.event))
                elif item.nodeType[-5:] == 'Token':
                    logger.debug(depth*"\t"+"TOKEN: "+item.getText()+"\t"+item.pos+"\t\tEvent:"+str(item.event))
                elif item.nodeType[-5:] == 'Chunk':
                    logger.debug(depth*"\t"+"CHUNK: "+item.nodeType+"\t\tEvent:"+str(item.event))
                elif item.nodeType == EVENT:
                    logger.debug(depth*"\t"+"EVENT: "+item.text+"\t"+item.pos)
                elif item.nodeType == TIMEX:
                    logger.debug(depth*"\t"+"TIMEX: "+item.getText())
                else:
                    raise "ERROR: unknown item type: "+item.nodeType
        except:
            logger.warn('Debugging error')
                
    def _lookForLink(self, restSentence, FSA_set):
        # Eventually, if we want to merge EVITA and SLINKET common stuff,
        # this method should call self._lookForStructuralPattern(FSA_set)
        # But careful: _lookForLink MUST return also fsaNum
        # and that will have effects on Evita code. 
        lenSubstring, fsaNum = self._identifySubstringInSentence(restSentence, FSA_set)
        if lenSubstring: 
            return (lenSubstring, fsaNum)   #return (tokenSentence[:lenSubstring], fsaNum)
        else:
            return 0

    def _identifySubstringInSentence(self, tokenSentence, FSAset):
        fsaCounter=-1  # DEBUGGING purposes
        for fsa in FSAset:
            fsaCounter = fsaCounter + 1
            logger.debug("FSA:\n"+str(fsa))
            lenSubstring = fsa.acceptsShortestSubstringOf(tokenSentence)
            if lenSubstring:
                return (lenSubstring, fsaCounter)
        else:
            return (0, fsaCounter)

    def _extractQuotation(self, fragment):
        for idx in range(len(fragment)):
            try:
                # For some reason, it may break here (though rarely)
                if (fragment[idx].getText() == "''" and
                    (fragment[idx-1].getText() == "," or
                     fragment[idx+1].getText() == ",")):
                    return fragment[1:idx]
            except:
                pass
        else:
            return None
