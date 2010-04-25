"""Pattern matching for cascaded regular expression patterns"""

import sys, re


def tokenize(s):
    """Split the string s into tokens and return a sequence of strings.
    The string is split on white space, on transitions between letters
    and digits, and on all symbols."""
    reWhitespace = re.compile(r'\s+')
    reToken = re.compile(r'[a-zA-Z]+|\d+|[-_()[\]{}<>.,;:!?"\'`@#$%^&*+=|\\/~]')
    p = 0
    n = len(s)
    v = [ ]
    while p < n:
        m = reWhitespace.match(s, p)
        if m:
            # skip whitespace
            p = m.end()
        if p < n:
            m = reToken.match(s, p)
            if not m:
                raise ValueError("Unknown character '%c'" % s[p])
            v.append(m.group())
            p = m.end()
    return v


class SuperToken:
    """A supertoken corresponds to a non-empty span of primary tokens
    and carries a label and an optional value. A supertoken is created
    through token lookup or through pattern matching. A supertoken can
    itself be matched in later stages of pattern matching."""

    def __init__(self, start, end, name, val=None, raw=None):
        self.start = start
        self.end = end
        self.name = name
        self.val = val
        self.raw = raw

    def __cmp__(self, o):
        return cmp(self.name, o)

    def __repr__(self):
        return 'SuperToken(start=%s,end=%s,name=%s,val=%s%s)' % (
          repr(self.start), repr(self.end), repr(self.name), repr(self.val),
          ((self.raw is not None) and (',raw=' + repr(self.raw))) or '' )


