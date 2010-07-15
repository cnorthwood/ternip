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
        
        if node.hasAttribute('PERIODICITY'):
            t.freq = node.getAttribute('PERIODICITY')[1:]
        
        if node.hasAttribute('GRANUALITY'):
            t.granuality = node.getAttribute('GRANUALITY')[1:]
        
        if node.hasAttribute('COMMENT'):
            t.comment = node.getAttribute('COMMENT')
        
        if node.hasAttribute('NON_SPECIFIC'):
            if node.getAttribute('NON_SPECIFIC').lower() == 'yes':
                t.non_specific = True
        
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
            node.setAttribute('PERIODICITY', 'F' + timex.freq)
        
        if timex.granuality != None:
            node.setAttribute('GRANUALITY', 'G' + timex.granuality)
        
        if timex.comment != None:
            node.setAttribute('COMMENT', timex.comment)
        
        if timex.non_specific:
            node.setAttribute('NON_SPECIFIC', 'YES')