#!/usr/bin/env python

import re

class rule:
    """
    Base class for recognition and normalisation rules
    """
    
    def _prep_re(self, exp):
        """
        Prepare a regular expression which uses <> for token boundaries
        """
        # This code is modified from NLTK's text.py for dealing with pattern
        # matching with tokenised strings, under the Apache License 2.0
        
        # Natural Language Toolkit (NLTK) http://www.nltk.org/
        # Copyright (C) 2001-2010 NLTK Project
        # Bird, Steven, Edward Loper and Ewan Klein (2009).
        # Natural Language Processing with Python.  O'Reilly Media Inc.
        
        exp = re.sub(r'\s', '', exp)
        exp = re.sub(r'<', '(?:<(?:', exp)
        exp = re.sub(r'>', ')>)', exp)
        exp = re.sub(r'(?<!\\)\.', '[^>]', exp)
        
        # End NLTK contribution
        
        return exp
    
    def _toks_to_str(self, toks):
        """
        Takes a list of (token, pos_tag, timexes) and converts it into the
        <token~pos> format for matching
        """
        
        # This code is modified from NLTK's text.py for dealing with pattern
        # matching with tokenised strings, under the Apache License 2.0
        
        # Natural Language Toolkit (NLTK) http://www.nltk.org/
        # Copyright (C) 2001-2010 NLTK Project
        # Bird, Steven, Edward Loper and Ewan Klein (2009).
        # Natural Language Processing with Python.  O'Reilly Media Inc.
        
        return ''.join('<'+w+'~'+pos+'>' for (w, pos, ts) in toks)
        
        # End NLTK contribution
    
    def _load_guards(self, guards):
        """
        Given a list of regexs, return a tuple of REs representing positive and
        negative guards.
        """
        pos = []
        neg = []
        
        for guard in guards:
            if guard[0] == '!':
                neg.append(re.compile(self._prep_re(guard[1:]), re.IGNORECASE))
            else:
                pos.append(re.compile(self._prep_re(guard), re.IGNORECASE))
        
        return (pos, neg)
    
    def _check_guards(self, to_check, (pos, neg)):
        """
        Given some text to check, and a tuple of positive and negative rules,
        check whether that text satisfies those guards
        """
        
        # first check positive rules
        for guard in pos:
            if not guard.search(to_check):
                return False
        
        # then negative rules
        for guard in neg:
            if guard.search(to_check):
                return False
        
        return True