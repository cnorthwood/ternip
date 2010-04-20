""" Module FSA -- methods to manipulate finite-state automata

Created by: Oliver Steele // Modified and enlarged by: Roser Sauri


This module defines an FSA class, for representing and operating on
finite-state automata (FSAs). FSAs can be used to represent regular expressions
and to test sequences for membership in the languages described by regular
expressions.

FSAs can be deterministic or nondeterministic, and they can contain epsilon
transitions. Methods to determinize an automaton (also eliminating its epsilon
transitions), and to minimize an automaton, are provided.

The transition labels for an FSA can be symbols from an alphabet, as in the
standard formal definition of an FSA, but they can also be instances which
represent predicates. If these instances implement instance.matches(), then the
FSA nextState() function and accepts() predicate can be used. If they implement
instance.complement() and instance.intersection(), the FSA can be be
determinized and minimized, to find a minimal deterministic FSA that accepts an
equivalent language.


===============
  Quick Start
===============

   ---------------------------
1. Creating FSAs out of labels:
   ---------------------------
   
Instances of FSA can be created out of labels (for instance, strings) by the
singleton() function, and combined to create more complex FSAs through the
complement(), closure(), concatenation(), union(), and other constructors. For
example, concatenation(singleton('a'), union(singleton('b'),
closure(singleton('c')))) creates an FSA that accepts the strings 'a', 'ab',
'ac', 'acc', 'accc', and so on.

   --------------------------------------
2. Creating FSAs using function compileRE:
   --------------------------------------

Instances of FSA can also be created with the compileRE(regex) function, which
compiles a simple regular expression (using only '*', '?', '+', '.', '|', '(', and
')' as metacharacters) into an FSA. For example, compileRE('a(b|c*)') returns
an FSA equivalent to the example in the previous paragraph.

   --------------------------------------
3. Creating FSAs using function compileOP:
   --------------------------------------

Finally, instances of FSA can also be generated using the function
compileOP(list), which stands for 'compile Object Pattern'. It allows
for creating FSAs out of string of characters (as with 'compileRE'
function), but also out of sequences of other kinds. Here is the list of
formats it accepts as input:

(a) Strings of characters. E.g., fsa1 = compileOP('a(b|c*)')
    ;;;;;;;;;;;;;;;;;;;;;

(b) Lists of characters. E.g., fsa2 = compileOP( [ 'a','(','b','|','c','*',')' ] )
    ;;;;;;;;;;;;;;;;;;;

In essence, options (a) and (b) above are equivalent to using the
compileRE function.However, compileRE is faster, so best practice is
using compileRE whenever possible.

In addition to (a) and (b), compileOP also allows as input sequences
of lexical items or chunks, which can be represented either as
sequences of characters strings (c), or sequences of grammatical
objects (d).

(c) Lists of characters strings. E.g.,
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;

    fsa3 = compileOP(['(','a','|','the',')', 'very', '*', '(', 'boring','|','nice', ')', '+', 'movie'])

(d) Lists of grammatical objects represented as Python dictionaries. E.g.,
    ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    fsa4 = compileOP( [ {'nodeType': 'Token', 'text': ['is','was','were','am','be',\"'s\", 'are', \"'re\",\"'m\",'been', 'being']',
             '(',
             {'nodeType':'Token', 'text': 'being'},             # Passive, PROGRESSIVE 
             {'nodeType':'Token', 'pos': ['VBD', 'VBN']},       # E.g., 'is being eaten' 
             '|',
             {'nodeType':'Token', 'pos': 'VBG'},                # Active, PROGRESSIVE (infinitive). E.g., '[be] eating'
             '|',
             {'nodeType':'Token', 'pos': ['VBD', 'VBN']},       # Passive, NONE. E.g. '[is] eaten'
             ')'
             ] )

    In other words, the elements of the FSA vocabulary can be
    conceived as clusters of attribute-value pairs, and represented
    using python dictionars. The format of the value in each key-value
    pair can be:

    -- An atomic element. E.g., {..., 'headForm':'is', ...}

    -- A list of possible values. E.g., {..., headForm': ['have',
    'has', 'had'], ...}  In this case, it is checked whether the value
    of the input is included within that list of value candidates.

    -- A negated value or list of values. Negation is represented by
    means of a 2-place tuple, whose initial position is the caret
    symbol '^', and its second position is either an atomic value or a
    list of atomic values that need not match the value of the input
    object. E.g.,
        {..., 'headPos':('^', 'MD') ...}, or
        {..., 'headPos':('^', ['MD', 'RB']) ...}

    On the other hand, input objects can be represented as:

    -- Python dictionaries, like the FSA vocabulary. 

    -- Instances of classes describing grammatical objects, customized
    by the particular application using the current FSA module. E.g.,
    Noun Chunks, Verb Chunks, Lexical tokens, etc, in Evita. In this
    case, the only additional requirement is creating, within the
    class, a method capable of mapping the FSA vocabulary items (of
    the format described above) into your instance. As example, refer
    to the use of the function _matchChunk, specific for Evita, which
    is called from labelMatches function (this module) and described
    in the Chunk class (Chunk.py)).

    
Additional notes on the use of compileOP:
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

The metacharacters allowed here are the same as for compileRE: '*',
'?', '+', '.', '|', '(', and '). Note however that these
metacharacters need to be represented as independent items of the
list. This could be improved, but we leave it for later when we are
all unemployed and bored to death.

   -------------------
4. Accepting sequences
   -------------------

We can check whether a FSA accepts or rejects a sequence using the
following methods:

(a) accepts: 
    ;;;;;;;
    Taking as argument an input sequence and returning True or False.
    E.g., using fsa3 compiled in (c) above:
    
    >>> fsa3.accepts(['a', 'very', 'very', 'very', 'boring', 'movie'])
    1
    >>> fsa3.accepts(['a', 'very', 'movie'])
    0
    >>> fsa3.accepts(['a', 'very', 'nice', 'movie', 'theater'])
    0

(b) acceptsSubstringOf:
    ;;;;;;;;;;;;;;;;;;
    Taking as argument an input sequence, and returning the length of
    the longest subsequence being accepted by the FSA.
    E.g., using fsa3 compiled in (c) above:

    >>> fsa3.acceptsSubstringOf(['a', 'very', 'very', 'very', 'boring', 'movie'])
    6
    >>> fsa3.acceptsSubstringOf(['a', 'very', 'movie'])
    0
    >>> fsa3.acceptsSubstringOf(['a', 'very', 'nice', 'movie', 'theater'])
    4
    
Both functions, accepts and acceptsSubstringOf, can be used with any
of the FSA vocabulary and input format described in (a)-(d) sections
above.

   ---------------------------------
5. Determinizing and minimizing FSAs
   ---------------------------------

FSAs can be determinized, to create equivalent FSAs (FSAs accepting
the same language) with unique successor states for each input, and
minimized, to create an equivalent deterministic FSA with the smallest
number of states. FSAs can also be complemented, intersected, unioned,
and so forth as described under 'FSA Functions' below.


=======================
  Module Description
=======================

  ------------
* FSA Methods
  ------------

The class FSA defines the following methods.

Acceptance:
        - fsa.nextStates(state, input) returns a list of states
        - fsa.nextState(state, input) returns None or a single state if
                |nextStates| <= 1, otherwise it raises an exception
        - fsa.nextStateSet(states, input) returns a list of states
        - fsa.accepts(sequence) returns true or false
        - fsa.acceptsSubstringOf(list) returns the lentgh of the
          longest sublist accepted.

Accessors and predicates:
        - isEmpty() returns true iff the language accepted by the FSA is the empty language
        - labels() returns a list of labels that are used in any transition
        - nextAvailableState() returns an integer n such that no states in the FSA
                are numeric values >= n

Reductions:
        - sorted(initial=0) returns an equivalent FSA whose states are numbered
                upwards from 0
        - determinized() returns an equivalent deterministic FSA
        - minimized() returns an equivalent minimal FSA
        - trimmed() returns an equivalent FSA that contains no unreachable or dead
                states

Presentation:
        - toDotString() returns a string suitable as *.dot file for the 'dot'
                program from AT&T GraphViz
        - view() views the FSA with a gs viewer, if gs and dot are installed

        
  --------------
* FSA Functions
  --------------

Construction from FSAs:
- complement(a) returns an fsa that accepts exactly those sequences that it's
        argument does not
- closure(a) returns an fsa that accepts sequences composed of zero or more
        concatenations of sequences accepted by the argument
- concatenation(a, b) returns an fsa that accepts sequences composed of a
        sequence accepted by a, followed by a sequence accepted by b
- containment(a, occurrences=1) returns an fsa that accepts sequences that
        contain at least occurrences occurrences of a subsequence recognized by the
        argument.
- difference(a, b) returns an fsa that accepts those sequences accepted by a
        but not b
- intersection(a, b) returns an fsa that accepts sequences accepted by both a
        and b
- iteration(a, min=1, max=None) returns an fsa that accepts sequences
        consisting of from min to max (or any number, if max is None) of sequences
        accepted by its first argument
- option(a) is equivalent to union(a, EMPTY_STRING_FSA)
- reverse(a) returns an fsa that accepts strings whose reversal is accepted by
        the argument
- union(a, b) returns an fsa that accepts sequences accepted by both a and b

Predicates:
- equivalent(a, b) returns true iff a and b accept the same language

Reductions (these equivalent to the similarly-named methods):
- determinize(fsa) returns an equivalent deterministic FSA
- minimize(fsa) returns an equivalent minimal FSA
- sort(fsa, initial=0) returns an equivalent FSA whose states are numbered from
        initial
- trim(fsa) returns an equivalent FSA that contains no dead or unreachable
        states

Construction from labels:
- compileRE(string) returns an FSA that accepts the language described by
        string, where string is a list of symbols and '*', '+', '?', and '|' operators,
        with '(' and ')' to control precedence.
- sequence(sequence) returns an fsa that accepts sequences that are matched by
        the elements of the argument. For example, sequence('abc') returns an fsa that
        accepts 'abc' and ['a', 'b', 'c'].
- singleton(label) returns an fsa that accepts singletons whose elements are
        matched by label. For example, singleton('a') returns an fsa that accepts only
        the string 'a'.

  --------------
* FSA Constants
  --------------

EMPTY_STRING_FSA is an FSA that accepts the language consisting only of the
empty string.

NULL_FSA is an FSA that accepts the null language.

UNIVERSAL_FSA is an FSA that accepts S*, where S is any object.

  ----------------------
* FSA instance creation
  ----------------------

FSA is initialized with a list of states, an alphabet, a list of transition, an
initial state, and a list of final states. If fsa is an FSA, fsa.tuple()
returns these values in that order, i.e. (states, alphabet, transitions,
initialState, finalStates). They're also available as fields of fsa with those
names.

Each element of transition is a tuple of a start state, an end state, and a
label: (startState, endSTate, label).

If the list of states is None, it's computed from initialState, finalStates,
and the states in transitions.

If alphabet is None, an open alphabet is used: labels are assumed to be objects
that implements label.matches(input), label.complement(), and
label.intersection() as follows:
        - label.matches(input) returns true iff label matches input
        - label.complement() returnseither a label or a list of labels which,
                together with the receiver, partition the input alphabet
        - label.intersection(other) returns either None (if label and other don't
                both match any symbol), or a label that matches the set of symbols that
                both label and other match

As a special case, strings can be used as labels. If a strings 'a' and 'b' are
used as a label and there's no alphabet, '~a' and '~b' are their respective
complements, and '~a&~b' is the intersection of '~a' and '~b'. (The
intersections of 'a' and 'b', 'a' and '~b', and '~a' and 'b' are, respectively,
None, 'a', and 'b'.)


=========
  Goals
=========

Design Goals:
        - easy to use
        - easy to read (simple implementation, direct expression of algorithms)
        - extensible

Non-Goals:
        - efficiency


================================================        
  Chronology of modifications and enlargements  
================================================        

Febrary 2005:

- Fixed bugs in compileRE and related functions (Roser)

April 2005:

- Added functionality of compileOP and related functions (Roser)
- Enlarged module documentation. (Roser)
        
"""


