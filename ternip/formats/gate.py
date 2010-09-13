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
        dct = None
        
        for line in file.splitlines():
            parts = line.split('\t')
            if dct is None:
                dct = parts[3]
            if parts[2] == 'I':
                sent.append((parts[0], parts[1], set()))
            else:
                if len(sent) > 0:
                    sents.append(sent)
                sent = [(parts[0], parts[1], set())]
        sents.append(sent)
        
        self._sents = sents
        self._dct = dct
    
    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        """
        return copy.deepcopy(self._sents)
    
    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        """
        return [[(self._dct, 'DCT', set())]]
    
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
    
    def _get_attrs(self, timex):
        
        s = ""
        
        if timex.id != None:
            s += "\tid=t"+str(timex.id)
        
        if timex.value != None:
            s += "\tvalue="+timex.value
        
        if timex.type != None:
            s += "\ttype="+timex.type.upper()
        
        if timex.mod != None:
            s += "\tmod="+timex.mod
        
        if timex.freq != None:
            s += "\tfreq="+timex.freq
        
        if timex.quant != None:
            s += "\tquant="+timex.quant
        
        if timex.temporal_function:
            s += "\ttemporalFunction=true"
        
        if timex.document_role != None:
            s += "\tfunctionInDocument="+timex.document_role
        
        if timex.begin_timex != None:
            s += "\tbeginPoint=t"+str(timex.begin_timex.id)
        
        if timex.end_timex != None:
            s += "\tendPoint=t"+str(timex.end_timex.id)
        
        if timex.context != None:
            s += "\tanchorTimeID=t"+str(timex.context.id)
        
        return s
    
    def __str__(self):
        """
        Output format
        """
        s = ''
        open_timexes = set()
        for sent in self._sents:
            for (tok, pos, ts) in sent:
                s += tok + "\t"
                mode = 'O'
                for timex in ts:
                    if timex in open_timexes:
                        mode = 'I'
                    else:
                        mode = 'B' + self._get_attrs(timex)
                        open_timexes.add(timex)
                        break
                s += mode + "\n"
        return s