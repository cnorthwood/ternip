#!/usr/bin/env python

import xml_doc

class timex2(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX2 tags to it.
    
    Appears to work fine with the TERN data, even though that's technically SGML
    """
    
    _timex_tag_name = 'TIMEX2'