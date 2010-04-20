#!/bin/env python
#-*- coding: latin1 -*-
"""Python wrapper for TreeTagger.

For TreeTagger, see:
U{http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/DecisionTreeTagger.html}

For this module, see:
U{http://www.limsi.fr/Individu/pointal/python/treetaggerwrapper.py}
and
U{http://www.limsi.fr/Individu/pointal/python.html#scripts}

This wrapper tool is intended to be used into larger projects, where multiple 
chunk of texts must be processed via TreeTagger (else you may simply use the
base TreeTagger installation as an external command).

Installation:
=============
Simply put the module in a directory listed in the Python path.

You must set up an environment variable B{C{TAGDIR}} to reference the
TreeTagger installation directory (the one with bin, lib and cmd 
subdirectories). 
If you dont set up such a variable, you can give a C{TAGDIR} named argument
when building a TreeTagger object to provide this information.

To build the documentation with epydoc::
    epydoc --html -o treetaggerwrapper-doc -n treetaggerwrapper treetaggerwrapper.py

Usage:
======
Example::
    import treetaggerwrapper
    #1) build a TreeTagger wrapper:
    tagger = treetaggerwrapper.TreeTagger(TAGLANG='en',TAGDIR='~/TreeTagger')
    #2) tag your text.
    tags = tagger.TagText("This is a very short text to tag.")
    #3) use the tags list... (list of string output from TreeTagger).
    print tags

Result::
    ['This\tDT\tthis',
     'is\tVBZ\tbe',
     'a\tDT\ta',
     'very\tRB\tvery',
     'short\tJJ\tshort',
     'text\tNN\ttext',
     'to\tTO\tto',
     'tag\tVB\ttag',
     '.\tSENT\t.']

The module can be used as a command line tool too, for more information
ask for module help::
    python treetaggerwrapper.py --help

Processing:
===========
This module do two main things:
-------------------------------
    - Manage preprocessing of text in place of external Perl scripts as in
      base TreeTagger installation, thus avoid starting Perl each time a chunk
      of text must be tagged.
    - Keep alive a pipe connected to TreeTagger process, and use that pipe
      to send data and retrieve tags, thus avoid starting TreeTagger each
      time.
Use of pipes avoid writing/reading temporary files on disk too.

Other things done by this module:
---------------------------------
    - Can number lines into XML tags (to identify lines after TreeTagger
      processing).
    - Can mark whitespaces with XML tags.
    - By default replace non-talk parts like URLs, emails, IP addresses,
      DNS names (can be turned off). Replaced by a 'replaced-xxx' string
      followed by an XML tag containing the replaced text as attribute.
    - Acronyms like U.S.A. are systematically written with a final dot,
      even if it is missing in original file.


In normal mode, all journal outputs are done via Python standard logging system,
standard output is only used if a) you run the module in pipe mode (ie.
results goes to stdout), or b) you set DEBUG or DEBUG_PREPROCESS global
variables and you use the module directly on command line (which make journal 
and other traces to be sent to stdout).

For an example of logging use, see at the end of this module.

TO DO 
=====
Waiting for modification requests :-).


HISTORY
=======
2005-09-29 - Added support for darwin on the request of (and with tests from)
    Mauro Cherubini.

@note: Some non-exported functions and globals can be nice to use in other
       contexts:
       L{SGML_tag}, L{SGML_tag_re}, L{IsSGMLTag}, L{SplitSGML},
       L{Ip_expression}, L{IpMatch_re}, L{DnsHost_expression}, 
       L{DnsHostMatch_re}, L{UrlMatch_expression}, L{UrlMatch_re}, 
       L{EmailMatch_expression}, L{EmailMatch_re}.
@author: Laurent Pointal (laurent.pointal@limsi.fr)
@organization: CNRS - LIMSI
@copyright: CNRS - 2004
@license: GNU-GPL Version 2
@version: 1.0
@var DEBUG: global to set to enable debugging code (mainly logs).
@type DEBUG: boolean
@var DEBUG_PREPROCESS: global to set to enable preprocessing specific
                       debugging code.
@type DEBUG_PREPROCESS: boolean
@var logger: logging Logger object for this module.
@var STARTOFTEXT: tag to identify begin of a text in the data flow.
@type STARTOFTEXT: string
@var ENDOFTEXT: tag to identify end of a text in the data flow.
@type ENDOFTEXT: string
@var NUMBEROFLINE: tag to identify line numbers from source text.
@type NUMBEROFLINE: string
@var TAGSPACE: tag to identify spaces in output.
@type TAGSPACE: string
@var TAGTAB = tag to identify horizontal tabulations in output.
@type TAGTAB: string
@var TAGLF = tag to identify line feeds in output.
@type TAGLF: string
@var TAGCR = tag to identify carriage returns in output.
@type TAGCR: string
@var TAGVT = tag to identify vertical tabulations in output.
@type TAGVT: string
@var TAGFF = tag to identify form feeds in output.
@type TAGFF: string
@var alonemarks: string containing chars which must be kept alone (this string
                 is used in regular expressions inside square brackets parts).
@type alonemarks: string
@var g_langsupport: dictionnary with data for each usable langage.
@type g_langsupport: dict [langage] ==> dict of data
@var SGML_name: regular expression string for XML names
@type SGML_name: string
@var SGML_tag: regular expression string to match XML tags.
@type SGML_tag: string
@var SGML_tag_re: regular expression object to match XML tags.
@type SGML_tag_re: SRE_Pattern
@var Ip_expression: regular expression string to match IP addresses.
@type Ip_expression: string
@var IpMatch_re: regular expression object to match IP addresses.
@type IpMatch_re: SRE_Pattern
@var DnsHost_expression: regular expression string to match DNS names.
@type DnsHost_expression: string
@var DnsHostMatch_re: regular expression object to match DNS names.
@type DnsHostMatch_re: SRE_Pattern
@var UrlMatch_expression: regular expression string to match URLs.
@type UrlMatch_expression: string
@var UrlMatch_re: regular expression object to match URLs.
@type UrlMatch_re: SRE_Pattern
@var EmailMatch_expression: regular expression string to match email addresses.
@type EmailMatch_expression: string
@var EmailMatch_re: regular expression object to match email addresses.
@type EmailMatch_re: SRE_Pattern
"""
# Note: I use re.VERBOSE option everywhere to allow spaces and comments into
#       regular expressions (more readable). And (?:...) allow to have
#       semantic groups of things in the expression but no submatch group
#       corresponding in the match object.
#==============================================================================
__all__ = ["TreeTaggerError","TreeTagger"]
import os
import string
import logging
import threading
import glob
import re
import sys
import getopt


DEBUG = 0
DEBUG_PREPROCESS = 0

