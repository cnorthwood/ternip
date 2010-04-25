"""Contains functionality specific to documents."""

import sys
import re

from library.timeMLspec import EID, EIID, EVENTID
from library.timeMLspec import ALINK, SLINK, TLINK


class Document:

    """Implements the shallow tree that is input to some of the Tarsqi components.

    Instance variables
    
        nodeList - a list of strings, each representing a document element
        sentenceList - a list of Sentences
        nodeCounter - an integer
        sourceFileName  an absolute path
        taggedEventsDict - a dictionary containing tagged event in the input
        instanceCounter - an integer
        insertDict - dictionary (integer --> string)

        event_dict - dictionary (eid --> EventTag)
        instance_dict a dictionary (eiid --> InstanceTag)
        alink_list - a list of AlinkTags
        slink_list - a list of SlinkTags
        tlink_list - a list of TlinkTags

        eventCount - an integer
        alinkCount - an integer
        slinkCount - an integer
        tlinkCount - an integer
        linkCount - an integer
        positionCount - an integer

    The taggedEventsDicts is used by Slinket, storing events indexed
    on event IDs, its function can probably be taken over by the
    event_dict variable. The insertDict variable is used by Evita. It
    keeps track of event and instance tags that need to be inserted
    and indexes them on the index in the nodeList where they need to
    be inserted.

    The variables event_dict, instance_dict, alink_list, slink_list
    and tlink_list are filled in by the FragmentConverter.

    The counters are incremented when elements are added, most
    counters are used to create unique ids for newly created tags. The
    positionCount is incremented when a sentence or a timex is added
    to the document (using addSentence or addTimex). It is used so the
    position variable can be set on Sentences (that is, the Sentence
    knows at what position in the document it occurrs)."""


    def __init__(self, fileName):
        """Initialize all dictionaries, list and counters and set the file name."""
        self.nodeList = []
        self.sentenceList = []
        self.nodeCounter = 0
        self.sourceFileName = fileName
        self.taggedEventsDict = {}        # used by slinket's event parser
        self.instanceCounter = 0
        self.insertDict = {}              # filled in by Evita
        self.event_dict = {}              # next five created by the FragmentConverter
        self.instance_dict = {}
        self.alink_list = []
        self.slink_list = []
        self.tlink_list = []
        self.eventCount = 0
        self.alinkCount = 0
        self.slinkCount = 0 
        self.tlinkCount = 0 
        self.linkCount = 1                # used by S2T
        self.positionCount = 0            # obsolete?

    def __len__(self):
        """Length is determined by the length of the sentenceList."""
        return len(self.sentenceList)

    def __getitem__(self, index):
        """Indexing occurs on the sentenceList variable."""
        return self.sentenceList[index]

    def __getslice__(self, i, j):
        """Slice from the sentenceList variable."""
        return self.sentenceList[i:j]

    def addDocNode(self, string):
        """Add a node to the document's nodeList. Inserts it at the location
        indicated by the nodeCounter.
        Arguments
           string - a string representing a tag or text"""
        # could probably add it by appending it to nodeList
        self.nodeList.insert(self.nodeCounter, string)
        self.nodeCounter = self.nodeCounter + 1 

    def addDocLink(self, loc, string):
        """Add a node to the document's nodeList. Inserts it at the specified
        location and not at the ned of the document (as indicated by
        noedeCounter. Still increments the nodeCounter becasue the
        document grows by one element. This is much like addDocNode,
        but it used for adding nodes that were not in the input but
        that were created by a Tarsqi component.
        Arguments
           loc - an integer, iundicating the location of the insert point
           string - a string representing a tag or text"""
        self.nodeList.insert(loc, string)
        self.nodeCounter = self.nodeCounter + 1
                
    def addSentence(self, sentence):
        """Append a Sentence to the sentenceList and sets the parent feature
        of the sentence to the document. Also increments the
        positionCount."""
        sentence.setParent(self)
        self.sentenceList.append(sentence)
        self.positionCount += 1

    def addTimex(self, timex):
        """Applied when a timex cannot be added to a Chunk or a Sentence,
        probably intended for the DCT."""
        # NOTE: this is probably wrong, test it with a document where
        # the DCT will not end up in a sentence tag
        timex.setParent(self)
        self.positionCount += 1
    
    def hasEventWithAttribute(self, eid, att):
        """Returns the attribute value if the taggedEventsDict has an event
        with the given id that has a value for the given attribute,
        returns False otherwise
        Arguments
           eid - a string indicating the eid of the event
           att - a string indicating the attribute"""
        return self.taggedEventsDict.get(eid,{}).get(att,False)

    def _OLD_storeEventValues(self, pairs):
        print "PAIRS:", pairs
        try: eid = pairs[EID]
        except: eid = pairs[EVENTID]
        try:
            eventInfo = self.taggedEventsDict[eid]
            # There is already info for that event, therefore, tag is
            # an INSTANCE tag or STRING data
            for (att, val) in pairs.items():
                self.taggedEventsDict[eid][att] = val
        except:
            # tag is an EVENT tag
            evInfo = {}
            for att in pairs.keys():
                #evInfo = {}
                evInfo[att] = pairs[att]
                #if att == EID: pass
                #else: evInfo[att] = pairs[att]
                self.taggedEventsDict[eid] = evInfo
            print 'EVINFO', evInfo
    
    def storeEventValues(self, pairs):
        """Store attributes associated to an event (that is, they live on an
        event or makeinstance tag) in the taggedEventsDictionary.
        Arguments
           pairs - a dcitionary of attributes"""
        # get eid from event or instance
        try: eid = pairs[EID]
        except KeyError: eid = pairs[EVENTID]
        # initialize dictionary if it is not there yet
        if not eid in self.taggedEventsDict:
            self.taggedEventsDict[eid] = {}
        # add data
        for (att, val) in pairs.items():
            self.taggedEventsDict[eid][att] = val

    def document(self):
        """Returns the document itself."""
        return self

    def addTimexTag(self, timex):
        """Adds a timex tag to the document. Works similarly to the
        addEvent method. This method is used by post-GUTime
        processing, filling in some gaps. Should not be confused with
        addTimex, which is used when the document if first created.
        Arguments
           timex - a TimexTag"""
        timex.attrs["tid"] = self._getNextTimexID()
        startLoc = timex.dtrs[0].textIdx - 1
        endLoc = timex.dtrs[-1].textIdx + 2
        self._insertNode(startLoc, startElementString("TIMEX3", timex.attrs))
        self._insertNode(endLoc, endElementString("TIMEX3"))
    
    def addEvent(self, event):
        """Adds an event to the document. Retrieves the document location from
        the tokens embedded in the event (tokens contain a textIdx
        variable which is set with the valiue of the nodeCounter of
        the Document). Events are added by inserting a node into the
        insertDict variable. Also adds the instance to the insertDict.
        Arguments
           event - an Event"""
        event.attrs["eid"] = self._getNextEventID()
        # substract 1 to get opening EVENT tag outside of lex tag
        startLoc = event.tokenList[0].textIdx 
        # add 2 to get closing EVENT tag outside of lex tag
        endLoc = event.tokenList[-1].textIdx + 1
        self._insertNode(startLoc, startElementString("EVENT", event.attrs))
        self._insertNode(endLoc, endElementString("EVENT"))
        instLoc = endLoc
        for instance in event.instanceList:
            instance.attrs["eiid"] = self._getNextInstanceID()
            instance.attrs["eventID"] = event.attrs["eid"]
            instLoc = instLoc + 1
            self._insertNode(instLoc,
                             emptyContentString("MAKEINSTANCE", instance.attrs))
            
    def addLink(self, linkAttrs, linkType):
        """Add an Alink or Slink to the document. Adds it at the end of the
        dopcument, that is, at the position indicated by the instance
        variable nodeCount. This means that the resulting file is not
        valid XML, but this is not problematic since the file is a
        fragment that is inserted back into the whole file. This will
        break down though is the fragment happens to be the outermost
        tag of the input file. This method should probably use
        addDocLink instead of addDocNode.
        Note that TLinks are added directly to the xml document and
        not to the Document. Evita and Slinket are not yet updated to
        add to the xmldoc and hence need this method.
        Arguments
           linkAttrs - dictionary of attributes
           linkType - "ALINK" | "SLINK" """
        linkAttrs['lid'] = self._getNextLinkID(linkType)
        self.addDocNode(emptyContentString(linkType, linkAttrs))

    def _XXX_addSlink(self, relType, slinkingEid, slinkedEid, patternName):
        """Add an Slink to the end of the document. Uses addLink.
        Seems to be obsolete.
        Arguments
           relType - an Slink relType
           slinkingEid - an eiid
           slinkedEid - an eiid
           patternName - a string"""
        slinkAttrs = {'eventInstanceID': slinkingEid,
                      'subordinatedEventInstance': slinkedEid,
                      'relType': relType,
                      'syntax': patternName}
        self.addLink(slinkAttrs, SLINK)

    def _XXX_addTlink(self, relType, instance, relatedInstance, allAlinks, allTlinks, allSlinks, origin):
        """This method is now obsolete since S2T and Blinker add tlinks to the
        xmldoc and not to the Document."""
        lid = self._getNextLinkID()
        tlinkAttrs = {'eventInstanceID': instance,
                      'relatedToEventInstance': relatedInstance,
                      'relType': relType,
                      'lid': lid,
                      'origin': origin}
        self.addDocNode(emptyContentString("TLINK", tlinkAttrs))

    def _getNextTimexID(self):
        tids = []
        re_tid = re.compile('tid="t(\d+)"')
        for node in self.nodeList:
            if node.startswith('<TIMEX3'):
                match = re_tid.search(node)
                if match:
                    id = match.group(1)
                    tids.append(int(id))
        tids.sort()
        try:
            next_id = tids[-1] + 1
        except IndexError:
            next_id = 1
        return "t%d" % next_id

    def _getNextEventID(self):
        """Increment eventCount and return a new unique eid. Assumes that all
        events are added using this method, otherwise, non-unique eids could
        be assigned."""
        self.eventCount += 1
        return "e"+str(self.eventCount) 
        
    def _getNextInstanceID(self):
        """Increment eventCount and return a new unique eiid. Assumes that all
        instances are added using this method, otherwise, non-unique
        eiids could be assigned."""
        self.instanceCounter += 1
        return "ei"+str(self.instanceCounter)

    def _getNextLinkID(self, linkType):
        """Return a unique lid. The linkType argument has no influence over
        the lid that is returned but determines what link counter is
        incremented. Assumes that all links are added using the link
        counters in the document. Breaks down if there are already
        links added without using those counters.
        Arguments
           linkType = ALINK|SLINK|TLINK """
        if linkType == ALINK:
            return self._getNextAlinkID()
        elif linkType == SLINK:
            return self._getNextSlinkID()
        elif linkType == TLINK:
            return self._getNextSlinkID()
        else:
            logger.error("Could not create link ID for link type" + str(linkType))

    def _getNextAlinkID(self):
        """Increment alinkCount and return a new unique lid."""
        self.alinkCount += 1
        return "l"+str(self.alinkCount + self.slinkCount + self.tlinkCount)
    
    def _getNextSlinkID(self):
        """Increment slinkCount and return a new unique lid."""
        self.slinkCount += 1
        return "l"+str(self.alinkCount + self.slinkCount + self.tlinkCount)

    def _getNextTlinkID(self):
        """Increment tlinkCount and return a new unique lid."""
        self.tlinkCount += 1
        return "l"+str(self.alinkCount + self.slinkCount + self.tlinkCount)

    def _insertNode(self, nodeNo, string):
        """Inserts a new event tag or instance tag into the insertDict."""
        if self.insertDict.has_key(nodeNo):
            logger.error("Already have inserted an event or instance tag for node: "+str(nodeNo))
        else:
            self.insertDict[nodeNo] = string
    
    def _XXX_insertEventsInText(self):
        """obsolete"""
        for event in self.eventDict.values():
            startLoc = event.tokenList[0].textIdx - 1
            endLoc = event.tokenList[-1].textIdx + 2
            self._insertNode(startLoc, startElementString("EVENT", event.attrs))
            self._insertNode(endLoc, endElementString("EVENT"))
            instLoc = endLoc
            for instance in event.instanceList:
                instLoc = instLoc + 1
                self._insertNode(instLoc, emptyContentString("MAKEINSTANCE", instance.attrs))
        
    def _XXX_insertSignalsInText(self):                               
        """obsolete"""
        for signal in self.signalDict.values():                  
            startLoc = signal.tokenList[0].textIdx - 1              
            endLoc = signal.tokenList[-1].textIdx + 2
            self._insertNode(startLoc, startElementString("SIGNAL", signal.attrs))  
            self._insertNode(endLoc, endElementString("SIGNAL"))  
            instLoc = endLoc                                     
    
    def _XXX_addHeader(self):
        """obsolete"""
        decString = '<?xml version="1.0" ?>\n'
        self.addDocNode(decString)
        rootDict = {
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 
            'xsi:noNamespaceSchemaLocation': 'http://www.timeml.org/timeMLdocs/TimeML.xsd' }
        rootStart = startElementString('TimeML', rootDict)
        self.addDocNode(rootStart)

    def printOut(self, fileName = "STDOUT"):
        """Print the document to a file or to standard output.
        Arguments
           fileName - "STDOUT" or an absolute path, the first by default """
        # determine output
        if fileName == "STDOUT":
            file = sys.stdout
        else:
            file = open(fileName, "w")
        # loop through document
        for i in range(len(self.nodeList)):
            if self.insertDict.has_key(i):
                file.write(self.insertDict[i])
            node = self.nodeList[i]
            node = protectNode(node)
            file.write(node)
                
    def pretty_print(self):
        """Pretty printer that prints all instance variables and a neat
        representation of the sentence list."""
        print "\n<<Document %s>>\n" % self.sourceFileName
        print 'nodeCounter', self.nodeCounter
        print 'taggedEventsDict'
        eids = self.taggedEventsDict.keys()
        eids.sort()
        for eid in eids:
            print ' ', eid, '=> {',
            attrs = self.taggedEventsDict[eid].keys()
            attrs.sort()
            for attr in attrs:
                print "%s=%s" % (attr, str(self.taggedEventsDict[eid][attr])),
            print '}'
        print 'instanceCounter =', self.instanceCounter
        print 'insertDict =', self.insertDict
        print 'eventCount =', self.eventCount
        print 'alinkCount =', self.alinkCount
        print 'slinkCount =', self.slinkCount
        print 'linkCount =', self.linkCount
        print 'postionCount =', self.positionCount
        count = 0
        for sentence in self.sentenceList:
            count = count + 1
            print "\nSENTENCE " + str(count) + "\n"
            sentence.pretty_print()
        print "\n"

        
