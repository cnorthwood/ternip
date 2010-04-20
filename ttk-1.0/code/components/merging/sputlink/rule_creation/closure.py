
from objects import TemporalObject, Link, PLink
import string


class Axiom(TemporalObject):

    def __init__(self,inRel,outRel,resultRel):
        self.inRel = inRel
        self.outRel = outRel
        self.resultRel = resultRel

    def __str__(self):
        return "<%s %s %s>" % (self.inRel,self.outRel,self.resultRel)


class Closure:

    def __init__(self,environment,closureType):
        """Initialize a closure object, there is a separate closure object for each graph
        that closure is run over. isConsistent is set to 0 if closure derives a link that 
        is not consistent with an existing one. isClosed is only usefull if it is set to 0
        each time a link is added."""
        self.isConsistent = 1
        self.isClosed = 0
        self.debug = 0
        self.environment = environment
        self.closureType = closureType
        if closureType == 'nodes':
            self.nodes = environment.NODES
            self.links = environment.LINKS
            self.axioms = environment.AXIOMS
            self.linkType = Link
        elif closureType == 'points':
            self.nodes = environment.POINTS
            self.links = environment.PLINKS
            self.axioms = environment.POINT_AXIOMS
            self.linkType = PLink
        else:
            print "ERROR: unknown closure type"
            return
        
    def computeClosure(self):
        """Main loop for closure algorithm. Find dirty nodes and and close them. Closure
        creates new links and link creation by default causes the begin and end nodes to
        be marked dirty. But only link creation outside of closure should introduce new
        dirtyness. Overwrite this by cleaning all nodes after closure.""" 
        for node in self.nodes:
            if node.isDirty: self.closeNode(node)
        for node in self.nodes:
            node.isDirty = 0
        self.isClosed = 1

    def closeNode(self,node):
        if self.debug: 
            print "Closing node %s" % (node.string)
            print node.inLinks
            print node.outLinks
        for inLink in node.inLinks:
            for outLink in node.outLinks:
                if self.debug: print inLink.asPrettyString(),outLink.asPrettyString()
                axiom = self.findAxiom(inLink,outLink)
                if axiom:
                    self.printMessage1(node, axiom, inLink, outLink)
                    self.addLink(inLink,outLink,axiom.resultRel)
        self.isDirty = 0

    def addLink(self,inlink,outlink,relation):
        node1 = inlink.begin
        node2 = outlink.end
        # find link from begin to end
        existingLink = self.findLink(node1,relation,node2)
        if existingLink:
            #print "CLOSURE, existing link", existingLink
            # existingLink either has < or =, check whether it is the same as
            # the new link, if not, give inconsistency warning and return
            if existingLink.relation != relation:
                self.isConsistent = 0
                #self.printMessage2(existingLink,relation,inlink,outlink)
            return
        # find reversed link from end to begin
        existingLink = self.findLink(node2,relation,node1)
        if existingLink:
            #print "CLOSURE, existing reversed link", existingLink
            # existing link can be < or =, < will clash with new relation,
            # so only allowed combination is to have two ='s
            if existingLink.relation == '<' or relation == '<':
                self.isConsistent = 0
                #self.printMessage2(existingLink,relation,inlink,outlink)
            return
        # Use stored link type so code can abstract away from
        # node versus point distinction
        newLink = self.linkType(self.environment,node1,relation,node2)
        # BUT, that didn't work in PythonWin 2.2.3, it did not allow using
        # __init__ on the superclass, therefore, 
        if self.closureType == 'xpoints':
            newLink = PLink(self.environment,node1,relation,node2)
        if self.closureType == 'xnodes':
            newLink = Link(self.environment,node1,relation,node2)
        #print "CLOSURE, adding link", newLink
        newLink.history = "closure"

    def findAxiom(self,link1,link2):
        """Quick and dirty way, really want to index the axioms to speed
        this up for large axiom set."""
        for axiom in self.axioms:
            if link1.relation == axiom.inRel and link2.relation == axiom.outRel:
                return axiom
        return None

    def findLink(self,node1,rel,node2):
        """Quick and dirty, index links to speed this up."""
        #print "Finding link:", node1, rel, node2
        for link in self.links:
            if link.begin == node1 and link.end == node2:
                return link
        return None
    
    def debugOn(self): self.debug = 1
    def debugOff(self): self.debug = 0
    
    def printMessage1(self,node,axiom,inlink,outlink):
        if self.debug:
            print "Closing:.."
            print "  ", node
            print "  ", axiom
            print "  ", inlink
            print "  ", outlink
    
    def printMessage2(self,existingLink,relation,inlink,outlink):
        print "\nWARNING: link already exists"
        print "  %s" % (existingLink)
        print "  %s" % (string.upper(relation))
        print "    %s" % (inlink)
        print "    %s" % (outlink)