import string, os, tempfile
from types import InstanceType, ListType, TupleType, IntType, LongType, DictType, StringType
IntegerTypes = (IntType, LongType)

try:
        import NumFSAUtils
except ImportError:
        NumFSAUtils = None

ANY = 'ANY'
EPSILON = None

TRACE_LABEL_MULTIPLICATIONS = 0
NUMPY_DETERMINIZATION_CUTOFF = 50


#debugFile = open(os.getcwd()+'/FSAdebugOutput.txt', 'w')   

class FSA:
        def __init__(self, states, alphabet, transitions, initialState, finalStates, arcMetadata=[]):
                if states == None:
                        states = self.collectStates(transitions, initialState, finalStates)
                else:
                        assert not filter(lambda s, states=states:s not in states, self.collectStates(transitions, initialState, finalStates))
                self.states = states
                self.alphabet = alphabet
                self.transitions = transitions
                self.initialState = initialState
                self.finalStates = finalStates
                self.setArcMetadata(arcMetadata)
        
        
        #
        # Initialization
        #
        def makeStateTable(self, default=None):
                for state in self.states:
                        if type(state) != IntType:
                                return {}
                if reduce(min, self.states) < 0: return {}
                if reduce(max, self.states) > max(100, len(self.states) * 2): return {}
                return [default] * (reduce(max, self.states) + 1)
        
        def initializeTransitionTables(self):
                self._transitionsFrom = self.makeStateTable()
                for s in self.states:
                        self._transitionsFrom[s] = []
                for transition in self.transitions:
                        s, _, label = transition
                        self._transitionsFrom[s].append(transition)
        
        def collectStates(self, transitions, initialState, finalStates):
                states = finalStates[:]
                if initialState not in states:
                        states.append(initialState)
                for s0, s1, _ in transitions:
                        if s0 not in states: states.append(s0)
                        if s1 not in states: states.append(s1)
                return states
        
        def computeEpsilonClosure(self, state):
                states = [state]
                index = 0
                while index < len(states):
                        state, index = states[index], index + 1
                        for _, s, label in self.transitionsFrom(state):
                                if label == EPSILON and s not in states:
                                        states.append(s)
                states.sort()
                return states
        
        def computeEpsilonClosures(self):
                self._epsilonClosures = self.makeStateTable()
                for s in self.states:
                        self._epsilonClosures[s] = self.computeEpsilonClosure(s)
        
        
        #
        # Copying
        #
        def create(self, *args):
                return apply(self.__class__, args)
        
        def copy(self, *args):
                fsa = apply(self.__class__, args)
                if hasattr(self, 'label'):
                        fsa.label = self.label
                return fsa
        
        def creationArgs(self):
                return self.tuple() + (self.getArcMetadata(),)
        
        def coerce(self, klass):
                return apply(klass, self.creationArgs())
        
        
        #
        # Accessors
        #
        def epsilonClosure(self, state):
                try:
                        return self._epsilonClosures[state]
                except AttributeError:
                        self.computeEpsilonClosures()
                return self._epsilonClosures[state]
        
        def labels(self):
                """Returns a list of transition labels."""
                labels = []
                for (_, __, label) in self.transitions: #added underscore
                        if label and label not in labels:
                                labels.append(label)
                return labels
        
        def nextAvailableState(self):
                return reduce(max, filter(lambda s:type(s) in IntegerTypes, self.states), -1) + 1
        
        def transitionsFrom(self, state):
                try:
                        return self._transitionsFrom[state]
                except AttributeError:
                        self.initializeTransitionTables()
                return self._transitionsFrom[state]
        
        def tuple(self):
                return self.states, self.alphabet, self.transitions, self.initialState, self.finalStates
        
        
        #
        # Arc Metadata Accessors
        #
        def hasArcMetadata(self):
                return hasattr(self, '_arcMetadata')
        
        def getArcMetadata(self):
                return getattr(self, '_arcMetadata', {}).items()
        
        def setArcMetadata(self, list):
                arcMetadata = {}
                for (arc, data) in list:
                        arcMetadata[arc] = data
                self._arcMetadata = arcMetadata
        
        def addArcMetadata(self, list):
                for (arc, data) in list:
                        self.addArcMetadataFor(arc, data)
        
        def addArcMetadataFor(self, transition, data):
                if not hasattr(self, '_arcMetadata'):
                        self._arcMetadata = {}
                oldData = self._arcMetadata.get(transition)
                if oldData:
                        for item in data:
                                if item not in oldData:
                                        oldData.append(item)
                else:
                        self._arcMetadata[transition] = data
                
        def setArcMetadataFor(self, transition, data):
                if not hasattr(self, '_arcMetadata'):
                        self._arcMetadata = {}
                self._arcMetadata[transition] = data
        
        def getArcMetadataFor(self, transition):
                #debugFile.write( "\n--------------> TRANSITION!!!!: "+str(transition)+"\n\t\t"+str((str(transition[0]), str(transition[1]),str(transition[2]))))
                ar=getattr(self, '_arcMetadata', {})
                #debugFile.write( "\n--------------> getattr(self, '_arcMetadata': "+str(ar))
                #debugFile.write( "\n--------------> ALL together: "+ar.get(transition))
                myTransition = (transition[0], transition[1], str(transition[2]))
                try:
                        return getattr(self, '_arcMetadata', {}).get(transition)
                except:
                        return getattr(self, '_arcMetadata', {}).get(myTransition)
                        
        
        
        #
        # Predicates
        #
        def isEmpty(self):
                return not self.minimized().finalStates
        
        def isFSA(self):
                return 1
        
        
        #
        # Accepting
        #
        def labelMatches(self, label, input):
                #debugFile.write( "\n\nPASS: ...labelMatches 1: "+str(input))
                #print "\n\nPASS: ...LABEL:", label, "INPUT:", input
                return labelMatches(label, input)
        
        def nextStates(self, state, input):
                #debugFile.write( "\n\nPASS: ...nextStates 1: "+str(input))
                states = []
                for _, sink, label in self.transitionsFrom(state):
                        #print "\tMY LABEL:"+str(label)
                        if self.labelMatches(label, input):
                                #print "\t\tPASSED first test"
                                if sink not in states:
                                        #print "\t\tCHECK case 1"
                                        states.extend(self.epsilonClosure(sink))
                        elif label == 'ALL':                                        
                                #print "\t\tCHECK case ALL"
                                #debugFile.write( "\n--------------> ANY condition found here!!") 
                                states.extend(self.epsilonClosure(sink))            
                        elif label[0] == '^':                                       
                                label = label[1:]                                   
                                #print "\t\tLABEL MUST NOT MATCH", label
                                if (not self.labelMatches(label, input)) and sink not in states:  
                                        states.extend(self.epsilonClosure(sink))
                        #else:
                               #print "\t\tMISSED"
                return states
        
        def nextState(self, state, input):
                #debugFile.write( "\n\nPASS: ...nextState 1: "+str(input))
                states = self.nextStates(state, input)
                assert len(states) <= 1
                return states and states[0]
        
        def nextStateSet(self, states, input):
               # debugFile.write( "\n\nPASS: ...nextStateSet 1: "+str(input))
                successors = []
                for state in states:
                        for _, sink, label in self.transitionsFrom(state):
                                if self.labelMatches(label, input) and sink not in successors:
                                        successors.append(sink)
                return successors
        
        def accepts(self, sequence):
                #print "SEQUENCE:", sequence
                states = [self.initialState]
                for item in sequence:
                        newStates = []
                        for state in states:
                                #debugFile.write( "\n\nPASS: ...accepts 1: "+str(item))
                                for s1 in self.nextStates(state, item):
                                        if s1 not in newStates:
                                                newStates.append(s1)
                        states = newStates
                        
                """Returning the length of the list containing all states s in states
                that are also in self.finalStates"""
                return len(filter(lambda s, finals=self.finalStates: s in finals, states)) > 0
                #return len(filter(lambda s: s in self.finalStates, states)) > 0

        def acceptsSubstringOf(self, sequence):   #looking for Longest Subsequence
                """ As accepts() method, but accepting also substrings of sequence.
                Returning length of longest piece of sequence that has been matched"""
