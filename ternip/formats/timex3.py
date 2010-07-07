#!/usr/bin/env python

import xml_doc

class timex3(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX3 tags to it.
    
    Suitable for use with Timebank
    """
    
    _timex_tag_name = 'TIMEX3'