# Extension added for result files.
RESEXT = "ttr"

# We dont print for errors/warnings, we use Python logging system.
logger = logging.getLogger("TreeTagger")

# A tag to identify begin/end of a text in the data flow.
# (avoid to restart TreeTagger process each time)
STARTOFTEXT = "<This-is-the-start-of-the-text />"
ENDOFTEXT = "<This-is-the-end-of-the-text />"
# A tag to identify line numbers from source text.
NUMBEROFLINE = "<This-is-line-number num=\"%d\" />"
# And tags to identify location of whitespaces in source text.
TAGSPACE = "<This-is-a-space />"
TAGTAB = "<This-is-a-tab />"
TAGLF = "<This-is-a-lf />"
TAGCR = "<This-is-a-cr />"
TAGVT = "<This-is-a-vt />"
TAGFF = "<This-is-a-ff />"


#==============================================================================
# Langage support.
# Dictionnary g_langsupport is indexed by langage code (en, fr, de...).
# Each langage code has a dictionnary as value, with corresponding entries:
#   tagparfile: name of the TreeTagger langage file in TreeTagger lib dir.
#   abbrevfile: name of the abbreviations text file in TreeTagger lib dir.
#   pchar: characters which have to be cut off at the beginning of a word.
#          must be usable into a [] regular expression part.
#   fchar: characters which have to be cut off at the end of a word.
#          must be usable into a [] regular expression part.
#   pclictic: character sequences which have to be cut off at the beginning
#               of a word.
#   fclictic: character sequences which have to be cut off at the end of
#               a word.
#   number: representation of numbers in the langage.
#          must be a full regular expression for numbers.
#   dummysentence: a langage valid sentence (sent to ensure that TreeTagger 
#          push remaining data). Sentence must only contain words and spaces
#          (even spaces between punctuation as string is simply splitted
#          on whitespaces before being sent to TreeTagger.
#   replurlexp: regular expression subtitution string for URLs.
#   replemailexp: regular expression subtitution string for emails.
#   replipexp: regular expression subtitution string for IP addresses.
#   repldnsexp: regular expression subtitution string for DNS names.
# Chars alonemarks:
#         !?¿;…,*•¤@°:%‰|¦/()[]{}<>«»‹›“”´`‘’ˆ¨„&~=#±†‡–—€£¥$©®™"
# must have spaces around them to make them tokens.
# Notes: they may be in pchar or fchar too, to identify punctuation after
#        a fchar.
#        \202 is a special ,
#        \226 \227 are special -
alonemarks = "!?¿;…,\202*•¤@°:%‰|¦/()[\]{}<>«»‹›“”´`‘’ˆ¨„&~=#±†‡\226"+\
             "\227€£¥$©®™\""
g_langsupport = {
    "en": { "binfile-win": "tree-tagger.exe",
            "binfile-lin": "tree-tagger",
            "binfile-darwin": "tree-tagger",
            "tagparfile": "english.par",
            "abbrevfile": "english-abbreviations",
            "pchar"     : alonemarks+r"'",
            "fchar"     : alonemarks+r"'",
            "pclictic"  : r"",
            "fclictic"  : r"'(s|re|ve|d|m|em|ll)|n't",
            "number"    : r"""(
                            [-+]?[0-9]+(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?
                                |
                            [-+]?\.[0-9]+(?:[eE][-+]?[0-9]+)?
                              )""",
            "dummysentence": "This is a dummy sentence to ensure data push .",
            "replurlexp": r' replaced-url <repurl text="\1" />',
            "replemailexp": r' replaced-email <repemail text="\1" />',
            "replipexp" : r' replaced-ip <repip text="\1" />',
            "repldnsexp" : r' replaced-dns <repdns text="\1" />'
          },
    "fr": { "binfile-win": "tree-tagger.exe",
            "binfile-lin": "tree-tagger",
            "binfile-darwin": "tree-tagger",
            "tagparfile": "french.par",
            "abbrevfile": "french-abbreviations",
            "pchar"     : alonemarks+r"'",
            "fchar"     : alonemarks+r"'",
            "pclictic"  : r"[dcjlmnstDCJLNMST]'|[Qq]u'|[Jj]usqu'|[Ll]orsqu'",
            "fclictic"  : r"'-t-elles|-t-ils|-t-on|-ce|-elles|-ils|-je|-la|"+\
                          r"-les|-leur|-lui|-mêmes|-m'|-moi|-on|-toi|-tu|-t'|"+\
                          r"-vous|-en|-y|-ci|-là",
            "number"    : r"""(
                            [-+]?[0-9]+(?:[.,][0-9]*)?(?:[eE][-+]?[0-9]+)?
                                |
                            [-+]?[.,][0-9]+(?:[eE][-+]?[0-9]+)?
                               )""",
            "dummysentence": "Cela est une phrase inutile pour assurer la "+\
                          "transmission des données .",
            "replurlexp": r' url-remplacée <repurl text="\1" />',
            "replemailexp": r' email-remplacé <repemail text="\1" />',
            "replipexp" : r' ip-remplacée <repdip text="\1" />',
            "repldnsexp" : r' dns-remplacé <repdns text="\1" />'
          },
    "de": { "binfile-win": "tree-tagger.exe",
            "binfile-lin": "tree-tagger",
            "binfile-darwin": "tree-tagger",
            "tagparfile": "german.par",
            "abbrevfile": "german-abbreviations",
            "pchar"     : alonemarks+r"'",
            "fchar"     : alonemarks+r"'",
            "pclictic"  : r"",
            "fclictic"  : r"'(s|re|ve|d|m|em|ll)|n't",
            "number"    : r"""(
                            [-+]?[0-9]+(?:\.[0-9]*)?(?:[eE][-+]?[0-9]+)?
                                |
                            [-+]?\.[0-9]+(?:[eE][-+]?[0-9]+)?
                              )""",
            "dummysentence": "Das ist ein Testsatz um das Stossen der "+\
                            "Daten sicherzustellen .",
            "replurlexp": r' replaced-url <repurl text="\1" />',
            "replemailexp": r' replaced-email <repemail text="\1" />',
            "replipexp" : r' replaced-ip <repip text="\1" />',
            "repldnsexp" : r' replaced-dns <repdns text="\1" />'
          }
    }

# We consider following rules to apply whatever be the langage.
# ... is an ellipsis, put spaces around before splitting on spaces
# (make it a token)
ellipfind_re = re.compile(r"(\.\.\.)",
                          re.IGNORECASE|re.VERBOSE)
ellipfind_subst = r" ... "
# A regexp to put spaces if missing after alone marks.
punct1find_re = re.compile(r"(["+alonemarks+"])([^ ])",
                           re.IGNORECASE|re.VERBOSE)
