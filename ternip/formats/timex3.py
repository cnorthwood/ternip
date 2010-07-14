#!/usr/bin/env python

# Attribute     TIMEX2      TIMEX3
#---------------------------------
# ID            None        X tid ('t' + ID)
# value         val         value
# mod           mod         mod
# type          set         X type
#               (only if type=set)
# freq          periodicity freq
#               ('f' + freq)
# quant         None        quant
# granuality    granuality  None
# comment       comment     comment
# non_specific  non_specific None
# temporal_function None    temporalFunction
# role          None        functionInDocument
# begin_timex   None        beginPoint (ID of begin_timex)
# end_timex     None        endPoint (ID of end_timex)
# context       None        anchorTimeID (ID of context)

import xml_doc
import ternip

class timex3(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX3 tags to it.
    
    Suitable for use with Timebank, which contains many superfluous tags that
    aren't in the TimeML spec, even though it claims to be TimeML.
    """
    
    _timex_tag_name = 'TIMEX3'
    
    def _timex_from_node(self, node):
        return ternip.timex()
    
    def _annotate_node_from_timex(self, timex, node):
        """
        Add attributes to this TIMEX3 node
        """
        
        if timex.id != None:
            node.setAttribute('tid', 't' + str(timex.id))
        
        if timex.value != None:
            node.setAttribute('value', timex.value)
        
        if timex.mod != None:
            node.setAttribute('mod', timex.mod)
        
        if timex.type != None:
            node.setAttribute('type', timex.type.upper())
        
        if timex.freq != None:
            node.setAttribute('freq', timex.freq)
        
        if timex.comment != None:
            node.setAttribute('comment', timex.comment)
        
        if timex.quant != None:
            node.setAttribute('quant', timex.quant)
        
        if timex.temporal_function:
            node.setAttribute('temporalFunction', 'true')
        
        if timex.document_role != None:
            node.setAttribute('functionInDocument', timex.document_role)
        
        if timex.begin_timex != None:
            node.setAttribute('beginPoint', 't' + str(timex.begin_timex.id))
        
        if timex.end_timex != None:
            node.setAttribute('endPoint', 't' + str(timex.end_timex.id))
        
        if timex.context != None:
            node.setAttribute('anchorTimeID', 't' + str(timex.context.id))