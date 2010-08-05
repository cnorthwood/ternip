
    TERNIP: Temporal Expression Recognition and Normalisation in Python
    
    Created by Chris Northwood as part of an MSc in Computer Science with
    Speech and Language Processing at The University of Sheffield's Department
    of Computer Science.
    
    Version 0.9.dev

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

    Loading Documents In

    Doing The Recognition/Normalisation

    Writing Documents Out

    Changing How TERNIP Handles Warnings

EXTENDING TERNIP

    Writing Your Own Rules

        TODO

    Writing New Tagging or Annotating Modules

        TODO

    Writing A New Document Format

        TODO

EXTRAS

    Some Corpora

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
        ruleblock but with a comment at the top of each rule indicating it's
        index in the file. It is highly recommended to run this if you write
        your own rules, as it makes quickly identifying faulty rules easy.

    runtests.py

        This file executes the unit test suite for TERNIP.

RELATED READING

    Full API documentation: http://www.pling.org.uk/projects/ternip/doc/