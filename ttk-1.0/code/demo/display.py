"""

Module that is responsible for creating the HTML files used when the
Toolkit GUI presents the results of a parse. Use this module by
creating a generator on an input file and asking it to create various
output files:

    from demo.display import HtmlGenerator
    generator = HtmlGenerator('data/tmp/in1.cla.xml')
    generator.create_file('out.bli.html', [BLINKER])
    generator.create_file('out.all.html', [S2T, BLINKER, CLASSIFIER])

The second line creates a generator on the file
data/tml/in1.cla.xml. In the third line an output file is created with all
sentences grouped with links from blinker

In addition, the generator can create a couple of html tables with
events, timexes and tlinks:
    
    generator.create_events_table('out.events.html')
    generator.create_timexes_table('out.timexes.html')
    generator.create_links_table('out.links.html')
    
"""

from ttk_path import TTK_ROOT
from docmodel.xml_parser import Parser
from library.tarsqi_constants import BLINKER, SLINKET, S2T, CLASSIFIER


class HtmlGenerator:

    """An HtmlGenerator is created for an XML file with TimeML tags. It is
    used to create HTML files that display the text with events and
    times highlighted and links lined up with the sentences. It can
    also be used to create tables for events, times and links.

    Instance variables:
       file_name - an absolute path
       xmldoc - an XmlDocument
       sentences - a list
       instances - a mapping from eiid and eid to XmlDocElements that contain an instance
       links - a mapping from eids and tids to links that contain them"""

    def __init__(self, file_name):
        self.file_name = file_name
        file = open(file_name,'r')
        self.xmldoc = Parser().parse_file(file)
        self.sentences = []
        self.instance_idx = {}
        self.event_idx = {}
        self.timex_idx = {}
        self.events = []
        self.timexes = []
        self.links = {}
        self._init_sentence_list()
        self._init_indexes()
        self._init_events_list()
        self._init_timexes_list()
        self._init_link_index()

    def _init_sentence_list(self):
        """Fill in the self.sentences list. Sentences do not include their
        opening and closing tags."""
        for open_s_tag in self.xmldoc.get_tags('s'):
            close_s_tag = open_s_tag.get_closing_tag()
            elements = open_s_tag.get_slice_till(close_s_tag.id)
            self.sentences.append(Sentence(elements))

    def _init_events_list(self):
        for event in self.xmldoc.get_tags('EVENT'):
            eid = event.attrs['eid']
            instance = self.instance_idx[eid]
            self.events.append(Event(event, instance))
            
    def _init_timexes_list(self):
        self.timexes = self.xmldoc.get_tags('TIMEX3')
            
    def _init_indexes(self):
        """The value for these indixes are always XML elements."""
        for instance in self.xmldoc.get_tags('MAKEINSTANCE'):
            eiid = instance.attrs.get('eiid')
            eid = instance.attrs.get('eventID')
            self.instance_idx[eiid] = instance
            self.instance_idx[eid] = instance
        for event in self.xmldoc.get_tags('EVENT'):
            eid = event.attrs.get('eid')
            self.event_idx[eid] = event
        for timex in self.xmldoc.get_tags('TIMEX3'):
            tid = timex.attrs.get('tid')
            self.timex_idx[tid] = timex

    def _init_link_index(self):
        link_elements = \
            self.xmldoc.get_tags('ALINK') + \
            self.xmldoc.get_tags('SLINK') + \
            self.xmldoc.get_tags('TLINK')
        for link_element in link_elements:
            link = Link(link_element, self.instance_idx)
            id = link.get_id(['eventInstanceID', 'timeID'])
            try:
                self.links[id].append(link)
            except KeyError:
                self.links[id] = [link]
                
    def create_file(self, outfile, creators):
        """Creates a file with all sentences and the links lined up with the
        sentences."""
        fh = open(outfile, 'w')
        fh.write(
            "<html>\n<head><style>\n" + 
            "s {display: block; text-decoration: none}\n" +
            "</style>\n<body>\n" +
            "<table cellpadding=4" +
            "<tr>\n  <td>source\n  <td>%s\n" % self.file_name +
            "<tr>\n  <td>components\n  <td>%s\n" % ' + '.join(creators) +
            "</table>\n\n" +
            "<hr>\n\n" +
            "<table cellspacing=7pt>\n" )
        for sentence in self.sentences:
            fh.write("\n<tr>\n  <td>")
            sentence.print_html(fh)
            fh.write("  <td>")
            for id in sentence.get_ids():
                links = self.links.get(id,[])
                for link in links:
                    if link.creator in creators:
                        fh.write('   ' + link.convert() + "<br/>\n")
        fh.write("\n</table>\n</body>\n</html>\n")
        
    def create_events_table(self, file):
        fh = open(file,'w')
        fh.write("<html>\n<body>\n<table cellpadding=4>\n" +
                 "<tr align=\"left\">\n" +
                 "  <th bgcolor=\"#dddddd\">event\n" +
                 "  <th bgcolor=\"#dddddd\">pos\n" +
                 "  <th bgcolor=\"#dddddd\">class\n" +
                 "  <th bgcolor=\"#dddddd\">tense\n" +
                 "  <th bgcolor=\"#dddddd\">aspect\n" +
                 "  <th bgcolor=\"#dddddd\">polarity\n" +
                 "  <th bgcolor=\"#dddddd\">modality\n" +
                 "</tr>\n")
        celltag = '<td bgcolor="#dddddd">'
        for event in self.events:
            fh.write("<tr>\n")
            eid = event.attrs['eid']
            text = event.attrs['text']
            pos = event.attrs['pos'].lower()
            eclass = event.attrs['class'].lower()
            tense = event.attrs['tense'].lower()
            aspect = event.attrs['aspect'].lower()
            polarity = event.attrs['polarity'].lower()
            modality = event.attrs.get('modality', '').lower()
            if tense == 'none': tense = ''
            if aspect == 'none': aspect = ''
            if polarity == 'pos': polarity = ''
            if aspect == 'perfective_progressive': aspect = 'perf_prog'
            fh.write("  %s<font color=red>%s_%s</font>\n" % (celltag, text, eid))
            fh.write("  %s%s\n" % (celltag, pos))
            fh.write("  %s%s\n" % (celltag, eclass))
            fh.write("  %s%s\n" % (celltag, tense))
            fh.write("  %s%s\n" % (celltag, aspect))
            fh.write("  %s%s\n" % (celltag, polarity))
            fh.write("  %s%s\n" % (celltag, modality))
        fh.write("</table>\n</body>\n<html>\n")

    def create_timexes_table(self, file):
        fh = open(file,'w')
        fh.write("<html>\n<body>\n<table cellpadding=4>\n" +
                 "<tr align=\"left\">\n" +
                 "  <th bgcolor=\"#dddddd\">timex\n" +
                 "  <th bgcolor=\"#dddddd\">type\n" +
                 "  <th bgcolor=\"#dddddd\">value\n" +
                 "</tr>\n")
        celltag = '<td bgcolor="#dddddd">'
        for timex in self.timexes:
            fh.write("<tr>\n")
            tid = timex.attrs['tid']
            text = timex.collect_content()
            type = timex.attrs['TYPE'].lower()
            value = timex.attrs.get('VAL')
            fh.write("  %s<font color=blue>%s_%s</font>\n" % (celltag, text, tid))
            fh.write("  %s%s\n" % (celltag, type))
            fh.write("  %s%s\n" % (celltag, str(value)))
        fh.write("</table>\n</body>\n<html>\n")

    def create_links_table(self, file):
        fh = open(file,'w')
        fh.write("<html>\n<body>\n<table cellpadding=4>\n")
        celltag = '<td bgcolor="#dddddd">'
        for sentence in self.sentences:
            for id in sentence.get_ids():
                for link in self.links.get(id,[]):
                    id1 = link.get_id1()
                    id2 = link.get_id2()
                    text1 = self._get_text(id1)
                    text2 = self._get_text(id2)
                    full_text1 = color_text(text1, id1)
                    full_text2 = color_text(text2, id2)
                    origin = link.attrs.get('origin')
                    if not origin:
                        origin = link.attrs.get('syntax')
                    fh.write("<tr>\n")
                    fh.write("  %s%s\n" % (celltag, full_text1))
                    fh.write("  %s%s\n" % (celltag, link.attrs['relType']))
                    fh.write("  %s%s\n" % (celltag, full_text2))
                    fh.write("  %s%s\n" % (celltag, origin))
                    fh.write("</tr>\n")
        fh.write("</table>\n</body>\n<html>\n")

    def _get_text(self, id):
        if id.startswith('t'):
            timex = self.timex_idx[id]
            return timex.collect_content()
        if id.startswith('e'):
            instance = self.instance_idx[id]
            eid = instance.attrs['eventID']
            event = self.event_idx[eid]
            return event.collect_content()
        


        