#                print "\n........Entering acceptsSubstringOf......\n"
                stateSequences = self.findSubstringsOf(sequence, self.initialState, [])
                return self.longestSequence(stateSequences)[0] 

        def acceptsShortestSubstringOf(self, sequence):
                """ As accepts() method, but accepting also substrings of sequence.
                Returning length of shortest piece of sequence that has been matched"""
                print "\n........Entering acceptsSubstringOf......\n"
                stateSequences = self.findSubstringsOf(sequence, self.initialState, [])
                #log("\n\nSUBSTRINGS: "+str(stateSequences))
                return self.shortestSequence(stateSequences)[0]                 
        
        def findSubstringsOf(self, sequence, state, visitedStates): 
                """Returning a list of state sequences matching pattern """
                #debugFile.write( "\n\nInitialStates: "+str(state))
                stateSequences = []
                #print self
                for i in range(len(sequence)):
                        #print sequence[i].pp()
                        #log("\n   NEW i:"+str(i))
                        #log("\nstateSequences:"+str(stateSequences))
                        #log("\nvisitedStates:"+str(visitedStates))
                        if i > 0 and (not visitedStates or
                                      visitedStates[-1] != state):     #Hacking, but oh well...  
                                #log("\nHACKING here")               #Hacking, but oh well...
                                visitedStates.append(state)          #Hacking, but oh well...  
                        #if i > 0 and not visitedStates:     #Hacking, but oh well...                                
                        #    return self.updateStateSequences(visitedStates, stateSequences)
                        #else:
                        #log("\n"+25*"=")
                        #log("\nITEM: "+str(sequence[i].getText())+" || type:"+sequence[i].nodeType+" \n\tCURRENT STATE:"+str(state))
                        nextStateList = self.nextStates(state, sequence[i])
                        #log("\n\tVISITED STATES: "+str(visitedStates))
                        #log("\n\tNEXT STATES: "+str(nextStateList))
                        if len(nextStateList) == 0:
                                #log("\n\nRETURNING HERE 1")
                                #print "\n....len(nextStateList) == 0"
                                #print "visitedStates:",visitedStates
                                return self.updateStateSequences(visitedStates, stateSequences)
                        elif len(nextStateList) == 1:
                                #print "\n....len(nextStateList) == 1"
                                nextState = nextStateList[0] 
                                #debugFile.write( "\n\tself.nextState: "+str(nextState))
                                #print "\n\tself.nextState: "+str(nextState)
                                visitedStates.append(nextState)
                                #print "visitedStates:",visitedStates 
                                state = nextState
                        else: 
                                #log("\n....len(nextStateList) == "+str(len(nextStateList)))
                                if len(sequence) > i+1:
                                        c = len(nextStateList)                         #DEBUG
                                        #print "\n\t....len(sequence) > i+1"
                                        for state in nextStateList:
                                                localVisitedStates = visitedStates+[state]
                                                #log("\nAPPLYING HERE sub-3, COUNTER:"+str(c)) #DEBUG
                                                c = c+1                           #DEBUG
                                                moreSequences = self.findSubstringsOf(sequence[i+1:], state, localVisitedStates)
                                                #print "moreSequences", moreSequences
                                                stateSequences = stateSequences + moreSequences
                                                #print "stateSequences", stateSequences
                                else:
                                        #log("\n\nRETURNING HERE sub-3")
                                        #print "\n\t....ELSE: len(sequence) "
                                        return self.updateStateSequences(visitedStates, stateSequences)
                #debugFile.write("\n\nRETURNING HERE 2")
                #log("\nRETURNING HERE 2")
                #debugFile.write("\nvisited states:"+str(visitedStates))
                #print "\nvisited states: "+str(visitedStates)
                return self.updateStateSequences(visitedStates, stateSequences)                

        def shortestSequence(self, stateSequences):
                """Return lists containing (len(shortestSubsequence), shortestSubsequence) """
                #debugFile.write("\nSTATE SUBSEQUENCE CANDIDATES:"+str(stateSequences))
                lenStateSubsequences = []
                for subsequence in stateSequences:
                        lenStateSubsequences.append([len(subsequence), subsequence])
                #debugFile.write("\tSORTED: "+str(lenStateSubsequences.reverse()))
                if lenStateSubsequences:
                        lenStateSubsequences.sort()
                        #print "STATE SUBSEQUENCE:"+str(lenStateSubsequences)+" "+str(type(lenStateSubsequences))
                        return lenStateSubsequences[0]
                else:
                        return [0, None]                
        
        def longestSequence(self, stateSequences):
                """Return lists containing (len(longestSubsequence), longestSubsequence) """
                #debugFile.write("\nSTATE SUBSEQUENCE CANDIDATES:"+str(stateSequences))
                lenStateSubsequences = []
                for subsequence in stateSequences:
                        lenStateSubsequences.append([len(subsequence), subsequence])
                #debugFile.write("\tSORTED: "+str(lenStateSubsequences.reverse()))
                if lenStateSubsequences:
                        lenStateSubsequences.sort()
                        #print "STATE SUBSEQUENCE:"+str(lenStateSubsequences)+" "+str(type(lenStateSubsequences))
                        return lenStateSubsequences[-1]
                else:
                        return [0, None]
                
        def indexOfLastVisitedFinalState(self, visitedStates):
                """Return position+1 or 0"""
                for i in range(len(visitedStates)-1, -1, -1):
                        if visitedStates[i] in self.finalStates:
                                #print "FINAL STATE in pos:", i+1, "for", visitedStates
                                return i+1
                        else:
                                #print "FINAL STATE: next, for", visitedStates
                                return self.indexOfLastVisitedFinalState(visitedStates[:-1])
                else:
                        #print "FINAL STATE: none, for:", visitedStates
                        return 0
        
        def updateStateSequences(self, visitedStates, stateSequences):
                #log("\nentering updateStateSequences:")
                #log("\n\t\tvisited states:"+str(visitedStates))
                #log("\n\t\tstateSequences:"+str(stateSequences))
                lengthMatched = self.indexOfLastVisitedFinalState(visitedStates)
                if lengthMatched:
                        stateSequences.append(visitedStates[:lengthMatched])
                #log("\n\t\tnow stateSequences:"+str(stateSequences))
                return stateSequences
                                
        #
        # FSA operations
        #
        def complement(self):
                states, alpha, transitions, start, finals = completion(self.determinized()).tuple()
                return self.create(states, alpha, transitions, start, filter(lambda s,f=finals:s not in f, states))#.trimmed()
        
        
        #
        # Reductions
        #
        def sorted(self, initial=0):
                if hasattr(self, '_isSorted'):
#                        print "\nALREADY SORTED!!!\n" 
                        return self
                else:
