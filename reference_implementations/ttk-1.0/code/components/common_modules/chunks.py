"""Implements the behaviour of chunks.

Chunks are embedded in sentences and contain event tags, timex tags
and tokens. Much of the functionality of Evita and Slinket is
delegated to chunks.

"""

import string
from types import ListType, TupleType

import library.forms as forms
import library.patterns as patterns
from library.timeMLspec import FORM, STEM, POS, TENSE, ASPECT, EPOS, MOD, POL
from library.timeMLspec import EVENTID, EIID, CLASS, EVENT, TIMEX
from library.timeMLspec import ALINK, SLINK
from utilities import logger
from components.common_modules.constituent import Constituent
from components.evita.event import Event
from components.evita.gramChunk import GramNChunk, GramAChunk, GramVChunkList  


class Chunk(Constituent):

    """Implements the common behaviour of chunks. Chunks are embedded in sentences
    and contain event tags, timex tags and tokens.

    Instance variables
       phraseType -  string indicating the chunk type, usually 'VG' or 'NG'
       dtrs - a list of Tokens, EventTags and TimexTags
       positionCount = 0
       position = None
       parent = None
       cachedGramChunk = 0
       event = None
       eid = None
       isEmbedded = 0
       createdLexicalSlink = 0
       createdAlink = 0
       flagCheckedForEvents = 0

    """
    
    def __init__(self, phraseType):
        self.phraseType = phraseType
        self.dtrs = []
        self.positionCount = 0
        self.position = None
        self.parent = None
        self.cachedGramChunk = 0
        self.event = None
        self.eid = None
        self.isEmbedded = 0
        self.createdLexicalSlink = 0
        self.createdAlink = 0
        self.flagCheckedForEvents = 0

    def __len__(self):
        """Returns the lenght of the dtrs variable."""
        return len(self.dtrs)

    def __setitem__(self, index, val):
        """Sets a value on the dtrs variable."""
        self.dtrs[index] = val

    def __getitem__(self, index):
        """Returns an element from the dtrs variable."""
        return self.dtrs[index]

    def __getslice__(self, i, j):
        """Get a slice from the dtrs variable."""
        return self.dtrs[i:j]

    def __getattr__(self, name):
        """Used by Sentence._match. Needs cases for all instance
        variables used in the pattern matching phase."""
        if name == 'nodeType':
            return self.__class__.__name__
        elif name == 'nodeName':
            return self.phraseType
        # the next two were taken from the evita version
        elif name == 'text':
            return None
        elif name == 'pos':
            return None
        # and this one from the slinket/s2t version
        elif name in ['eventStatus', 'text', FORM, STEM, POS, TENSE, ASPECT,
                      EPOS, MOD, POL, EVENTID, EIID, CLASS]: #NF_MORPH, 
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

    def _createMultiChunk(self, multiChunkEnd): # *** MUST GO to Chunk??
        """for evita."""
        multiChunkInit = self.getTokens(self)
        return multiChunkInit + multiChunkEnd

    def _processEventInChunk(self, gramChunk):
        """for evita."""
        doc = self.document()
        if (gramChunk.head and
            gramChunk.head.getText() not in forms.be and
            gramChunk.head.getText() not in forms.spuriousVerb and
            gramChunk.evClass):
            doc.addEvent(Event(gramChunk))

    # the next methods (up to, but not including endVerbs) were all
    # taken from the slinket/s2t version.
            
    def _matchChunk(self, chunkDescription):
        """Match the chunk instance to the patterns in chunkDescriptions.
        chunkDescription is a dictionary with keys-values pairs that
        match instance variables and their values on GramChunks.

        The value in key-value pairs can be:
        - an atomic value. E.g., {..., 'headForm':'is', ...} 
        - a list of possible values. E.g., {..., headForm': forms.have, ...}   
        In this case, _matchChunk checks whether the chunk feature is
        included within this list.
        - a negated value. It is done by introducing it as
        a second constituent of a 2-position tuple whose initial position
        is the caret symbol: '^'. E.g., {..., 'headPos': ('^', 'MD') ...}
        
        This method is also implemented in the chunkAnalyzer.GramChunk class
        """

        #logger.out("entering")
        #logger.out("self is a", self.__class__.__name__)
        #logger.out("chunkDescription =", chunkDescription)
        
        for feat in chunkDescription.keys():
            #logger.debug("\nVALUE TO MATCH: "+str(feat)+"\t|| VALUE in expression: "+str(self.__getattr__(feat)))
            value = chunkDescription[feat]
            #logger.out('feature', feat, '=', value) 
            if type(value) is TupleType:
                #logger.out('value is a Tuple')
                if value[0] == '^':
                    newvalue = self._hackToSolveProblemsInValue(value[1])
                    if type(newvalue) is ListType:
                        if self.__getattr__(feat) in newvalue:
                            return 0
                    else:
                        if self.__getattr__(feat) == newvalue:
                            return 0
                else:
                    raise "ERROR specifying description of pattern" 
            elif type(value) is ListType:
                #logger.out('value is a List')
                if self.__getattr__(feat) not in value:
                    if feat != 'text':
                        return 0
                    else:
                        self._getHeadText()
                        if self._getHeadText() not in value:
                            return 0
            else:
                #logger.out('value is something else')
                value = self._hackToSolveProblemsInValue(value)
                #logger.out('value is now', value)
                feat_on_self = self.__getattr__(feat)
                #logger.out('feature on self =', feat_on_self)
                #logger.out('self.event =', self.event)
                if self.__getattr__(feat) != value:
                    #logger.out('match failed')
                    return 0
        return 1

    def _getHeadText(self):
        headText = string.split(self.getText())[-1]
        return headText.strip()
    

    def embedded_event(self):
        """Returns the embedded event of the chunk if it has one, returns None
        otherwise."""
        for item in self:
            if item.isEvent():
                return item
        return None
            
    def setEmbedded(self):
        """Keeping track of chunks embedded
        within other chunks, for parsing purposes"""
        self.isEmbedded = 1

    def resetEmbedded(self):
        self.isEmbedded = 0
        
    def startHead(self):
        pass

    def startVerbs(self):
        pass

    def endVerbs(self):
        pass
    
    def addToken(self, token):
        token.setParent(self)
        self.dtrs.append(token)
        self.positionCount += 1

    def setEventInfo(self, eid):
        self.event = 1
        self.eid = eid
        
    def getText(self):
        string = ""
        for token in self.dtrs:
            string = string+' '+str(token.getText())
        return string

    def getTokens(self, sequence):
        """Given a sequence of sentence elements, de-chunk it and return a
        list of plain tokens. Used for mapping sentences slices into
        RegEx-based patterns."""
        tokensList = []
        for item in sequence:
            if item.nodeType[-5:] == 'Token':
                tokensList.append(item)
            elif item.nodeType[-5:] == 'Chunk':
                chunkTokens = self.getTokens(item)
                tokensList = tokensList + chunkTokens
            elif item.nodeType == 'EVENT':
                tokensList.append(item)
            elif item.nodeType == 'TIMEX3':
                timexTokens = self.getTokens(item)
                tokensList = tokensList + timexTokens
            else:
                raise "ERROR: unknown item type: "+item.nodeType
        return tokensList


    ### START OF SLINKET SLINK METHODS

    def find_forward_slink(self, fsa_reltype_groups):
        """Tries to create forward Slinks, using a group of FSAs.
        Arguments:
           fsa_reltype_groups -
               a list of two lists, the first list is a list of fsa
               lists, the second list is a list of relation types
               [ [ [fsa, fsa, ...], [fsa, fsa, ...], ...],
                 [ reltype, reltype, ... ] ] """
        fsa_lists = fsa_reltype_groups[0]
        reltypes_list = fsa_reltype_groups[1]
        # chunks following the current event chunk 
        event_context = self.parent[self.position+1:]
        self._find_slink(event_context, fsa_lists, reltypes_list) 

    def find_backward_slink(self, fsa_reltype_groups):
        """Tries to create backward Slinks, using a group of FSAs.
        Arguments:
           fsa_reltype_groups - see createForwardSlinks """
        # Backward Slinks should have been checked for the adequacy
        # (e.g., in terms of TENSE or ASPECT) of the Subordinating
        # Event. For cases such as 'the <EVENT>transaction</EVENT> has
        # been <EVENT>approved</EVENT>'
        fsa_lists = fsa_reltype_groups[0]
        reltypes_list = fsa_reltype_groups[1]
        # chunks before the current event chunk
        event_context = self.parent[:self.position+1]
        # why is this reversed?
        event_context.reverse()
        self._find_slink(event_context, fsa_lists, reltypes_list) 
        
    def find_reporting_slink(self, reportingSlink):
        """Reporting Slinks are applied to reporting predicates ('say', 'told', etc)
        that link an event in a preceeding quoted sentence which is
        separated from the clause of the reporting event by a comma; e.g.,
            ``I <EVENT>want</EVENT> a referendum,'' Howard <EVENT class='REPORTING'>said</EVENT>.
        Slinket assumes that these quoted clauses always initiate the main sentence.
        Therefore, the first item in the sentence are quotation marks.
        """
        sentenceBeginning = self.parent[:self.position]
        if len(sentenceBeginning) > 0 and sentenceBeginning[0].getText() == "``":
            """quotation does not contain quotation marks"""
            quotation = self._extractQuotation(sentenceBeginning)
            if quotation is not None:
                logger.debug("TRYING reporting slink")
                self._find_slink(quotation, reportingSlink[0], reportingSlink[1])

    def _find_slink(self, event_context, fsa_lists, reltype_list):
        """Try to find an slink in the given event_context using lists of
        FSAs. If the context matches an FSA, then create an slink and
        insert it in the document.""" 
        for i in range(len(fsa_lists)):
            
            fsa_list = fsa_lists[i]
            try:
                reltype = reltype_list[i]
            except IndexError:
                # take last element of reltype list if it happens to
                # be shorter than the fsa_lists
                reltype = reltype_list[-1]
            result = self._look_for_link(event_context, fsa_list)
            #logger.out(result)
            if result:
                (length_of_match, fsa_num) = result
                fsa = fsa_list[fsa_num]
                #print fsa
                #logger.out("match found, FSA=%s size=%d reltype=%s"
                #           % (fsa.fsaname, length_of_match, reltype))
                logger.debug(21*"."+"ACCEPTED SLINK!!! LENGTH: "+str(length_of_match)+
                             " "+ str(reltype)+" || FSA: "+str(i)+"."+str(fsa_num)+
                             " PatternName: "+fsa.fsaname)
                slinkAttrs = {
                    'eventInstanceID': self.eiid,
                    'subordinatedEventInstance': event_context[length_of_match-1].eiid,
                    'relType': reltype,
                    'syntax': fsa.fsaname }
                self.document().addLink(slinkAttrs, SLINK)
                self.createdLexicalSlink = 1
                break
            else:
                logger.debug(".....................REJECTED SLINK by FSA: "+str(i)+".?")
                
    def _look_for_link(self, sentence_slice, fsa_list):
        """Given a slice of a sentence and a list of FSAs, return a tuple of
        the size of the matching slize and the number of the FSA that
        featured in the match. Return False if there is no match."""
        #logger.out('object = ', self)
        lenSubstring, fsaNum = self._identify_substring(sentence_slice, fsa_list)
        if lenSubstring: 
            return (lenSubstring, fsaNum)
        else:
            return False

    def _identify_substring(self, sentence_slice, fsa_list):
        """Checks whether a token sequnce matches an pattern. Returns a tuple
        of sub sequence lenght that matched the pattern (where a
        lenght of 0 indicates no match) and the index of the FSA that
        applied the succesfull match. This is the method where the FSA
        is asked to find a substring in the sequence that matches the
        FSA.
        Arguments:
           sentence_slice - a list of Chunks and Tokens
           fsa_list - a list of FSAs """
        #print 'EVENT_CONTEXT'
        #for item in sentence_slice: item.pp()
        fsaCounter = -1 
        for fsa in fsa_list:
            fsaCounter += 1
            #logger.out('Trying FSA', fsa.fsaname)
            lenSubstring = fsa.acceptsShortestSubstringOf(sentence_slice)
            #logger.out('length of found match', lenSubstring)
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

        
    ### START OF SLINKET ALINK METHODS
        
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
            result = self._look_for_link(alinkedEventContext, syntaxPatternLists[i])
            if result:
                #logger.debug("substring\n"+str(substring)+"\n")
                substringLength = result[0]
                subpatternNum = result[1]
                relType = relTypeList[i]
                patternName = syntaxPatternLists[i][subpatternNum]
                logger.debug("\n"+21*"."+"ACCEPTED ALINK!!! LENGTH: "+str(substringLength)+" "+str(relType)+
                      " || FSA: "+str(i)+"."+str(subpatternNum)+" PatternName: "+patternName.fsaname)
                logger.debug("\n"+70*"*"+"\n")
                alinkAttrs = { 'eventInstanceID': self.eiid, 
                               'relatedToEventInstance': alinkedEventContext[substringLength-1].eiid,
                               'relType': relType,
                               'syntax': patternName.fsaname
                             }
                #relType, self.eiid, alinkedEventContext[substringLength-1].eiid, patternName.fsaname)
                self.document().addLink(alinkAttrs, ALINK)
                self.createdAlink = 1
                break    
            else:
                logger.debug(".....................REJECTED ALINK by FSA: "+str(i)+".?")  


    ### END OF SLINKET METHODS


    def startHead(self):
        pass

    def isChunk(self):
        return 1

    def isTimex(self):
        if self.phraseType and self.phraseType[:5] == 'TIMEX':
            return 1
        else: return 0

    def isNChHead(self):
        if self.phraseType and self.phraseType[:4] == 'HEAD':
            return 1
        else: return 0

    def pretty_print(self, indent=0):
        print indent * ' ' + '<' + self.phraseType + '>'
        for tok in self.dtrs:
            #print tok
            tok.pretty_print(indent+2)


        
