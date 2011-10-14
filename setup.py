#!/usr/bin/env python

from distutils.core import setup

setup(
    name='TERNIP',
    version='1.1dev',
    packages=['ternip', 'ternip.formats', 'ternip.rule_engine', 'ternip.rule_engine.normalisation_functions'],
    package_data={'ternip': ['rules/*/*.ruleblock', 'rules/*/*.pyrule', 'rules/*/*.rule']},
    scripts=['annotate_timex'],
    author='Chris Northwood',
    author_email='chris@pling.org.uk',
    install_requires=['python-dateutil'],
    description='Temporal Expression Recognition and Normalisation in Python',
    long_description="""
    TERNIP is a library which can recognise and normalise temporal expressions
    in text. A temporal expression is one such as '8th July 2010' - those which
    refer to some form of time (either a point in time, a duration, etc).
    
    The two functions TERNIP performs is first to identify these expressions in
    some text, and then to figure out the absolute date (as close as it can)
    that is refers to.
    
    TERNIP can handle a number of formats for representing documents and the
    metadata associated with a TIMEX. The most common form is TimeML.
    """
)