punct1find_subst = r"\1 \2"
# A regexp to put spaces if missing before alone marks.
punct2find_re = re.compile(r"([^ ])([["+alonemarks+"])",
                           re.IGNORECASE|re.VERBOSE)
punct2find_subst = r"\1 \2"
# A regexp to identify acronyms like U.S.A. or U.S.A (written to force
# at least two chars in the acronym, and the final dot optionnal).
acronymexpr_re = re.compile(r"^[a-zÀ-ÿ]+(\.[a-zÀ-ÿ])+\.?$",
                           re.IGNORECASE|re.VERBOSE)

#==============================================================================
class TreeTaggerError (Exception) :
    """For exceptions generated directly by TreeTagger class code.
    """
    pass


#==============================================================================
def PipeWriter(pipe,text,flushsequence) :
    """Write a text to a pipe and manage pre-post data to ensure flushing.
    
    For internal use.

    @param  pipe: the pipe on what to write the text.
    @type   pipe: pipe object (file-like with write and flush methods)
    @param  text: the text to write.
    @type   text: string or list of strings
    @param  flushsequence: lines of tokens to ensure flush by TreeTagger.
    @type   flushsequence: string (with \\n between tokens)
    """
    try :
        # Warn the user of possible bad usage.
        if not text :
            logger.warning("Requested to tag an empty text.")
            # We continue to unlock the thread waiting for the ENDOFTEXT on
            # TreeTagger output.

        logger.info("Writing starting part to pipe.")
        pipe.write(STARTOFTEXT+"\n")

        logger.info("Writing data to pipe.")

        if text :
            if isinstance(text,basestring) :
                # Typically if called without pre-processing.
                pipe.write(text)
                if text[-1] != '\n' : pipe.write("\n")
            else :
                # Typically when we have done pre-processing.
                for line in text :
                    pipe.write(line)
                    pipe.write("\n")

        logger.info("Writing ending and flushing part to pipe.")
        pipe.write(ENDOFTEXT+"\n.\n"+flushsequence+"\n")
        pipe.flush()
        logger.info("Finished writing data to pipe. Pipe flushed.")
    except :
        logger.error("Failure during pipe writing.",exc_info=True)


