"""Classes and methods for converting formats in the TARSQI preprocessing pipeline
    
"""

# NOTE: string only used for strip, change this deprecated use of
# strip (MV)
import sys, string, re


def normalizeXML(word):
    """Returns a string with occurrences of '&', '<' and '>' replaced with
    with '&amp;', '&lt;' and '&gt;' respectively.
    Arguments
       word - a string"""
    word = re.sub('&', '&amp;', word)
    word = re.sub('<', '&lt;', word)
    word = re.sub('>', '&gt;', word)
    return word
                
def normalizePOS(pos):
    if pos == 'SENT':
        pos ='.'
    elif pos[0] == 'V':
        if pos[1] in ['V', 'H']:
            if len(pos) > 2:
                rest = pos[2:]
            else: rest = ''
            pos = 'VB' + rest
    elif pos == "NP":
        pos = "NNP"
    # new version of treetagger changed the tag for 'that'
    elif pos == 'IN/that':
        pos = 'IN'
    return pos
        

class Conversor:
    def __init__(self, inf, outf):
        self.infile = open(inf, 'r')
        self.outfile = open(outf, 'w')

    def convert(self):
        pass

    def closeFiles(self):
        self.infile.close()
        self.outfile.close()

class Tokenizer2treeTagger(Conversor):
    """Given a tokenized text as input,
    it verticalizes it and add <s> tags
    (but not </s> --treeTagger doesn't recognize them.
    """
    def __init__(self, inf, outf):
        Conversor.__init__(self, inf, outf)

    def convert(self):    
        text = self.infile.readlines()
        for line in text:
            if line == "\n":
                #print "EMPTY LINE"
                pass
            else:
                lineList = string.split(line)
                self.outfile.write("<s>")
                for item in lineList:
                    self.outfile.write("\n"+item)
                self.outfile.write("\n")


class TreeTagger2chunkerMarc(Conversor):
    """Given a verticalized text, tagged by treetagger
    in the following format:
            word\tPOS\tlemma\n
    it generates a sequential output, where each word is
    tagged as follows: word/POS\b
    Tags for the begin of sentence are replaced for \n.
    """
    def __init__(self, inf, outf):
        Conversor.__init__(self, inf, outf)

    def convertSentenceTag(self):
        self.outfile.write('\n')

    def printLine(self, line):
        lineList = string.split(string.strip(line, '\n'))
        if len(lineList) == 3:
            [word, pos, stem] = lineList 
            #if stem == '<unknown>': stem = 'UNKNOWN'
            #lex = '<lex pos="'+pos+'" stem="'+stem+'>'+word+'</lex> '
            word = normalizeXML(word)
            pos = normalizePOS(pos)
            lex = word+"/"+pos+" "
            self.outfile.write(lex)
        else:
            print "ERROR length list:", lineList
            sys.exit()
               
    def convert(self):
        firstLine = 1
        line = self.infile.readline()
        while line != '':
            if line == '<s>\n':
                if firstLine: firstLine = 0
                else: self.convertSentenceTag()
            elif line == '\n': pass
            else: self.printLine(line)
            line = self.infile.readline()
        self.outfile.write('\n')
        

class TreeTagger2chunkerBen(Conversor):  #Ben's chunker
    """Given a verticalized text, tagged by treetagger
    in the following format:
            word\tPOS\tlemma
    it generates a sequential output, where each word is
    tagged as follows: <lex pos='POS' stem='lemma'>word</lex>.
    Tags for the ending of sentence are also introduced.
    """
    def __init__(self, inf, outf):
        Conversor.__init__(self, inf, outf)

    def printLine(self, line):
        lineList = string.split(string.strip(line, '\n'))
        if len(lineList) == 3:
            [word, pos, stem] = lineList 
            #if stem == '<unknown>': stem = 'UNKNOWN'
            #lex = '<lex pos="'+pos+'" stem="'+stem+'>'+word+'</lex> '
            word = normalizeXML(word)
            pos = normalizePOS(pos)
            lex = '<lex pos="'+pos+'">'+word+'</lex> '
            self.outfile.write(lex)
        else:
            print "ERROR length list:", lineList
            sys.exit()
               
    def print1SentenceTag(self):
        self.outfile.write('<s>')
        
    def print2SentenceTags(self):
        self.outfile.write('</s>\n<s>')
        
    def convert(self):
        firstLine = 1
        self.outfile.write('<DOC>\n')
        line = self.infile.readline()
        while line != '':
            if line == '<s>\n':
                if firstLine:
                    self.print1SentenceTag()
                    firstLine = 0
                else: self.print2SentenceTags()
            elif line == '\n': pass
            else: self.printLine(line)
            line = self.infile.readline()
        self.outfile.write('</s>\n</DOC>')


