#!/usr/bin/env python

import xml_doc

class timex3(xml_doc.xml_doc):
    """
    A class which takes any random XML document and adds TIMEX3 tags to it.
    
    Suitable for use with Timebank
    """
    
    def strip_timexes(self):
        self._strip_tags(self._xml_doc, 'TIMEX3', self._xml_body)