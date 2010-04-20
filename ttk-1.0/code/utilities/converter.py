"""Contains converters to map between representations.

Currently contains only one converter. FragmentConverter takes an
XmlDocument and creates an instance of the Document class.

"""

import time

from components.common_modules.document import Document
from components.common_modules.sentence import Sentence
from components.common_modules.chunks import NounChunk, VerbChunk
from components.common_modules.tokens import Token, AdjectiveToken
from components.common_modules.tags import EventTag, InstanceTag, TimexTag
from components.common_modules.tags import AlinkTag, SlinkTag, TlinkTag
from library.tarsqi_constants import SLINKET, BLINKER
from library.timeMLspec import SENTENCE, NOUNCHUNK, VERBCHUNK, TOKEN
from library.timeMLspec import EVENT, INSTANCE, TIMEX, ALINK, SLINK, TLINK
from library.timeMLspec import EID, EIID, EVENTID
from library.timeMLspec import POS, POS_ADJ, FORM, EPOS
from utilities import logger



class FragmentConverter:

    """Takes a fragment formatted as a simple list of xml elements (an
    XmlDocument object) and convert it into a shallow tree implemented
    as a Document object. Also maintain lists and dictionaries of
    events, instances, and links.

    Instance variables:
       xmldoc - an XmlDocument
       doc - a Document
       currentSentence - a Sentence 
       currentChunk - a NounChunk or VerbChunk
       currentToken - a Token or AdjectiveToken
       currentTimex - a TimexTag
       currentEvent - an EventTag

    The Document instance in doc contains a list of Sentences where
    each Sentence is a list of Tokens and Chunks. Chunks can contain
    TimexTags and EventTags.

    Chunks are always embedded in Sentences (that is, they are direct
    daughters of Sentences), TimexTags are always embedded in Chunks,
    EventTags are embedded in Chunks or Sentences (the latter for
    adjectival events) and Tokens are embedded in Events, TimexTags,
    Chunks or Sentences. Here is an example pretty print of a short
    Sentence:

      <NG>
        <lex pos="PP" text="He">
      <VG>
         <EVENT eid=e6 eiid=ei6 class=OCCURRENCE>
            <lex pos="VBD" text="slept">
      <lex pos="IN" text="on">
      <NG>
         <TIMEX3 tid=t2 TYPE=DATE VAL=20070525TNI>
            <lex pos="NNP" text="Friday">
            <lex pos="NN" text="night">
      <lex pos="." text="."> """

    
    def __init__(self, xmldoc, filename):
        """Initializes xmldoc and doc, using two arguments: xmldoc (an
        XmlDocument) and filename (a string). Also sets instance
        variables currentSentence, currentChunk, currentToken,
        currentEvent and currentTimex to None."""
        self.xmldoc = xmldoc
        self.doc = Document(filename)
        self.currentSentence = None
        self.currentChunk = None
        self.currentToken = None
        self.currentTimex = None
        self.currentEvent = None

    def convert(self, user=None):
        """Convert the flat list of XML elements in xmldoc into a Document and
        store it in self.doc. Returns the value of self.doc."""
        #t1 = time.time()
        for element in self.xmldoc:
            if element.is_opening_tag():
                self._process_opening_tag(element)
            elif element.is_closing_tag():         
                self._process_closing_tag(element)
            else:
                self._process_element(element)
            self.doc.addDocNode(element.content)
        #t2 = time.time()
        #logger.out("converted xmldoc in %.3f" % (t2 - t1))
        if user in [SLINKET, BLINKER]:
            self._massage_doc()
        if user == SLINKET:
            self._build_event_dictionary()
            self._set_event_lists()
        return self.doc

    def _process_opening_tag(self, element):
        """Process an opening tag, calling the appropriate handler depending
        on the tag."""
        logger.debug('>>'+ element.content)
        if element.tag == SENTENCE:
            self.currentSentence = Sentence()
            self.doc.addSentence(self.currentSentence)
        elif element.tag == NOUNCHUNK:
            self._process_opening_chunk(NounChunk, element)
        elif element.tag == VERBCHUNK:
            self._process_opening_chunk(VerbChunk, element)
        elif element.tag == TOKEN:
            self._process_opening_lex(element)
        elif element.tag == EVENT:
            self._process_opening_event(element)
        elif element.tag == INSTANCE:
            self._process_opening_make_instance(element)
        elif element.tag == TIMEX:
            self._process_opening_timex(element)
        elif element.tag == ALINK:
            self._process_alink(element)
        elif element.tag == SLINK:
            self._process_slink(element)
        elif element.tag == TLINK:
            self._process_tlink(element)

    def _process_opening_chunk(self, chunk_class, element):
        """Create a VerbChunl or NounCHunk and add it to the current sentence."""
        self.currentChunk = chunk_class(element.tag)
        self.currentSentence.add(self.currentChunk)

    def _process_opening_lex(self, element):
        """Creates a Token or AdjectviveToken and adds it to the current timex
        if there is one, otherwise to the current chunk if there is one, and
        otherwise to the current sentence if there is one."""
        logger.debug('    opening lex')
        pos = element.attrs[POS]
        if pos.startswith(POS_ADJ):
            self.currentToken = AdjectiveToken(self.doc, pos)
        else:
            self.currentToken = Token(self.doc, pos)
        # this is needed for later when tokens and events are swapped,
        # the default is that a token does not contain an event, this
        # can be changed when an event tag is processed
        self.currentToken.contains_event = False
        self.currentToken.lex_tag = element
        logger.debug('    current chunk '+ str(self.currentChunk))
        logger.debug('    current sent  '+ str(self.currentSentence))
        # previously, just checked the truth of self.currentChunk and
        # self.currentSentence, which worked fine for the latter but
        # not for the former (no idea why that was the case, MV)
        if self.currentTimex is not None:
            logger.debug('    adding token to chunk')
            self.currentTimex.add(self.currentToken)
        elif self.currentChunk is not None:
            logger.debug('    adding token to chunk')
            self.currentChunk.addToken(self.currentToken)
        elif self.currentSentence is not None:
            logger.debug('    adding token to sentence')
            self.currentSentence.add(self.currentToken)

    def _process_opening_event(self, element):
        """Creates an EventTag and add it to the event dictionary on the
        Document instance. Also sets the contains_event flag on the
        current token to indicate that the token has an event embedded
        in it (due to an Evita peculiarity of embedding events inside
        of tokens). The EventTag is not added to any consituent,
        _massage_doc takes care of that."""
        event = EventTag(element.attrs)
        self.currentEvent = event
        eid = event.attrs[EID]
        self.doc.event_dict[eid] = event
        self.currentToken.contains_event = True
        # add event info to containing adjective tokens and chunks, it
        # is not set on other tokens because they do not respond to
        # setEventInfo
        if self.currentToken.isAdjToken():
            self.currentToken.setEventInfo(eid)
        else:
            self.currentChunk.setEventInfo(eid)
        self.currentToken.event_tag = event

    def _process_opening_make_instance(self, element):
        """Creates an InstanceTag and adds it to the instance dictionary on
        the Document. Also copies all attributes on the instance to
        the event. The InstanceTag is not added to a Chunk or Sentence
        or any other element of the shallow tree."""
        instance = InstanceTag(element.attrs)
        eid = instance.attrs[EVENTID]
        eiid = instance.attrs[EIID]
        for (key, value) in instance.attrs.items():
            if key == EVENTID: continue
            self.doc.event_dict[eid].attrs[key] = value
        self.doc.instance_dict[eiid] = instance

    def _process_opening_timex(self, element):
        """Creates a TimeTag and embed it in the current chunk if there is
        one, otherwise add it to the sentence."""
        self.currentTimex = TimexTag(element.attrs)
        logger.debug(str(self.currentTimex.__dict__))
        logger.debug('TYPE:'+ str(type(self.currentTimex)))
        if self.currentChunk != None:
            self.currentChunk.addToken(self.currentTimex)
        else:
            self.currentSentence.add(self.currentTimex)

    def _process_alink(self, element):
        """Add an AlinkTag to the Alinks list on the Document."""
        alink = AlinkTag(element.attrs)
        self.doc.alink_list.append(alink)
    
    def _process_slink(self, element):
        """Add an SlinkTag to the Slinks list on the Document."""
        slink = SlinkTag(element.attrs)
        self.doc.slink_list.append(slink)
        
    def _process_tlink(self, element):
        """Add an TlinkTag to the Tlinks list on the Document."""
        tlink = TlinkTag(element.attrs)
        self.doc.tlink_list.append(tlink)
    
    def _process_closing_tag(self, element):
        """Resets currentSentence or other currently open constituent to None,
        depending on the closing tag.""" 
        logger.debug('>>' + element.content)
        if element.tag == SENTENCE: self.currentSentence = None
        if element.tag == NOUNCHUNK: self.currentChunk = None
        if element.tag == VERBCHUNK: self.currentChunk = None
        if element.tag == TOKEN: self.currentToken = None
        if element.tag == EVENT: self.currentEvent = None
        if element.tag == TIMEX: self.currentTimex = None

    def _process_element(self, element):
        """Non-tags are treated as text nodes and added to the current token
        if there is one."""
        logger.debug('>>"'+element.content+'"')
        if self.currentToken != None:
            self.currentToken.setTextNode(self.doc.nodeCounter)

    def _massage_doc(self):
        """This method has only one goal and that is to normalize tag
        order of lex tags and event tags. Evita creates event tags
        inside lex tags, which is not what we want. Take each lex tags
        and check if its event feature is set, if so, replace the lex
        tag with an event tag and embed the lex in the event tag. This
        method method will become obsolete once Evita does the right
        thing, but _process_opening_event will need to be changed when
        that happens."""
        
        def _massage_sequence(sequence, indent=0):
            """Traverse down the tree, seeking tokens."""
            for index in range(0, len(sequence)):
                item = sequence[index]
                if item.isToken():
                    logger.debug("%s%d Token" % (indent * ' ', index))
                    _massage_token(item, sequence, index)
                elif item.isChunk():
                    logger.debug("%s%d Chunk" % (indent * ' ', index))
                    _massage_sequence(item.dtrs, indent+3)
                elif item.isTimex():
                    logger.debug("%s%d Timex" % (indent * ' ', index))
                    _massage_sequence(item.dtrs, indent+3)

        def _massage_token(token, sequence, index):
            """If a token was marked as having an event, replace it with the event
            and insert the token inside the event."""
            if token.contains_event:
                # next line only to prevent printing, may have dire
                # consequence, but shouldn't (MV, 2007/06/16)
                token.contains_event = None
                token.event_tag.dtrs = [token]
                sequence[index] = token.event_tag

        for sentence in self.doc:
            _massage_sequence(sentence.dtrs, 3)


    def _build_event_dictionary(self):
        """Creates a dictionary with events on the self.doc variable."""
        instances = {}
        for instance in self.xmldoc.get_tags(INSTANCE):
            instances[instance.attrs[EVENTID]] = instance.attrs
        events = {}
        for event in self.xmldoc.get_tags(EVENT):
            eid = event.attrs[EID]
            events[eid] = event.attrs
            events[eid].update(instances[eid])
            # Now get the form and the part of speech. This is a bit
            # tricky since it relies on the fact that an event tag is
            # always preceded by a lex tag and followed by plain text
            pos = event.previous.attrs[POS]
            form = event.next.content
            events[eid][FORM] = form
            events[eid][EPOS] = events[eid][POS]
            events[eid][POS] = pos
        self.doc.taggedEventsDict = events

    def _set_event_lists(self):
        for sentence in self.doc:
            sentence.set_event_list()
