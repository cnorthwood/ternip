#!/usr/bin/env python

import xml.dom.minidom
from timex3 import timex3

class timeml(timex3):
    """
    A class which holds a TimeML representation of a document.
    """
    
    @staticmethod
    def create(sents, tok_offsets = None, add_S = False, output_pos=False):
        """
        Returns a TimeML object which is a representation of this in internal
        form.
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        
        tok_offsets is used to correctly reinsert whitespace lost in
        tokenisation. It's in the format of a list of lists of integers, where
        each integer is the offset from the start of the sentence of that token.
        If set to None (the default), then a single space is assumed between
        all tokens.
        
        The following two attributes if set to True mean that a non-compliant
        TimeML document is generated. But <s> tags in particular appear to be
        very popular.
        
        add_S means that sentence boundaries are indicated by the <s> tag
        
        output_pos indicates whether or not 'lex' tags with POS attributes
        should be used to indicate the token boundaries
        """
        
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument('http://www.timeml.org/site/publications/timeMLdocs/timeml_1.2.1.dtd', 'TimeML', None)
        
        for i in len(sents):
            # Now <s> tags for each tag
            if add_S:
                s_tag = doc.createElement('s')
            else:
                s_tag = doc.documentElement
            s_offset = 0
            
            for j in len(sent):
                (tok, pos, ts) = sents[i][j]
                
                # Do we know what token offsets are in order to reinstate them?
                if tok_offsets is not None:
                    # Add whitespace between tokens if needed
                    while s_offset < tok_offsets[i][j]:
                        s_tag.appendChild(doc.createTextNode(' '))
                        s_offset += 1
                
                # Now add each token, inside a lex tag if need be
                if output_pos:
                    lex_tag = doc.createElement('lex')
                    lex_tag.setAttribute('pos', pos)
                    s_tag.appendChild(lex_tag)
                else:
                    s_tag.appendChild(doc.createTextNode(tok))
                
                # If we're not using token offsets, assume a single space is
                # what's used
                if tok_offsets is None:
                    s_tag.appendChild(doc.createTextNode(' '))
                else:
                    # Increase our current sentence offset
                    s_offset += len(tok)
            
            if add_S:
                s_tag.normalize()
                doc.documentElement.appendChild(s_tag)
        
        if not add_S:
            doc.documentElement.normalize()
        
        return timeml(doc)