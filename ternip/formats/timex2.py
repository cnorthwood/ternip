#!/usr/bin/env python

import xml_doc
import ternip

class timex2(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX2 tags to it.
    """
    
    _timex_tag_name = 'TIMEX2'
    
    def _timex_from_node(self, node):
        """
        Given a TIMEX2 node, create a timex object with the values of that node
        """
        t = ternip.timex()
        
        if node.hasAttribute('SET'):
            if node.getAttribute('SET').lower() == 'yes':
                t.type = 'set'
        
        if node.hasAttribute('VAL'):
            t.value = node.getAttribute('VAL')
        
        if node.hasAttribute('MOD'):
            t.mod = node.getAttribute('MOD')
        
        if node.hasAttribute('GRANUALITY'):
            t.freq = node.getAttribute('GRANUALITY')[1:]
        
        if node.hasAttribute('COMMENT'):
            t.comment = node.getAttribute('COMMENT')
        
        return t
    
    def _annotate_node_from_timex(self, timex, node):
        """
        Add attributes to this TIMEX2 node
        """
        
        if timex.value != None:
            node.setAttribute('VAL', timex.value)
        
        if timex.mod != None:
            node.setAttribute('MOD', timex.mod)
        
        if timex.type != None:
            if timex.type.lower() == 'set':
                node.setAttribute('SET', 'YES')
        
        if timex.freq != None:
            node.setAttribute('GRANUALITY', 'G' + timex.freq)
        
        if timex.comment != None:
            node.setAttribute('COMMENT', timex.comment)