#                        print "\nNOT SORTED YET\n"
                        return self.sortedObligatory(initial)

        def sortedObligatory(self, initial):
                stateMap = {}
                nextState = initial
                states, index = [self.initialState], 0
                while index < len(states) or len(states) < len(self.states):
                        if index >= len(states):
                                for state in self.states:
                                        if stateMap.get(state) == None:
                                                break
                                states.append(state)
                        state, index = states[index], index + 1
                        new, nextState = nextState, nextState + 1
                        stateMap[state] = new
                        for _, s, _ in self.transitionsFrom(state):
                                if s not in states:
                                        states.append(s)
                states = stateMap.values()
                transitions = map(lambda (s0,s1,l),m=stateMap:(m[s0], m[s1], l), self.transitions)
                arcMetadata = map(lambda ((s0, s1, label), data), m=stateMap: ((m[s0], m[s1], label), data), self.getArcMetadata())
                copy = self.copy(states, self.alphabet, transitions, stateMap[self.initialState], map(stateMap.get, self.finalStates), arcMetadata)
                copy._isSorted = 1
                return copy
        
        def trimmed(self):
                """Returns an equivalent FSA that doesn't include unreachable states,
                or states that only lead to dead states."""
                if hasattr(self, '_isTrimmed'):
                        return self
                states, alpha, transitions, initial, finals = self.tuple()
                reachable, index = [initial], 0
                while index < len(reachable):
                        state, index = reachable[index], index + 1
                        for (_, s, _) in self.transitionsFrom(state):
                                if s not in reachable:
                                        reachable.append(s)
                endable, index = list(finals), 0
                while index < len(endable):
                        state, index = endable[index], index + 1
                        for (s0, s1, _) in transitions:
                                if s1 == state and s0 not in endable:
                                        endable.append(s0)
                states = []
                for s in reachable:
                        if s in endable:
                                states.append(s)
                if not states:
                        if self.__class__  == FSA:
                                return NULL_FSA
                        else:
                                return NULL_FSA.coerce(self.__class__)
                transitions = filter(lambda (s0, s1, _), states=states:s0 in states and s1 in states, transitions)
                arcMetadata = filter(lambda ((s0, s1, _), __), states=states: s0 in states and s1 in states, self.getArcMetadata())  #R: added underscore
                result = self.copy(states, alpha, transitions, initial, filter(lambda s, states=states:s in states, finals), arcMetadata).sorted()
                result._isTrimmed = 1
                return result
        
        def withoutEpsilons(self):
                # replace each state by its epsilon closure
                states0, alphabet, transitions0, initial0, finals0 = self.tuple()
                initial = self.epsilonClosure(self.initialState)
                initial.sort()
                initial = tuple(initial)
                stateSets, index = [initial], 0
                transitions = []
                while index < len(stateSets):
                        stateSet, index = stateSets[index], index + 1
                        for (s0, s1, label) in transitions0:
                                if s0 in stateSet and label:
                                        target = self.epsilonClosure(s1)
                                        target.sort()
                                        target = tuple(target)
                                        transition = (stateSet, target, label)
                                        if transition not in transitions:
                                                transitions.append(transition)
                                        if target not in stateSets:
                                                stateSets.append(target)
                finalStates = []
                for stateSet in stateSets:
                        if filter(lambda s, finalStates=self.finalStates:s in finalStates, stateSet):
                                finalStates.append(stateSet)
                copy = self.copy(stateSets, alphabet, transitions, stateSets[0], finalStates).sorted()
                copy._isTrimmed = 1
                return copy
        
        def determinized(self):
                """Returns a deterministic FSA that accepts the same language."""
                #debugFile.write( "\n\nEntering determinized............")
                if hasattr(self, '_isDeterminized'):
                        #debugFile.write( "\n..............already determinzed")
                        return self
                if len(self.states) > NUMPY_DETERMINIZATION_CUTOFF and NumFSAUtils and not self.getArcMetadata():
                        #debugFile.write( "\n..............determinzed option 1")
                        data = apply(NumFSAUtils.determinize, self.tuple() + (self.epsilonClosure,))
                        result = apply(self.copy, data).sorted()
                        result._isDeterminized = 1
                        return result
                transitions = []
                stateSets, index = [tuple(self.epsilonClosure(self.initialState))], 0
                arcMetadata = []
                while index < len(stateSets):
                        #debugFile.write( "\n..............determinzed option 2")
                        stateSet, index = stateSets[index], index + 1
                        localTransitions = filter(lambda (s0,s1,l), set=stateSet:l and s0 in set, self.transitions)
                        if localTransitions:
                                #debugFile.write( "\n..............determinzed option 2.1")
                                localLabels = map(lambda(_,__,label):label, localTransitions)  #R: added an underscore
                                #debugFile.write( "\n..............determinzed option 2.1.1")
                                labelMap = constructLabelMap(localLabels, self.alphabet)
                                #debugFile.write( "\n..............determinzed option 2.1.2")
                                labelTargets = {}        # a map from labels to target states
                                for transition in localTransitions:
                                        #debugFile.write( "\n..............determinzed option 2.2")
                                        _, s1, l1 = transition
                                        for label, positives in labelMap:
                                                #debugFile.write( "\n..............determinzed option 2.3")
                                                #debugFile.write( "\n              POSITIVES:"+str(positives))
                                                #debugFile.write( "\n              l1"+l1)
                                                if l1 in positives:
                                                        #debugFile.write( "\n..............determinzed option 2.4")
                                                        successorStates = labelTargets[label] = labelTargets.get(label) or []
                                                        for s2 in self.epsilonClosure(s1):
                                                                #debugFile.write( "\n..............determinzed option 2.5")
                                                                if s2 not in successorStates:
                                                                        #debugFile.write( "\n..............determinzed option 2.6")
                                                                        successorStates.append(s2)
                                                        if self.getArcMetadataFor(transition):
                                                                #debugFile.write( "\n..............determinzed option 2.7")
                                                                arcMetadata.append(((stateSet, successorStates, label), self.getArcMetadataFor(transition)))
                                for label, successorStates in labelTargets.items():
                                        #debugFile.write( "\n..............determinzed option 2.8")
                                        successorStates.sort()
                                        successorStates = tuple(successorStates)
                                        transitions.append((stateSet, successorStates, label))
                                        if successorStates not in stateSets:
                                                #debugFile.write( "\n..............determinzed option 2.9")
                                                stateSets.append(successorStates)
                finalStates = []
                for stateSet in stateSets:
                        #debugFile.write( "\n..............determinzed option 3")
                        if filter(lambda s,finalStates=self.finalStates:s in finalStates, stateSet):
                                #debugFile.write( "\n..............determinzed option 3.1")
                                finalStates.append(stateSet)
                if arcMetadata:
                        #debugFile.write( "\n..............determinzed option 4")
                        def fixArc(pair):
                                (s0, s1, label), data = pair
                                s1.sort()
                                s1 = tuple(s1)
                                return ((s0, s1, label), data)
                        arcMetadata = map(fixArc, arcMetadata)
                result = self.copy(stateSets, self.alphabet, transitions, stateSets[0], finalStates, arcMetadata).sorted()
                result._isDeterminized = 1
                result._isTrimmed = 1
                return result
        
        def minimized(self):
                """Returns a minimal FSA that accepts the same language."""
                if hasattr(self, '_isMinimized'):
                        return self
                #debugFile.write( "\n\tTRIMMED:\n\t\t"+str(self.trimmed()))
                #debugFile.write( "\n\tDETERMINED:\n\t\t" + str(self.trimmed().determinized()))
                self = self.trimmed().determinized()
                states0, alpha0, transitions0, initial0, finals0 = self.tuple()
                sinkState = self.nextAvailableState()
                labels = self.labels()
                states = filter(None, [
                                tuple(filter(lambda s, finalStates=self.finalStates:s not in finalStates, states0)),
                                tuple(filter(lambda s, finalStates=self.finalStates:s in finalStates, states0))])
                labelMap = {}
                for state in states0:
                        for label in labels:
                                found = 0
                                for s0, s1, l in self.transitionsFrom(state):
                                        if l == label:
                                                assert not found
                                                found = 1
                                                labelMap[(state, label)] = s1
                changed = 1
                iteration = 0
                while changed:
                        changed = 0
                        iteration = iteration + 1
                        #print 'iteration', iteration
                        partitionMap = {sinkState: sinkState}
                        for set in states:
                                for state in set:
                                        partitionMap[state] = set
                        #print 'states =', states
                        for index in range(len(states)):
                                set = states[index]
                                if len(set) > 1:
                                        for label in labels:
                                                destinationMap = {}
                                                for state in set:
                                                        nextSet = partitionMap[labelMap.get((state, label), sinkState)]
                                                        targets = destinationMap[nextSet] = destinationMap.get(nextSet) or []
                                                        targets.append(state)
                                                #print 'destinationMap from', set, label, ' =', destinationMap
                                                if len(destinationMap.values()) > 1:
                                                        values = destinationMap.values()
                                                        #print 'splitting', destinationMap.keys()
                                                        for value in values:
                                                                value.sort()
                                                        states[index:index+1] = map(tuple, values)
                                                        changed = 1
                                                        break
                transitions = removeDuplicates(map(lambda (s0,s1,label), m=partitionMap:(m[s0], m[s1], label), transitions0))
                arcMetadata = map(lambda ((s0, s1, label), data), m=partitionMap:((m[s0], m[s1], label), data), self.getArcMetadata())
                if not alpha0:
                        newTransitions = consolidateTransitions(transitions)
                        if arcMetadata:
                                newArcMetadata = []
                                for transition, data in arcMetadata:
                                        s0, s1, label = transition
                                        for newTransition in newTransitions:
                                                
                                                if (newTransition[0] == s0 and newTransition[1] == s1):
#                                                        if labelIntersection(newTransition[2], label):
#                                                                debugFile.write( "\n\nEntered HERE (10)\n")
                                                        newArcMetadata.append((newTransition, data))
                                arcMetadata = newArcMetadata
                        transitions = newTransitions
                initial = partitionMap[initial0]
                finals = removeDuplicates(map(lambda s, m=partitionMap:m[s], finals0))
                result = self.copy(states, self.alphabet, transitions, initial, finals, arcMetadata).sorted()
                result._isDeterminized = 1
                result._isMinimized = 1
                result._isTrimmed = 1
                return result
        
        
        #
        # Presentation Methods
        #
        def __repr__(self):
                if hasattr(self, 'label') and self.label:
                        return '<%s on %s>' % (self.__class__.__name__, self.label)
                else:
                        return '<%s.%s instance>' % (self.__class__.__module__, self.__class__.__name__)
        
        def __str__(self):
                output = []
                output.append('%s {' % (self.__class__.__name__,))
                output.append('\tname = %s;' % (self.fsaname,))
                output.append('\tinitialState = ' + `self.initialState` + ';')
                if self.finalStates:
                        output.append('\tfinalStates = ' + string.join(map(str, self.finalStates), ', ') + ';')
                transitions = list(self.transitions)
                transitions.sort()
                for transition in transitions:
                        (s0, s1, label) = transition
                        additionalInfo = self.additionalTransitionInfoString(transition)
                        output.append('\t%s -> %s %s%s;' % (s0, s1, labelString(label), additionalInfo and ' ' + additionalInfo or ''));
                output.append('}');
                return string.join(output, '\n')
        
        def additionalTransitionInfoString(self, transition):
                if self.getArcMetadataFor(transition):
                        return '<' + string.join(map(str, self.getArcMetadataFor(transition)), ', ') + '>'
        
        def stateLabelString(self, state):
                """A template method for specifying a state's label, for use in dot
                diagrams. If this returns None, the default (the string representation
                of the state) is used."""
                return None
        
        def toDotString(self):
                """Returns a string that can be printed by the DOT tool at
                http://www.research.att.com/sw/tools/graphviz/ ."""
                output = []
                output.append('digraph finite_state_machine {');
                if self.finalStates:
                                output.append('\tnode [shape = doublecircle]; ' + string.join(map(str, self.finalStates), '; ') + ';' );
                output.append('\tnode [shape = circle];');
                output.append('\trankdir=LR;');
                output.append('\t%s [style = bold];' % (self.initialState,))
                for state in self.states:
                        if self.stateLabelString(state):
                                output.append('\t%s [label = "%s"];' % (state, string.replace(self.stateLabelString(state), '\n', '\\n')))
                transitions = list(self.transitions)
                transitions.sort()
                for (s0, s1, label) in transitions:
                        output.append('\t%s -> %s  [label = "%s"];' % (s0, s1, string.replace(labelString(label), '\n', '\\n')));
                output.append('}');
                return string.join(output, '\n')
        
        def view(self):
                view(self.toDotString())


