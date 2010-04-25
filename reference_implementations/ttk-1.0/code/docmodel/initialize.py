"""

Initialization of the document model.

This module is responsible for initializing the document module
instance variables on a TarsqiControl instance, it also provides a way
to manage what components need to be applied.

"""

import os

from docmodel.model import SimpleXmlModel
from docmodel.model import MetaDataParser_TimeBank
from docmodel.model import MetaDataParser_SimpleXml
from docmodel.model import MetaDataParser_RTE
from docmodel.model import MetaDataParser_ATEE

from components.preprocessing.wrapper import PreprocessorWrapper
from components.gutime.wrapper import GUTimeWrapper
from components.evita.wrapper import EvitaWrapper
from components.slinket.wrapper import SlinketWrapper
from components.s2t.wrapper import S2tWrapper
from components.blinker.wrapper import BlinkerWrapper
from components.classifier.wrapper import ClassifierWrapper
from components.merging.wrapper import MergerWrapper

from utilities import logger
from library.tarsqi_constants import PREPROCESSOR, GUTIME, EVITA, SLINKET
from library.tarsqi_constants import S2T, CLASSIFIER, BLINKER, LINK_MERGER


class DocumentModelInitializer:

    """Class that is used solely to set up the document model instance
    variables on a tarsqi instance. It takes a TarsqiControl instance
    and sets up the right docement model functionality on it, given
    the data source and the processing options.

    Instance variables:
       dsi_to_docmodelconstructor - a mapping from strings to bound methods
    """

    def __init__(self):
        """Register all data source identifiers and link them to a
        constructor in the dsi_to_docmodelconstructor dictionary."""
        self.dsi_to_docmodelconstructor = {
            'simple-xml': self._setup_docmodel_simple_xml,
            'timebank': self._setup_docmodel_timebank,
            'atee': self._setup_docmodel_atee,
            'rte3': self._setup_docmodel_rte }
            

    def setup_docmodel(self, tarsqi_instance):

        """Initialize the document_model and processing_parameters instance
        variables of a TarsqiControl instance, using its data source
        identifier and processing options.
        
        Arguments:
           tarsqi_instance - a TarsqiControl instance
        
        No return value."""

        tarsqi_instance.processing_parameters = ProcessingParameters(tarsqi_instance)
        data_source_identifier = tarsqi_instance.data_source_identifier

        constructor = self.dsi_to_docmodelconstructor.get(data_source_identifier, None)
        try:
            constructor(tarsqi_instance)
        except TypeError, e:
            # log error and use simple-xml as a default
            logger.error("Unknown data source identifier, using simple-xml")
            tarsqi_instance.data_source_identifier = 'simple-xml'
            data_source_identifier = tarsqi_instance.data_source_identifier
            self._setup_docmodel_simple_xml(tarsqi_instance)
        
        # copy content_tag from document model for convenience
        tarsqi_instance.content_tag = tarsqi_instance.document_model.get_content_tag()


    def _setup_docmodel_simple_xml(self, tarsqi_instance):
        """Sets up the document model for the TarsqiControl instance if the
        data source is 'simple-xml' or 'simple-xml-preprocessed'. Uses
        SimpleXmlModel and MetaDataParser_TimeBank and sets the
        content tag to 'TEXT'. Differences in preprocessing chains are
        handled when the pipeline is set. User options that can
        override default settings will be taken into consideration in
        sub methods. Is now identical to the timebank document model
        but will need to get a more default MetaData Parser. Takes a
        TarsqiControl instance and has no return value."""
        self._setup_docmodel(tarsqi_instance,
                             SimpleXmlModel(tarsqi_instance.input),
                             'TEXT',
                             MetaDataParser_SimpleXml())
        
    def _setup_docmodel_timebank(self, tarsqi_instance):
        """Sets up the document model for the TarsqiControl instance if the
        data source is 'timebank-source' or 'timebank-preprocessed'. Uses
        SimpleXmlModel and MetaDataParser_TimeBank, and sets the
        content tag to 'TEXT'. Differences in preprocessing chains are
        handled when the pipeline is set. Takes a TarsqiControl
        instance and has no return value."""
        self._setup_docmodel(tarsqi_instance,
                             SimpleXmlModel(tarsqi_instance.input),
                             'TEXT',
                             MetaDataParser_TimeBank())
        
    def _setup_docmodel_rte(self, tarsqi_instance):
        """Sets up the document model for the TarsqiControl instance if the
        data source is 'RTE3'. Uses SimpleXmlModel and MetaDataParser_RTE,
        and sets the content tag to 'PAIR'. Takes a TarsqiControl
        instance and has no return value."""
        self._setup_docmodel(tarsqi_instance,
                             SimpleXmlModel(tarsqi_instance.input),
                             'pair',
                             MetaDataParser_RTE())

    def _setup_docmodel_atee(self, tarsqi_instance):
        """Sets up the document model for the TarsqiControl instance if the
        data source is 'ATEE'. Uses SimpleXmlModel and MetaDataParser_ATEE,
        and sets the content tag to 'TailParas'. Takes a TarsqiControl
        instance and has no return value."""
        self._setup_docmodel(tarsqi_instance,
                             SimpleXmlModel(tarsqi_instance.input),
                             'TailParas',
                             MetaDataParser_ATEE())

    def _setup_docmodel(self, tarsqi_instance, docmodel, content_tag, metadata_parser):
        """Initialize the document model and set its metadata parser. Then set
        the content tag and the pipeline, in both cases default values
        from the data source identifier can be overruled by user
        options."""
        tarsqi_instance.document_model = docmodel
        tarsqi_instance.document_model.set_metadata_parser(metadata_parser)
        self._set_content_tag(content_tag, tarsqi_instance)
        self._set_pipeline(tarsqi_instance)

    def _set_content_tag(self, default_tag, tarsqi_instance):
        """Sets the content tag using the procided default, overriding it if a
        user option was specified."""
        tarsqi_instance.document_model.set_content_tag(default_tag)
        content_tag = tarsqi_instance.getopt_content_tag()
        if content_tag:
            tarsqi_instance.document_model.set_content_tag(content_tag)

    def _set_pipeline(self, tarsqi_instance):
        """Retrieves the data source identifier and uses it to set a default
        pipeline. Gives precedence to a user option if one was
        specified."""
        dsi = tarsqi_instance.data_source_identifier
        pipeline = tarsqi_instance.document_model.get_default_pipeline(dsi)
        if tarsqi_instance.getopt_pipeline():
            pipeline = tarsqi_instance.getopt_pipeline().split(',')
        tarsqi_instance.processing_parameters.set_pipeline(pipeline)
        



