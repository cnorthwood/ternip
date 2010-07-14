#!/usr/bin/env python

import xml_doc

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
        return node