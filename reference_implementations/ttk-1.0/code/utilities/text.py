"""
Text and string utilities for the Tarsqi Toolkit.

"""

import sgmllib
import HTMLParser

from htmlentitydefs import entitydefs # replace entitydefs from sgmllib


class SgmlFilter(sgmllib.SGMLParser):

    """Strips tags from the input. Allows definition of tags that should
    not be stripped. Also strips html comments. Does not deal well with
    tags like <br/>. This class can be used as follows:
        filter = SgmlFilter()
        filter.feed("string with <b>tags</b>")
        filter.close()
        filter.cleanup()
        return filter.result"""
    
    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'a', 'i', 'br', 'p')
    valid_tags = ()
    
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:       
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if k[0:2].lower() != 'on' and v[0:10].lower() != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)    
            self.result = self.result + '>'
                
    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]    




class HtmlFilter(HTMLParser.HTMLParser):
    
    """ Strip tags fron the input. Can deal with things like <br/>, but
    does not remove all HTML comments , eg the ones inside a style
    tag). Also does not allow exceptions. Is used as follows:
    
        filter = HtmlFilter()
        filter.feed("string with <b>tags</b>")
        filter.close()
        filter.cleanup()
        return filter.result"""    

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def cleanup(self):
        pass
        

def strip_tags(s, filter_class=HtmlFilter):
    """ Strip HTML tags from string s."""
    filter = filter_class()
    filter.feed(s)
    filter.close()
    filter.cleanup()
    return filter.result



if __name__ == '__main__':

    example_string = \
        """
        <head>Do we strip?</head>
        What about <complex tag=1> tags</complex> and what about things like <br/><br/>.
        And <b>what</b> about comments
        <style>
        <!--
        
        yadayada
        -->
        </style>
        And stray tags like </oops>?
        """

    print "\n== Stripping using HtmlFilter:\n"
    print strip_tags(example_string)
    print "\n== Stripping using SgmlFilter:\n"
    print strip_tags(example_string, SgmlFilter)

