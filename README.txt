
    TERNIP: Temporal Expression Recognition and Normalisation in Python
    
    Created by Chris Northwood as part of an MSc in Computer Science with
    Speech and Language Processing at The University of Sheffield's Department
    of Computer Science.
    
    Version 1.0

WHAT IS TERNIP?

    TERNIP is a library which can recognise and normalise temporal expressions
    in text. A temporal expression is one such as '8th July 2010' - those which
    refer to some form of time (either a point in time, a duration, etc).
    
    The two functions TERNIP performs is first to identify these expressions in
    some text, and then to figure out the absolute date (as close as it can)
    that is refers to.
    
    TERNIP can handle a number of formats for representing documents and the
    metadata associated with a TIMEX. The most common form is TimeML.

INSTALLING

    TERNIP was developed on Python 2.6 and has not been tested on earlier
    versions nor Python 3.0. Therefore, Python 2.x, where x >= 6 is recommended,
    but your mileage my vary on other systems.
    
    TERNIP also depends on NLTK and dateutil. Please ensure both of these Python
    packages are installed.
    
    TERNIP uses Python's distutils to install itself. To install TERNIP, please
    run:
    
        python setup.py install

USING ANNOTATE_TIMEX

    The annotate_timex command provides a simple front-end to TERNIP. Running
    'annotate_timex' with no arguments shows you the default usage for the
    script.

USING THE API

    Doing The Recognition/Normalisation

        Two functions are provided which returns instances of the default
        recognisers and normalisers:
        
          * ternip.recogniser()
          * ternip.normaliser()
        
        You can also manually load the recognition and normalisation rule
        engines (currently the only modules for recognition and normalisation).
        
        This can be done by instantiating the objects:
        
          * ternip.rule_engine.recognition_rule_engine()
          * ternip.rule_engine.normalisation_rule_engine()
        
        And then calling the load_rules(path) with a path to where the rules to
        be loaded are stored.
        
        Once this has been done, the recogniser supports a single method:
        
          * tag(sents): This takes a list of sentences (in the format detailed
                        in the section below) and returns a list of sentences in
                        the same format, with the third element of the token
                        tuple filled with ternip.timex objects indicating the
                        type and extent of the expression covered.
        
        Once this has been done, the normaliser can be used on the recognised
        time expression extents to fill the other attributes. Again, a single
        method exists on the normaliser class:
        
          * annotate(sents, dct): This takes sentences where the third element
                                  in the token tuple is filled with timex
                                  extents and the document creation time (or the
                                  context to be considered when computing
                                  relative date offsets) and fills the
                                  attributes of the timex objects where it can.
                                  The DCT is expected to be a string in ISO 8601
                                  (basic) format.

    Handling TIMEX-annotated documents

        The annotation functions expect input in the format of a list of
        sentences, where a sentence is a list of tuples consisting of the token,
        the part-of-speech tag and a set of timexes tagged with that object,
        
        i.e., [[('token', 'POS-tag', set([timex1, timex2, ...])), ...], ...]
        
        In the ternip.formats package, a number of classes exist which can
        convert to and from document formats and this internal format.
        
        These classes can be instantiated by passing in a string containing the
        document to the constructor, with different classes also supporting
        optional keyword arguments which can specify additional metadata (as
        fully documented in the API documentation). These classes will also use
        the NLTK to tokenise and part-of-speech tag the document text.
        
        These document classes then support a standard interface for accessing
        the data:
        
          * get_sents(): Get the text from the document in the format required
                         for the annotator
          * get_dct_sents(): If the document format contains the document
                             creation time, then get that in the format ready
                             for the annotator
          * reconcile(sents): Add the TIMEX metadata from the annotated sents to
                              the document - XML documents also allow adding
                              part-of-speech and tokenisation metadata to the
                              document
          * reconcile_dct(sents): Add TIMEX metadata to the document creation
                                  time information (from get_dct_sents())
          * __str__(): Returns the document in a string, ready to be written
                       out or similar.
        
        Some classes also support a create static method, which can be used to
        create new instances of that document from the internal representation.
        This can be useful without the annotator functions to transform TIMEX
        annotated documents between 2 formats.
        
        The supported formats included with TERNIP are:
        
          * ternip.formats.tern: An XML parser for the TERN dataset (note, the
                                 TERN dataset is SGML, a superset of XML, so
                                 some documents may not correctly parse as XML)
          * ternip.formats.timeml: Documents in TimeML format
          * ternip.formats.timex2: Generic XML documents annotated with the
                                   TIMEX2 tag
          * ternip.formats.timex3: Generic XML documents annotated with TimeML's
                                   TIMEX3 tag
          * ternip.formats.tempeval2: The tabulated format used for the
                                      TempEval-2 competition

    Changing How TERNIP Handles Warnings

        To use TERNIP in a larger program, the default method for reporting
        warnings during program execution, writing to stderr, may not be
        appropriate. To work around this, you can override the default warning
        function by setting the variable ternip.warn to your own function.
        
        Your function must accept a string as the first argument containing a
        description of the warning, and the second the raised exception
        containing more information about the error that generated the warning.

