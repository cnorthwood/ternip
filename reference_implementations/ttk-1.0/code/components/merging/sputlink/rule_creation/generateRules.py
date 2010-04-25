#!/usr/bin/python

""" Based on compileAxioms5.py. The main difference is that Allen
basic relations are used instead of TimeML relations. Also produces an
extra short output for consumption of Perl scripts. """

import sys
import string

from objects import \
     ObjectList, TemporalObject, AbstractNode, AbstractLink, \
     Node, EventNode, TimexNode, Point, Link, PLink 
     
from closure import Axiom, Closure

settings = {}
settings['debug'] = 0


def initializeGlobalData():

    global LINK_TYPES
    global PLINK_TYPES
    global LINK2PLINK
    global AXIOMS
    global POINT_AXIOMS

    PLINK_TYPES = ['<','>','=',None]

    LINK_TYPES = ['<', 'm' '>', 'mi', 'd', 'di',
                  '=', 's', 'f', 'si', 'fi', 'o', 'oi', None]

    LINK2PLINK = {
        "<"   : [['b','e', "<", 'e','b']],
        "m"   : [['b','e', "=", 'e','b']],
        ">"   : [['e','e', "<", 'b','b']],
        "mi"  : [['e','e', "=", 'b','b']],
        "o"   : [['b','b', '<', 'e','b'],['e','b', '<', 'b','e'],['b','e', '<', 'e','e']],
        "oi"  : [['e','b', '<', 'b','b'],['b','b', '<', 'e','e'],['e','e', '<', 'b','e']],
        "di"  : [['b','b', "<", 'e','b'],['e','e', "<", 'b','e']],
        "d"   : [['e','b', "<", 'b','b'],['b','e', "<", 'e','e']],
        "="   : [['b','b', "=", 'e','b'],['b','e', "=", 'e','e']],
        "s"   : [['b','b', "=", 'e','b'],['b','e', "<", 'e','e']],
        "f"   : [['e','b', "<", 'b','b'],['b','e', "=", 'e','e']],
        "si"  : [['e','b', "=", 'b','b'],['e','e', "<", 'b','e']],
        "fi"  : [['b','b', "<", 'e','b'],['e','e', "=", 'b','e']] }

    AXIOMS = ObjectList("Axioms")
    
    POINT_AXIOMS = ObjectList("Point_Axioms")
    POINT_AXIOMS.add(Axiom('<','<','<'))
    POINT_AXIOMS.add(Axiom('<','=','<'))
    POINT_AXIOMS.add(Axiom('=','<','<'))
    POINT_AXIOMS.add(Axiom('=','=','='))