#==============================================================================
class TreeTagger (object) :
    """Wrap TreeTagger binary to optimize its usage on multiple texts.


    @ivar   lang: langage supported by this tagger ('en', 'fr'...).
    @type   lang: string
    @ivar   langsupport: dictionnary of langage specific values (ref. to
                         g_langsupport[lang] dictionnary).
    @type   langsupport: dict
    @ivar   tagdir: path to directory of installation of TreeTagger.
                    Set via TAGDIR env. var or construction param.
    @type   tagdir: string
    @ivar   tagbindir: path to binary dir into TreeTagger dir.
    @type   tagbindir: string
    @ivar   tagcmddir: path to commands dir into TreeTagger dir.
    @type   tagcmddir: string
    @ivar   taglibdir: path to libraries dir into TreeTagger dir.
    @type   taglibdir: string
    @ivar   tagbin: path to TreeTagger binary file (used to launch process).
    @type   tagbin: string
    @ivar   tagopt: command line options for TreeTagger.
    @type   tagopt: string
    @ivar   tagparfile: path to TreeTagger library file.
    @type   tagparfile: string
    @ivar   abbrevfile: path to abbreviations file.
    @type   abbrevfile: string
    @ivar   abbterms: dictionnary of abbreviation terms for fast lookup.
                      Filled when reading abbreviations file.
    @type   abbterms: dict  [ form ] ==> term
    @ivar   pchar: characters which have to be cut off at the beginning of
                   a word.
                   Filled from g_langsupport dict.
    @type   pchar: string
    @ivar   pchar_re: regular expression object to cut-off such chars.
    @type   pchar_re: SRE_Pattern
    @ivar   fchar: characters which have to be cut off at the end of a word.
                   Filled from g_langsupport dict.
    @type   fchar: string
    @ivar   fchar_re: regular expression object to cut-off such chars.
    @type   fchar_re: SRE_Pattern
    @ivar   pclictic: character sequences which have to be cut off at the
                      beginning of a word.
                      Filled from g_langsupport dict.
    @type   pclictic: string
    @ivar   pclictic_re: regular expression object to cut-off pclictic
                         sequences.
    @type   pclictic_re: SRE_Pattern
    @ivar   fclictic: character sequences which have to be cut off at the end
                      of a word.
                      Filled from g_langsupport dict.
    @type   fclictic: string
    @ivar   fclictic_re: regular expression object to cut-off fclictic
                         sequences.
    @type   fclictic_re: SRE_Pattern
    @ivar   number: regular expression of number recognition for the langage.
                    Filled from g_langsupport dict.
    @type   number: string
    @ivar   number_re: regular expression object to identify numbers.
    @type   number_re: SRE_Pattern
    @ivar   dummysequence: just a small but complete sentence in the langage.
                           Filled from g_langsupport dict.
    @type   dummysequence: string
    @ivar   replurlexp: regular expression subtitution string for URLs.
    @type   replurlexp: string
    @ivar   replemailexp: regular expression subtitution string for emails.
    @type   replemailexp: string
    @ivar   replipexp: regular expression subtitution string for IP addresses.
    @type   replipexp: string
    @ivar   repldnsexp: regular expression subtitution string for DNS names.
    @type   repldnsexp: string
    @ivar   taginput: pipe to write to TreeTagger input. Set whe opening pipe.
    @type   taginput: write stream
    @ivar   tagoutput: pipe to read from TreeTagger input. Set whe opening
                       pipe.
    @type   tagoutput: read stream
    """
    #--------------------------------------------------------------------------
    def __init__ (self,**kargs) :
        """Construction of a wrapper for a TreeTagger process.

        You can specify several parameters at construction time. 
        These parameters can be set via environment variables too.
        Most of them have default values.

        @keyword TAGLANG: langage code for texts ('en','fr',...)
                          (default to 'en').
        @type   TAGLANG: string
        @keyword  TAGDIR: path to TreeTagger installation directory
                          (optionnal but highly recommended).
        @type   TAGDIR: string
        @keyword  TAGOPT: options for TreeTagger
                          (default to '-token -lemma -sgml').
        @type   TAGOPT: string
        @keyword  TAGPARFILE: parameter file for TreeTagger.
                              (default available for supported langages).
                              Use value None to force use of default if
                              environment variable define a value you dont wants
                              to use.
        @type   TAGPARFILE: string
        @keyword  TAGABBREV: abbreviation file for preprocessing.
                             (default available for supported langages).
        @type   TAGABBREV: string

        """
        # Get data in different place, setup context for preprocessing and
        # processing.
        self.SetLangage(kargs)
        self.SetTagger(kargs)
        self.SetPreprocessor(kargs)
        # Note: TreeTagger process is started later, when really needed.

    #-------------------------------------------------------------------------
    def SetLangage(self,kargs) :
        """Set langage for tagger.

        Internal use.
        """
        #----- Find langage to tag.
        if kargs.has_key("TAGLANG") :
            self.lang = kargs["TAGLANG"]
        elif os.environ.has_key("TAGLANG") :
            self.lang = os.environ["TAGLANG"]
        else :
            self.lang = "en"
        self.lang = self.lang[:2].lower()
        if not g_langsupport.has_key(self.lang) :
            logger.error("Langage %s not supported.",self.lang)
            raise TreeTaggerError,"Unsupported langage code: "+self.lang
        logger.info("lang=%s",self.lang)
        self.langsupport = g_langsupport[self.lang]

    #-------------------------------------------------------------------------
    def SetTagger(self,kargs) :
        """Set tagger paths, files, and options.

        Internal use.
        """
        #----- Find TreeTagger directory.
        if kargs.has_key("TAGDIR") :
            self.tagdir = kargs["TAGDIR"]
        elif os.environ.has_key("TAGDIR") :
            self.tagdir = os.environ["TAGDIR"]
        else :
            logger.error("Cant locate TreeTagger directory via TAGDIR.")
            raise TreeTaggerError,"Cant locate TreeTagger directory via TAGDIR."
        self.tagdir = os.path.abspath(self.tagdir)
        if not os.path.isdir(self.tagdir) :
            logger.error("Bad TreeTagger directory: %s",self.tagdir)
            raise TreeTaggerError,"Bad TreeTagger directory: "+self.tagdir
        logger.info("tagdir=%s",self.tagdir)

        #----- Set subdirectories.
        self.tagbindir = os.path.join(self.tagdir,"bin")
        self.tagcmddir = os.path.join(self.tagdir,"cmd")
        self.taglibdir = os.path.join(self.tagdir,"lib")

        #----- Set binary by platform.
        if sys.platform == "win32" :
            self.tagbin = os.path.join(self.tagbindir,self.langsupport["binfile-win"])
        elif sys.platform == "linux2" :
            self.tagbin =os.path.join(self.tagbindir,self.langsupport["binfile-lin"])
        elif sys.platform == "darwin" :
            self.tagbin =os.path.join(self.tagbindir,self.langsupport ["binfile-darwin"])
        else :
            logger.error("TreeTagger binary name undefined for platform %s",
                                                                sys.platform)
            raise TreeTaggerError,"TreeTagger binary name undefined "+\
                                  "for platform "+sys.platform
        if not os.path.isfile(self.tagbin) :
            logger.error("TreeTagger binary invalid: %s", self.tagbin)
            raise TreeTaggerError,"TreeTagger binary invalid: " + self.tagbin
        logger.info("tagbin=%s",self.tagbin)

        #----- Find options.
        if kargs.has_key("TAGOPT") :
            self.tagopt = kargs["TAGOPT"]
        elif os.environ.has_key("TAGOPT") :
            self.tagopt = os.environ["TAGOPT"]
        else :
            self.tagopt = "-token -lemma -sgml"
        # this may seem wrong because it removes the sgml when there
        # is no -sgml flag, but 'fixing' it did screw everythig up (MV
        # 11/09/07)
        if self.tagopt.find("-sgml") == -1 :
            self.tagopt = "-sgml "+self.tagopt
            self.removesgml = True
        else :
            self.removesgml = False
        logger.info("tagopt=%s",self.tagopt)

        #----- Find parameter file.
        if kargs.has_key("TAGPARFILE") :
            self.tagparfile = kargs["TAGPARFILE"]
        elif os.environ.has_key("TAGPARFILE") :
            self.tagparfile = os.environ["TAGPARFILE"]
        else :
            self.tagparfile = None
        # Not in previous else to manage None parameter in kargs.
        if self.tagparfile is None :
            self.tagparfile = self.langsupport["tagparfile"]
        # If its directly a visible file, then use it, else try to locate
        # it in TreeTagger library directory.
        maybefile = os.path.abspath(self.tagparfile)
        if os.path.isfile(maybefile) :
            self.tagparfile = maybefile
        else :
            maybefile = os.path.join(self.taglibdir,self.tagparfile)
            if os.path.isfile(maybefile) :
                self.tagparfile = maybefile
            else :
                logger.error("TreeTagger parameter file invalid: %s",
                                                        self.tagparfile)
                raise TreeTaggerError,"TreeTagger parameter file invalid: "+\
                                      self.tagparfile
        logger.info("tagparfile=%s",self.tagparfile)

        # TreeTagger is started later (when needed).
        self.taginput = None
        self.tagoutput = None

    #-------------------------------------------------------------------------
    def SetPreprocessor(self,kargs) :
        """Set preprocessing files, and options.

        Internal use.
        """
        #----- Find abbreviations file.
        if kargs.has_key("TAGABBREV") :
            self.abbrevfile = kargs["TAGABBREV"]
        elif os.environ.has_key("TAGABBREV") :
            self.abbrevfile = os.environ["TAGABBREV"]
        else :
            self.abbrevfile = None
        # Not in previous else to manage None parameter in kargs.
        if self.abbrevfile is None :
            self.abbrevfile = self.langsupport["abbrevfile"]
        # If its directly a visible file, then use it, else try to locate
        # it in TreeTagger library directory.
        maybefile = os.path.abspath(self.abbrevfile)
        if os.path.isfile(maybefile) :
            self.abbrevfile = maybefile
        else :
            maybefile = os.path.join(self.taglibdir,self.abbrevfile)
            if os.path.isfile(maybefile) :
                self.abbrevfile = maybefile
            else :
                logger.error("Abbreviation file invalid: %s",self.abbrevfile)
                raise TreeTaggerError,"Abbreviation file invalid: "+\
                                      self.abbrevfile
        logger.info("abbrevfile=%s",self.abbrevfile)

        #----- Read file containing list of abbrevitations.
        self.abbterms = {}
        try :
            f = open(self.abbrevfile,"rU")
            try :
                for line in f :
                    line = line.strip() # Remove blanks after and before.
                    if not line : continue  # Ignore empty lines
                    if line[0]=='#' : continue  # Ignore comment lines.
                    self.abbterms[line.lower()] = line  # Store as a dict keys.
            finally :
                f.close()
            logger.info("Read %d abbreviations from file: %s",
                                len(self.abbterms),self.abbrevfile)
        except :
            logger.error("Failure to read abbreviations file: %s",\
                                self.abbrevfile,exc_info=True)
            raise

        #----- Prefix chars at begining of string.
        self.pchar = self.langsupport["pchar"]
        if self.pchar :
            self.pchar_re = re.compile("^(["+self.pchar+"])(.*)$",
                                        re.IGNORECASE|re.VERBOSE)
        else :
            self.pchar_re = None

        #----- Suffix chars at end of string.
        self.fchar = self.langsupport["fchar"]
        if self.fchar :
            self.fchar_re = re.compile("^(.*)(["+self.fchar+"])$",
                                        re.IGNORECASE|re.VERBOSE)
            self.fcharandperiod_re = re.compile("(.*)(["+self.fchar+".])\\.$")
        else :
            self.fchar_re = None
            self.fcharandperiod_re = None
        self.pclictic = self.langsupport["pclictic"]

        #----- Character sequences to cut-off at begining of words.
        if self.pclictic :
            self.pclictic_re = re.compile("^("+self.pclictic+")(.*)",
                                            re.IGNORECASE|re.VERBOSE)
        else:
            self.pclictic_re = None

        #----- Character sequences to cut-off at end of words.
        self.fclictic = self.langsupport["fclictic"]
        if self.fclictic :
            self.fclictic_re = re.compile("(.*)("+self.fclictic+")$",
                                            re.IGNORECASE|re.VERBOSE)
        else :
            self.fclictic_re = None

        #----- Numbers recognition.
        self.number = self.langsupport["number"]
        self.number_re = re.compile(self.number,re.IGNORECASE|re.VERBOSE)

        #----- Dummy string to flush
        sentence = self.langsupport["dummysentence"]
        self.dummysequence = "\n".join(sentence.split())
        
        #----- Replacement string for 
        self.replurlexp = self.langsupport["replurlexp"]
        self.replemailexp = self.langsupport["replemailexp"]
        self.replipexp = self.langsupport["replipexp"]
        self.repldnsexp = self.langsupport["repldnsexp"]

    #--------------------------------------------------------------------------
    def StartProcess(self) :
        """Start TreeTagger processing chain.

        Internal use.
        """
        #----- Start the TreeTagger.
        tagcmd = self.tagbin+" "+self.tagopt+" "+self.tagparfile
        try :
            self.taginput,self.tagoutput = os.popen2(tagcmd)
            logger.info("Started TreeTagger from command: %s",tagcmd)
        except :
            logger.error("Failure to start TreeTagger with: %s",\
                                tagcmd,exc_info=True)
            raise

    #--------------------------------------------------------------------------
    def __del__ (self) :
        """Wrapper to be deleted.

        Cut links with TreeTagger process.
        """
        if self.taginput :
            self.taginput.close()
            self.taginput = None
        if self.tagoutput :
            self.tagoutput.close()
            self.tagoutput = None

    #--------------------------------------------------------------------------
    def TagText(self,text,numlines=False,tagonly=False,
                prepronly=False,tagblanks=False,notagurl=False,
                notagemail=False,notagip=False,notagdns=False) :
        """Tag a text and return corresponding lines.

        This is normally the method you use on this class. Other methods
        are only helpers of this one.

        @param  text: the text to tag.
        @type   text: string
        @param  numlines: indicator to keep line numbering information in
                          data flow (done via SGML tags).
        @type   numlines: boolean (default to False)
        @param  tagonly: indicator to only do TreeTagger tagging processing
                         on input.
        @type   tagonly: boolesn (default to False)
        @param  prepronly: indicator to only do preprocessing of text without
                           tagging.
        @type   prepronly: boolean (default to False)
        @param  tagblanks: indicator to keep blanks characters information in
                           data flow (done via SGML tags).
        @type   tagblanks: boolean (default to False)
        @param  notagurl: indicator to not do URL replacement.
        @type   notagurl: boolean (default to False)
        @param  notagemail: indicator to not do email address replacement.
        @type   notagemail: boolean (default to False)
        @param  notagip: indicator to not do IP address replacement.
        @type   notagip: boolean (default to False)
        @param  notagdns: indicator to not do DNS names replacement.
        @type   notagdns: boolean (default to False)
        @return: List of lines from the tagger.
        @rtype:  list of strings
        """
        # Check for incompatible options.
        if (tagblanks or numlines) and self.removesgml :
            logger.error("Line numbering/blanks tagging need use of -sgml "+\
                         "option for TreeTagger.")
            raise TreeTaggerError,"Line numbering/blanks tagging need use "+\
                                  "of -sgml option for TreeTagger."
        # Preprocess text (prepare for TreeTagger).
        if not tagonly :
            logger.debug("Pre-processing text.")
            lines = self.PrepareText(text,tagblanks=tagblanks,numlines=numlines,
                                notagurl=notagurl,notagemail=notagemail,
                                notagip=notagip,notagdns=notagdns)
        if prepronly :
            return lines

        # TreeTagger process is started at firest need.
        if self.taginput is None :
            self.StartProcess()

        # Send text to TreeTagger, get result.
        logger.debug("Tagging text.")
        t = threading.Thread(target=PipeWriter,args=(self.taginput,
                                        lines,self.dummysequence))
        t.start()

        result = []
        intext = False
        while True :
            line = self.tagoutput.readline()
            line = line.strip()
            if DEBUG : print "Read from TreeTagger:",line
            if line == STARTOFTEXT :
                intext = True
                continue
            if line == ENDOFTEXT :  # The flag we sent to identify texts.
                intext = False
                break
            if intext and line :
                if not (self.removesgml and IsSGMLTag(line)) :
                    result.append(line)

        # Synchronize to avoid possible problems.
        t.join()

        return result

    #--------------------------------------------------------------------------
    def PrepareText(self,text,tagblanks,numlines,notagurl,\
                notagemail,notagip,notagdns) :
        """Prepare a text for processing by TreeTagger.

        @param  text: the text to split into base elements.
        @type   text: string or list of strings
        @param  tagblanks: transform blanks chars into SGML tags.
        @type   tagblanks: boolean
        @param  numlines: indicator to pur tag for line numbering.
        @type   numlines: boolean
        @param  notagurl: indicator to not do URL replacement.
        @type   notagurl: boolean (default to False)
        @param  notagemail: indicator to not do email address replacement.
        @type   notagemail: boolean (default to False)
        @param  notagip: indicator to not do IP address replacement.
        @type   notagip: boolean (default to False)
        @param  notagdns: indicator to not do DNS names replacement.
        @type   notagdns: boolean (default to False)
        @return: List of lines to process as TreeTagger input.
        @rtype: list of strings (no \\n at end of line).
        """
        logger.debug("Preparing text for tagger (tagblanks=%d, "\
                    "numlines=%d).",tagblanks,numlines)

        # If necessary, add line numbering SGML tags (which will
        # be passed out as is by TreeTagger and which could be
        # used to identify lines in the flow of tags).
        if numlines :
            logger.debug("Numbering lines.")
            if isinstance(text,basestring) :
                lines = text.splitlines()
            else :
                lines = text
            newlines = []
            for num,line in enumerate(lines) :
                newlines.append(NUMBEROFLINE%(num+1,))
                newlines.append(line)
            s = " ".join(newlines)
            # Remove temporary storage.
            del lines
            del newlines
            logger.debug("Inserted line numbers as SGML tags between lines.")
        else :
            if not isinstance(text,basestring) :
                s = " ".join(text)
            else :
                s = text

        # First, we split the text between SGML tags and non SGML
        # part tags.
        logger.debug("Identifying SGML tags.")
        parts = SplitSGML(s)
        logger.debug("Splitted between SGML tags and others.")

        newparts = []
        if tagblanks:
            # If requested, replace internal blanks by other SGML tags.
            logger.debug("Replacing blanks by corresponding SGML tags.")
            for part in parts :
                if IsSGMLTag(part) :
                    newparts.append(part)
                else :
                    part = BlankToTag(part)
                    newparts.extend(SplitSGML(part))
        else :
            # Else, replace cr, lf, vt, ff, and tab characters with blanks.
            logger.debug("Replacing blanks by spaces.")
            for part in parts :
                newparts.append(BlankToSpace(part))
        parts = newparts
        logger.debug("Blanks replacement done.")

        if not notagurl :
            logger.debug("Replacing URLs.")
            newparts = []
            for part in parts :
                if IsSGMLTag(part) :
                    newparts.append(part)
                else :
                    part = UrlMatch_re.sub(self.replurlexp,part)
                    newparts.extend(SplitSGML(part))
            parts = newparts
            logger.debug("URLs replacement done.")

        if not notagemail :
            logger.debug("Replacing Emails.")
            newparts = []
            for part in parts :
                if IsSGMLTag(part) :
                    newparts.append(part)
                else :
                    part = EmailMatch_re.sub(self.replemailexp,part)
                    newparts.extend(SplitSGML(part))
            parts = newparts
            logger.debug("Emails replacement done.")

        if not notagip :
            logger.debug("Replacing IP addresses.")
            newparts = []
            for part in parts :
                if IsSGMLTag(part) :
                    newparts.append(part)
                else :
                    part = IpMatch_re.sub(self.replipexp,part)
                    newparts.extend(SplitSGML(part))
            parts = newparts
            logger.debug("IP adresses replacement done.")

        if not notagdns :
            logger.debug("Replacing DNS names.")
            newparts = []
            for part in parts :
                if IsSGMLTag(part) :
                    newparts.append(part)
                else :
                    part = DnsHostMatch_re.sub(self.repldnsexp,part)
                    newparts.extend(SplitSGML(part))
            parts = newparts
            logger.debug("DNS names replacement done.")

        # Process part by part, some parts wille be SGML tags, other dont.
        logger.debug("Splittint parts of text.")
        newparts = []
        for part in parts :
            if IsSGMLTag(part) :
                # TreeTagger process by line... a tag cannot be on multiple
                # lines (in case it occured in source text).
                part = part.replace("\n"," ")
                if DEBUG_PREPROCESS : print "Seen TAG: ",repr(part)
                newparts.append(part)
            else :
                # This is another part which need more analysis.
                newparts.extend(self.PreparePart(part))
        parts = newparts

        logger.debug("Text preprocessed, parts splitted by line.")

        return parts

    #--------------------------------------------------------------------------
    def PreparePart(self,text) :
        """Prepare a basic text.

        Prepare non-SGML text parts.

        @param  text: text of part to process.
        @type   text: string
        @return: List of lines to process as TreeTagger input.
        @rtype: list of strings
        """
        # May occur when recursively calling after splitting on dot, if there
        # are two consecutive dots.
        if not text : return []

        text = " "+text+" "

        # Put blanks before and after '...' (extract ellipsis).
        text = ellipfind_re.sub(ellipfind_subst,text)

        # Put space between punctuation ;!?:, and following text if space missing.
        text = punct1find_re.sub(punct1find_subst,text)

        # Put space between text and punctuation ;!?:, if space missing.
        text = punct2find_re.sub(punct2find_subst,text)


        # Here some script put blanks after dots (while processing : and , too).
        # This break recognition of texts like U.S.A later.

        # Cut on whitespace, and find subpart by subpart.
        # We put prefix subparts in the prefix list, and suffix subparts in the
        # suffix list, at the end prefix + part + suffix are added to newparts.
        parts = text.split()
        newparts = []
        for part in parts :
            if DEBUG_PREPROCESS : print "Processing part:",repr(part)
            # For single characters or ellipsis, no more processing.
            if len(part)==1 or part == "..." :
                newparts.append(part)
                continue
            prefix = []
            suffix = []
            # Separate punctuation and parentheses from words.
            while True :
                finished = True         # Exit at end if no match.
                # cut off preceding punctuation
                if self.pchar_re != None :
                    matchobj = self.pchar_re.match(part)
                    if matchobj != None :
                        if DEBUG_PREPROCESS :
                            print "Splitting preceding punct.",matchobj.group(1)
                        prefix.append(matchobj.group(1))    # First pchar.
                        part = matchobj.group(2)            # Rest of text.
                        finished = False
                # cut off trailing punctuation
                if self.fchar_re != None :
                    matchobj = self.fchar_re.match(part)
                    if matchobj != None :
                        if DEBUG_PREPROCESS :
                            print "Splitting following punct:",matchobj.group(2)
                        suffix.insert(0,matchobj.group(2))
                        part = matchobj.group(1)
                        finished = False
                # cut off trailing periods if punctuation precedes
                if self.fcharandperiod_re != None :
                    matchobj = self.fcharandperiod_re.match(part)
                    if matchobj != None :
                        if DEBUG_PREPROCESS :
                            print "Splitting dot after following punct: ."
                        suffix.insert(0,".")                        # Last dot.
                        part = matchobj.group(1)+matchobj.group(2)  # Other.
                        finished = False
                # Exit while loop if no match in regular expressions.
                if finished : break

            # Process with the dot problem...
            # Look for acronyms of the form U.S.A. or U.S.A
            if acronymexpr_re.match(part) :
                if DEBUG_PREPROCESS : print "Found acronym:",part
                # Force final dot to have homogeneous acronyms.
                if part[-1] != '.' : part += '.'
                newparts.extend(prefix)
                newparts.append(part)
                newparts.extend(suffix)
                continue

            # identify numbers.
            matchobj = self.number_re.match(part)
            if matchobj!=None :
                # If there is only a dot after the number which is not
                # recognized, then split it and take the number.
                if matchobj.group()==part[:-1] and part[-1]=="." :
                    part = part[:-1]    # Validate next if... process number.
                    suffix.insert(0,".")
                if matchobj.group()==part : # Its a *full* number.
                    if DEBUG_PREPROCESS : print "Found number:",part
                    newparts.extend(prefix)
                    newparts.append(part)
                    newparts.extend(suffix)
                    continue

            # Remove possible trailing dots.
            while part and part[-1]=='.' :
                if DEBUG_PREPROCESS : print "Found trailing dot: ."
                suffix.insert(0,".")
                part = part[:-1]

            # handle explicitly listed tokens
            if self.abbterms.has_key(part.lower()) :
                if DEBUG_PREPROCESS : print "Found explicit token:",part
                newparts.extend(prefix)
                newparts.append(part)
                newparts.extend(suffix)
                continue

            # If still has dot, split around dot, and process subpart by subpart
            # (call this method recursively).
            # 2004-08-30 - LP
            # As now DNS names and so on are pre-processed, there should no
            # longer be things like www.limsi.fr, remaining dots may be parts
            # of names as in J.S.Bach. 
            # So commented the code out (keep it here).
            #if "." in part :
            #    if DEBUG_PREPROCESS :
            #        print "Splitting around remaining dots:",part
            #    newparts.extend(prefix)
            #    subparts = part.split(".")
            #    for index,subpart in enumerate(subparts) :
            #        newparts.extend(self.PreparePart(subpart))
            #        if index+1<len(subparts) :
            #            newparts.append(".")
            #    newparts.extend(suffix)
            #    continue

            # cut off clictics
            if self.pclictic_re != None :
                retry = True
                while retry :
                    matchobj = self.pclictic_re.match(part)
                    if matchobj != None :
                        if DEBUG_PREPROCESS : 
                            print "Splitting begin clictic:",matchobj.group(1),\
                                                             matchobj.group(2)
                        prefix.append(matchobj.group(1))
                        part = matchobj.group(2)
                    else :
                        retry = False

            if self.fclictic_re != None :
                retry = True
                while retry :
                    matchobj = self.fclictic_re.match(part)
                    if matchobj != None :
                        if DEBUG_PREPROCESS :
                            print "Splitting end clictic:",matchobj.group(1),\
                                                           matchobj.group(2)
                        suffix.append(matchobj.group(2))
                        part = matchobj.group(1)
                    else :
                        retry = False

            newparts.extend(prefix)
            newparts.append(part)
            newparts.extend(suffix)

        return newparts


