#!/usr/bin/env python

import xml.dom
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
        
        if isinstance(file, xml.dom.Document):
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
    
    def reconcile(self, sents):
        """
        Reconciles this document against the new internal representation
        (basically, add timexes)
        """
        raise NotImplementedError
    
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