EXTENDING TERNIP

    Writing Your Own Rules

        The rule engines (normalisation and recognition) in TERNIP support three
        types of files: single rules, rule blocks and complex rules. Single
        rules and rule blocks consist of files with lines in the format:
        
            Key: Value
        
        Where the acceptable keys and value formats depend on the exact type of
        rule (recognition or normalisation) and are defined further below.
        
        Rule blocks can contain many rules, separated by three dashes on a line.
        Additionally, the first section of the file is a header for the rule
        block.
        
        Complex rules are Python files which contain a class called 'rule' which
        is instantiated. These classes must implement an interface depending on
        which type of rule it is.
        
        Rule regular expressions undertake some preprocessing. Apart from when
        specified using the 'Tokenise' option on normalisation rules, sentences
        are converted into the form <token~pos><token~pos> with no spaces, so
        this is what the rules are matched against. Additionally, < and >, which
        indicate token boundaries are preprocessed and the token open bracket
        must be at the same parenthesis nesting level as the closing one.
        
        For example,
        
            <hello~.+>(<world~.+>)? is valid
            <hello(~.+><world)?~.+> is not, and will not match as expected
        
        Finally, the quantifiers + and ? on the matching character . will not
        match across token boundaries, apart from if matching Deliminated number
        word sequences (i.e., NUM_START.+NUM_END).
        
        When number delimination is enabled, then sequences of number words will
        be surrounded with NUM_START and NUM_END, and of ordinal sequences with
        NUM_ORD_START and NUM_ORD_END, e.g.,
        
            NUM_START<twenty~CD><four~CD>NUM_END
            NUM_ORD_START<sixty~CD><seventh~CD>NUM_END
        
        Additionally, in regular expressions, the following words will be
        replaced with predefined regular expression groups:
        
          * $ORDINAL_WORDS: which consist of word forms of ordinal values,
          * $ORDINAL_NUMS: the number forms (including suffixes) of ordinal values,
          * $DAYS: day names
          * $MONTHS: month names
          * $MONTH_ABBRS: three-letter abbreviations of month names
          * $RELATIVE_DAYS: relative expressions referring to days
          * $DAY_HOLIDAYS: holidays that have "day" in the name
          * $NTH_DOW_HOLIDAYS: holidays which always appear on a particular day
                               in the nth week of a given month
          * $FIXED_HOLIDAYS: holidays which have a fixed date (including token
                             boundaries)
          * $LUNAR_HOLIDAYS: holidays which are relative to Easter (including
                             token boundaries)
        
        The exact format of regular expressions is as implemented in the Python
        're' module: http://docs.python.org/library/re.html
        
        When dealing with guard regular expressions, if the first character of
        the regular expression is a !, this makes the regular expression
        negative - the rule will only execute if that regular expression does
        not match.

        Rule Blocks

            Rule blocks consist of sections separated by three dashes (---) on
            a line by themselves. The first section in a rule block is the
            header of the block and is in the following format, regardless of
            whether it's a recognition or normalisation rule. The format of the
            following sections is in the format of the single rules described
            below, except keys relating to ordering (ID and After) are erroneous
            as ordering is defined by the rule block.
            
            The following keys are valid in the header:
            
              * Block-Type: this can be either 'run-all' or 'run-until-success'.
                            In the case of run-all, all rules are run regardless
                            of whether or not previous rules succeeded or not,
                            and 'run-until-success' which will run until the
                            first rule successfully applies.
              * ID: This is an (optional) string containing an identifier which
                    can be referred to by other rules to express ordering.
              * After: This can exist multiple times in a header and defines
                       an ID which must have executed (successfully or not)
                       before this rule block runs.

        Single Recognition Rule

            The following keys are valid in recognition rules:
            
              * ID: This is an (optional) string containing an identifier which
                    can be referred to by other rules to express ordering.
              * After: This can exist multiple times in a header and defines
                       an ID which must have executed (successfully or not)
                       before this rule runs.
              * Type: This is a compulsory field which indicates the type of
                      temporal expression this rule matches.
              * Match: A compulsory regular expression, where the part of a
                       sentence that matches is marked as the extent of a new
                       timex
              * Squelch: Defaults to false, but if set to true, then removes any
                         timexes in the matched extent. True/false are allowed
                         values.
              * Case-Sensitive: true/false, defaults to false. Indicates whether
                                or not the regular expressions should be case
                                sensitive
              * Deliminate-Numbers: true/false, defaults to false, whether or
                                    not number sequences are deliminated as
                                    described above
              * Guard: multiple allowed, a regular expression the entire
                       sentence should match to be allowed to execute
              * Before-Guard: multiple allowed, as a guard, but only matches
                              on the tokens before the extent that was matched
                              by the 'Match' rule. (Anchors such as $ can be
                              useful here)
              * After-Guard: multiple allowed. As a Before-Guard, but instead
                             matches on the tokens after the extent matched by
                             Match (Anchors such as ^ can be useful here).

        Complex Recognition Rule

            Complex recognition rules are Python classes with a single method
            and two static variables:
            
              * id: A string (or None) containing an identifier for this rule
                    which can be used for ordering
              * after: A list of strings containing identifiers which must
                       have run before this rule is executed
              * apply(sent): This function is called when this rule is executed.
                             'sent' is a list of sentences in the internal
                             format described above, and the function is
                             expected to return a tuple where the first element
                             is the sentence with timex objects added and the
                             second element is a Boolean indicating whether or
                             not the rule altered the sentence or not.

        Single Normalisation Rule

            In the Python expressions described below, you can use the shortcut
            text {#X} which is replaced with the matched regular expression
            group X, e.g., {#1} will be the part of the sentence that matched
            the first parenthesis group in the text. {#0} would be the entire
            matched expression (this is equivalent to the group member of the
            Python re.match class).
            
            Additionally, a number of variables and support functions are
            available to these Python expressions which can assist the writing
            of normalisation rules.
            
            The following variables are available:
            
              * timex: The timex object which is currently being annotated.
              * cur_context: The ISO 8601 basic string containing the current
                             date-time context of this sentence.
              * dct: The ISO 8601 basic string containing the document creation
                     time of this document.
              * body: The part of the sentence which is covered by the extent of
                      this timex, in internal format (self._toks_to_str() can be
                      useful to convert this into a string format described
                      above).
              * before: The part of the sentence preceding the timex, in
                        internal format
              * after: The part of the sentence processing the timex, in
                       internal format.
            
            The functions in the ternip.rule_engine.normalisation_functions
            package are all imported in the same namespace as the expression
            being evaluated, so you can call the functions directly. You can
            find more details about these functions and their signatures in the
            API documentation.
            
            The timex fields are fully documented in the ternip.timex class,
            and are related to their meaning in the TimeML specification.
            
            The following keys are valid in normalisation rule definitions:
            
              * ID: This is an (optional) string containing an identifier which
                    can be referred to by other rules to express ordering.
              * After: This can exist multiple times in a header and defines
                       an ID which must have executed (successfully or not)
                       before this rule runs.
              * Type: an optional string which the type of the timex must match
                      for this rule to be applied
              * Match: A regular expression which the body of the timex must
                       match for this rule to be applied. The groups in this
                       regular expression are available in the annotation
                       expressions below.
              * Guard: A regular expression which the body of the timex must
                       match for this rule to be applied. Unlike 'Match', the
                       regular expression groups are not available in other
                       expressions.
              * After-Guard: A regular expression like Guard, except it matches
                             the part of the sentence after the timex.
              * Before-Guard: A regular expression like Guard, except it matches
                              the part of the sentence before the timex.
              * Sent-Guard: A regular expression like Guard, except that it
                            matches against the entire sentence.
              * Value: A Python expression which the results of evaluating are
                       set to the 'value' attribute of the timex.
              * Change-Type: A Python expression which, if set, changes the type
                             of the timex to what it evaluates to.
              * Freq: A Python expression which, if set, sets the freq attribute
                      on the timex.
              * Quant: A Python expression which, if set, sets the quant
                       attribute on the timex.
              * Mod: A Python expression which, if set, sets the mod attribute
                     on the timex.
              * Tokenise: Whether or not to prepare the sentence into the form
                          described above for the regular expressions. If set to
                          true (the default), then it it converted into the
                          tokenised string format described above. Otherwise,
                          the value is used as the separator between the tokens
                          when detokenising. The special values 'space' and
                          'null' can be used to indicate the token separator
                          should be the single space, or no gap at all. Note, if
                          tokenise is not true, then Deliminate-Numbers can not
                          be used, and part-of-speech tags are not available to
                          the regular expressions.
              * Deliminate-Numbers: If set to true (defaults to false), then
                                    sequences of number words are delimited with
                                    the tokens NUM_START and NUM_END, and
                                    ordinals with NUM_ORD_START and NUM_ORD_END.

        Complex Normalisation Rule

            Complex normalisation rules are Python classes with a single method
            and two static variables:
            
              * id: A string (or None) containing an identifier for this rule
                    which can be used for ordering
              * after: A list of strings containing identifiers which must
                       have been executed (successfully or not) before this rule
                       is executed
              * apply(timex, cur_context, dct, body, before, after):
                    The function that is called when this rule is being executed.
                    The first argument is the TIMEX to be annotated (the fields
                    of the timex object which could be annotated are detailed in
                    the API documentation for the ternip.timex class), the
                    second argument is a string in ISO 8601 basic format
                    representation of the current context of the document. The
                    'dct' argument is the creation time of the document and
                    'body', 'before' and 'after' contain the list of tokens
                    (in the internal form) of the extent of the timex,
                    preceding and following the timex extent. This function is
                    expected to a return a tuple where the first element
                    consists of a Boolean indicating whether or not this rule
                    successfully ran, and the second element consists of the
                    current date/time context (in ISO 8601 basic form), which
                    may have been changed by this rule.

    Writing New Tagging or Annotating Modules

        New tagging and annotation modules are expected to implement the same
        interface as the rule engines described above.

    Writing New Document Formats

        New document formats are expected to contain the same interface as
        described above. If you are writing a new document format based around
        XML, the ternip.formats.xml_doc.xml_doc class may provide useful
        functionality.
    
    Enabling Debug Functionality

        The classes normalisation_rule and recognition_rule have a member called
        _DEBUG which is a Boolean to help in debugging rules. When _DEBUG is set
        to True, then the comment attribute of the timex is set to the
        identifier of the rule which tagged/annotated it.

EXTRAS

    sample_data

        In the sample_data folder you will find varying corpora of documents
        with TIMEX tags annotated in varying formats. You can use these
        (perhaps stripping the TIMEX tags first) to test the system, as well as
        aiding in development of your own rules/modules/etc

    extras/terneval.py

        This handy little script runs TERNIP against the TERN sample data and
        reports the performance at the end. This also requires Perl to be
        installed and on your path, as that's what the TERN scorer uses.
        
        (NOTE: The TERN scorer appears to give very low results on Linux)
    
    extras/tempeval2.py

        As with the TERN script, this runs TERNIP against the TempEval-2 corpus
        provided in the sample data, and reports its performance at the end.
        Both this and terneval.py demonstrate samples on how to use the TERNIP
        API. 

    extras/add_rule_numbers.py

        This handy little script takes a ruleblock file and outputs the same
        ruleblock but with a comment at the top of each rule indicating its
        index in the file. It is highly recommended to run this if you write
        your own rules, as it makes quickly identifying faulty rules easy.

    extras/preprocesstern.py

        This will take the TERN corpus and annotate it with tokenisation/part-of
        -speech metadata to make document loading quicker.

    extras/performance.py

        This takes the pre-processed documents (produced by the script above)
        and annotates them all, giving speed statistics at the end.

    runtests.py

        This file executes the unit test suite for TERNIP.

    gate/ternip.xgapp

        This provides a .xgapp file which can be loaded into GATE to use TERNIP
        as a processing resource.

RELATED READING

    Full API documentation: http://www.pling.org.uk/projects/ternip/doc/