#!/usr/bin/env python

import xml.dom.minidom
from timex3 import timex3

class timeml(timex3):
    """
    A class which holds a TimeML representation of a document.
    
    Suitable for use with the AQUAINT dataset.
    """
    
    @staticmethod
    def create(sents, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        """
        Creates a TimeML document from the internal representation
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        
        tok_offsets is used to correctly reinsert whitespace lost in
        tokenisation. It's in the format of a list of lists of integers, where
        each integer is the offset from the start of the sentence of that token.
        If set to None (the default), then a single space is assumed between
        all tokens.
        
        If add_S is set to something other than false, then the tags to indicate
        sentence boundaries are added, with the name of the tag being the value
        of add_S
        
        add_LEX is similar, but for token boundaries
        
        pos_attr is similar but refers to the name of the attribute on the LEX
        (or whatever) tag that holds the POS tag.
        """
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument('http://www.timeml.org/site/publications/timeMLdocs/timeml_1.2.1.dtd', 'TimeML', None)
        
        # Create a document with just text nodes
        x = xml_doc(xml_doc._add_words_to_node_from_sents(doc, doc.documentElement, sents, tok_offsets), doc.documentElement)
        
        # Now reconcile the S, LEX and TIMEX tags
        x.reconcile(sents, add_S, add_LEX, pos_attr)
        
        return timeml(doc)