#
# Recognizers for special-case languages
#

NULL_FSA = FSA([0], None, [], 0, [])
EMPTY_STRING_FSA = FSA([0], None, [], 0, [0])
UNIVERSAL_FSA = FSA([0], None, [(0, 0, ANY)], 0, [0])


#
# Utility functions
#

def removeDuplicates(sequence):
        result = []
        for x in sequence:
                if x not in result:
                        result.append(x)
        return result

def toFSA(arg):
        if hasattr(arg, 'isFSA') and arg.isFSA:
                #debugFile.write("\nIS FSA: "+str(arg))
                #print "\nIS FSA: "+str(arg)
                return arg
        else:
                #debugFile.write("\nIS NOT FSA: "+str(arg))
                #print "\nIS NOT FSA: "+str(arg)
                return singleton(arg)

def view(str):
        dotfile = tempfile.mktemp()
        psfile = tempfile.mktemp()
        open(dotfile, 'w').write(str)
        dotter = 'dot'
        psviewer = 'gv'
        psoptions = '-antialias'
        os.system("%s -Tps %s -o %s" % (dotter, dotfile, psfile))
        os.system("%s %s %s&" % (psviewer, psoptions, psfile))


#
# Operations on languages (via their recognizers)
# These generally return nondeterministic FSAs.
#

def closure(arg):
        fsa = toFSA(arg)
        states, alpha, transitions, initial, finals = fsa.tuple()
        final = fsa.nextAvailableState()
        transitions = transitions[:]
        for s in finals:
                transitions.append((s, final, None))
        transitions.append((initial, final, None))
        transitions.append((final, initial, None))
        return fsa.create(states + [final], alpha, transitions, initial, [final], fsa.getArcMetadata())

def complement(arg):
        """Returns an FSA that accepts exactly those strings that the argument does
        not."""
        return toFSA(arg).complement()

def concatenation(a, *args):
        """Returns an FSA that accepts the language consisting of the concatenation
        of strings recognized by the arguments."""
        a = toFSA(a)
        for b in args:
                b = toFSA(b).sorted(a.nextAvailableState())
                states0, alpha0, transitions0, initial0, finals0 = a.tuple()
                states1, alpha1, transitions1, initial1, finals1 = b.tuple()
                a = a.create(states0 + states1, alpha0, transitions0 + transitions1 + map(lambda  s0, s1=initial1:(s0, s1, EPSILON), finals0), initial0, finals1, a.getArcMetadata() + b.getArcMetadata())
        return a

def containment(arg, occurrences=1):
        """Returns an FSA that matches sequences containing at least _count_
        occurrences
        of _symbol_."""
        arg = toFSA(arg)
        fsa = closure(singleton(ANY))
        for i in range(occurrences):
                fsa = concatenation(fsa, concatenation(arg, closure(singleton(ANY))))
        return fsa

def difference(a, b):
        """Returns an FSA that accepts those strings accepted by the first
        argument, but not the second."""
        return intersection(a, complement(b))

def equivalent(a, b):
        """Return true ifff a and b accept the same language."""
        return difference(a, b).isEmpty() and difference(b, a).isEmpty()

def intersection(a, b):
        """Returns the intersection of two FSAs"""
        #debugFile.write("\n\nEntering intersection..............")
        #debugFile.write("\n\nB DETERMINIZED(): "+str(b.determinized()))
        a, b = completion(a.determinized()), completion(b.determinized()) #***FALLA AQUI, accio sobre b
        #debugFile.write("\n\nA DETERMINIZED: "+str(a))
        #debugFile.write("\n\nB DETERMINIZED: "+str(b))
        states0, alpha0, transitions0, start0, finals0 = a.tuple()
        states1, alpha1, transitions1, start1, finals1 = b.tuple()
        states = [(start0, start1)]
        index = 0
        transitions = []
        arcMetadata = []
        buildArcMetadata = a.hasArcMetadata() or b.hasArcMetadata()
        while index < len(states):
                state = states[index]
                index = index + 1
                for sa0, sa1, la in a.transitionsFrom(state[0]):
                        for sb0, sb1, lb in b.transitionsFrom(state[1]):
                                label = labelIntersection(la, lb)
#                                debugFile.write( "\n\nEntered HERE (20)\n")
                                if label:
                                        s = (sa1, sb1)
                                        transition = (state, s, label)
                                        transitions.append(transition)
                                        if s not in states:
                                                states.append(s)
                                        if buildArcMetadata:
                                                if a.getArcMetadataFor((sa0, sa1, la)):
                                                        arcMetadata.append((transition, a.getArcMetadataFor((sa0, sa1, la))))
                                                if b.getArcMetadataFor((sa0, sa1, la)):
                                                        arcMetadata.append((transition, b.getArcMetadataFor((sa0, sa1, la))))
        finals = filter(lambda (s0, s1), f0=finals0, f1=finals1:s0 in f0 and s1 in f1, states)
        return a.create(states, alpha0, transitions, states[0], finals, arcMetadata).sorted()

def iteration(fsa, min=1, max=None):
        """
        >>> equivalent(iteration(singleton('a', 0, 2)), compileRE('|a|aa'))
        >>> equivalent(iteration(singleton('a', 1, 2)), compileRE('a|aa'))
        >>> equivalent(iteration(singleton('a', 1)), compileRE('aa*'))
        """
        if min:
                return concatenation(fsa, iteration(fsa, min=min - 1, max=(max and max - 1)))
        elif max:
                return option(concatenation(fsa), iteration(fsa, min=min, max=max - 1))
        else:
                return closure(fsa)

def option(fsa):
        return union(fsa, EMPTY_STRING_FSA)

def reverse(fsa):
        states, alpha, transitions, initial, finals = fsa.tuple()
        newInitial = fsa.nextAvailableState()
        return fsa.create(states + [newInitial], alpha, map(lambda (s0, s1, l):(s1, s0, l), transitions) + map(lambda s1, s0=newInitial:(s0, s1, EPSILON), finals), [initial])

def union(*args):
        initial = 1
        final = 2
        states = [initial, final]
        transitions = []
        arcMetadata = []
        for arg in args:
                #debugFile.write("\nARG (1): "+str(arg))
                #if arg: print "\nARG (1):", arg.tuple()
                #arg = toFSA(arg).sorted(reduce(max, states) + 1)
                arg = toFSA(arg).sortedObligatory(reduce(max, states) + 1)
                #debugFile.write("\nARG (2): "+str(arg))
                #if arg: print "\n\tARG (2):", arg.tuple()
                states1, alpha1, transitions1, initial1, finals1 = arg.tuple()
                states.extend(states1)
                #print "STATES:", states
                transitions.extend(list(transitions1))
                transitions.append((initial, initial1, None))
                #print "TRANSITIONS:", transitions
                for s in finals1:
                        transitions.append((s, final, None))
                arcMetadata.extend(arg.getArcMetadata())
        if len(args):
                #print "RETURN 1:"
                newFSA= toFSA(args[0]).create(states, alpha1, transitions, initial, [final], arcMetadata)
                #print "\t", newFSA
                return newFSA
        else:
                #print "RETURN 2"
                return FSA(states, alpha1, transitions, initial, [final])


#
# FSA Functions
#

def completion(fsa):
        """Returns an FSA that accepts the same language as the argument, but that
        lands in a defined state for every input."""
        states, alphabet, transitions, start, finals = fsa.tuple()
        transitions = transitions[:]
        sinkState = fsa.nextAvailableState()
        for state in states:
                labels = map(lambda (_, __, label):label, fsa.transitionsFrom(state)) #added underscore insecond argument
                for label in complementLabelSet(labels, alphabet):
                        transitions.append((state, sinkState, label))  #added parenthesis pair 
        if alphabet:
                transitions.extend(map(lambda symbol, s=sinkState:(s, s, symbol), alphabet))
        else:
                transitions.append((sinkState, sinkState, ANY))
        return fsa.copy(states + [sinkState], alphabet, transitions, start, finals, fsa.getArcMetadata())

def determinize(fsa):
        return fsa.determinized()

def minimize(fsa):
        return fsa.minimized()

def sort(fsa):
        return fsa.sorted()

def trim(fsa):
        return fsa.trimmed()


#
# Label operations
#

TRACE_LABEL_OPERATIONS = 0

def labelComplements(label, alphabet):
        #debugFile.write( "\n\nEntering labelComplementSSS...........")
        complement = labelComplement(label, alphabet) or []
        if TRACE_LABEL_OPERATIONS:
                pass
                #log('complement(%s) = %s' % (label, complement))
        if  type(complement) != ListType:
                complement = [complement]
        return complement

def labelComplement(label, alphabet):
        #debugFile.write( "\n\nEntering labelComplement...........")
        if type(label) == InstanceType:
                #debugFile.write( "\nHERE.......1")
                return label.complement()
        elif alphabet:
                #debugFile.write( "\nHERE.......2")
                return filter(lambda s, s1=label:s != s1, alphabet)
        elif label == ANY:
                #debugFile.write( "\nHERE.......3")
                return None
        else:
                #debugFile.write( "\nHERE.......4")
                return symbolComplement(label)

