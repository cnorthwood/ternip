#!/usr/bin/env python

import xml.dom.minidom

import timex2


class TernDocument(timex2.Timex2XmlDocument):
    """
    A class which can handle TERN documents
    """

    @staticmethod
    def create(sents, docid, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False, dct=''):
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
        
        dct is the document creation time string
        """

        # Create a blank XML document
        impl = xml.dom.minidom.getDOMImplementation()
        doc = impl.createDocument(None, 'DOC', None)

        # Add necessary tags
        docid_tag = doc.createElement('DOCNO')
        docid_tag.appendChild(doc.createTextNode(docid))
        doc.documentElement.appendChild(docid_tag)

        if dct != '':
            dct_tag = doc.createElement('DATE_TIME')
            dct_tag.appendChild(doc.createTextNode(dct[4:6] + '/' + dct[6:8] + '/' + dct[:4]))
            doc.documentElement.appendChild(dct_tag)

        body_tag = doc.createElement('BODY')
        doc.documentElement.appendChild(body_tag)

        text_tag = doc.createElement('TEXT')
        body_tag.appendChild(text_tag)

        # Add text to document
        TernDocument._add_words_to_node_from_sents(doc, text_tag, sents, tok_offsets)

        # Now create the object
        x = TernDocument(doc)

        # Now reconcile the S, LEX and TIMEX tags
        x.reconcile(sents, add_S, add_LEX, pos_attr)

        return x

    def __init__(self, file, nodename='TEXT', has_S=False, has_LEX=False, pos_attr=False):
        timex2.Timex2XmlDocument.__init__(self, file, nodename, has_S, has_LEX, pos_attr)

    def _dct_to_xml_body(self):
        """
        Set the XML body to be the tag containing the document creation time
        """
        dtags = self._xml_doc.documentElement.getElementsByTagName('DATE_TIME')
        if len(dtags) == 1:
            self._xml_body = dtags[0]
        else:
            dtags = self._xml_doc.documentElement.getElementsByTagName('DATE')
            if len(dtags) == 1:
                self._xml_body = dtags[0]
            else:
                return False

    def get_dct_sents(self):
        """
        Returns the creation time sents for this document.
        """
        old_xml_body = self._xml_body
        if self._dct_to_xml_body() is False:
            return [[]]
        s = self.get_sents()
        self._xml_body = old_xml_body
        return s

    def reconcile_dct(self, dct, add_S=False, add_LEX=False, pos_attr=False):
        """
        Adds a TIMEX to the DCT tag and return the DCT
        """
        old_xml_body = self._xml_body
        old_has_S = self._has_S
        old_has_LEX = self._has_LEX
        old_pos_attr = self._pos_attr
        if self._dct_to_xml_body() is False:
            return
            # Set functionInDocument
        for sent in dct:
            for (doc, pos, ts) in sent:
                for t in ts:
                    t.document_role = 'CREATION_TIME'
        self.reconcile(dct, add_S, add_LEX, pos_attr)
        self._xml_body = old_xml_body
        self._has_S = old_has_S
        self._has_LEX = old_has_LEX
        self._pos_attr = old_pos_attr