class OLD_ChunkerMarc2tarsqi(Conversor):
    def __init__(self, inf, outf):
        Conversor.__init__(self, inf, outf)

    def decompose(self, item):
        beginChk = ''
        endChk = ''
        if item[:4] in ['<VG>', '<NG>']:
            beginChk = item[:4]
            item = item[4:]
        if item[-5:] in ['</VG>', '</NG>']:
            endChk = item[-5:]
            item = item[:-5]
        if item =='<TEXT>':
            word = item
            pos = ''
        elif item =='</TEXT>':
            word = item
            pos = ''
        elif item == '//SYM':
            word = '/'
            pos = 'SYM'
        else:
            # may need to trap some other thingies here
            #print string.split(item, '/')
            print item
            [word, pos] = string.split(item, '/')
        word = normalizeXML(word)
        return (beginChk, word, pos, endChk)
        
    def convertSentence(self, line):
        line = string.strip(line, "/n")
        lineList = string.split(line)
        for item in lineList:
            (begChk, word, pos, endChk) = self.decompose(item)
            if pos:
                lex = begChk+'<lex pos="'+pos+'">'+word+'</lex>'+endChk+' '
                self.outfile.write(lex)

    def convert(self):
        #self.outfile.write("<TEXT>")
        line = self.infile.readline()
        while line != '':
            if line != "\n":
                self.outfile.write('<s>')
                self.convertSentence(line)
                self.outfile.write('</s>\n')
            else: pass
            line = self.infile.readline()
        #self.outfile.write("</TEXT>")


class ChunkerMarc2tarsqi(Conversor):

    """ """
    def __init__(self, inf, outf):
        Conversor.__init__(self, inf, outf)

    def decompose(self, item):
        beginChk = ''
        endChk = ''
        #print item, ' ==> ', 
        if item[:4] in ['<VG>', '<NG>']:
            beginChk = item[:4]
            item = item[4:]
        if item[-5:] in ['</VG>', '</NG>']:
            endChk = item[-5:]
            item = item[:-5]
        if item =='<TEXT>':
            word = item
            pos = ''
        elif item =='</TEXT>':
            word = item
            pos = ''
        elif item == '//SYM':
            word = '/'
            pos = 'SYM'
        elif '>' in item:
            # get rid of tags
            (crap, item) = item.split('>')
            (word, pos) = item.split('/')
        else:
            try:
                [word, pos] = string.split(item, '/')
            except ValueError:
                # ignore single tokens, these result from tokenizer
                # problems with tags
                (word, pos) = ('', None)
        word = normalizeXML(word)
        #print word, pos
        return (beginChk, word, pos, endChk)
        
    def convertSentence(self, line):
        line = string.strip(line, "/n")
        lineList = string.split(line)
        for item in lineList:
            (begChk, word, pos, endChk) = self.decompose(item)
            if pos:
                lex = begChk+'<lex pos="'+pos+'">'+word+'</lex>'+endChk+' '
                self.outfile.write(lex)

    def convert(self):
        #self.outfile.write("<TEXT>")
        line = self.infile.readline()
        while line != '':
            if line != "\n":
                self.outfile.write('<s>')
                self.convertSentence(line)
                self.outfile.write('</s>\n')
            else: pass
            line = self.infile.readline()
        #self.outfile.write("</TEXT>")


            
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__+"\n")
        sys.exit()
    else:
        tokenizer2treeTagger(sys.argv[1], sys.argv[2])
      
        
        
