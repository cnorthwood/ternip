

class ObjectList:
    """Class that provides interface for global PointLink and Link data
    bases. Just a wrapper around a list. Assumes that all elements are 
    temporal objects because it uses isTrivial to skip some elements
    for printing"""

    def __init__(self,name):
        self.name = name
        self.data = []

    def __getitem__(self,key):
        return self.data[key]
        
    def add(self,pLink):
        self.data.append(pLink)

    def asList(self):
        return self.data

    def __str__(self):
        returnStr = "\n==> " + self.name + " <==\n"
        for object in self.data:
            if not object.isTrivial():
                returnStr = returnStr + "\n" + str(object)
        return returnStr



class TemporalObject:
    """Abstract class that is a super class of all link and node classes. Only
    responsible for providing unique IDs."""
    
    __count__ = 0

    def newID(self):
        TemporalObject.__count__ = TemporalObject.__count__ + 1
        return TemporalObject.__count__
        
    def isTrivial(self): return 0

    
class AbstractNode(TemporalObject):

    def addInLink(self,pointlink):
        self.inLinks.append(pointlink)
        self.isDirty = 1

    def addOutLink(self,pointlink):
        self.outLinks.append(pointlink)
        self.isDirty = 1

        

class Node(AbstractNode):

    def __init__(self,environment):
        self.id = self.newID()
        self.begin = None
        self.end = None
        self.hasPoints = 0
        self.pointLinks = []
        self.inLinks = []
        self.outLinks = []
        self.isDirty = 1
        environment.addNode(self)

    def isEvent(self): return 0
    def isTimex(self): return 0

    def generatePoints(self,environment):
        if self.hasPoints: return
        self.begin = Point(environment,self,"begin")
        self.end = Point(environment,self,"end")
        # PLink initialization takes care of adding links to points
        # and to environment
        self.pointLinks.append(PLink(environment,self.begin,'<',self.end))
        self.hasPoints = 1


class EventNode(Node):

    def __init__(self,environment,eventString,eventClass,addPoints=1):
        Node.__init__(self,environment)
        self.string = eventString
        self.type = 'EVENT'
        self.eventClass = eventClass
        if addPoints: self.generatePoints(environment)

    def isEvent(self): return 1

    def __str__(self):
        return "EventNode(%s,%s,%s)" % (self.id, self.string,self.eventClass)

    def printVerbosely(self):
        print "\nEVENT(%s %s %s)" % (self.id, self.string, self.eventClass)
        print "  inLinks:"
        for link in self.inLinks:
            print "    %s --(%s,%s)--> SELF" % (link.begin, link.id, link.relation)
        print "  outLinks:"
        for link in self.outLinks:
            print "    SELF --(%s,%s)--> %s" % (link.id, link.relation, link.end)
        

class TimexNode(Node):

    def __init__(self,environment,timexString,timexClass,addPoints=1):
        Node.__init__(self,environment)
        self.type = 'TIMEX3'
        self.string = timexString
        self.timexClass = timexClass
        if addPoints: self.generatePoints(environment)

    def isTimex(self): return 1


class Point(AbstractNode):

    def __init__(self,environment,interval,boundary):
        self.id = self.newID()
        self.interval = interval
        self.boundary = boundary
        self.inLinks = []
        self.outLinks = []
        self.isDirty = 1
        environment.addPoint(self)
        # give the point a name derived from the name of the interval
        self.string = interval.string
        if boundary == 'begin':
            self.string = "%s%s" % (self.string,1)
        if boundary == 'end':
            self.string = "%s%s" % (self.string,2)
    def __str__(self):
        return "Point(%s,%s,%s)" % (self.id,self.interval.string,self.boundary)

    def copy(self,newEnvironment):
        """Only copies the interval and the boundaries, does not copy inlinks
        outlinks and anything else. Creates a new Point with unique id."""
        return Point(newEnvironment,self.interval,self.boundary)

    def printVerbosely(self):
        print "\nPoint(%s)" % (self.id)
        print "  %s - %s" % (self.interval,self.boundary)
        print "  inLinks:"
        for link in self.inLinks: print "      ", link
        print "  outLinks:"
        for link in self.outLinks: print "      ", link


class AbstractLink(TemporalObject):

    def __init__(self,begin,relation,end):
        """Create a new link. Perhaps add an existency check and
        return None if new link already exists."""
        self.id = self.newID()
        self.begin = begin
        self.end = end
        self.history = None
        self.relation = relation
        self.begin.addOutLink(self)
        self.end.addInLink(self)

    def __str__(self):
        return "LinkDescription  %s  %s  %s" % \
               (self.begin,string.upper(self.relation),self.end)

    
class Link(AbstractLink):

    def __init__(self,environment,beginNode,relation,endNode,addPLinks=1):
        AbstractLink.__init__(self,beginNode,relation,endNode)
        environment.addLink(self)
        self.pointLinks = []
        self.pointLinksAdded = 0
        if addPLinks: self.generatePLinks(environment)

    def generatePLinks(self,environment):
        if self.pointLinksAdded: return
        pLinks = LINK2PLINK[self.relation]
        for pLink in pLinks:
            #print pLink
            point1 = self.findPoint(pLink[0],pLink[1])
            point2 = self.findPoint(pLink[3],pLink[4])
            rel = pLink[2]
            newPLink = PLink(environment,point1,rel,point2)
            self.pointLinks.append(newPLink)
        self.pointLinksAdded = 1

    def findPoint(self,node,point):
        if node == "begin" and point == "begin": return self.begin.begin
        if node == "begin" and point == "end": return self.begin.end
        if node == "end" and point == "begin": return self.end.begin
        if node == "end" and point == "end": return self.end.end
        return None
           
    def __str__(self):
        return "Link(%s)  %s --%s-->  %s" % \
               (self.id, self.begin,string.upper(self.relation),self.end)

    def printVerbosely(self):
        def printPLinks(point):
            print "      inLinks:"
            for link in point.inLinks: print "           ", link
            print "      outLinks:"
            for link in point.outLinks: print "           ", link
        print "\nTimeML_Link(%s)" % (self.id)
        print "  %s" % (string.upper(self.relation))
        print "  %s" % (self.begin)
        print "    %s" % (self.begin.begin)
        printPLinks(self.begin.begin)
        print "    %s" % (self.begin.end)
        printPLinks(self.begin.end)
        print "  %s" % (self.end)
        print "    %s" % (self.end.begin)
        printPLinks(self.end.begin)
        print "    %s" % (self.end.end)
        printPLinks(self.end.end)


class PLink(AbstractLink):

    def __init__(self,environment,point1,relation,point2):
        if not relation: return None
        if relation == '>':
            AbstractLink.__init__(self,point2,'<',point1)
        else:
            AbstractLink.__init__(self,point1,relation,point2)
        environment.addPLink(self)
        
    def isTrivial(self):
        if self.begin.interval == self.end.interval: return 1
        else: return 0

    def asPrettyString(self):
        return "[%s %s %s]" % (self.begin.string, self.relation, self.end.string)
        
    def __cmp__(self,other):
        comparison1 = cmp(self.begin.string,other.begin.string)
        if comparison1: return comparison1
        comparison2 = cmp(self.end.string,other.end.string)
        if comparison2: return comparison2
        return cmp(self.relation,other.relation)
        
    def __str__(self):
        return "PLink(%s) [%s.%s %s %s.%s]" % \
               (self.id, self.begin.id, self.begin.string,
                self.relation, self.end.id, self.end.string )

