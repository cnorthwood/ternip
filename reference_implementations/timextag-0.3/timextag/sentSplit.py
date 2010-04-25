#!/usr/bin/env python

import sys, getopt, re, operator, fileinput, os

def findfile(path):
    """Find the file named path in the sys.path.
    Returns the full path name if found, None if not found"""
    for dirname in sys.path:
        possible = os.path.join(dirname, path)
        if os.path.isfile(possible):
            return possible
    return None

###############################
# General utility functions

def mappend(fn, list):
    "Append the results of calling fn on each element of list."
    if list: return reduce(lambda x,y: x+y, map(fn, list))
    else: return []

def group(iterator, count):
    itr = iter(iterator)
    while True:
        yield tuple([itr.next() for i in range(count)])

###############################
# Language processing functions

# Data
# Separators
reAlwaysSep = re.compile(r'''(``|[?!()";/\|,`])''')
reBeginSep0 = re.compile(r"""^(['&])""")
reBeginSep = re.compile(r"""(?<!\w)(['&])""")
reEndSep0 = re.compile(r"""([':-])$""")
reEndSep = re.compile(r"""([':-])(?!\w)""")
reSentenceBoundary = re.compile(r'''( (?:\.|\?|\!)(?: ")?(?: |$))''')
reInitials = re.compile(r'''^([A-Za-z]\.)+$''')

# English abbreviations
# I've liberalized this and reInitials to allow lowercase abbrevs
# (for all-lowercase bc/bn transcripts)
abbreviations = dict()
for line in open(findfile('english_lc.abbr')):
    abbreviations[line.strip()] = True

# Utility function for tokenization
def separatePeriod(word):
    if word.endswith('.'):
        if abbreviations.get(word.lower(), False) or reInitials.match(word):
            return word
        else:
            return word[:len(word)-1] + ' .'
    else:
        return word

# Tokenization
def tokenize(text):
    # Based on Gregory Grefenstette's gawk code from pg. 149 of:
    # @BOOK{grefen94,#AUTHOR = "Gregory Grefenstette",
    # TITLE = "Explorations in Automatic Thesaurus Discovery",
    # PUBLISHER = "Kluwer Academic Press",
    # ADDRESS= "Boston",
    # YEAR = 1994 }

    # Put blanks around characters that are unambiguous separators
    text = reAlwaysSep.sub(r''' \1 ''', text)

    # If a word is a separator in the beginning of a token,
    # separate it here
#    text = reBeginSep0.sub(r'''\1 ''', text)
    text = reBeginSep.sub(r'''\1 ''', text)

    # Idem for final separators
#    text = reEndSep0.sub(r''' \1''', text)
    text = reEndSep.sub(r''' \1''', text)

    # Split text into words on whitespace
    words = text.split()

    # For each word ending with a period,
    # separate period unless abbreviation
    words = [ separatePeriod(word) for word in words ]

    return ' '.join(words)

# Sentence splitting
def splitSentences(text):
    """Split plain text string into sentences; return a list of strings."""
    text = tokenize(text)
    # Split on sentence separators
    sentences = reSentenceBoundary.split(text)
    # Group sentences together with their terminating separators,
    # but group sequences of consecutive separators together.
    sents = [ ]
    for s in sentences:
        if sents and reSentenceBoundary.match(s):
            sents[-1] += s
        elif s:
            sents.append(s)
#    # Should I check for ' . [a-z]'? (It wouldn't work for bn.)
#    sentences = [ fragment for fragment in sentences if fragment ]
#    sents = [ sentence + ending for (sentence, ending) in group(sentences, 2) ]
#    # In case the last sentence isn't terminated.
#    if len(sentences) % 2 == 1:
#        sents.append(sentences[len(sentences)-1])
    return sents

###############################
# Command-line stuff

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=[__name__]):
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)

        if args:
            for file in args:
                text = open(file).read()
                sents = splitSentences(text)
                outFile = open(file + '.sents', 'w')
                outFile.write('\n'.join(sents))
                outFile.write('\n')
                outFile.close()
        else:
            text = ''
            for line in fileinput.input():
                text = '%s%s' % (text, line)
                sents = splitSentences(text)
                sys.stdout.write('\n'.join(sents))
                sys.stdout.write('\n')

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv))

