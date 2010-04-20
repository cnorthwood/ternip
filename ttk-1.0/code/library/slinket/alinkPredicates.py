from timeMLspec import INIT, CULM, TERM, CONT, REINIT

# FORWARD patterns:
#from slinketPatterns import THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report, THAT_clause_SIMPLE, THAT_clause_NOT_tensed, THAT_clause_if, IND_INTERROG
from slinketPatterns import TO_clause1, TO_clause3, TO_clause5, TO_clause7, IND_INTERROG_nonfin#TO_clause1, TO_clause2, TO_clause3, TO_clause4, TO_clause5, TO_clause6, TO_clause7, IND_INTERROG_nonfin
from slinketPatterns import ING_clause#, ABOUT_ING_clause, AGAINST_ING_clause, AT_ING_clause, FOR_ING_clause, FROM_ING_clause, IN_ING_clause, OF_ING_clause, WITH_ING_clause
from slinketPatterns import ABOUT_NPev, AT_NPev, FOR_NPev, FROM_NPev, IN_NPev, OF_NPev, ON_NPev, OVER_NPev, TO_NPev, WITH_NPev, PP_ABOUT
from slinketPatterns import NP_ev1, NP_ev2, NP_evAsSubj1, NP_evAsSubj2
from slinketPatterns import OBJCOMPL_pastPart, OBJCOMPL_adj
# BACKWARD patterns:
from slinketPatterns import Passive1, RelClauseExplic, RelClauseExplicPerfect, RelClauseRestric, RelClauseRestricPerfect
# REPORTING patterns:
#from slinketPatterns import MAINsentence


"""
Each entry in the Predicate Dictionaries has the following structure:

* KEY: the form of the predicate (eventually, er may want to think on the stem).
* VALUE: a dictionary presenting always the same pair of keys: 'forward' and 'backwards'.
  Key 'forward' stores the contexts for SLINKs that connect the main predicate with an event
  located forward in the text. Key 'backwards' has the contexts for SLINks going from the
  main predicate backwards in the text.
  The value for each of these 2 keys are always a tuple containing 2 lists:
     - List 1: Contains the different subcategorization patterns for the predicate.
               It is a list of one or more sublists. Each sublist is a set of variations
               of the same subcategorization structure (e.g., that clause with
               complementizer, without, etc.).
               It is VERY IMPORTANT that subcat patterns are sorted from the most to the
               least possible one (or an approximation of it).
     - List 2: Contains the different SLINK relType values associated to each set of
               subcategorization patterns.

"""


nounDict = {
    #BEGINNING
    "beginning" : {'forward' : ([[NP_ev1, NP_ev2, OF_NPev]], [INIT])
                 },
    "beginnings" : {'forward' : ([[NP_ev1, NP_ev2, OF_NPev]], [INIT])
                 },
    #CLOSE
    "close" : {'forward' : ([[OF_NPev]], [TERM])
               },    
    #COMPLETION
    "completion" : {'forward' : ([[OF_NPev]], [CULM])
                    },    
    #ENDING
    "ending" : {'forward' : ([[NP_ev1, NP_ev2, OF_NPev]], [TERM])
                 },    
    #OPENING
    "opening" : {'forward' : ([[NP_ev1, NP_ev2, OF_NPev]], [INIT])
                 },
    #STARTING
    "starting" : {'forward' : ([[NP_ev1, NP_ev2, OF_NPev]], [INIT])
                 },

    
    }