def labelIntersection(l1, l2):
        intersection = _labelIntersection(l1, l2)
        if TRACE_LABEL_OPERATIONS:
            pass
            #log('intersection(%s, %s) = %s' % (l1, l2, intersection))
        return intersection

def _labelIntersection(l1, l2):
#        debugFile.write( "\n\n--------\nLABELS:"+ l1 +" " + l2 + "\n--------\n")
        if l1 == l2:
        #if l1 == l2 or l1 == ANY:       
#                debugFile.write( "\n\nSOLUTION 1")
                return l1
        #todo: is the following ever true
        elif not l1 or not l2:
#                debugFile.write( "\n\nSOLUTION 2")
                return None
        elif l1 == ANY:
#                debugFile.write( "\n\nSOLUTION 3")
                return l2
        elif l2 == ANY:
#                debugFile.write( "\n\nSOLUTION 4")
                return l1
        elif type(l1) == InstanceType:
#                debugFile.write( "\n\nSOLUTION 5")
                return l1.intersection(l2)
        elif type(l2) == InstanceType:
#                debugFile.write( "\n\nSOLUTION 6")
                return l2.intersection(l1)
        else:
#                debugFile.write( "\n\nSOLUTION 7")
                return symbolIntersection(l1, l2)

def labelString(label):
        return str(label)

def labelDict(label):
        """Given a dict that at some point was string-ified (str(dict)),
        return it into a python dictionary """
        return eval(label)

def labelMatches(label, input):
        #log( "\n\nLABEL MATCHES:"+label+"  "+ str(input)+"?")
        #print "LABEL MATCHES:"+label+"  "+ str(input)+"?"
        if (type(label) is StringType and (label[0] == '{' or label[-1] == '}')):
                """Pattern expression has been given in a Python dictionary format """
                label = labelDict(label)
                #print "LABEL in FSA (1): "+str(label)
                #log("\tMATCH (0.1), STRING:"+str(input))
                #print "\t\tINPUT class name: "+str(input.__class__.__name__)
                if (type(input) is InstanceType and
                    input.__class__.__name__ in ['Constituent', 'Chunk', 'NounChunk',
                                                 'VerbChunk', 'Token', 'AdjectiveToken',
                                                 'EventTag', 'TimexTag']):
                        """Specific for Evita"""
                        #print "EVITA: LABEL in FSA (2): "+str(label)
                        return input._matchChunk(label)
                elif type(input) is DictType:
                        """ Open to other dictionary-based object matching applications"""
                        #print "NON-EVITA: LABEL in FSA (2): "+str(label)
                        return matchDict(label, input)
                else:
                        #print "LABEL:", label, "\nINPUT:", input.nodeType
                        raise "ERROR: possibly label is in dict format, but not the input"
        elif type(label) == InstanceType and hasattr(label, 'matches'):
                #debugFile.write("\n\tMATCH (1)")
                #print "\n\tMATCH (1)"
                return label.matches(input)
        else:
                #debugFile.write("\n\tMATCH (2)")
                #print "\n\tMATCH (2)"
                return label == input    
        
def matchDict(label, input):
        """Match input to the pattern described by label.
        Both label and input are dictionaries with keys-values pairs.

        The format of the value in each key-value pair of label can be:
        - an atomic element. E.g., {..., 'headForm':'is', ...} 
        - a list of possible values. E.g., {..., headForm': ['have', 'has', 'had'], ...}   
        In this case, matchDict checks whether the input value is
        included within this list.
        - a negated value. Negation is represented by means of a
        2-place tuple, whose initial position is the caret symbol,
        and its second position is the atomic value or list of atomic values
        that need to be negated: '^'. E.g., {..., 'headPos': ('^', 'MD') ...}
        """        
        labelKeys = label.keys()
        inputKeys = input.keys()
        for key in labelKeys:
                #print "KEY:", key, "VALUE:", label[key]
                if key in inputKeys:
                    value = label[key]
                    if type(value) is TupleType:
                        #print "\t\t......TUPLE TYPE"
                        if value[0] == '^':
                            value = value[1]
                            if type(value) is ListType:
                                if input[key] in value:
                                    return 0
                            else:
                                if input[key] == value:
                                    return 0
                        else:
                            raise "ERROR specifying description of pattern"
                    elif type(value) is ListType:
                        #print "\t\t......LIST TYPE"
                        if input[key] not in value:
                            return 0

                    else:
                        #print "\t\t......ATOMIC TYPE"    
                        if input[key] != label[key]:
                            return 0
                else: return 0
        else: return 1
        
#
# Label set operations
#

TRACE_LABEL_SET_OPERATIONS = 0

def complementLabelSet(labels, alphabet=None):
        if not labels:
                return alphabet or [ANY]
        result = labelComplements(labels[0], alphabet)
        for label in labels[1:]:
                result = intersectLabelSets(labelComplements(label, alphabet), result)
        if TRACE_LABEL_SET_OPERATIONS:
                pass
                #log('complement(%s) = %s' % (labels, result))
        return result

def intersectLabelSets(alist, blist):
        clist = []
        for a in alist:
                for b in blist:
                        c = labelIntersection(a, b)
#                        debugFile.write( "\n\nEntered HERE (30)\n")
                        if c:
                                clist.append(c)
        if TRACE_LABEL_SET_OPERATIONS:
                pass
                #log('intersection%s = %s' % ((alist, blist), clist))
        return clist

def unionLabelSets(alist, blist, alphabet=None):
        result = complementLabelSet(intersectLabelSets(complementLabelSet(alist, alphabet), complementLabelSet(blist, alphabet)), alphabet)
        if TRACE_LABEL_SET_OPERATIONS:
                pass
                #log('union%s = %s' % ((alist, blist), result))
        return result


#
# Transition and Label utility operations
#

TRACE_CONSOLIDATE_TRANSITIONS = 0
TRACE_CONSTRUCT_LABEL_MAP = 0

def consolidateTransitions(transitions):
        result = []
        for s0, s1 in removeDuplicates(map(lambda (s0, s1, _):(s0,s1), transitions)):
                labels = []
                for ss0, ss1, label in transitions:
                        if ss0 == s0 and ss1 == s1:
                                labels.append(label)
                if len(labels) > 1:
                        reduced = reduce(unionLabelSets, map(lambda label:[label], labels))
                        if TRACE_LABEL_OPERATIONS or TRACE_CONSOLIDATE_TRANSITIONS:
                                pass
                                #log('consolidateTransitions(%s) -> %s' % (labels, reduced))
                        labels = reduced
                for label in labels:
                        result.append((s0, s1, label))
        return result

def constructLabelMap(labels, alphabet, includeComplements=0):
        """Return a list of (newLabel, positives), where newLabel is an
        intersection of elements from labels and their complemens, and positives is
        a list of labels that have non-empty intersections with newLabel."""
        label = labels[0]
        #if hasattr(label, 'constructLabelMap'):
        #        return label.constructLabelMap(labels)
        #debugFile.write( "\n\nEntered HERE (130)\n")
        complements = labelComplements(label, alphabet)
        #debugFile.write( "\n\nEntered HERE (140)\n")
        if len(labels) == 1:
                #debugFile.write( "\n\nEntered HERE (150)\n")
                results = [(label, [label])]
                if includeComplements:
                        #debugFile.write( "\n\nEntered HERE (160)\n")
                        #debugFile.write( "\nCOMPLEMENTS: "+str(complements))
                        for complement in complements:
                                #debugFile.write( "\n\nEntered HERE (170)\n")
                                results.append((complement, []))
                return results
        results = []
        for newLabel, positives in constructLabelMap(labels[1:], alphabet, includeComplements=1):
                #debugFile.write( "\n\nEntered HERE (180)\n")
                newPositive = labelIntersection(label, newLabel)
                #debugFile.write( "\n\nEntered HERE (40)\n")
                if newPositive:
                        results.append((newPositive, [label] + positives))
                for complement in complements:
                        if positives or includeComplements:
                                newNegative = labelIntersection(complement, newLabel)
                                #debugFile.write( "\n\nEntered HERE (50)\n")
                                if newNegative:
                                        results.append((newNegative, positives))
        if TRACE_CONSTRUCT_LABEL_MAP:
                pass
                #log('consolidateTransitions(%s) -> %s' % (labels, results))
        return results


#
# Symbol operations
#

def symbolComplement(symbol):
        #debugFile.write( "\nSYMBOL: "+str(symbol))
        if type(symbol) is not StringType:
                symbol = str(symbol)

        if '&' in symbol:
                #debugFile.write( "\nSYMBOL .........1")
                return map(symbolComplement, string.split(symbol, '&'))
        elif symbol[0] == '~':
                #debugFile.write( "\nSYMBOL .........2")
                return symbol[1:]
        else:
                #debugFile.write( "\nSYMBOL .........3")
                return '~' + str(symbol)
              
        

def symbolIntersection(s1, s2):
        if type(s1) is StringType: set1 = string.split(s1, '&')
        else: set1 = [str(s1)]

        if type(s2) is StringType: set2 = string.split(s2, '&')
        else: set2 = [str(s2)]
                
        for symbol in set1:
                if symbolComplement(symbol) in set2:
                        return None
        for symbol in set2:
                if symbol not in set1:
                        set1.append(symbol)
                        
        if type(s1) is StringType:
                #debugFile.write( "\nS1:"+s1)
                nonNegatedSymbols = filter(lambda s:s[0] != '~', set1)
        else:
                nonNegatedSymbols = set1
               
        if len(nonNegatedSymbols) > 1:
                return None
        if nonNegatedSymbols:
                return nonNegatedSymbols[0]
        set1.sort()
        return string.join(set1, '&')


