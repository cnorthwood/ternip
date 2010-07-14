#!/usr/bin/env python

import xml_doc


# Attribute     TIMEX2      TIMEX3
#---------------------------------
# granuality    granuality  None
# comment       comment     comment
# non_specific  non_specific None



class timex2(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX2 tags to it.
    
    Appears to work fine with the TERN data, even though that's technically SGML
    """
    
    _timex_tag_name = 'TIMEX2'
    
    def _timex_from_node(self, node):
        t = ternip.timex()
        return t
    
    def _annotate_node_from_timex(self, timex, node):
        """
        Add attributes to this TIMEX node
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