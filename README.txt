
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

USING TAG.PY

    tag.py is a simple front-end to TERNIP. Running tag.py with no arguments
    will show you the correct usage.

USING THE API

    TODO

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
        (perhaps stripping the TIMEX3 tags first) to test the system, as well as
        aiding in development of your own tools

    extras/terneval.py (TODO)

        This handy little script runs TERNIP against the TERN sample data and
        reports the performance at the end.
    
    extras/tempeval2.py (TODO)

        As with the TERN script, this runs TERNIP against the TempEval-2 corpus
        provided in the sample data, and reports its performance at the end.
        Both this and terneval.py demonstrate samples on how to use the TERNIP
        API.

    extras/add_rule_numbers.py (TODO)

        This handy little script takes a ruleblock file and outputs the same
        ruleblock but with a comment at the top of each rule indicating it's
        index in the file. It is highly recommended to run this if you write
        your own rules, as it makes quickly identifying faulty rules easy.

RELATED READING

    Full API documentation: http://www.pling.org.uk/projects/ternip/doc/