class Sentence:
    
    """A Sentence is a list of XmlDocElements."""

    def __init__(self, elements):
        self.elements = elements

    def get_ids(self):
        ids = []
        for element in self.elements:
            if element.is_opening_tag():
                if element.tag == 'EVENT':
                    ids.append(element.attrs['eid'])
                elif element.tag == 'TIMEX3':
                    ids.append(element.attrs['tid'])
        return ids
    
    def print_html(self, file):
        for element in self.elements:
            if element.is_opening_tag():
                if element.tag == 'EVENT':
                    file.write('<font color="#ff0000">')
                    saved_id = element.attrs['eid']
                elif element.tag == 'TIMEX3':
                    file.write('<font color="#0000ff">')
                    saved_id = element.attrs['tid']
            elif element.is_closing_tag():
                if element.tag in ('EVENT', 'TIMEX3'):
                    file.write('</font>')
                    file.write("_%s" % saved_id)
            else:
                file.write(element.content)


class Event:

    def __init__(self, event, instance):
        
        self.event = event
        self.instance = instance
        self.attrs = event.attrs
        self.attrs.update(instance.attrs)
        self.attrs['text'] = event.collect_content()

        
class Link:

    def __init__(self, xmlelement, instances):
        self.xmlelement = xmlelement
        self.instances = instances
        self.creator = self.set_creator()
        self.attrs = xmlelement.attrs
        
    def set_creator(self):
        attrs = self.xmlelement.attrs
        if attrs.get('origin','').startswith('Blinker'):
            return BLINKER
        elif attrs.get('origin','').startswith('CLASSIFIER'):
            return CLASSIFIER
        elif attrs.get('origin','').startswith('S2T'):
            return S2T
        elif attrs.get('syntax',''):
            return SLINKET
        else:
            return 'UNKNOWN'

    def get_id1(self):
        return self.get_id(['eventInstanceID', 'timeID'])

    def get_id2(self):
        return self.get_id(['relatedToEventInstance', 'subordinatedEventInstance', 'relatedToTime'])
                            
    def get_id(self, attrs):
        id = None
        for attr in attrs:
            id = self.attrs.get(attr)
            if id:
                break
        if id.startswith('ei'):
            id = self.instances[id].attrs['eventID']
        return id

    def convert(self):
        id1 = self.get_id(['eventInstanceID', 'timeID'])
        id2 = self.get_id(['relatedToEventInstance',
                           'subordinatedEventInstance', 'relatedToTime'])
        rel = self.attrs['relType'].lower()
        id1 = color_id(id1)
        id2 = color_id(id2)
        return "%s(%s,%s)" % (rel, id1, id2)

    
def color_id(id):
    if id.startswith('e'):
        return '<font color="#ff0000">' + id + '</font>'
    elif id.startswith('t'):
        return '<font color="#0000ff">' + id + '</font>'
    else:
        return id

def color_text(text, id):
    if id.startswith('e'):
        return '<font color="#ff0000">' + text + '_' + id + '</font>'
    elif id.startswith('t'):
        return '<font color="#0000ff">' + text + '_' + id + '</font>'
    else:
        return id

    

if __name__ == '__main__':
    generator = HtmlGenerator('data/tmp/in1.cla.xml')
    generator.create_file('out.s2t.html', [SLINKET, S2T])
    generator.create_file('out.bli.html', [BLINKER])
    generator.create_file('out.cla.html', [CLASSIFIER])
    generator.create_file('out.all.html', [S2T, BLINKER, CLASSIFIER])
    generator = HtmlGenerator('data/tmp/in1.mer.xml')
    generator.create_file('out.mer.html', [S2T, BLINKER, CLASSIFIER])
    generator.create_events_table('out.events.html')
    generator.create_timexes_table('out.timexes.html')
    generator.create_links_table('out.links.html')