#==============================================================================
# XML names syntax:
SGML_name = r"[_A-Za-zÀ-ÿ][-_\.:A-Za-zÀ-ÿ0-9]*"
# XML tags (as group, with parenthesis !!!).
SGML_tag = r"""
        (
        <!-- .*? -->                # XML/SGML comment
            |                           # -- OR --
        <[!?/]?"""+SGML_name+"""    # Start of tag/directive
            [^>]*                   # +Process all up to the first >
            >                       # +End of tag/directive
        )"""
SGML_tag_re = re.compile(SGML_tag,re.IGNORECASE|re.VERBOSE|re.DOTALL)
def IsSGMLTag(text) :
    """Test if a text is - completly - a SGML tag.

    @param  text: the text to test.
    @type  text: string
    @return: True if its an SGML tag.
    @rtype: boolean
    """
    return SGML_tag_re.match(text)


#==============================================================================
def SplitSGML(text) :
    """Split a text between SGML-tags and non-SGML-tags parts.

    @param  text: the text to split.
    @type  text: string
    @return: List of parts in their apparition order.
    @rtype: list of string.
    """
    # Simply split on XML tags recognized by regular expression.
    return SGML_tag_re.split(text)


#==============================================================================
BlankToTag_tags = [(' ',TAGSPACE),('\t',TAGTAB),('\n',TAGLF),
                   ('\r',TAGCR),('\v',TAGVT),('\f',TAGFF)]
