DEBUG_BAYES = 0

# Specify at which frequency training data are allowed to have an
# impact on sense disambiguation
MINIMAL_FREQUENCY = 2.0


class DisambiguationError(LookupError):
    """Use a special exception class to distinguish general KeyErrors
    from errors due to failed disambiguation. """
    pass


class BayesEventRecognizer:

    def __init__(self, senseProbs, condProbs):
        self.senseProbs = senseProbs
        self.condProbs = condProbs


    def isEvent(self, nominalForm, context):

        self.debug("BayesEventRecognizer.isEvent("+nominalForm+")")
        self.context = context
        self.nominalForm = nominalForm

        # retrieve probability data and get event and non-event
        # probabilities
        
        try:
            senseProbData = self.senseProbs[nominalForm]
        except KeyError:
            senseProbData = [0.0, 0.0]
        self.debug("  " + str(senseProbData))

        frequency = senseProbData[0] + senseProbData[1]
        if frequency < MINIMAL_FREQUENCY:
            self.debug("  Sparse data: "+nominalForm)
            raise DisambiguationError('sparse data for "' + nominalForm + '"')

        probEvent = senseProbData[1] / frequency
        probNonEvent = 1 - probEvent
        self.debug("  " + str(probEvent) + " > " + str(probNonEvent))

        if probEvent == 1:
            return True
        if probNonEvent == 1:
            return False

        # adjust probablities with probabilities of contextual
        # elements, ignore contexts for which we have no data
        
        for contextForm in context:
            try:
                contextData = self.condProbs[nominalForm][contextForm]
                self.debug("  "+contextForm+": "+str(contextData))
                probEvent *= contextData[1]
                probNonEvent *= contextData[0]
            except KeyError:
                pass

        self.debug("  " + str(probEvent) + " > " + str(probNonEvent))
        return probEvent > probNonEvent


    def debug(self, string):
        if DEBUG_BAYES: print string
