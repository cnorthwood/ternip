"""Document model and meta data parser

This module contains classes that implement the document model and the
meta data parser. Document model and meta data parser are responsible
for dealing with the document-specific aspects of a text, including
location of fragments that need to be processed and meta data like the
document creation time. The document model contains the code to read a
document, typically using an XML parser.

Local variables:

   COMPONENTS

      An ordered list of all Tarsqi components
      
   DSI_DEFAULTS

      Dictionary with all defaults for each declared data source
      identifier. Now only used by the gui, should be used by the
      initializer as well.

"""

import os
import re
import time

from docmodel.xml_parser import Parser

from library.tarsqi_constants import PREPROCESSOR, GUTIME, EVITA, SLINKET
from library.tarsqi_constants import S2T, CLASSIFIER, BLINKER, LINK_MERGER

from utilities import logger


COMPONENTS = [ PREPROCESSOR, GUTIME, EVITA, SLINKET,
               S2T, BLINKER, CLASSIFIER, LINK_MERGER ]

DSI_DEFAULTS = {
    'simple-xml': {
        'pipeline': COMPONENTS,
        'content_tag': 'TEXT' },
    'timebank': {
        'pipeline': COMPONENTS,
        'content_tag': 'TEXT' },
    'rte3': {
        'pipeline': COMPONENTS[1:],
        'content_tag': 'pair' },
    'atee': {
        'pipeline': COMPONENTS,
        'content_tag': 'TailParas' }}



class DocumentModel:

    """Abstract class that contains some shared accessors."""

    def get_xml_document(self):
        """Accessor to retrieve the value of self.xml_document."""
        return self.xml_document

    def get_metadata(self):
        """Accessor to retrieve the value of self.metadata."""
        return self.metadata

    def get_content_tag(self):
        """Accessor to retrieve the value of self.content_tag."""
        return self.content_tag

    def set_metadata_parser(self, parser):
        """Accessor that sets the value of self.metadata_parser to an
        instance of MetaDataParser or subclass thereof."""
        self.metadata_parser = parser

    def set_content_tag(self, tag):
        """Accessor that sets the value of self.content_tag. The
        argument is a string like 'TEXT', 'para', or 'DOC'."""
        self.content_tag = tag

    def get_default_content_tag(self, doctype):
        """Returns a default content_tag for the given document type."""
        return self._get_default(doctype, 'content_tag', 'TEXT')

    def get_default_pipeline(self, doctype):
        """Returns a default pipeline for the given document type."""
        return self._get_default(doctype, 'pipeline', [])
            
    def _get_default(self, doctype, feature, fallback):
        """Returns a default for a particular feature given a document
        type. Return the fallback is no value is available"""
        try:
            return DSI_DEFAULTS[doctype][feature]
        except KeyError:
            logger.error("No default %s for document type %s" % (feature, doctype))
            return fallback
            


class SimpleXmlModel(DocumentModel):

    """Document model for simple XML documents.

    Instance variables:
       input_document         - absolute path
       xml_document           - an XmlDocument
       content_tag            - string
       processing_parameters  - dictionary
       metadata_parser        - a MetaDataParser
       metadata               - dictionary"""
    

    def __init__(self, file):
        """Here, self.content_tag is the beginning of what is called fragment ids in
        the specifications. Should probably be a set of XPATH expressions. For now,
        self.xml_document is the simple representation given by the xml_parser, we
        could use a full DOM from python's minidom implementation."""
        self.input_document = file
        self.xml_document = None
        self.content_tag = None
        #self.processing_parameters = None
        self.metadata_parser = None
        self.metadata = None

    def read_document(self):
        """Reads the input document by calling the xml parser and the
        meta data parser. No return value."""
        self.parse_xml()
        self.parse_metadata()

    def parse_xml(self):
        """Use the expat parser to read in the document. Takes the
        value of self.input_document and puts the result in
        self.xml_document."""
        # NOTES:
        # - Uses a new parser each time when reading a new document.
        #   Previously, this was done only once in an initialization
        #   method, but at some point segmentation faults showed up that
        #   could only be fixed by creating a new parser for each file.
        # - This method can probably be moved to the superclass.
        xmlfile = open(self.input_document, "r")
        self.xml_document = Parser().parse_file(xmlfile)
        
    def parse_metadata(self):
        """Sets the metadat dictionary by calling the meta data parser. It
        currently only sets the DCT."""
        self.metadata = {}
        self.metadata['dct'] = self.metadata_parser.get_dct(self.xml_document)



class MetaDataParser:

    """Abstract class. May in the future contain all kinds of default behaviour,
    like finding a DCT in any document."""

    def get_dct(self):
        return get_today()

    


