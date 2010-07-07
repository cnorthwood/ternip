#!/usr/bin/env python

import xml_doc

class timex2(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX2 tags to it.
    
    Appears to work fine with the TERN data, even though that's technically SGML
    """
    
    def strip_timexes(self):
        self._strip_tags(self._xml_doc, 'TIMEX2', self._xml_body)