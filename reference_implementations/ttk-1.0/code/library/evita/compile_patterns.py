import cPickle
from FSA import compileOP
from evitaUncompiledPatterns import patternsGroups

"""
    Taking each list of patterns (from uncompiledPatterns.patternsGroups)
    as input, compiling the patterns into FSA, and converting the list
    into a pickle object to be stored into ./Patterns/.
"""


DIR_PATTERNS = "Patterns/"

if __name__ == "__main__":
    for (listName,patternsList) in patternsGroups:
        pickleFile = open(DIR_PATTERNS+listName+".pickle", 'w')
        toPickle = []

        for pattern in patternsList:
            toPickle.append(compileOP(pattern))
        
        cPickle.dump(toPickle,pickleFile)
