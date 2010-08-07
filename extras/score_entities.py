"""

== score_entities.py

Script to calculate scores for events and timexes, both for the extents and the
attributes. Prints the counts and the calculated statistics to the standard output.


== usage

    % python score_extents.py tokens extent_key extent_res attr_key attribute_res

       tokens      the base-segmentation.tab file
       extent_key  the annotation gold standard with event or timex extents
       extent_res  the response file from the system with event or timex extents
       attr_key    the annotation gold standard with event or timex attributes
       attr_res    the response file from the system with event or timex attributes

    The response files need to have the sdame format as the key files. Some hickups, like
    empty lines will not break the script, but may influence the scores.

    
== extents

The script counts include true positives (tp), true negatives (tn), false positives (fp)
and false negatives (fn). Counts are on a token by token basis. That is, if the key
contains a timex 'Sunday morning', and the response has 'morning', then there will be one
true positive and one false negative (the latter because 'Sunday' was not recognized as
part of the timex).

The statistics calculated are:

    precision  = tp / (tp + fp)
    recall     = tp / (tp + fn)
    accuracy   = (tp + tn) / (tp + tn + fp + fn)
    f1-measure = 2 * (precision * recall) / (precision + recall)

The accuracy is of limited use due to the typically large number of true negatives.


== attributes

Attribtues are compared only for those events and timexes where the key and the response
are identical, that is, systems are not penalized for their attribute scores if the
extents do not match up with the gold standard.

The scores are calculated for each attribute by counting correct and incorrect values and
simply dividing the correct values by the total values. The score is between 0 and 1.

Systems are not penalized for adding attributes that are not in the gold standard.

"""


import sys
import re


def score_entities(tokens, key_extents, response_extents, key_attrs, response_attrs):

    fh1 = open(tokens)
    fh2 = open(key_extents)
    fh3 = open(response_extents)
    fh4 = open(key_attrs)
    fh5 = open(response_attrs)
    

    scores = Scores()
    
    for line in fh1:
        try:
            file, sid, tid = line.strip("\n").split("\t")[0:3]
            scores.initialize(file, sid, tid)
        except ValueError:
            pass
        
    for line in fh2:
        try:
            file, sid, tid = line.strip("\n").split("\t")[0:3]
            scores.add_key_extent_data(file, sid, tid)
        except ValueError:
            pass

    for line in fh3:
        try:
            file, sid, tid = line.strip("\n").split("\t")[0:3]
            scores.add_response_extent_data(file, sid, tid)
        except ValueError:
            pass

    for line in fh4:
        try:
            fields = line.strip("\n").split("\t")
            file, sid, tid = fields[0:3]
            attr, val = fields[6:8]
            scores.add_key_attribute_data(file, sid, tid, attr, val)
        except ValueError:
            pass

    for line in fh5:
        try:
            fields = line.strip("\n").split("\t")
            file, sid, tid = fields[0:3]
            attr, val = fields[6:8]
            scores.add_response_attribute_data(file, sid, tid, attr, val)
        except ValueError:
            pass
    
    fh1.close()
    fh2.close()
    fh3.close()
    fh4.close()
    fh5.close()
    
    scores.calculate_extent_scores()
    scores.calculate_attribute_scores()
    
    print
    #scores.pp_data()
    #scores.pp_counts()
    scores.pp_stats()
    

class Scores:

    def __init__(self):
        self.data = {}
        self.tp, self.fp, self.tn, self.fn = 0.0, 0.0, 0.0, 0.0
        self.precision, self.recall, self.fmeasure,self.accuracy = None, None, None, None
        self.attribute_counts = {}
        self.attribute_scores = {}

    def initialize(self, file, sid, tid):
        position = "%s-%s-%s" % (file, sid, tid)
        self.data[position] = [0,0,{},{}]

    def add_key_extent_data(self, file, sid, tid):
        position = "%s-%s-%s" % (file, sid, tid)
        self.data[position][0] = 1
                
    def add_response_extent_data(self, file, sid, tid):
        position = "%s-%s-%s" % (file, sid, tid)
        self.data[position][1] = 1

    def add_key_attribute_data(self, file, sid, tid, attr, val):
        position = "%s-%s-%s" % (file, sid, tid)
        if attr == 'value': val = re.sub(r'(-|:)', '', val) # convert to ISO basic
        self.data[position][2][attr] = val
                
    def add_response_attribute_data(self, file, sid, tid, attr, val):
        position = "%s-%s-%s" % (file, sid, tid)
        if attr == 'value': val = re.sub(r'(-|:)', '', val) # convert to ISO basic
        self.data[position][3][attr] = val

        
    def calculate_extent_scores(self):
        # collect counts...
        for k, r, a1, a2 in self.data.values():
            if k==1 and r==1: self.tp += 1
            if k==1 and r==0: self.fn += 1
            if k==0 and r==1: self.fp += 1
            if k==0 and r==0: self.tn += 1
        # and calculate
        self.precision = self.tp / (self.tp + self.fp)
        self.recall = self.tp / (self.tp + self.fn)
        self.fmeasure = 2 * (self.precision * self.recall) / (self.precision + self.recall) 
        self.accuracy = (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)

    def calculate_attribute_scores(self):
        # collect counts...
        for k, r, a1, a2 in self.data.values():
            if k==1 and r==1:
                for a,v in a1.items():
                    if not self.attribute_counts.has_key(a):
                        self.attribute_counts[a] = {'correct': 0.0, 'incorrect': 0.0}
                    if a2.get(a) == v:
                        self.attribute_counts[a]['correct'] += 1
                    else:
                        self.attribute_counts[a]['incorrect'] += 1
        # and calculate
        for attr, counts in self.attribute_counts.items():
            correct = counts['correct']
            incorrect = counts['incorrect']
            self.attribute_scores[attr] = correct / (correct + incorrect) 
        
    def pp_data(self):
        for position in self.data.keys():
            k, r, ka, ra = self.data[position]
            print "%-30s %s %s  %s %s" % (position, k, r, ka ,ra)
        print
        
    def pp_counts(self):
        print "true positives:   %s" % int(self.tp)
        print "true negatives:   %s" % int(self.tn)
        print "false positives:  %s" % int(self.fp)
        print "false negatives:  %s" % int(self.fn)
        print
        for attr, counts in self.attribute_counts.items():
            print "attribute %s: +%s -%s" % (attr, counts['correct'], counts['incorrect'])
        print
        
    def pp_stats(self):
        print "precision   %.2f" % self.precision
        print "recall      %.2f" % self.recall
        print "f1-measure  %.2f" % self.fmeasure
        print "accuracy    %.2f" % self.accuracy        
        print
        for attr, score in self.attribute_scores.items():
            print "attribute %-10s %.2f " % (attr, score)
        print


        
if __name__ == '__main__':

    tokens, key_extents, response_extents, key_attrs, response_attrs = sys.argv[1:6]
    score_entities(tokens, key_extents,response_extents, key_attrs, response_attrs)