class AdjChunk(Chunk):
    def __init__(self, phraseType):
        Chunk.__init__(self, phraseType)
        self.head = -1

    def getHead(self):
        return self.dtrs[self.head]

    def isAdjChunk(self):
        return 1
    

class NounChunk(Chunk):

    def __init__(self, phraseType):
        Chunk.__init__(self, phraseType)
        self.head = -1
        self.poss = None

    def getHead(self):
        return self.dtrs[self.head]

    def getPoss(self):
        return self.dtrs[self.poss]

    def startHead(self):
        self.head = len(self.dtrs)

    def startPOSS(self):
        if self.dtrs:
            self.poss = len(self.dtrs)
        else:
            self.poss = 0

    def isNounChunk(self):
        return 1

    def _createGramChunk(self):
        self.cachedGramChunk = GramNChunk(self)

    def isDefinite(self):
        for token in self.dtrs[:self.head]:
            if token.pos == 'POS' or token.pos == 'PRP$':
                return True
            elif token.pos == 'DET' and token.getText() in ['the', 'this', 'that', 'these', 'those']:
                return True
        # in the slinket/s2t version, the following line used to be
        # included as an else above
        return False

    def createEvent(self, verbGramFeat='nil'):
        """for evita"""
        logger.debug("createEvent in NounChunk")
        # Do not try to create an event if the chunk is empty (which
        # is happening due to a crazy bug in the converter code) (mv
        # 11/08/07)
        if not self.dtrs:
            return
        GramNCh = self.gramChunk()
        """ To percolate gram features from verb
        in case of nominal events that are the head of
        predicative complements"""
        if verbGramFeat !='nil':
            GramNCh.tense = verbGramFeat['tense']
            GramNCh.aspect = verbGramFeat['aspect']
            GramNCh.modality = verbGramFeat['modality']
            GramNCh.polarity = verbGramFeat['polarity']
            logger.debug('[N_NPC] ' + GramNCh.as_extended_string())
        else:
            logger.debug('[1] ' + GramNCh.as_extended_string())
        # Even if preceded by a BE or a HAVE form,
        # only tagging N Chunks headed by an eventive noun
        # E.g., "was an intern" will NOT be tagged
        if GramNCh.isEventCandidate_Syn() and GramNCh.isEventCandidate_Sem():
            logger.debug("Accepted Nominal")
            self._processEventInChunk(GramNCh)


