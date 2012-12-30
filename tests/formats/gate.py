#!/usr/bin/env python

import unittest
from ternip.formats.gate import GateDocument
from ternip.timex import Timex

class GateDocumentTest(unittest.TestCase):
    
    def test_get_sents(self):
        t = GateDocument("""This	POS	B	20101010
is	POS	I
a	POS	I
sentence	POS	I
.	.	I
And	POS	B
a	POS	I
second	POS	I
sentence	POS	I
.	POS	I
Outside	POS	O""")
        self.assertEquals(t.get_sents(), [[('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set()), ('sentence', 'POS', set()), ('.', '.', set())], [('And', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence', 'POS', set()), ('.', 'POS', set()), ], [('Outside', 'POS', set())]])
    
    def test_get_dct_sents(self):
        t = GateDocument("""This	POS	B	20101010
is	POS	I
a	POS	I
sentence	POS	I
.	.	I
And	POS	B
a	POS	I
second	POS	I
sentence	POS	I
.	POS	I
Outside	POS	O""")
        self.assertEquals(t.get_dct_sents(), [[('20101010', 'DCT', set())]])
    
    def test_reconcile_sents(self):
        d = GateDocument("""This	POS	B	20101010
is	POS	I
a	POS	I
sentence	POS	I
.	.	I
And	POS	B
a	POS	I
second	POS	I
sentence	POS	I
.	POS	I
Outside	POS	O""")
        t = Timex(id=1)
        d.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t])), ('sentence', 'POS', set([t])), ('.', '.', set())], [('And', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence', 'POS', set()), ('.', 'POS', set()), ], [('Outside', 'POS', set())]])
        self.assertEquals(str(d), """This		
is		
a	id=t1	
sentence		t1
.		
And		
a		
second		
sentence		
.		
Outside		
""")
    
    def test_reconcile_sents_attrs(self):
        t1 = Timex(id=1, type='date')
        t2 = Timex(id=2)
        t3 = Timex(id=3)
        t1.value = "20100710"
        t1.mod = "BEFORE"
        t1.freq = "1M"
        t1.comment = "Test"
        t1.granuality = "1D"
        t1.non_specific = True
        t1.quant = 'EVERY'
        t1.temporal_function = True
        t1.document_role = 'MODIFICATION_TIME'
        t1.begin_timex = t1
        t1.end_timex = t2
        t1.context = t3
        d = GateDocument("""This	POS	B	20101010
is	POS	I
a	POS	I
sentence	POS	I
.	.	I
And	POS	B
a	POS	I
second	POS	I
sentence	POS	I
.	POS	I
Outside	POS	O""")
        d.reconcile([[('This', 'POS', set()), ('is', 'POS', set()), ('a', 'POS', set([t1])), ('sentence', 'POS', set([t1])), ('.', '.', set())], [('And', 'POS', set()), ('a', 'POS', set()), ('second', 'POS', set()), ('sentence', 'POS', set()), ('.', 'POS', set()), ], [('Outside', 'POS', set())]])
        self.assertEquals(str(d), """This		
is		
a	id=t1,value=20100710,type=DATE,mod=BEFORE,freq=1M,quant=EVERY,temporalFunction=true,functionInDocument=MODIFICATION_TIME,beginPoint=t1,endPoint=t2,anchorTimeID=t3	
sentence		t1
.		
And		
a		
second		
sentence		
.		
Outside		
""")