def BlankToTag(text) :
    """Replace blanks characters by corresponding SGML tags.

    @param  text: the text to transform from blanks.
    @type  text: string
    @return: Text with replacement done.
    @rtype: string.
    """
    for c,r in BlankToTag_tags :
        text = text.replace(c,r)
    return text


#==============================================================================
BlankToSpace_table = string.maketrans (u"\r\n\t\v\f",u"     ")
def BlankToSpace(text) :
    """Replace blanks characters by real spaces.

    May be good to prepare for regular expressions & Co based on whitespaces.

    @param  text: the text to clean from blanks.
    @type  text: string
    @return: List of parts in their apparition order.
    @rtype: list of string.
    """
    return text.translate(BlankToSpace_table)


#==============================================================================
# Not perfect, but work mostly.
# From http://www.faqs.org/rfcs/rfc1884.html
# Ip_expression = r"""
#     (?:                         # ----- Classic dotted IP V4 address -----
#         (?:[0-9]{1,3}\.){3}[0-9]{1,3}
#     )
#             |
#     (?:                         # ----- IPV6 format. -----
#       (?:[0-9A-F]{1,4}:){1,6}(?::[0-9A-F]{1,4}){1,6}        # :: inside
#                 |
#       (?:[0-9A-F]{1,4}:){1,6}:                              # :: at end
#                 |
#       :(?::[0-9A-F]{1,4}){1,6}                              # :: at begining
#                 |
#       (?:[0-9A-F]{1,4}:){7}[0-9A-F]{1,4}                    # Full IPV6
#                 |
#                 ::                                          # Empty IPV6
#     )
#         (?:(?:\.[0-9]{1,3}){3})?    # Followed by a classic IPV4.
#                                     # (first number matched by previous rule...
#                                     #  which may match hexa number too (bad) )
# """
# 2004-08-30 - LP
# As IP V6 can interfer with :: in copy/past code, and as its (currently)
# not really common, I comment out the IP V6 recognition.
Ip_expression = r"""
    (?:                         # ----- Classic dotted IP V4 address -----
        (?:[0-9]{1,3}\.){3}[0-9]{1,3}
    )
    """