#
# Construction from labels
#

def singleton(symbol, alphabet=None, arcMetadata=None):
        #debugFile.write( "\nSINGLETON")
        fsa = FSA([0,1], alphabet, [(0, 1, symbol)], 0, [1])
        if arcMetadata:
                fsa.setArcMetadataFor((0, 1, symbol), arcMetadata)
        fsa.label = `symbol`
        return fsa

def sequence(sequence, alphabet=None):
        fsa = reduce(concatenation, map(lambda label, alphabet=alphabet:singleton(label, alphabet), sequence), EMPTY_STRING_FSA)
        fsa.label = `sequence`
        return fsa


#
# Compiling Object Patterns represented a la Regular Expressions 
#
"""
print compileRE('')         =>  compileOP([''])
print compileRE('a')        =>  compileOP(['a'])
print compileRE('a?')        =>  compileOP(['a'])
print compileRE('a+')        =>  compileOP(['a'])
print compileRE('a*')        =>  compileOP(['a'])

print compileRE('ab')       =>  compileOP(['a', 'b'])
print compileRE('ab?')       =>  compileOP(['a', 'b'])
print compileRE('ab+')       =>  compileOP(['a', 'b'])
print compileRE('ab*')       =>  compileOP(['a', 'b'])
print compileRE('a?b')       =>  compileOP(['a', 'b'])
print compileRE('a+b')       =>  compileOP(['a', 'b'])
print compileRE('a*b')       =>  compileOP(['a', 'b'])

print compileRE('abc')      =>  compileOP(['a', 'b', 'c'])
print compileRE('a?bc')      =>  compileOP(['a', 'b', 'c'])
print compileRE('a+bc')      =>  compileOP(['a', 'b', 'c'])
print compileRE('a*bc')      =>  compileOP(['a', 'b', 'c'])
print compileRE('ab?c')     =>  compileOP(['a', 'b','?', 'c'])
print compileRE('ab+c')     =>  compileOP(['a', 'b', '+', 'c'])
print compileRE('ab*c')     =>  compileOP(['a', 'b', '*', 'c'])
print compileRE('abc?')      =>  compileOP(['a', 'b', 'c'])
print compileRE('abc+')      =>  compileOP(['a', 'b', 'c'])
print compileRE('abc*')      =>  compileOP(['a', 'b', 'c'])

print compileRE('ab|c')     =>  compileOP(['a', 'b', '|' 'c']) 
print compileRE('a(b|c)')   =>  compileOP(['a', '(', 'b', '|', 'c', ')'])


print FSA_test.compileOP(['a', 'd', '*', '(', 'b', '|', 'c', ')'])
print FSA_test.compileOP(['a', 'd', '+', 'e', '(', 'b', '|', 'c', ')'])
print FSA_test.compileOP(['a', 'd', '+', 'e', '(', 'b', '|', 'c', ')', 'f'])
print FSA_test.compileOP(['a', 'd', '+', 'e', '(', 'b', '|', 'c', ')', '(', 'f', '*', 'g', '|', 'h', ')'])
print FSA_test.compileOP(['a', 'd', '+', 'e', '(', 'b', '|', 'c', ')', '(', 'f', '*', 'g', '|', 'h', ')', 'i'])
"""

class Sequence:

        def __init__(self, pattern):
#                print "\nENTERING SEQUENCE............\n"
                self.sequence = pattern
                self.bordersDict = {}
                self.buildBordersDict()

        def __getitem__(self, index):
                if index < len(self.sequence):
                        return self.sequence[index]
                else:
                        return

        def __getslice__(self, i, j):
                return self.sequence[i:j]

        def __len__(self):
                return len(self.sequence)

                        
        def buildBordersDict(self):
                """*** COMMENT needs to be added ***"""
                previousBorder = {}
                currentSubpattern = 0
                previousBorder[currentSubpattern] = 0   # Index of previous bar in currentSubpattern
                for i in range(len(self.sequence)):
                    #print "ITEM:", i, self.sequence[i], "CURRENT SUBPATTERN:", currentSubpattern
                    if type(self.sequence[i]) is StringType : 
                        if self.sequence[i] == '(':
                                currentSubpattern = currentSubpattern+1
                                #print "\tCURRENT SUBPATTERN:", currentSubpattern
                               
                        elif self.sequence[i][0] == ')':
                                try:
                                        previousBorderIndex = previousBorder[currentSubpattern]
                                        self.bordersDict[previousBorderIndex] = i
                                except: pass

                                previousBorder[currentSubpattern] = None
                                if currentSubpattern:
                                        currentSubpattern = currentSubpattern-1
                                else:
                                        """currentSubpattern may be 0 either because there is an error,
                                        or because we are in a subpattern that resetted
                                        the currentSubpattern variable to 0 """
                                        if self.__class__.__name__ == "Sequence": pass
                                        else: raise "ERROR (1): expression missing at least one '('"
                                        
                        elif self.sequence[i] == '|':
                                try:
                                        previousBorderIndex = previousBorder[currentSubpattern]
                                        self.bordersDict[previousBorderIndex] = i
                                except: pass
                                previousBorder[currentSubpattern] = i
                if currentSubpattern != 0:
                        raise "ERROR (2): expression missing at least one ')'"
                                
        def getNextBorder(self, index):
                try: return self.bordersDict[index]
                except: return -1                

class SyntaxSequence(Sequence):

        def __init__(self, description):
                #print "\nENTERING SYNTAX SEQUENCE............\n"
                Sequence.__init__(self, description)
                self.description = description
                self.label = string.join(str(self.description), '_')
                self.sequence = self.atomizeDescription()

        def atomizeDescription(self):
            #print "ATOMIZING descriotion...\n"
            res = []
            for item in self.description:
                    #debugFile.write( "\nITEM: "+str(item))
                    if len(item) > 1:
                            #if type(item) is StringType:
                            if type(item) is not StringType:
                                    item = str(item)
                                    
                            if item[0] in ['(','[','|']:
                                    #print "SIT 1"
                                    if len(item) > 1:
                                        raise 'ERROR (1): check syntax for pattern: '+ str(self.description)
                                    else:
                                        res.append(item)
                            if item[0] == '~':
                                    #print "SIT 2"
                                    res.append(item[0])
                                    res.append(item[1:])

                            elif item[-1] in ['(','[','|']:
                                    #print "SIT 3"
                                    if len(item) > 1:
                                        raise 'ERROR (2): check syntax for pattern: '+ str(self.description)
                                    else:
                                        pass
                            elif item[-1] in [')',']']:
                                    #print "SIT 4"
                                    if len(item) > 1:
                                        raise 'ERROR (3): check syntax for pattern: '+ str(self.description)
                                    else:
                                        res.append(item)
                            elif item[-1] in ['*','+','?']:
                                    #print "SIT 5"
                                    res.append(item[:-1])
                                    res.append(item[-1])
                            else:
                                    #print "SIT 6"
                                    res.append(item)

#                            else:
#                                    #debugFile.write( "\nAPPENDING...(1)"+str(item))
#                                    res.append(item)
                    else:
                            #debugFile.write( "\nAPPENDING...(2)"+str(item))
                            res.append(str(item))
            return res


                

def compileOP(description, **options):
        """description is a list of labels describing constituents,
        where each constituent can be a lexical item (token)
        or a chunk. *** CONTINUAR

        Labels in description CAN NOT use '_' (underscore)
        """

        pattern = SyntaxSequence(description)
        #debugFile.write( "\nENTIRE PATTERN: "+str(pattern.sequence))
        
        fsa, index = compileOPExpr(pattern, 0, options)
        #debugFile.write( "PATERN:"+str(pattern)+"INDEX:"+str(index))


        if index < len(pattern):
                raise 'extra character in pattern (possibly ")" )'
        fsa.label = pattern.label
        #debugFile.write( "\n=\n\tFSA MINIMIZED:\n\t\t")
        #debugFile.write(str(fsa.minimized()))
        fsa_min = fsa.minimized()
        #print "FSA min:\n\t"+str(fsa_min)
        #debugFile.close()
        fsa_min.fsaname = options.get('name')
        #print fsa_min
        return fsa_min

def compileOPExpr(pattern, index, options):
        #debugFile.write( "\n\nCOMPILE OP EXPR")
        barFlag = 0
        fsa = None
        while index < len(pattern) and pattern[index] != ')':
                #debugFile.write( "\ncompileOPExpr_while")

                if  pattern[index] == '|':
                        index = index + 1
                        endIndex = pattern.getNextBorder(index-1)
                        if endIndex == -1:
                                pattern2 = Sequence(pattern[index:])
                                #debugFile.write( "\nSUBPATTEW 1:"+str(pattern[index:]))
                                #print "SUBPATTEW 1:"+str(pattern[index:])
                        else:
                                pattern2 = Sequence(pattern[index:endIndex])
                                #debugFile.write( "\nSUBPATTEW 2:"+str( pattern[index:endIndex]))
                                #print "SUBPATTEW 2:"+str( pattern[index:endIndex])
                        #debugFile.write( "\nINDEX:"+str(index))
                        #print "INDEX:"+str(index)
                        #debugFile.write( "\nNEXT BORDER"+str(pattern.getNextBorder(index-1)))
                        #print "NEXT BORDER"+str(pattern.getNextBorder(index-1))

                        fsa2, index2 = compileOPExpr(pattern2, 0, options)
                        index = index + index2

                else:
                        fsa2, index = compileConjunctionOP(pattern, index, options)
                       
                #debugFile.write( "\nFSA_compileOPExpr:\n\t\t"+str(fsa))
                #if fsa: debugFile.write("\nvoc: "+str(fsa.states)+" "+str(fsa.alphabet)+" "+str(fsa.transitions)+" "+str(fsa.initialState)+" "+str(fsa.finalStates)+" ")#+str(fsa.arcMetadata))
                                        
                #debugFile.write( "\nFSA2_compileOPExpr:\n\t\t"+str(fsa2))
                #if fsa2: debugFile.write("\nvoc: "+str(fsa2.states)+" "+str(fsa2.alphabet)+" "+str(fsa2.transitions)+" "+str(fsa2.initialState)+" "+str(fsa2.finalStates)+" ")#+str(fsa2.arcMetadata))
                fsa3= union(fsa, fsa2) ##debug
                #debugFile.write( "\nFSA_compileOPExpr_Union:\n\t\t"+str(fsa3))
                #print "UNION:", union(fsa, fsa2)

                fsa = (fsa and union(fsa, fsa2)) or fsa2
                #debugFile.write( "\nFSA_Result :\n\t\t"+str(fsa))
                fsa4 = fsa.minimized() #debug
                #debugFile.write( "\nFSA_Result min:\n\t\t"+str(fsa4))
                #print "MINIMIZD:", fsa.minimized()
        
        return (fsa or EMPTY_STRING_FSA), index

