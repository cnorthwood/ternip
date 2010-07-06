#!/usr/bin/env python

import nltk
import xml.dom.minidom

class xml_doc:
    """
    An abstract base class which all XML types can inherit from. This implements
    almost everything, apart from the conversion of timex objects to and from
    timex tags in the XML. This is done by child classes 
    """
    
    @staticmethod
    def _add_words_to_node_from_sents(doc, node, sents, tok_offsets=None):
        """
        Uses the given node and adds an XML form of sents to it. The node
        passed in should have no children (be an empty element)
        """
        
        # Just add text here, then leave it up to reconcile to add all other
        # tags
        
        for i in len(sents):
            
            for j in len(sent):
                (tok, pos, ts) = sents[i][j]
                
                # Do we know what token offsets are in order to reinstate them?
                if tok_offsets is not None:
                    # Add whitespace between tokens if needed
                    while s_offset < tok_offsets[i][j]:
                        s_tag.appendChild(doc.createTextNode(' '))
                        s_offset += 1
                
                # Add the text
                s_tag.appendChild(doc.createTextNode(tok))
                
                # If we're not using token offsets, assume a single space is
                # what's used
                if tok_offsets is None:
                    s_tag.appendChild(doc.createTextNode(' '))
                else:
                    # Increase our current sentence offset
                    s_offset += len(tok)
        
        node.normalize()
    
    @staticmethod
    def create(sents, tok_offsets=None, add_S=False, add_LEX=False, pos_attr=False):
        """
        Override this to build a document from internal representation only.
        The output this produces is pretty generic, as can be expected at this
        high level. The root node is called 'root' and no DTD is used.
        
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
        doc = impl.createDocument(None, 'root', None)
        
        xml_doc._add_words_to_node_from_sents(doc, doc.documentElement, sents, tok_offsets)
        
        # Now reconcile
        
        return xml_doc(doc)
    
    def __init__(self, file, nodename=None, has_S=False, has_LEX=False, pos_attr=False):
        """
        Passes in an XML document (as one consecutive string) which is used
        as the basis for this object.
        
        Alternatively, you can pass in an xml.dom.Document class which means
        that it's not parsed. This is used by the static create function.
        
        Node name is the name of the "body" of this document to be considered.
        If set to None (it's default), then the root node is considered to be
        the document body.
        
        has_S means that the document uses XML tags to mark sentence boundaries.
        This defaults to False, but if your XML document does, you should set it
        to the name of your sentence boundary tag (normally 'S').
        
        has_LEX is similar to has_S, but for token boundaries. Again, set this
        to your tag for token boundaries (not as common, but sometimes it's
        'lex')
        
        pos_attr is the name of the attribute on your LEX (or whatever) tags
        that indicates the POS tag for that token.
        
        The tagger needs tokenised sentences and tokenised and POS tagged tokens
        in order to be able to tag. If the input does not supply this data, the
        NLTK is used to fill the blanks.
        """
        
        if isinstance(file, xml.dom.minidom.Document):
            self._xml_doc = file
        else:
            self._xml_doc = xml.dom.minidom.parseString(file)
        
        if nodename is None:
            self._xml_body = self._xml_doc.documentElement
        else:
            tags = self._xml_doc.getElementsByTagName(nodename)
            if len(tags) != 1:
                raise bad_node_name_error()
            self._xml_body = tags[0]
    
    def reconcile(self, sents, add_S = False, add_LEX = False, pos_attr=False):
        """
        Reconciles this document against the new internal representation. If
        add_S is set to anything other than False, this means tags are indicated
        to indicate the sentence boundaries, with the tag names being the value
        of add_S. add_LEX is the same, but for marking token boundaries, and
        pos_attr is the name of the attribute which holds the POS tag for that
        token. This is mainly useful for transforming the TERN documents into
        something that GUTime can parse.
        
        If your document already contains S and LEX tags
        """
        raise NotImplementedError
    
    def _strip_tags(self, doc, tagname, node):
        """
        Recursively remove a tag from this node
        """
        
        # Recursive step - depth-first search
        for child in node.childNodes:
            
            # Get the list of nodes which replace this one (if any)
            rep = self._strip_tags(doc, tagname, child)
            
            if len(rep) == 1:
                # If it's a single node that's taking the place of this one (e.g.,
                # if there was no change, or a timex tag that only had some text
                # inside it), but only if the node's changed
                if rep[0] is not child:
                    node.replaceChild(rep[0], child)
            else:
                # There were multiple child nodes, need to insert all of them
                # where in the same location, in order, where their parent
                # node was. Unfortunately replaceChild can't do replacement
                # of a node with multiple nodes.
                before = child.nextSibling
                node.removeChild(child)
                for new_node in rep:
                    node.insertBefore(new_node, before)
                node.normalize()
        
        # Base step
        if node.nodeType == node.ELEMENT_NODE and node.tagName == tagname:
            return [child for child in node.childNodes]
        else:
            return [node]
    
    def strip_timexes(self):
        """
        Strips all timexes from this document. Useful if we're evaluating the
        software - we can just feed in the gold standard directly and compare
        the output then.
        """
        raise NotImplementedError
    
    def get_sents(self):
        """
        Returns a representation of this document in the
        [[(word, pos, timexes), ...], ...] format.
        """
        raise NotImplementedError
    
    def __str__(self):
        """
        String representation of this document
        """
        return self._xml_doc.toxml()

class bad_node_name_error(Exception):
        
    def __str__(self):
        return "The specified tag name does not exist exactly once in the document"