class ProcessingParameters:

    """Instances of this class can be used to determine what Tarsqi
    components need to be applied The instance is created using a
    TarsqiControl instance .

    Instance variables:

       pipeline
          a list of components, each component is a tuple of component
          name, component wrapper, input file and output file
       input
          an absolute path
       output
          an absolute path
       tarsqi_components
          a dictionary, mapping each component name to a
          wrapper-filename pair where the filename is the name of the
          file created by the components"""

    
    def __init__(self, tarsqi_instance):
        
        """Initialize input, output and tarsqi_components instance
        variables. Takes a TarsqiControl instance as the sole
        argument."""

        self.pipeline = []
        self.input = tarsqi_instance.input
        self.output = tarsqi_instance.output
        self.tarsqi_components = {
            PREPROCESSOR: (PreprocessorWrapper, tarsqi_instance.FILE_PRE),
            GUTIME: (GUTimeWrapper, tarsqi_instance.FILE_GUT),
            EVITA: (EvitaWrapper, tarsqi_instance.FILE_EVI),
            SLINKET: (SlinketWrapper, tarsqi_instance.FILE_SLI),
            S2T: (S2tWrapper, tarsqi_instance.FILE_S2T),
            BLINKER: (BlinkerWrapper, tarsqi_instance.FILE_BLI),
            CLASSIFIER: (ClassifierWrapper, tarsqi_instance.FILE_CLA),
            LINK_MERGER: (MergerWrapper, tarsqi_instance.FILE_MER) }

    def set_pipeline(self, list):
        """Takes a list with component names and sets the pipeline and
        component variables conform that list."""
        self.pipeline = []
        component_input = self.input
        for component in list:
            (wrapper, outfile) = self.tarsqi_components[component]
            self.pipeline.append([component, wrapper, component_input, outfile])
            component_input = outfile
        


    