def protectNode(node):
    """Make sure that the node remains well-formed XML"""

    # NOTE: should move this to other module

    # this test for <?xml seemed to be necessary for Slinket
    # and S2T, but not for Evita, probably because the xml
    # parsers are different
    if  node[0:5] == '<?xml':
        return node
    else:
        # The XML parser replaces &amp; etc with the one-character
        # equivalents, which means that the result is not XML.
        # Protect &, < and >. A hack, needs to be done more elegantly
        if not _isTag(node):
            node = node.replace('&','&amp;')
            node = node.replace('"','&quot;')
            node = node.replace('<','&lt;')
            node = node.replace('>','&gt;')
        elif node[0:4] == '<lex':
            node = node.replace('&','&amp;')
            node = node.replace('"""','"&quot;"')
            # this is a total hack, just here for the RTE data
            node = node.replace(' "Gus" ',' &quot;Gus&quot; ')
            node = node.replace(' "Tookie" ',' &quot;Tookie&quot; ')
        return node

def _isTag(token):
    """Return True if the sting argument is a tag. Cannot simply check for
    final > because sometimes python expat leaves trailing newline as part
    of token."""
    return token[0] == '<' and token.find('>') > -1



def endElementString(name):
    """Return the string representation of a closing tag.
    Arguments
       name - the name of a tag"""
    return '</'+name+'>'

def startElementString(name, attrs):
    """Return the string representation of an opening tag.
    Arguments
       name - the name of a tag
       attrs - a dictionary of attributes"""
    string = '<'+name
    for att in attrs.items():
        name = att[0]
        value = att[1]
        if not (name is None or value is None):
            string = string+' '+name+'="'+value+'"'
    string = string+'>'
    return string

def emptyContentString(name, attrs):
    """Return the string representation of a non-consuming tag.
    Arguments
       name - the name of a tag
       attrs - a dictionary of attributes"""
    string_as_opening_string = startElementString(name, attrs)
    return string_as_opening_string[:-1] + '/>'