verbDict = {
    #BEGIN
    "begin" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5], [NP_ev1, NP_ev2]], [INIT, INIT]),
              'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect ]], [INIT])
              },
    "began" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [INIT]),
                'forward' : ([[ING_clause, TO_clause1, TO_clause5], [NP_ev1, NP_ev2]], [INIT, INIT])
                },
    "begins" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5], [NP_ev1, NP_ev2]], [INIT, INIT]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [INIT])
                 },
    "beginning" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5], [NP_ev1, NP_ev2]], [INIT, INIT]),
               'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [INIT])
               },
    "begun" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5], [NP_ev1, NP_ev2]], [INIT, INIT]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [INIT])
                },
    #BREAK
    "break" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },
    "broke" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },
    "breaking" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },
    "breaks" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },

    #CLOSE
    "close" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM])
               },
    "closed" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM])
               },
    "closing" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM])
               },
    "closes" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM])
               },

    #COMPLETE
    "complete" : {'forward' : ([[NP_ev1, NP_ev2]], [CULM]),
                  'backwards' : ([[RelClauseRestric,RelClauseRestricPerfect]], [CULM])
                  },
    "completed" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect, Passive1]], [CULM]),
                   'forward' : ([[NP_ev1, NP_ev2]], [CULM])
                   },
    "completing" : {'forward' : ([[NP_ev1, NP_ev2]], [CULM])
                    },
    "completes" : {'forward' : ([[NP_ev1, NP_ev2]], [CULM]),
                  'backwards' : ([[RelClauseRestric,RelClauseRestricPerfect]], [CULM])
                  },

    #CONTINUE
    "continue" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5, TO_clause7, NP_ev1, NP_ev2, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                  'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect ]], [CONT])
              },
    "continued" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [CONT]),
                   'forward' : ([[ING_clause, TO_clause1, TO_clause5, TO_clause7, NP_ev1, NP_ev2, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])
                   },
    "continues" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5, TO_clause7, NP_ev1, NP_ev2, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                   'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [CONT])
                 },
    "continuing" : {'forward' : ([[ING_clause, TO_clause1, TO_clause5, TO_clause7, NP_ev1, NP_ev2, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                    'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [CONT])
               },

    #END
    "end" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
             'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },
    "ended" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [TERM]),
               'forward' : ([[NP_ev1, NP_ev2]], [TERM])
                },
    "ending" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },
    "ends" : {'forward' : ([[NP_ev1, NP_ev2]], [TERM]),
              'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect]], [TERM])
               },

    #ENTER
    "enter" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    "entered" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [INIT]),
                'forward' : ([[NP_ev1, NP_ev2]], [INIT])},
    "entering" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    "enters" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    
    #FINISH
    "finish" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [CULM]),
                  'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [CULM])
                },
    "finished" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect, Passive1]], [CULM]),
                  'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [CULM])
                  },
    "finishing" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [CULM])
                   },
    "finishes" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [CULM]),
                  'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [CULM])
                  },
    #KEEP
    "keep" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])#,
              #'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
               },
    "kept" : {'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [CONT]),
              'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])
              },
    "keeps" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])#,
              # 'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
               },
    "keeping" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])#,
                 #'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
                 },
    #LAUNCH
    "launch" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    "launched" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])#,
                 #'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [INIT])
                },
    "launching" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    "launches" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT])
               },
    
    #OPEN
    "open" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT]),
              'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [INIT])
              },
    "opened" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [INIT]),
                'forward' : ([[NP_ev1, NP_ev2]], [INIT])
                },
    "opening" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [INIT])
                 },
    "opens" : {'forward' : ([[NP_ev1, NP_ev2]], [INIT]),
               'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect]], [INIT])
               },
    #REMAIN
    "remain" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
               },
    "remains" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                 'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
                 },
    "remained" : {'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [CONT]),
                  'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT])
                  },
    "remaining" : {'forward' : ([[ING_clause, OBJCOMPL_pastPart, OBJCOMPL_adj]], [CONT]),
                   'backwards' : ([[NP_evAsSubj2, NP_evAsSubj2]], [CONT])
                   },

    #RENEW
    "renew" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT]),
               'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [REINIT])
               },
    "renewed" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect, Passive1]], [REINIT]),
                 'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT])
                 },
    "renewing" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT])
                  },
    "renews" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [REINIT])
                },
    #RESUME
    "resume" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT]),
                  'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [REINIT])
                },
    "resumed" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric,RelClauseRestricPerfect, Passive1]], [REINIT]),
                  'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT])
                  },
    "resuming" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT])
                   },
    "resumes" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [REINIT]),
                  'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [REINIT])
                  },
    #START
    "start" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [INIT]),
                 'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect]], [INIT])
              },
    "started" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [INIT]),
                'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [INIT])
                 },
    "starting" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [INIT])
               },
    "starts" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [INIT]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect]], [INIT])
               },

    #STOP
    "stop" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [TERM]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect]], [TERM])
               },
    "stopped" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect, Passive1]], [TERM]),
                 'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [TERM])
                 },
    "stoping" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [TERM])
               },
    "stops" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [TERM]),
                'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2, RelClauseRestric, RelClauseRestricPerfect]], [TERM])
               }
    
    }