IpMatch_re = re.compile(r"("+Ip_expression+")",
                re.VERBOSE|re.IGNORECASE)


#==============================================================================
DnsHost_expression = r"""
        (?:
            [-a-z0-9]+\.                # Host name
            (?:[-a-z0-9]+\.)*           # Intermediate domains
                                        # And top level domain below

            (?:
            com|edu|gov|int|mil|net|org|            # Common historical TLDs
            biz|info|name|pro|aero|coop|museum|     # Added TLDs
            arts|firm|info|nom|rec|shop|web|        # ICANN tests...
            asia|cat|jobs|mail|mobi|post|tel|
            travel|xxx|
            glue|indy|geek|null|oss|parody|bbs|     # OpenNIC
            localdomain|                            # Default 127.0.0.0
                    # And here the country TLDs
            ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|
            ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|
            ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|
            de|dj|dk|dm|do|dz|
            ec|ee|eg|eh|er|es|et|
            fi|fj|fk|fm|fo|fr|
            ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|
            hk|hm|hn|hr|ht|hu|
            id|ie|il|im|in|io|iq|ir|is|it|
            je|jm|jo|jp|
            ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|
            la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|
            ma|mc|md|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|
            na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|
            om|
            pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|
            qa|
            re|ro|ru|rw|
            sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|sv|sy|sz|
            tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|
            ua|ug|uk|um|us|uy|uz|
            va|vc|ve|vg|vi|vn|vu|
            wf|ws|
            ye|yt|yu|
            za|zm|zw
            )
                |
        localhost
        )"""
