class Event:

    def __init__(self, gramCh):
        tokenList = [gramCh.head]
        self.tokenList = tokenList
        self.attrs = {
            "eid": None,
            "class": None
            }
        self.instanceList = []
        self.addInstance()
        
        self.setAttribute("class", gramCh.evClass)
        self.setAttribute("tense", gramCh.tense)
        self.setAttribute("aspect", gramCh.aspect)
        self.setAttribute("pos", gramCh.nf_morph)
        if gramCh.modality != 'NONE':
            self.setAttribute("modality", gramCh.modality)
        if gramCh.polarity != 'POS':
            self.setAttribute("polarity", "NEG")
            
    def setAttribute(self, attr, value):
        if attr == "class":
            self.attrs["class"] = value
        else:
            for instance in self.instanceList:
                instance.setAttribute(attr, value)
            
    def addInstance(self, instance = None):
        if instance is None: instance = Instance(self)
        self.instanceList.append(instance) 
    
    #this method is here for backwards compatibility.
    #use setAttribute() now
    def setClass(self, value):
        self.attrs["class"] = value


class Instance:
    def __init__(self, event):
        self.event = event
        self.attrs = { 
            "eiid": None,
            "eventID": None,
            "signalID": None,
            "cardinality": None,
            "modality": None,
            "polarity": "POS",
            "tense": "NONE",
            "aspect": "NONE",
            "pos": "NONE"
            }

    def setAttribute(self, attr, value):
        if self.attrs.has_key(attr):
            self.attrs[attr] = value
        else:
            raise Error("no such attribute: "+attr)
