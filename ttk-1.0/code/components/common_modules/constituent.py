from types import ListType, StringType, TupleType

from utilities import logger


class Constituent:
    """An abstract class that contains some methods that are identical
    for Chunks and Tokens plus a couple of default methods."""

    def setParent(self, parent):
        self.parent = parent
        self.position = parent.positionCount

    def document(self):
        return self.parent.document()

    def isToken(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isAdjToken(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isChunk(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isVerbChunk(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isNounChunk(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isAdjChunk(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isTimex(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isEvent(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isNChHead(self):
        """Always returns False. Overrides are specified as needed."""
        return False

    def isPreposition(self):
        """Always returns False. Overrides are specified as needed."""
        return False
    
    def __getattr__(self, name):
        """Used by node._matchChunk. Needs cases for all instance
        variables used in the pattern matching phase."""
        if name == 'nodeType':
            return self.__class__.__name__
        elif name == 'text':
            return None
        elif name == 'pos':
            return None        
        else:
            raise AttributeError, name

    def setFlagCheckedForEvents(self):
        if self.parent.__class__.__name__ == 'Sentence':
            if not self.flagCheckedForEvents:
                self.flagCheckedForEvents = 1
        else:
            self.parent.setFlagCheckedForEvents()

    def getText(self):
        pass

    def nextNode(self):
        """Works only dreamily when called on Sentence elements. If
        called on a token that is embedded in a chunk, then it should
        really look into the next chunk is self is a chunk-final
        token."""
        try:
            return self.parent[self.position+1]
        except IndexError:
            return ''

    def gramChunk(self):
        """Use a cache to increase speed for the code that checks
        patterns. That patterns code breaks because this method
        appears to return None is certain ill-understood cases. Used
        in Evita only."""
        if not self.cachedGramChunk:
            self._createGramChunk()
        return self.cachedGramChunk

    def _createGramChunk(self):
        """Used in Evita only"""
        self.cachedGramChunk = 0

    def createEvent(self):
        """Used in Evita only"""
        logger.debug("CreateEvent in Consituent")
        pass

    def _hackToSolveProblemsInValue(self, value):
        """From slinket/s2t"""
        #logger.out('self is a', self.__class__.__name__, '; value =', value)
        if type(value) is ListType:
            if len(value) == 2 and value[0] == '' and value[1] == '':
                return [',']
            else:
                return value
        elif type(value) is StringType:
            if value == '':
                return '"'
            else:
                return value
        else:
            return value

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
    
        This method is also implemented in the chunkAnalyzer.GramChunk class """
        for feat in chunkDescription.keys():
            value = chunkDescription[feat]
            if type(value) is TupleType:
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
                if self.__getattr__(feat) not in value:
                    return 0
            else:
                value = self._hackToSolveProblemsInValue(value)
                if self.__getattr__(feat) != value:
                    return 0
        return 1


    def get_event(self):
        """Return None or the EventTag that is contained in the
        constituent."""
        if self.isEvent():
            return self
        elif self.isChunk:
            for element in self:
                if element.isEvent():
                    return element
        return None

    def get_timex(self):
        """Return None or the TimexTag that is contained in the
        constituent."""
        if self.isTimex():
            return self
        elif self.isChunk:
            for element in self:
                if element.isTimex():
                    return element
        return None

    def pp(self):
        self.pretty_print()

    def pretty_print(self):
        print "<<pretty_print() not defined for this object>>"
