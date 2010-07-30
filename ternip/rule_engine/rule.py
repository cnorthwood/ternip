#!/usr/bin/env python

import re
import expressions

class rule:
    """
    Base class for recognition and normalisation rules
    """
    
    def _replace_predefs(self, match):
        """
        Substitute some special values for their actual RE values. To be
        overriden by child.
        """
        return match
    
    def _prep_re(self, exp):
        """
        Prepare a regular expression which uses <> for token boundaries
        """
        
        exp = self._replace_predefs(exp)
        
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
        
        # Fix for NUM_START/NUM_ORD_START which really wants to match on ., but
        # in a non-greedy way
        exp = re.sub(r'_START\[\^>\]', '_START(.(?!NUM_START))', exp)
        
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
    
    def _do_deliminate_numbers(self, sent):
        """
        Translation of GUTime function 'deliminateNumbers' - marks up number
        sequences
        """
        
        rest = sent
        sent = ''
        previous_word = ''
        current_word = ''
        
        in_number = False
        
        while re.search(r'<[a-zA-Z-]+~.+?>', rest):
            m = re.search(r'<(?P<word>[a-zA-Z-]+)~(?P<pos>.+?)>', rest)
            sent += m.string[:m.start()]
            rest = m.string[m.end():]
            
            current_word = m.group('word')
            
            # Get next word
            n = re.search(r'<(?P<word>[a-zA-Z-]+)~(?P<pos>.+?)>', rest)
            if n != None:
                next_word = n.group('word')
            else:
                next_word = ''
            
            # the following deals reasonably well with hypenated numbers like "twenty-one"
            if re.match(expressions.NUMBER_TERM + '(-' + expressions.NUMBER_TERM + ')*', current_word, re.I) != None:
                # This current word is identified as a number
                if not in_number:
                    # first in (possible) series of numbers
                    to_add = 'NUM_START<' + m.group('word') + '~' + m.group('pos') + '>'
                    in_number = True
                else:
                    # either not first in series, or between ordinal and regular nums (i.e. "first two")
                    if (re.search(expressions.ORD_UNIT_NUMS + r'$', previous_word) != None) or (re.search(expressions.ORD_OTHER_NUMS + r'$', previous_word) != None):
                        # between ordinal and regular
                        sent = re.sub(r'(NUM_START((.(?!NUM_START))*))$', r'NUM_ORD_START\2', sent) # replace with NUM_ORD_START
                        sent += 'NUM_ORD_END'
                        to_add = 'NUM_START<' + m.group('word') + '~' + m.group('pos') + '>'
                    else:
                        # number is continuing
                        to_add = '<' + m.group('word') + '~' + m.group('pos') + '>'
            
            else:
                # current word is not a number
                if in_number:
                    # previous word was a number
                    # following works fairly well...it avoids marking things like "six and two" as a single
                    # number while still marking things like "two hundred and one" as a single number
                    if (current_word.lower() == 'and') and \
                       (re.search(expressions.HIGHER_NUMS, previous_word, re.I) != None) and \
                       ((re.search(expressions.UNIT_NUMS, next_word, re.I) != None) or \
                        (re.search(expressions.UNIQUE_NUMS, next_word, re.I) != None) or \
                        (re.search(expressions.TENS_NUMS+'(-'+expressions.UNIT_NUMS+'|'+expressions.ORD_UNIT_NUMS+')?', next_word, re.I) != None) or \
                        (re.search(expressions.ORD_UNIT_NUMS, next_word, re.I) != None) or \
                        (re.search(expressions.ORD_OTHER_NUMS, next_word, re.I) != None)):
                        to_add = '<' + m.group('word') + '~' + m.group('pos') + '>'
                    else:
                        # number doesn't continue
                        in_number = False
                        if (re.search(expressions.ORD_UNIT_NUMS + r'$', previous_word) != None) or (re.search(expressions.ORD_OTHER_NUMS + r'$', previous_word) != None):
                            sent = re.sub(r'(NUM_START((.(?!NUM_START))*))$', r'NUM_ORD_START\2', sent) # replace with NUM_ORD_START
                            sent += 'NUM_ORD_END'
                        else:
                            sent += 'NUM_END'
                        to_add = '<' + m.group('word') + '~' + m.group('pos') + '>'
                else:
                    to_add = '<' + m.group('word') + '~' + m.group('pos') + '>'
            
            sent += to_add
            previous_word = current_word
        
        if re.match(expressions.NUMBER_TERM + '(-' + expressions.NUMBER_TERM + ')*', current_word, re.I) != None:
            # final word is a number
            sent += 'NUM_END'
        
        sent += rest
        return sent
    
    def _set_timex_extents(self, t, sent, ti, tj, squelch):
        """
        Inserts the timex t in the appropriate points in the sentence sent
        (i.e., between the extents ti, tj). If squelch is set, remove timexes
        between those extents.
        """
        for i in range(len(sent)):
            # now get all tokens in the range and add the new timex if needed
            if i >= ti and i < tj:
                if squelch:
                    # in the case of this being a squelch rule, remove the
                    # timexes
                    sent[i] = (sent[i][0], sent[i][1], set())
                else:
                    # otherwise add the new timex to the list of timexes
                    # associated with this token
                    sent[i][2].add(t)