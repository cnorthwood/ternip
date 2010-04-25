"""Contains functionality specific to sentences in a document."""

from utilities import logger


class Sentence:

    """A Sentence is a top-level element of a Document. It contains a list
    of Chunks and Tokens.
    
    Instance variables
        dtrs - a list of Chunks and Tokens
        chunkIndex - an integer
        eventList - a list of (eLoc, eid) tuples
        position - an integer, reflecting the offset in the document 
        positionCount - an integer, reflecting the current position in the sentence 
        parent - a Document
        embeddedTags - a list

    The eventList variable stores (eLoc, eid) tuples of each tagged
    event in the sentence, the eLoc is the location of the event
    inside the embedding constituent, usually a chunk). The
    embeddedTags variable is a stack to keep track of all currently
    open elements, in order to deal with multiple embedding of the
    same element type; e.g., <T3><Chk><T3><Chk> ...
    </Chk></T3></Chk></T3> """

    def __init__(self):
        """Initialize all instance variables to 0, empty list or None."""
        self.dtrs = []
        self.chunkIndex = 0
        self.eventList = [] 
        self.position = None
        self.positionCount = 0
        self.parent = None
        self.embeddedTags = []
        
    def __len__(self):
        """Returns length of dtrs variable."""
        return len(self.dtrs)

    def __getitem__(self, index):
        """Get an item from the dtrs variable."""
        if index is None:
            logger.warn("Given index to __getitem__ in Sentence is None")
            return None
        else:
            return self.dtrs[index]

    def __getslice__(self, i, j):
        """Get a slice from the dtrs variable."""
        return self.dtrs[i:j]

    def document(self):
        """Return the document that the sentence is in."""
        return self.parent.document()

    def add(self, chunkOrToken):
        """Add a chunk or token to the end of the sentence. Sets the sentence
        as the value of the parents variable on the chunk or token.
        Arguments
           chunkOrToken - a Chunk or a Token"""
        chunkOrToken.setParent(self)
        self.dtrs.append(chunkOrToken)
        self.positionCount += 1

    def setParent(self, parent):
        """Set the parent feature of the sentence to the document. Also copies
        the postionCount variable of the parent to the position
        variable of the sentence.
        Arguments
           parent - a Document"""
        self.parent = parent
        self.position = parent.positionCount

    def storeEventLocation(self, evLoc, eid):
        """Appends a tuple of event location and event id to the eventList.
        Arguments
           evLoc - an integer
           eid - an eid"""
        self.eventList.append((evLoc, eid))

    def get_event_list(self):
        """Return the list of eLocation-eid tuples of the sentence."""
        event_list = []
        eventLocation = -1
        for element in self:
            eventLocation += 1
            if element.isChunk():
                event = element.embedded_event()
                if event:
                    event_list.append((eventLocation, event.eid))
        return event_list

    def set_event_list(self):
        """Set the value of self.eventList to the list of eLocation-eid tuples
        in the sentence. This is used by Slinket."""
        self.eventList = self.get_event_list()

    def trackEmbedding(self, tag):
        """Tracks embedding of event and timex tags relative to other
        chunks. Used when (i) a chunk is embedded in a timex, event or
        other chunk, (ii) an event is found inside a timex or other
        event, or (iii) a timex is found inside another timex or an
        event."""
        self.embeddedTags.append(tag)

    def hasEmbedded(self, tag):
        """Returns True if the given tag occurs in the last position of the
        embeddedTags list, return False otherwise.
        Arguments
           tag - a string indicating the tag name"""
        if self.embeddedTags and self.embeddedTags[-1] == tag:
            return True
        else:
            return False

    def removeEmbedded(self, tag):
        """Remove the last element of the embeddedTags list if it matches the
        given tag name.
        Arguments
           tag - string indicating the tag name"""
        self.embeddedTags = self.embeddedTags[:-1]
        
    def getTokens(self):
        """Return the list of tokens in a sentence."""
        # NOTE: seems to be used by the evitaNominalTrainer only
        tokenList = []
        for chunkOrToken in self.dtrs:
            if chunkOrToken.isToken():
                tokenList += [chunkOrToken]
            elif chunkOrToken.isChunk():
                tokenList += chunkOrToken.dtrs
            else:
                logger.warn("Sentence element that is not a chunk or token")
        return tokenList

    def pretty_print(self):
        """Pretty print the sentence by pretty printing all daughters"""
        for dtr in self.dtrs:
            dtr.pretty_print(indent=2)
        

        