DnsHostMatch_re = re.compile(r"("+DnsHost_expression+r")",
        re.VERBOSE|re.IGNORECASE)


#==============================================================================
# See http://www.ietf.org/rfc/rfc1738.txt?number=1738
UrlMatch_expression = r"""(
                # Scheme part
        (?:ftp|https?|gopher|mailto|news|nntp|telnet|wais|file|prospero):
                # IP Host specification (optionnal)
        (?:// (?:[-a-z0-9_;?&=](?::[-a-z0-9_;?&=]*)?@)?   # User authentication.
             (?:(?:"""+DnsHost_expression+r""")
                        |
                (?:"""+Ip_expression+""")
              )
              (?::[0-9]+)?      # Port specification
        /)?
                # Scheme specific extension.
        (?:[-a-z0-9;/?:@=&\$_.+!*'(~#%,]+)*
        )"""
UrlMatch_re = re.compile(UrlMatch_expression, re.VERBOSE|re.IGNORECASE)


#==============================================================================
EmailMatch_expression = r"""(
            [-a-z0-9._']+@
            """+DnsHost_expression+r"""
            )"""
EmailMatch_re = re.compile(EmailMatch_expression,re.VERBOSE|re.IGNORECASE)


#==============================================================================
help_string = """treetaggerwrapper.py

Usage:
    python treetaggerwrapper.py [options] input_file

Read data from specified files, process them one by one, sending data to
TreeTagger, and write TreeTagger output to files with ."""+RESEXT+""" extension.

    python treetaggerwrapper.py [options] --pipe < input_stream > output_stream

Read all data from the input stream, then preprocess it, send it to
TreeTagger, and write  TreeTagger output to output stream.

Options:
    -p          preprocess only (no tagger)
    -t          tagger only (no preprocessor)
    -n          number lines of original text as SGML tags
    -b          transform blanks into SGML tags
    -l lang     langage to tag (default to en)
    -d dir      TreeTagger base directory
Other options:
    --ttparamfile fic       file to use as TreeTagger parameter file.
    --ttoptions "options"   TreeTagger specific options (cumulated).
    --abbreviations fic     file to use as abbreviations terms.
    --pipe                  use pipe mode on standard input/output (no need of 
                            file on command line).

This Python module can be used as a tool for a larger project by creating a
TreeTagger object and using its TagText method.
If you dont wants to have to specify TreeTagger directory each time, you
can setup a TAGDIR environment variable containing TreeTagger installation
directory path.

Note: When numbering lines, you must ensure that SGML/XML tags in your data
file doesn't split around lines (else you will get line numberning tags into
your text tags... with bad result on tags recognition by regular expression).

Written by Laurent Pointal <laurent.pointal@limsi.fr> for CNRS-LIMSI.
"""
def main(*args) :
    """Test/command line usage code.
    """
    if args and args[0].lower() in ("-h","h","--help","-help","help",
                                    "--aide","-aide","aide","?"):
        print help_string
        sys.exit(0)

    # Set default, then process options.
    numlines=tagonly=prepronly=tagblanks=pipemode=False
    tagbuildopt = {}
    optlist,args = getopt.getopt(args, 'ptnl:f:b',["abbreviations=",
                                "ttparamfile=","ttoptions=","pipe"])
    for opt,val in optlist :
        if opt=='-p' :
            prepronly = True
        elif opt=='-t' :
            tagonly = True
        elif opt=='-n' :
            numlines = True
        elif opt=='-l' :
            tagbuildopt["TAGLANG"] = val
        elif opt=='-b' :
            tagblanks = True
        elif opt=='-d' :
            tagbuildopt["TAGDIR"]=val
        elif opt=="--ttparamfile" :
            tagbuildopt["TAGPARFILE"]=val
        elif opt=="--ttoptions" :
            tagbuildopt["TAGOPT"] = tagbuildopt.get("TAGOPT","")+" "+val
        elif opt=="--abbreviations" :
            tagbuildopt["TAGABBREV"]=val
        elif opt=="--pipe" :
            pipemode=True

    # Find files to process.
    files = []
    for f in args :
        files.extend(glob.glob(f))

    if pipemode and files :
        print help_string
        return -1

    if DEBUG : print "files to process:",files
    tagger = TreeTagger (**tagbuildopt)

    if pipemode :
        logger.info("Processing with stdin/stdout, reading input.")
        text = sys.stdin.read()
        logger.info("Processing with stdin/stdout, tagging.")
        res = tagger.TagText(text,numlines,tagonly,prepronly,tagblanks)
        logger.info("Processing with stdin/stdout, writing to stdout.")
        sys.stdout.write("\n".join(res))
        logger.info("Processing with stdin/stdout, finished.")
    else :

        for f in files :
            logger.info("Processing with file %s, reading input.",f)
            text = open(f,"rU").read()
            logger.info("Processing with file %s, tagging.",f)
            res = tagger.TagText(text,numlines,tagonly,prepronly,tagblanks)
            logger.info("Processing with file %s, writing to %s.%s.",f,f,RESEXT)
            open(f+"."+RESEXT,"wU").write("\n".join(res))
            logger.info("Processing with file %s, finished.",f)

    return 0

#==============================================================================
if __name__ == "__main__" :
    if DEBUG :
        # If debug is active, we log to a treetaggerwrapper.log file, and to
        # stdout too. If you wants to log for long time process, you may
        # take a look at RotatingFileHandler.
        hdlr = logging.FileHandler('./treetaggerwrapper.log')
        hdlr2 = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
                            'T%(thread)d %(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        hdlr2.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.addHandler(hdlr2)
        logger.setLevel(logging.DEBUG)
    sys.exit(main(*(sys.argv[1:])))


