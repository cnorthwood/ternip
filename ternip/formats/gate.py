#!/usr/bin/env python

from collections import defaultdict
import copy
import ternip

class gate:
    """
    A class to facilitate communication with GATE
    """
    
    def __init__(self, file):
        """
        Load a document
        """
        
        sents = []
        sent = []
        self.docid = docid
        
        for line in file.splitlines():
            parts = line.split('\t')
            if len(parts) > 1:
                sent.append((parts[0], parts[1], set()))
            else:
                sents.append(sent)
        
        self._sents = sents
    
    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        """
        return copy.deepcopy(self._sents)
    
    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        
        At the moment returns nothing. This needs to be revisted to make
        normalisation more useful, need to identify (perhaps first normalisable
        expression) as a DCT
        """
        return []
    
    def reconcile_dct(self, dct):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        pass
    
    def reconcile(self, sents):
        """
        Update this document with the newly annotated tokens.
        """
        self._sents = copy.deepcopy(sents)
    
    def __str__(self):
        """
        Output format
        """
        open_timexes = set()
        for sent in self._sents:
            for (tok, pos, ts) in sent:
                print tok + "\t",
                mode = 'O'
                for timex in ts:
                    if timex in open_timexes:
                        mode = 'I'
                    else:
                        mode = 'B\t' + self._attrs(timex)
                        break
                print mode