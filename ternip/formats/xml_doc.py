#!/usr/bin/env python

import xml.dom.minidom

class xml_doc:
    """
    An abstract base class which all XML types can inherit from.
    
    This class and the generic timex2 and timex3 child classes can not be
    created from internal data only as the representations are fairly generic.
    A more concrete standard is needed, e.g., TimeML.
    """
    
    @staticmethod
    def create(sents):
        """
        Override this to build a document from internal representation only.
        
        sents is the [[(word, pos, timexes), ...], ...] format.
        """
        raise NotImplementedError
    
    def __init__(self, file, nodename=None):
        """
        Passes in an XML document (as one consecutive string) which is used
        as the basis for this object.
        
        Alternatively, you can pass in an xml.dom.Document class which means
        that it's not parsed. This is used by the static create function.
        
        Node name is the name of the "body" of this document to be considered.
        If set to None (it's default), then the root node is considered to be
        the document body
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
    
    def reconcile(self, sents, add_S = False, add_LEX = False):
        """
        Reconciles this document against the new internal representation. If
        add_S is set to True, this means add S tags to indicate the sentence
        boundaries. If add_LEX is set to true, this means LEX tags are also
        added which contain the POS attribute. This is mainly useful for
        transforming the TERN documents into something that GUTime can parse.
        """
        raise NotImplementedError
    
    def _strip_timexes(self, doc, node):
        """
        Recursively remove TIMEX tags from this node
        """
        
        # Recursive step - depth-first search
        for child in node.childNodes:
            
            # Get the list of nodes which replace this one (if any)
            rep = self._strip_timexes(doc, child)
            
            # If it's a single node that's taking the place of this one (e.g.,
            # if there was no change, or a timex tag that only had some text
            # inside it)
            if len(rep) == 1:
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
        if node.nodeType == node.ELEMENT_NODE and node.tagName == self._timex_tag_name:
            return [child for child in node.childNodes]
        else:
            return [node]
    
    def strip_timexes(self):
        """
        Strips all timexes from this document. Useful if we're evaluating the
        software - we can just feed in the gold standard directly and compare
        the output then.
        """
        self._strip_timexes(self._xml_doc, self._xml_body)
    
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