class VerbChunk(Chunk):

    def __init__(self, phraseType):
        Chunk.__init__(self, phraseType)
        self.verbs = [-1,-1]

    def getVerbs(self):
        return self.dtrs[self.verbs[0]:self.verbs[1]]

    def startVerbs(self):
        self.verbs[0] = len(self.dtrs)

    def endVerbs(self):
        self.verbs[1] = len(self.dtrs) -1

    def isVerbChunk(self):
        return 1

    def _createGramChunk(self):
        self.cachedGramChunk = GramVChunkList(self)   

    def _updatePositionInSentence(self, endPosition):
        pass

    # The following methods are all from the Evita version. Slinket
    # threw an error when all methods were included, the culprit being
    # _identify_substring, which overrides a slightly
    # different method on Chunk and introduces an error, and whose
    # name was changed a bit for the slinket/s2t version. Need to find
    # better solution.
    # NOTE: this comment may be obsolete by now

    def XXX_identify_substring(self, sentence_slice, fsa_list):
        """Almost the same as Chunk._identify_substring, except that the fsa
        method called is acceptSubstringOf. Method may be obsolete."""
        fsaCounter = -1 
        for fsa in fsa_list:
            #logger.out('Trying FSA', fsa.fsaname)
            fsaCounter += 1
            logger.debug(str(fsa))
            lenSubstring = fsa.acceptsSubstringOf(sentence_slice)
            ##logger.out('length of found match', lenSubstring)
            if lenSubstring:
                return (lenSubstring, fsaCounter)
        else:
            return (0, fsaCounter)


    def _updateFlagCheckedForEvents(self, multiChunkEnd):
        """Update Position in sentence, by marking as already checked for EVENT
        upcoming Tokens and Chunks that are included in multi-chunk """
        for item in multiChunkEnd:
            item.setFlagCheckedForEvents()
            
    def _getRestSent(self, structure):
        """Obtaining the rest of the sentence, which can be
        in a flat, token-based structure, or chunked."""
        logger.debug("Entering _getRestSent")
        if structure == 'flat':
            restSentence = self.getTokens(self.parent[self.position+1:])
        elif structure == 'chunked':
            restSentence = self.parent[self.position+1:]
        else:
            raise "ERROR: unknown structure value"
        return restSentence
            
    def _lookForMultiChunk(self, FSA_set, STRUCT='flat'):
        """Default argument 'STRUCT' specifies the structural format
        of the rest of the sentence: either a flat, token-level representation
        or a chunked one."""
        logger.debug("Entering _lookForMultiChunk")
        restSentence = self._getRestSent(STRUCT)
        if STRUCT == 'flat':                                                  
            for item in restSentence:
                logger.debug("\t "+item.getText()+" "+item.pos)
        lenSubstring, fsaNum = self._identify_substring(restSentence, FSA_set)
        if lenSubstring:
            logger.debug("ACCEPTED by FSA, LENGTH:"+ str(lenSubstring) + "FSA:" + str(fsaNum))
            return restSentence[:lenSubstring]
        else:
            logger.debug("REJECTED by FSA:" + str(fsaNum))
            return 0

    def _processEventInMultiVChunk(self, substring):   
        GramMultiVChunk = GramVChunkList(self._createMultiChunk(substring))[0] 
        #logger.debug("[3] " + gramVCh.as_extended_string())
        self._processEventInChunk(GramMultiVChunk)
        self._updateFlagCheckedForEvents(substring)

    def _processEventInMultiNChunk(self, GramVCh, substring):
        nounChunk = substring[-1]
        verbGramFeatures = {'tense': GramVCh.tense,
                            'aspect': GramVCh.aspect,
                            'modality': GramVCh.modality,
                            'polarity': GramVCh.polarity}
        nounChunk.createEvent(verbGramFeatures)
        self._updateFlagCheckedForEvents(substring)

    def _processEventInMultiAChunk(self, GramVCh, substring):
        adjToken = substring[-1]
        verbGramFeatures = {'tense': GramVCh.tense,
                            'aspect': GramVCh.aspect,
                            'modality': GramVCh.modality,
                            'polarity': GramVCh.polarity}
        adjToken.createAdjEvent(verbGramFeatures)
        self._updateFlagCheckedForEvents(substring)

    def _processDoubleEventInMultiAChunk(self, GramVCh, substring):
        """Tagging EVENT in VChunk """
        logger.debug("[V_2Ev] " + GramVCh.as_extended_string())
        self._processEventInChunk(GramVCh)
        """Tagging EVENT in AdjToken"""
        adjToken = substring[-1]
        adjToken.createAdjEvent()
        self._updateFlagCheckedForEvents(substring)

    def _createEventOnRightmostVerb(self, GramVCh):
        if GramVCh.nodeIsNotEventCandidate():
            pass
        elif GramVCh.nodeIsModalForm(self.nextNode()):
            logger.debug("Entering checking for modal pattern............")
            substring = self._lookForMultiChunk(patterns.MODAL_FSAs)
            if substring:
                self._processEventInMultiVChunk(substring)

        elif GramVCh.nodeIsBeForm(self.nextNode()):
            logger.debug("Entering checking for toBe pattern............")
            """Looking for BE + NOM Predicative Complement """
            logger.debug("Looking for BE + NOM Predicative Complement ")
            substring = self._lookForMultiChunk(patterns.BE_N_FSAs, 'chunked')
            if substring:
                self._processEventInMultiNChunk(GramVCh, substring)  
            else:
                """Looking for BE + ADJ Predicative Complement """
                logger.debug("Looking for BE + ADJ Predicative Complement ")
                substring = self._lookForMultiChunk(patterns.BE_A_FSAs, 'chunked')
                if substring:
                    self._processEventInMultiAChunk(GramVCh, substring)  
                else:
                    """Looking for BE + additional VERBAL structure """
                    logger.debug("Looking for BE + VERB Predicative Complement ")
                    substring = self._lookForMultiChunk(patterns.BE_FSAs)
                    if substring:
                        self._processEventInMultiVChunk(substring)
                       
        elif GramVCh.nodeIsHaveForm():
            logger.debug("Entering checking for toHave pattern............")
            substring = self._lookForMultiChunk(patterns.HAVE_FSAs)
            if substring:
                self._processEventInMultiVChunk(substring)
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsFutureGoingTo():
            logger.debug("Entering checking for futureGoingTo pattern............")
            substring = self._lookForMultiChunk(patterns.GOINGto_FSAs)
            if substring:
                self._processEventInMultiVChunk(substring)
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsPastUsedTo():
            logger.debug("Entering checking for pastUsedTo pattern............")
            substring = self._lookForMultiChunk(patterns.USEDto_FSAs)
            if substring:
                self._processEventInMultiVChunk(substring)
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsDoAuxiliar():
            logger.debug("Entering checking for doAuxiliar pattern............")
            substring = self._lookForMultiChunk(patterns.DO_FSAs)
            if substring:
                self._processEventInMultiVChunk(substring)
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsBecomeForm(self.nextNode()):
            """Looking for BECOME + ADJ Predicative Complement
            e.g., He became famous at the age of 21"""
            logger.debug("Looking for BECOME + ADJ")
            substring = self._lookForMultiChunk(patterns.BECOME_A_FSAs, 'chunked')
            if substring:
                logger.debug("BECOME + ADJ found")
                self._processDoubleEventInMultiAChunk(GramVCh, substring)  
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsContinueForm(self.nextNode()):
            """Looking for CONTINUE + ADJ Predicative Complement
            e.g., Interest rate continued low."""
            logger.debug("Looking for CONTINUE + ADJ")
            substring = self._lookForMultiChunk(patterns.CONTINUE_A_FSAs, 'chunked')
            if substring:
                logger.debug("CONTINUE + ADJ found")
                self._processDoubleEventInMultiAChunk(GramVCh, substring)  
            else:
                self._processEventInChunk(GramVCh)

        elif GramVCh.nodeIsKeepForm(self.nextNode()):
            """Looking for KEEP + ADJ Predicative Complement
            e.g., The announcement kept everybody Adj."""
            logger.debug("Looking for KEEP + [NChunk] + ADJ ")
            substring = self._lookForMultiChunk(patterns.KEEP_A_FSAs, 'chunked')
            if substring:
                logger.debug("KEEP + ADJ found")
                self._processDoubleEventInMultiAChunk(GramVCh, substring)  
            else:
                self._processEventInChunk(GramVCh)
            
        else:
            logger.debug("[1] " + GramVCh.as_extended_string())
            self._processEventInChunk(GramVCh)

    def createEvent(self):
        logger.debug("createEvent in VerbChunk")
        #self.pretty_print()
        GramVChList = self.gramChunk()
        # do not attempt to create an event if there are no true
        # chunks in there
        true_chunks = GramVChList.trueChunkLists
        if len(true_chunks) == 1 and not true_chunks[0]:
            return
        # also skip if there is no content at all
        if len(GramVChList) == 0:
            logger.warn("Obtaining an empty GramVChList")
        # simple case
        elif len(GramVChList) == 1:
            logger.debug("len(GramVChList) == 1")
            self._createEventOnRightmostVerb(GramVChList[-1])
        # complex case
        else:
            logger.debug("len(GramVChList) > 1:" + str(len(GramVChList)))
            lastIdx = len(GramVChList)-1
            for idx in range(len(GramVChList)):
                gramVCh = GramVChList[idx]
                if idx == lastIdx:
                    self._createEventOnRightmostVerb(gramVCh)
                else:
                    logger.debug("[Not Last] " + gramVCh.as_extended_string())
                    if not gramVCh.isAuxVerb():
                        self._processEventInChunk(gramVCh)