class PatternMatcher:
    """Regular expression matching against a sequence of (super)tokens."""

    reLiteral = re.compile(r'"(([^\\"]|\\[\\"])*)"')
    reEsc = re.compile(r'\\([\\"])')
    reName = re.compile(r'([A-Z][0-9a-zA-Z]*)')

    def __init__(self, pattern, debug=0):
        """Compile expression into a finite state machine."""

        # Keep raw pattern string
        self.patternstr = pattern

        # In the machine construction phase, a state is either
        # - state 0, the final (accepting) state
        # - a token consuming state ( op, arg, captureset, nextstate )
        # - an epsilon state [ 'eps', nextstates, ... ]
        self.states = [ ('fin', None, (), 1) ]

        # Count the number of capture buffers
        self.ncapture = 0

        # Look for a begin assertion
        s = pattern.lstrip()
        if s[:1] == '^':
            self.forcebegin = 1
            s = s[1:].lstrip()
        else:
            self.forcebegin = 0

        # Build a list of token types referred to from this pattern
        self.tokenrefs = { }

        # Recursively compile the body of the regular expression
        s = self.compileOr(s, 0, ( ))
        self.tokenrefs = self.tokenrefs.keys()

        # Look for an end assertion
        if s[:1] == '$':
            self.forceend = 1
            s = s[1:].lstrip()
        else:
            self.forceend = 0
        if s:
            raise ValueError("Expected end of expression but got " + repr(s))

        # (debug) Print the compiled machine
        if debug:
            if self.forcebegin: print >>sys.stderr, "forcebegin"
            if self.forceend: print >>sys.stderr, "forceend"
            for i in range(len(self.states)):
                print >>sys.stderr, i, repr(self.states[i])

        # Eliminate epsilon states; after this step, all states except
        # except state 0 will be token consuming states
        # ( op, args, captureset, ( nextstates, ... ) )
        self.epsilonElim()
        # The set of initial states appears as the nextstate field of state 0
        self.initstates = self.states[0][-1]

        # (debug) Print the machine after epsilon removal
        if debug:
            for i in range(len(self.states)):
                if self.states[i]: print >>sys.stderr, i, self.states[i]

        # Matching empty sequences is a tricky business
        if 0 in self.initstates:
            raise ValueError("Expression matches the empty sequence")

    def __repr__(self):
        return 'PatternMatcher(' + repr(self.patternstr) + ')'
 
    def compileOr(self, s, endstate, captureset):
        """Compile a set of branches separated by '|' operators."""
        w = [ 'eps' ]
        self.states.append(w)
        while True:
            w.append(len(self.states))
            s = self.compileSeq(s, endstate, captureset)
            if not s or s[0] != '|':
                return s
            s = s[1:].lstrip()

    def compileSeq(self, s, endstate, captureset):
        """Compile a sequence of pieces."""
        a = len(self.states)
        self.states.append( [ 'eps' ] )
        while True:
            b = len(self.states)
            self.states.append( [ 'eps' ] )
            s = self.compileAtom(s, b, captureset)
            s = s.lstrip()
            if s[:1] == '?':
                # match the atom zero-or-one time
                s = s[1:].lstrip()
                self.states[a].append(b+1)
                self.states[a].append(b)
            elif s[:1] == '*':
                # match the atom zero-or-more times
                s = s[1:].lstrip()
                self.states[a].append(b)
                self.states[b].append(b+1)
            elif s[:1] == '+':
                # match the atom one-or-more times
                s = s[1:].lstrip()
                self.states[a].append(b+1)
                self.states[b].append(b+1)
            else:
                # match the atom exactly once
                self.states[a].append(b+1)
            a = b
            if not s or s[0] in '|)}$':
                # end of sequence
                self.states[a].append(endstate)
                return s

    def compileAtom(self, s, endstate, captureset):
        """Compile a single atom or a parenthesized subexpression."""
        if not s:
            raise ValueError("Expected atom but got end of expression")
        if s[0] == '(':   # parenthesized subexpression
            s = s[1:].lstrip()
            s = self.compileOr(s, endstate, captureset)
            if not s or s[0] != ')':
                raise ValueError("Expected ')' but got " + repr(s))
            return s[1:].lstrip()
        elif s[0] == '{': # capturing subexpression
            s = s[1:].lstrip()
            self.ncapture += 1
            s = self.compileOr(s, endstate, captureset + (self.ncapture-1,))
            if not s or s[0] != '}':
                raise ValueError("Expected '}' but got " + repr(s))
            return s[1:].lstrip()
        elif s[0] == '.': # wildcard
            self.states.append(('.', None, captureset, endstate))
            return s[1:].lstrip()
        elif s[0] == '"': # literal string
            m = self.reLiteral.match(s)
            if not m:
                raise ValueError("Expected token literal but got " + repr(s))
            t = m.group(1)
            t = self.reEsc.sub(r'\1', t)
            self.states.append(('str', t, captureset, endstate))
            return s[m.end():].lstrip()
        else:             # token name
            m = self.reName.match(s)
            if not m:
                raise ValueError("Expected token name but got " + repr(s))
            t = m.group()
            t = self.tokenrefs.setdefault(t, t)
            self.states.append(('tok', t, captureset, endstate))
            return s[m.end():].lstrip()

    def epsilonElim(self):
        """Eliminate epsilon transitions."""

        # Compute transitive closure over epsilon transitions
        target = [ None for s in self.states ]
        ref = [ [ ] for s in self.states ]
        for i in range(len(self.states)):
            if self.states[i][0] == 'eps':
                h = { }
                for j in self.states[i][1:]:
                    assert i != j
                    if j < i and target[j] is not None:
                        for k in target[j]:
                            if k != i and target[j][k] and k not in h:
                                assert k > i or self.states[k][0] != 'eps'
                                h[k] = 1
                                if k > i and self.states[k][0] == 'eps':
                                    ref[k].append(i)
                    else:
                        if j not in h:
                            h[j] = 1
                            if self.states[j][0] == 'eps':
                                ref[j].append(i)
                for k in ref[i]:
                    target[k][i] = 0
                    for j in h:
                        if j not in target[k]:
                            target[k][j] = 1
                            if j > i and self.states[j][0] == 'eps':
                                ref[j].append(k)
                target[i] = h
                ref[i] = None
        for i in range(len(self.states)):
            if target[i]:
                w = [ j for j in target[i] if target[i][j] ]
                target[i] = tuple(w)
            else:
                target[i] = (i,)

        # Resolve references to epsilon states
        for i in range(len(self.states)):
            if self.states[i][0] == 'eps':
                self.states[i] = None
            else:
                j = self.states[i][-1]
                self.states[i] = self.states[i][:-1] + (target[j],)

    def matchtoken(self, tok, curstates, isliteral):
        """Move from a set of current states to a set of new states by
        consuming one token; return the list of new (state, data) pairs."""
        nstates = [ ]
        for (i, v) in curstates:
            (op, arg, captureset, nextstate) = self.states[i]
            if (isliteral and op == '.') or \
               (isliteral and op == 'str' and tok == arg) or \
               (not isliteral and op == 'tok' and tok == arg):
                z = v
                for k in captureset:
                    z = z[:k] + (z[k] + (tok,),) + z[k+1:]
                nstates += [ (j, z) for j in nextstate ]
        return nstates

    def match(self, tokens, supertok, start=0):
        """Match a sequence of (super)tokens against the compiled patttern,
        starting at the given position in the token sequence.
        Return a list of matching (start, end, data) tuples, sorted by end.
        At most one match will be produced for any given (start, end) span."""

        # Partial matches: matchstate[pos][state] = captureseq
        matchstate = [ [ ] for p in range(len(tokens)+1) ]
        matchmap = [ { } for p in range(len(tokens)+1) ]

        # Set up initial states at start position
        matchstate[start] = [ (j, self.ncapture * ( (), ) )
                              for j in self.initstates ]

        # Move forward through the token sequence
        for p in range(start, len(tokens)):

            # Try to match a literal token
            for s in self.matchtoken(tokens[p], matchstate[p], 1):
                (j, z) = s
                if j not in matchmap[p+1]:
                    matchmap[p+1][j] = 1
                    matchstate[p+1].append(s)
                else:
                    print >>sys.stderr, "ambiguous pattern: p=%s t=%s" % (
                      repr(self), repr(tokens[start:]) )

            # Try to match a supertoken
            for tok in supertok[p]:
                pp = tok.end
                for s in self.matchtoken(tok, matchstate[p], 0):
                    (j, z) = s
                    if j not in matchmap[pp]:
                        matchmap[pp][j] = 1
                        matchstate[pp].append(s)
                    else:
                        print >>sys.stderr, "ambiguous pattern: p=%s t=%s" % (
                          repr(self), repr(tokens[start:]) )

        # Return complete matches
        if self.forceend:
            p = len(tokens)
            return [ (start, p, z)
                     for (j, z) in matchstate[p] if j == 0 ]
        else:
            return [ (start, p, z)
                     for p in range(start, len(tokens)+1)
                     for (j, z) in matchstate[p] if j == 0 ]

    def matchall(self, tokens, supertok):
        """Match a sequence of (super)tokens against the compiled pattern;
        return a sorted list of all matching (start, end, data) tuples.
        At most one match will be produced for any (start, end) span."""
        if self.forcebegin:
            return self.match(tokens, supertok, 0)
        else:
            matched = [ ]
            for p in range(len(tokens)):
                matched += self.match(tokens, supertok, p)
            return matched

    def matchfull(self, tokens, supertok):
        """Match the entire sequence of (super)tokens against the compiled
        pattern and return the matching (start, end, data) tuple, or
        return None if the match fails."""
        n = len(tokens)
        for s in self.match(tokens, supertok, 0):
            (start, end, data) = s
            assert start == 0
            if end == n:
                return s

    def matchfirst(self, tokens, supertok):
        """Return (start, end, data) for the first match of the compiled
        pattern in the sequence of (super)tokens. If there are multiple first
        matches, return the longest one. Return None if there is no match."""
        if self.forcebegin:
            v = self.match(tokens, supertok, 0)
            if v:
                return v[-1]
        else:
            for p in range(len(tokens)):
                v = self.match(tokens, supertok, p)
                if v:
                    return v[-1]