def compileConjunctionOP(pattern, index, options):
        #debugFile.write( "\n\n\tCOMPILE CONJUNCTION OP")
        fsa = UNIVERSAL_FSA
        while pattern[index] and pattern[index] not in [')','|']:
                #debugFile.write( "\n\tcompileConjunctionOP_while")
                conjunct, index = compileSequenceOP(pattern, index, options)
                if  pattern[index] == '&':
                        index = index + 1
                #debugFile.write( "\n\tFSA_compileConjunctionOP:\n\t\t"+str(fsa))
                #debugFile.write( "\n\tFSA_Conjunct:\n\t\t"+str(conjunct))
                
                fsa = intersection(fsa, conjunct)  #*** lo que falla es crida aqui
                #debugFile.write( "\n\tFSA_Result :\n\t\t"+str(fsa))
                #debugFile.write( "\n\tFSA_Result min:\n\t\t"+str(fsa.minimized()))
        return fsa, index

def compileSequenceOP(pattern, index, options):
        ##debugFile.write( "\n\n\t\tCOMPILE SEQUENCE OP")
        fsa = EMPTY_STRING_FSA
        while pattern[index] and pattern[index] not in [')','|','&']:
                ##debugFile.write( "\n\n\n======================================\n")
                ##debugFile.write( "\n======================================\n")
                ##debugFile.write( "\n\t\tcompileSequenceOP_while")
                ##debugFile.write( "\n\t\tcompileSequenceOP_Index1:"+ str(index))
                ##debugFile.write( "\n\t\tcompileSequenceOP_pattern[index]:"+ str(pattern[index]))
                fsa2, index = compileItemOP(pattern, index, options)
                ##debugFile.write( "\n\t\tcompileSequenceOP_FSA:\n\t\t"+str(fsa))
                ##debugFile.write( "\n\t\tFcompileSequenceOP_SA2:\n\t\t"+str(fsa2))
                fsa = concatenation(fsa, fsa2)
                ##debugFile.write( "\n\t\t===============================>>>>>>>  FSA_Concat:\n\t\t"+str(fsa))
                ##debugFile.write( "\n\tcompileSequenceOP_FSA_Concat min:\n\t\t"+str(fsa.minimized()))
        return fsa, index

def compileItemOP(pattern, index, options):
        ##debugFile.write( "\n\n\t\t\tCOMPILE ITEM OP")
        c = pattern[index]
        index = index + 1
        while c == ' ':
                ##debugFile.write( "\nHERE 1:")
                c = pattern[index]
                index = index + 1
        if c == '(':
                ##debugFile.write( "\nHERE 2:")
                fsa, index = compileOPExpr(pattern, index, options)
                assert pattern[index] == ')'
                index = index + 1
        elif c == '.':
                ##debugFile.write( "\nHERE 3:")
                fsa = singleton('ALL') #fsa = singleton(ANY) 
        elif c == '~':
                ##debugFile.write( "\nHERE 4:")
                fsa, index = compileItemOP(pattern, index, options)
                #print "SO FAR FSA:", fsa
                fsa = complement(fsa)
                #print "ITS COMPLEMENT:", fsa
        else:
                ##debugFile.write( "\nHERE 5:")
#                #debugFile.write( "\nC:", c)
                label = c
                if options.get('multichar'):
                #        #debugFile.write( "\nHERE 6:")
                        while ((pattern[index] in string.letters or pattern[index] in string.digits) and
                               index < len(pattern)):  ### CAL CANVIAR CONDICIONS string.letter!!!
                 #               #debugFile.write( "\nHERE 7:")
                                label = label + pattern[index]
                                index = index + 1
                if pattern[index] == ':':
                  #      #debugFile.write( "\nHERE 8:")
                        index = index + 1
                        upper = label
                        lower = pattern[index]
                        index = index + 1
                        if upper  == '0':
                   #             #debugFile.write( "\nHERE 9:")
                                upper  = EPSILON
                        if lower == '0':
                    #            #debugFile.write( "\nHERE 10:")
                                lower = EPSILON
                        label = (upper, lower)
                fsa = singleton(label)
        while pattern[index] in ['?','*','+']:
                ##debugFile.write( "\nHERE 11:")
                c = pattern[index]
                index = index + 1
                if c == '*':
                        fsa = closure(fsa)
                elif c == '?':
                        fsa = union(fsa, EMPTY_STRING_FSA)
                elif c == '+':
                        fsa = iteration(fsa)
                else:
                        raise 'unimplemented'
        return fsa, index


#
# Compiling Regular Expressions
#

def compileRE(s, **options):
        if not options.get('multichar'):
                s = string.replace(s, ' ', '')
        fsa, index = compileREExpr(s + ')', 0, options)
        if index < len(s):
                raise 'extra ' + `')'`
        fsa.label = str(s)
        return fsa.minimized()

def compileREExpr(str, index, options):
        fsa = None
        while index < len(str) and str[index] != ')':
                fsa2, index = compileConjunction(str, index, options)
                if  str[index] == '|': index = index + 1
                fsa = (fsa and union(fsa, fsa2)) or fsa2
        return (fsa or EMPTY_STRING_FSA), index

def compileConjunction(str, index, options):
        fsa = UNIVERSAL_FSA
        while str[index] not in ')|':
                conjunct, index = compileSequence(str, index, options)
                if  str[index] == '&': index = index + 1
                fsa = intersection(fsa, conjunct)
        return fsa, index

def compileSequence(str, index, options):
        fsa = EMPTY_STRING_FSA
        while str[index] not in ')|&':
                fsa2, index = compileItem(str, index, options)
                fsa = concatenation(fsa, fsa2)
        return fsa, index

def compileItem(str, index, options):
        c , index = str[index], index + 1
        while c == ' ':
                c, index = str[index], index + 1
        if c == '(':
                fsa, index = compileREExpr(str, index, options)
                assert str[index] == ')'
                index = index + 1
        elif c == '.':
                fsa = singleton('ALL')
        elif c == '~':
                fsa, index = compileItem(str, index, options)
                fsa = complement(fsa)
        else:
                label = c
                if options.get('multichar'):
                        ##debugFile.write( "\nMULTICHAR!")
                        while str[index] in string.letters or str[index] in string.digits:
                                label, index = label + str[index], index + 1
                if str[index] == ':':
                        index = index + 1
                        upper = label
                        lower, index = str[index], index + 1
                        if upper  == '0':
                                upper  = EPSILON
                        if lower == '0':
                                lower = EPSILON
                        label = (upper, lower)
                fsa = singleton(label)
        while str[index] in '?*+':
                c, index = str[index], index + 1
                if c == '*':
                        fsa = closure(fsa)
                elif c == '?':
                        fsa = union(fsa, EMPTY_STRING_FSA)
                elif c == '+':
                        fsa = iteration(fsa)
                else:
                        raise 'unimplemented'
        return fsa, index

"""
TRACE_LABEL_OPERATIONS = 1
TRACE_LABEL_OPERATIONS = 0

print compileRE('')
print compileRE('a')
print compileRE('ab')
print compileRE('abc')
print compileRE('ab*')
print compileRE('a*b')
print compileRE('ab*c')
print compileRE('ab?c')
print compileRE('ab+c')
print compileRE('ab|c')
print compileRE('a(b|c)')

print compileRE('abc').accepts('abc')
print compileRE('abc').accepts('ab')

print singleton('1', alphabet=['1']).minimized()
print complement(singleton('1')).minimized()
print singleton('1', alphabet=['1'])
print completion(singleton('1'))
print completion(singleton('1', alphabet=['1']))
print complement(singleton('1', alphabet=['1']))
print complement(singleton('1', alphabet=['1', '2']))
print complement(singleton('1', alphabet=['1', '2'])).minimized()

print intersection(compileRE('a*b'), compileRE('ab*'))
print intersection(compileRE('a*cb'), compileRE('acb*'))
print difference(compileRE('ab*'), compileRE('abb')).minimized()

print compileRE('n.*v.*n')
print compileRE('n.*v.*n&.*n.*n.*n.*')

print intersection(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*'))
print difference(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*'))
print difference(difference(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*')), compileRE('.*v.*v.*'))

print compileRE('a|~a').minimized()


print containment(singleton('a'), 2).minimized()
print difference(containment(singleton('a'), 2), containment(singleton('a'), 3)).minimized()
print difference(containment(singleton('a'), 3), containment(singleton('a'), 2)).minimized()

print difference(compileRE('a*b'), compileRE('ab*')).minimized()

"""
