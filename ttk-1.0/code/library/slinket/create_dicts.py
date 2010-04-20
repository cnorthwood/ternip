import cPickle


"""
    Taking dictionaries slinkPredicates and alinkPredicates
    and converting them into pickle objects to be stored into ./Dicts/.
"""


if __name__ == "__main__":
    print "Pickling dictionaries..."
    import slinkPredicates, alinkPredicates
    Dicts = [(slinkPredicates.nounDict, "slinkNouns"),
             (slinkPredicates.adjDict, "slinkAdjs"),
             (slinkPredicates.verbDict, "slinkVerbs"),
             (alinkPredicates.nounDict, "alinkNouns"),
             (alinkPredicates.verbDict, "alinkVerbs")]
    DIR_DICTS = "Dicts/"

    for (dict, name) in Dicts:
        pickleFile = open(DIR_DICTS+name+".pickle", 'w')
        cPickle.dump(dict,pickleFile)
    print "Done."
    