class Transducer:
    """Yet Another Finite state transduction engine.
    A Transducer instance contains a sequence of tokens and supertokens.
    It provides methods to match the tokens against cascaded regular
    expression patterns."""

    # patterncache is a class-wide shared cache of PatternMatcher objects
    patterndict = { }

    def __init__(self, tokens, supertok=None, resolved=None):
        """Create a transducer for the given sequence of tokens and
        corresponding supertokens."""
        self.tokens = tokens
        if supertok is None:
            self.supertok = [ [ ] for tok in tokens ]
        else:
            self.supertok = supertok
        self.resolved = None
        if resolved is not None:
            self.resolved = dict([ (n, 1) for n in resolved ])

    def resolvedeps(self, deps):
        """Resolve dependencies on subpatterns by recursively applying
        the subpatterns before applying the main pattern."""
        for n in deps:
            t = self.resolved.get(n)
            if t == 0:
                raise ValueError("Cyclic dependency on " + repr(n))
            if t is None:
                self.resolved[n] = 0
                rule = getattr(self, n)
                self.apply(rule)
                self.resolved[n] = 1

    def mkmatcher(self, pattern):
        """Return a PatternMatcher object for the given pattern string."""
        m = self.patterndict.get(pattern)
        if m is None:
            m = PatternMatcher(pattern)
            self.patterndict[pattern] = m
        if self.resolved is not None:
            self.resolvedeps(m.tokenrefs)
        return m

    def apply(self, rule):
        """Apply the given rule to the token sequence and create a new
        supertoken for every successful match.
        The rule is a Python function or bound method; its docstring specifies
        the regular expression pattern, and its name determines the label
        for supertokens induced by this rule.
        The function is invoked for every successful match with the sequence
        of capture buffers as its single argument.
        The function result becomes the value of the new supertoken;
        if the function returns None, no new supertoken is created."""
        name = rule.__name__
        pattern = rule.__doc__
        m = self.mkmatcher(pattern)
        for (start, end, z) in m.matchall(self.tokens, self.supertok):
            v = rule(z)
            if v is not None:
                tok = SuperToken(start=start, end=end, name=name, val=v)
                self.supertok[start].append(tok)
        self.resolved[name] = 1

    def fullmatch(self, rule):
        """Match the given rule to the full token sequence and return
        the resulting value, or return None if the match failed."""
        pattern = rule.__doc__
        m = self.mkmatcher(pattern)
        w = m.matchfull(self.tokens, self.supertok)
        if w:
            (start, end, z) = w
            return rule(z)

    def firstmatch(self, rule):
        """Find the first match of the given rule on the token sequence
        and return the resulting value, or return None if there is no match."""
        pattern = rule.__doc__
        m = self.mkmatcher(pattern)
        w = m.matchfirst(self.tokens, self.supertok)
        if w:
            (start, end, z) = w
            return rule(z)

    def fulltoken(self, name):
        """Return the supertoken with the given name that corresponds to
        the full token sequence; or return None if no such token exists."""
        if self.resolved is not None:
            self.resolvedeps((name,))
        n = len(self.tokens)
        for tok in self.supertok[0]:
            if tok.end == n and tok == name:
                return tok

    def firsttoken(self, name):
        """Return the first supertoken with the given name.
        If there are multiple first matches, take the one that represents
        the longest sequence of primary tokens. Return None if there is
        no matching supertoken."""
        if self.resolved is not None:
            self.resolvedeps((name,))
        n = len(self.tokens)
        w = None
        for p in range(n):
            for tok in self.supertok[p]:
                if tok == name:
                    if w is None or tok.end > w.end:
                        w = tok
            if w:
                return w
 
# End