class Environment:

    def __init__(self,id=0):
        self.id = id
        self.isConsistent = 1
        self.NODES = ObjectList("Nodes")
        self.LINKS = ObjectList("TimeML_Links")
        self.POINTS = ObjectList("Points")
        self.PLINKS = ObjectList("Point_Links")
        self.AXIOMS = AXIOMS
        self.POINT_AXIOMS = POINT_AXIOMS
        self.settings = settings
        
    def addNode(self,node): self.NODES.add(node)
    def addLink(self,link): self.LINKS.add(link)
    def addPoint(self,point): self.POINTS.add(point)
    def addPLink(self,plink): self.PLINKS.add(plink)

    def copy(self):
        newEnv = Environment()
        newEnv.id = self.id
        newEnv.isConsistent = self.isConsistent
        for node in self.NODES: newEnv.NODES.add(node)
        for link in self.LINKS: newEnv.LINKS.add(link)
        for point in self.POINTS:
            newPoint = point.copy(newEnv)
        for plink in self.PLINKS: 
            p1Name = plink.begin.string
            p2Name = plink.end.string
            p1 = newEnv.findPointWithName(p1Name)
            p2 = newEnv.findPointWithName(p2Name)
            PLink(newEnv,p1,plink.relation,p2)
        return newEnv

    def close(self,closureType,debug=0):
        closedEnv = self.copy()
        CLOS = Closure(closedEnv,closureType)
        if debug: CLOS.debugOn()
        CLOS.computeClosure()
        closedEnv.isConsistent = CLOS.isConsistent
        return closedEnv

    def translateEnvironment(self,name1,name2):
        """Take the PLinks and translate them into a disjunction of
        TimeML relations."""
        timemlRels = []
        for reltype in LINK2PLINK.keys():
            consistent = 1
            env = self.copy()
            for plink in LINK2PLINK[reltype]:
                rel = plink[2]
                p1Name = translateBoundaries(name1,name2,plink[0],plink[1])
                p2Name = translateBoundaries(name1,name2,plink[3],plink[4])
                p1 = env.findPointWithName(p1Name)
                p2 = env.findPointWithName(p2Name)
                if env.hasConflictingLink(p1,rel,p2): 
                    consistent = 0
                    continue 
                if env.findPLink(p1,rel,p2):
                    continue
                PLink(env,p1,rel,p2)
                if rel == '=': PLink(env,p2,rel,p1)
            if consistent:
                closedEnv = env.close("points")
                if closedEnv.isConsistent: 
                    timemlRels.append(reltype)
        relstring = ''
        for rel in sort(timemlRels):
            relstring = relstring + rel + ' '
        return relstring
    
    def hasConflictingLink(self,p1,rel,p2):
        existingLink = self.findPLink(p1,rel,p2)
        if existingLink:
            #print "    found existing link"
            if existingLink.relation != rel: 
                #print "    found existing inconsistent link"
                return 1
        existingLink = self.findPLink(p2,rel,p1)
        if existingLink:
            #print "    found existing reversed link"
            if existingLink.relation == '<' or rel == '<': 
                #print "    found existing inconsistent reversed link"
                return 1
        return 0

    def findPLink(self,node1,rel,node2):
        """Quick and dirty, index links to speed this up."""
        for link in self.PLINKS.asList():
            if link.begin.string == node1.string and link.end.string == node2.string:
                return link
        return None

    def findNodeWithName(self,name):
        for n in self.NODES:
            if n.string == name: return n
        return None

    def findPointWithName(self,name):
        for point in self.POINTS:
            if point.string == name: return point
        return None

    def getNewPLinks(self,nodeName):
        """Get all links created to bypass nodeName. This only works as
        expected for the axiom compilation stage."""
        newPLinks = []
        for plink in self.PLINKS:
            if plink.isTrivial(): continue
            if plink.begin.interval.string == nodeName: continue
            if plink.end.interval.string == nodeName: continue
            newPLinks.append(plink)
        return newPLinks
            
    def asPLinkString(self):
        plinks = self.PLINKS.asList()
        plinks.sort()
        plStr = "["
        for plink in plinks:
            if plink.isTrivial(): continue
            plStr = "%s %s" % (plStr,plink.asPrettyString())
        plStr = plStr + " ]"
        return plStr
    
    def __str__(self):
        return "\nENVIRONMENT(%s,%s)\n" % (self.id,self.isConsistent) + \
                str(self.NODES) + "\n" + str(self.LINKS) + "\n" + \
                str(self.POINTS) + "\n" + str(self.PLINKS)

    def printPointEnv(self):
        print "\nENVIRONMENT(%s)\n" % (self.id) , \
                str(self.POINTS) , "\n" , str(self.PLINKS), "\n" 

    def printPLinks(self,fh=sys.stdout):
        fh.write("  %s\n" % self.asPLinkString())


