from xml.parsers.expat import ExpatError

import logger

from docmodel.xml_parser import Parser
from docmodel.xml_parser import XmlDocElement


def merge_tags(infile1, infile2, merged_file):

    """Merge the tags from infile1, which has all tags from the input,
    with tags from infile2, which has only s, lex and TIMEX3 tags. The
    lex tags are used as the pivots and it is assumed that both files
    contain the same amount of lex tags."""

    # create the document objects and add lex_id values to the lex tags
    doc1 = Parser().parse_file(open(infile1,"r"))
    doc2 = Parser().parse_file(open(infile2,"r"))
    _mark_lex_tags(doc1)
    _mark_lex_tags(doc2)

    # get the timexes and embedded lex tags from infile2, and create
    # index of the lex tags of infile1 using lex_id
    extended_timexes = _get_timextags_with_contained_lextags(doc2)
    lexid_to_lextag = _create_lexid_index(doc1)
    

    for extended_timex in extended_timexes:

        # get first and last document element of infile1
        timex_tag = extended_timex[0]
        first_lex = extended_timex[1][0]
        last_lex = extended_timex[1][-1]
        first_element = lexid_to_lextag[first_lex]
        last_element = lexid_to_lextag[last_lex].get_closing_tag()

        # get the entire sequence that is to be embedded in the timex tag
        sequence = first_element.get_slice_till(last_element.id)
        sequence_string = ''
        for el in sequence:
            sequence_string = "%s%s" % (sequence_string, el.content)
        
        # check whether this sequence, when embedded in a tag, results
        # in well-formed XML, if so, add the new timex tag to infile1,
        # otherwise, ignore and print warning
        try:
            Parser().parse_string("<TAG>%s</TAG>" % sequence_string)
            # insert opening and closing timex tags
            first_element.insert_element_before(timex_tag)
            last_element.insert_element_after(XmlDocElement('</TIMEX3>', 'TIMEX3'))
        except ExpatError:
            logger.warn("Could not wrap TIMEX3 tag around\n\t %s" % sequence_string)

    # save the Document object of infile1 as the resulting merged file
    doc1.save_to_file(merged_file)

        
def _mark_lex_tags(doc):
    """Add a unique id to each lex tag."""
    lex_id = 0
    for element in doc:
        if element.is_opening_tag() and element.tag == 'lex':
            lex_id = lex_id + 1
            element.lex_id = lex_id


def _get_timextags_with_contained_lextags(doc):
    """Get all TIMEX3 tags, and associated them with the lex tags that are
    included in them."""
    timextags_with_lextags = []
    for timextag in doc.tags.get('TIMEX3',[]):
        lex_elements = []
        timex_elements = timextag.collect_contained_tags()
        for timex_element in timex_elements:
            if timex_element.tag == 'lex':
                lex_elements.append(timex_element.lex_id)
        timextags_with_lextags.append([timextag, lex_elements])
    return timextags_with_lextags


def _create_lexid_index(doc):
    index = {}
    for element in doc:
        if element.is_opening_tag() and element.tag == 'lex':
            id = element.lex_id
            index[id] = element
    return index
