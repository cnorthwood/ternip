#!/usr/bin/env python

import timex2
import xml.dom.minidom

class tern(timex2.timex2):
    """
    A class which can handle TERN documents
    """
    
    @staticmethod
    def create(sents, docid, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        """
        Creates a TERN document from the internal representation
        
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
        
        # Create a blank XML document
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, 'DOC', None)
        
        # Add necessary tags
        docid_tag = doc.createElement('DOCNO')
        docid_tag.appendChild(doc.createTextNode(docid))
        doc.documentElement.appendChild(docid_tag)
        
        body_tag = doc.createElement('BODY')
        doc.documentElement.appendChild(body_tag)
        
        text_tag = doc.createElement('TEXT')
        body_tag.appendChild(text_tag)
        
        # Add text to document
        tern._add_words_to_node_from_sents(doc, text_tag, sents, tok_offsets)
        
        # Now create the object
        x = tern(doc)
        
        # Now reconcile the S, LEX and TIMEX tags
        x.reconcile(sents, add_S, add_LEX, pos_attr)
        
        return x
    
    def __init__(self, file, nodename='TEXT', has_S=False, has_LEX=False, pos_attr=False):
        timex2.timex2.__init__(self, file, nodename, has_S, has_LEX, pos_attr)
    
    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        """
        
        old_xml_body = self._xml_body
        self._xml_body = self._xml_doc.documentElement.getElementsByTagName('DATE_TIME')[0]
        s = self.get_sents()
        self._xml_body = old_xml_body
        return s
    
    def reconcile_dct(self, dct):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        old_xml_body = self._xml_body
        self._xml_body = self._xml_doc.documentElement.getElementsByTagName('DATE_TIME')[0]
        self.reconcile(dct)
        self._xml_body = old_xml_body