class EnvironmentFactory:

    def allRelationCombinations(self):
        rels = []
        for r1 in PLINK_TYPES:
            for r2 in PLINK_TYPES:
                for r3 in PLINK_TYPES:
                    for r4 in PLINK_TYPES:
                        rels.append([r1,r2,r3,r4])
        return rels

    def createEnvironments(self,relationCombinations,name1,name2):
        """Create a list of allpossible environment of just two nodes
        and the relation between the points given by the relation
        combinations. The two nodes will be given names as specified."""
        envID = 0
        environments = []
        for relCombination in relationCombinations:
            envID = envID + 1
            environments.append(
                self.createEnvironment(relCombination,name1,name2,envID))
        return environments

    def createEnvironment(self,relationCombination,name1,name2,envID=0):
        """Create an environment consisting solely of two nodes and
        the relations between the four points as specified in the
        given relation combination. Give the nodes names as
        specified. Uses EventNodes with class OCCURRENCE (which is
        totally arbitrary).
        NewPLink is a wrapper around PLink creation. Need to make sure
        that when a link with '=' as the relation is created, the
        reverse link is put in as well. I don't want to make this a
        responsibility of the PLink.__init__, but of the environment
        in which PLinks are created."""
        def NewPLink(env,p1,rel,p2):
            PLink(env,p1,rel,p2)
            if rel == '=': PLink(env,p2,rel,p1)
        ENV = Environment(envID)
        r1 = relationCombination[0]
        r2 = relationCombination[1]
        r3 = relationCombination[2]
        r4 = relationCombination[3]
        nodeX = EventNode(ENV,name1,'OCCURRENCE')
        nodeY = EventNode(ENV,name2,'OCCURRENCE')
        NewPLink(ENV,nodeX.begin, r1, nodeY.begin)
        NewPLink(ENV,nodeX.begin, r2, nodeY.end)
        NewPLink(ENV,nodeX.end, r3, nodeY.begin)
        NewPLink(ENV,nodeX.end, r4, nodeY.end)
        return ENV

    def createConsistentEnvironments(self,relationCombinations,closureType,name1,name2):
        environments = self.createEnvironments(relationCombinations,name1,name2)
        environments = self.closeEnvironments(environments,closureType)
        environments = self.filterConsistentEnvironments(environments)
        return environments
        
    def createEnvironmentPairs(self,relationCombinations,closureType,name1,name2):
        """Return a list of pairs, where each pair consists of (i) a relation created using
        an element of the relationCombinations and (ii) the closure of that relation."""
        envs = self.createEnvironments(relationCombinations,name1,name2)
        envPairs = []
        for env in envs:
            envClosed = env.close(closureType)
            if envClosed.isConsistent:
                envPairs.append([env,envClosed])
        return envPairs
    
    def createEnvironmentFromPLinks(self,plinks,node1,node2):
        env = Environment()
        points = [node1.begin,node1.end,node2.begin,node2.end]
        for point in points:
            point.copy(env)
        for plink in plinks:
            rel = plink.relation
            p1Name = plink.begin.string
            p2Name = plink.end.string
            p1 = env.findPointWithName(p1Name)
            p2 = env.findPointWithName(p2Name)
            PLink(env,p1,rel,p2)
        return env
    
    def closeEnvironments(self,environments,closureType):
        closedEnvironments = []
        for ENV1 in environments: 
            ENV2 = ENV1.close(closureType)
            closedEnvironments.append(ENV2)
        return closedEnvironments

    def mergeEnvironments(self,env1,env2,nodeName):
        """Returns a new environment which is the union of env1 and env2.
        Assumes that all nodes are events. Also assumes that all names are
        unique and that both env1 and env2 contain a node with name nodeName.
        Only merges the Nodes (and Points) and the PLinks, no merging of
        Links. Only really usefull for axiom compilation."""
        def addPLink(env,plink):
            name1 = plink.begin.string
            name2 = plink.end.string
            node1 = env.findPointWithName(name1)
            node2 = env.findPointWithName(name2)
            rel = plink.relation
            PLink(env,node1,rel,node2)
        mergedEnv = Environment()
        for node in env1.NODES:
            EventNode(mergedEnv,node.string,node.eventClass)
        for node in env2.NODES:
            if not node.string == nodeName:
                EventNode(mergedEnv,node.string,node.eventClass)
        for plink in env1.PLINKS: addPLink(mergedEnv,plink)
        for plink in env2.PLINKS: addPLink(mergedEnv,plink)
        return mergedEnv
            
    def printConsistentEnvironments(self,environments,closedEnvironments):
        consistentCount = 0
        for i in range(len(environments)):
            #if i < 254: continue
            ENV1 = environments[i]
            ENV2 = closedEnvironments[i]
            if ENV2.isConsistent:
                consistentCount = consistentCount + 1
                print "\nENVIRONMENT(%s)\n" % (ENV1.id)
                ENV1.printPLinks()
                print "\nENVIRONMENT(%s)\n" % (ENV2.id)
                ENV2.printPLinks()
                print
        print "\n\nTotal number of consistent environments: %s\n\n" % (consistentCount)

    def filterConsistentEnvironments(self,environments):
        consistentEnvs = []
        for env in environments:
            if env.isConsistent:
                consistentEnvs.append(env)
        return consistentEnvs


def sort(list):
    list.sort()
    return list


def translateBoundaries(name1,name2,b1,b2):
    if b1 == 'b':
        if b2 == 'b': return "%s%s" % (name1,1)
        if b2 == 'e': return "%s%s" % (name1,2)
    if b1 == 'e':
        if b2 == 'b': return "%s%s" % (name2,1)
        if b2 == 'e': return "%s%s" % (name2,2)

def filterPLinks(links,nodeName):
    filteredLinks = []
    for link in links:
        if link.begin.interval.string == nodeName: continue
        if link.end.interval.string == nodeName: continue
        filteredLinks.append(link)
    return filteredLinks

def translateEnvironments(envs):
    for env in envs:
        print; env.printPLinks()
        print "\n  ==>  ",
        print env.translateEnvironment('x','y')
        print "\n"