class MetaDataParser_TimeBank(MetaDataParser):

    """The meta data parser for TimeBank documents."""

    def get_dct(self, xmldoc):
        """Takes an XmlDocument, extracts the document creation time,
        and returns it as a string of the form YYYYMMDD."""

        # set DCT default
        dct = get_today()

        docsource = self._get_doc_source(xmldoc)

        if docsource == 'ABC':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = docno[3:11]
            
        elif docsource == 'AP':
            fileid = xmldoc.tags['FILEID'][0].collect_content().strip()
            result = re.compile("(AP-NR-)?(\d+)-(\d+)-(\d+)").match(fileid)
            if result:
                (crap, month, day, year) = result.groups()
                dct = "19%s%s%s" % (year, month, day)
            else:
                logger.warn("Could not get date from %s" % fileid)
                
        elif docsource == 'APW':
            date_time = xmldoc.tags['DATE_TIME'][0].collect_content().strip()
            result = re.compile("(\d+)/(\d+)/(\d+)").match(date_time)
            if result:
                (month, day, year) = result.groups()
                dct = "%s%s%s" % (year, month, day)
            else:
                logger.warn("Could not get date from %s" % fileid)
            
        elif docsource == 'CNN':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = docno[3:11]

        elif docsource == 'NYT':
            date_time = xmldoc.tags['DATE_TIME'][0].collect_content().strip()
            result = re.compile("(\d+)/(\d+)/(\d+)").match(date_time)
            if result:
                (month, day, year) = result.groups()
                dct = "%s%s%s" % (year, month, day)
            else:
                logger.warn("Could not get date from %s" % fileid)

        elif docsource == 'PRI':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = docno[3:11]

        elif docsource == 'SJMN':
            pubdate = xmldoc.tags['PUBDATE'][0].collect_content().strip()
            dct = '19' + pubdate

        elif docsource == 'VOA':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = docno[3:11]

        elif docsource == 'WSJ':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = '19' + docno[3:9]

        elif docsource == 'eaX':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = '19' + docno[2:8]

        elif docsource == 'ea':
            docno = xmldoc.tags['DOCNO'][0].collect_content().strip()
            dct = '19' + docno[2:8]

        #logger.out("DCT (%s): %s" % (docsource, dct))
        return dct

    
    def _get_doc_source(self, xmldoc):
        """Returns the name of the content provider."""
        tag_DOCNO = xmldoc.tags['DOCNO'][0]
        content = tag_DOCNO.collect_content().strip()
        # TimeBank has only these providers
        for str in ('ABC', 'APW', 'AP', 'CNN', 'NYT', 'PRI', 'SJMN', 'VOA', 'WSJ', 'ea', 'ed'):
            if content.startswith(str):
                return str
        logger.warn("Could not determine document source from DOCNO tag")
        return 'GENERIC'


class MetaDataParser_SimpleXml(MetaDataParser):

    """The meta data parser for simple XML documents."""
    
    def get_dct(self, xmldoc):
        """For simple XML documents, just return the current data. May in the
        future use some default processing to find dates in particular
        tags."""
        return get_today()


class MetaDataParser_RTE(MetaDataParser):

    """The meta data parser for RTE documents."""
    
    def get_dct(self, xmldoc):
        """For RTE documents, there really isn't a DCT, so just return the
        current date."""
        return get_today()


class MetaDataParser_ATEE(MetaDataParser):

    """The meta data parser for ATEE documents."""
    
    def get_dct(self, xmldoc):
        """All ATEE documents have a DATE tag with a value attribute, the
        value of that attribute is returned."""
        date_tag = xmldoc.tags['DATE'][0]
        return date_tag.attrs['value']



def get_today():
    """Return today's date in YYYYMMDD format."""
    return time.strftime("%Y%m%d", time.localtime());


    
class SavedMethods:

    """This class is not used at all. It is simply there to store some
    functions taken from an older version and still kept lying around
    because their functionality may need to be added."""
    
    def find_dct(self):
        for fragment in self.fragments:
            tag = fragment[1]
            text = tag.collect_content()
            match = re_DCT.search(text)
            if match:
                dct = match.group()
                dct = dct.replace('tid="t100"', 'tid="t0"')
                return dct
        return None

    def set_dct(self):
        try:
            first_data_tag = self.document.tags['Date'][0]
            self.dct = first_data_tag.attrs['value']
        except:
            print "Warning: no DCT found in Date tag"
            self.dct = '20000101'
            
    def insert_dct(self, dct_string):
        if dct_string:
            article_tag = self.document.tags['Article'][0]
            article_tag.insert_string_after(dct_string)