def test1():
    """Just three nodes and two links, should derive one new link, uncomment 
    link3 and an inconsistency should be created."""
    ENV = Environment()
    AXIOMS.add(Axiom("before","before","before"))
    AXIOMS.add(Axiom("before","includes","before"))
    node1 = EventNode(ENV,'crashed','OCCURRENCE')
    node2 = EventNode(ENV,'flying','STATE')
    node3 = EventNode(ENV,'saw','PERCEPTION')
    node4 = EventNode(ENV,'heard','PERCEPTION')
    link1 = Link(ENV,node1,'before',node2)
    link2 = Link(ENV,node2,'includes',node3)
    link3 = Link(ENV,node1,'after',node3)
    clos = Closure(ENV,"nodes")
    clos.computeClosure()
    print ENV


def test2():
    """Get all consistent relations (without grouping them), create
    all 96^2 pairs of them, merge the pairs and run cosure on the
    result. Takes a long time and is pretty useless."""
    envFact = EnvironmentFactory()
    relations = envFact.allRelationCombinations()
    env1s = envFact.createConsistentEnvironments(relations,"points",'x','y')
    env2s = envFact.createConsistentEnvironments(relations,"points",'y','z')
    count = 0
    for env1 in env1s:
        for env2 in env2s:
            count = count + 1
            env3 = envFact.mergeEnvironments(env1,env2,'y')
            env4 = env3.close("points")
            print "\nAXIOM_COMPILATION %s:\n" % (count)
            env1.printPLinks()
            env2.printPLinks()
            print "\n  ==>\n\n  [",
            for plink in env4.getNewPLinks('y'): print plink.asPrettyString(),
            print "]\n"

            
def test3():

    def getMinimalRelations(factory,relations,closureType,name1,name2):
        sys.stderr.write("Creating %s-%s relations...\n" % (name1,name2))
        # get the relation pairs 
        ClosedToOriginal = {}
        envPairs = factory.createEnvironmentPairs(relations,closureType,name1,name2)
        for (env1,env2) in envPairs:
            key = env2.asPLinkString()
            # create the groupings
            try: ClosedToOriginal[key].append(env1)
            except: ClosedToOriginal[key] = [env1]
        # now collect the minimal ones simply by taking the last of the lists
        envs = []
        for list in ClosedToOriginal.values():
            envs.append(list[len(list)-1])
        return envs
    
    envFact = EnvironmentFactory()
    relations = envFact.allRelationCombinations()

    # 1. GET ALL X-Y and Y-Z RELATIONS
    envs1 = getMinimalRelations(envFact,relations,"points",'x','y')
    #translateEnvironments(envs1);
    #return
    envs2 = getMinimalRelations(envFact,relations,"points",'y','z')
    
    # 2. MERGE X-Y and Y-Z ENVIRONMENTS AND RUN CLOSURE
    sys.stderr.write("Merging and running closure...\n")
    indexes = range(len(envs1))
    #indexes = range(4)
    out = open("compositions_long.txt",'w')
    out2 = open("compositions_short.txt",'w')
    for i in indexes:
        sys.stderr.write("\n%s\n" % (i))
        for j in indexes:
            sys.stderr.write(" %s" % (j))
            env1 = envs1[i]
            env2 = envs2[j]
            env1 = env1.close("points")
            env2 = env2.close("points")
            mergedEnv = envFact.mergeEnvironments(env1,env2,'y')
            closedEnv = mergedEnv.close("points")
            newLinks = closedEnv.getNewPLinks('y')
            if newLinks:
                out.write("\n\nAXIOM %s.%s\n\n" % (i,j))
                env1.printPLinks(out)
                env2.printPLinks(out)
                out.write("\n  ==>  ")
                newLinks = filterPLinks(newLinks,'y')
                node1 = env1.findNodeWithName('x')
                node2 = env2.findNodeWithName('z')
                env3 = envFact.createEnvironmentFromPLinks(newLinks,node1,node2)
                for plink in newLinks:
                    out.write(plink.asPrettyString()+' ')
                out.write("\n\n")
                out.write("IN\t"  + env1.translateEnvironment('x','y') + "\n")
                out.write("OUT\t" + env2.translateEnvironment('y','z') + "\n")
                out.write("NEW\t" + env3.translateEnvironment('x','z') + "\n\n")
                out2.write(env1.translateEnvironment('x','y') + "\t")
                out2.write(env2.translateEnvironment('y','z') + "\t")
                out2.write(env3.translateEnvironment('x','z') + "\n")
    sys.stderr.write("\n\n")


if __name__ == '__main__':
    initializeGlobalData()
    test3()





