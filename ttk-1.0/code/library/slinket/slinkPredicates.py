
from timeMLspec import *

# FORWARD patterns:
from slinketPatterns import THAT_clause_that, THAT_clause_NOT_that, THAT_clausePAST_that, THAT_clausePERFECTIVE_NEG_that, THAT_clausePAST_NOT_that, THAT_clausePERFECTIVE_NEG_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report, THAT_clause_SIMPLE, THAT_clause_NOT_tensed, THAT_clause_if
from slinketPatterns import IND_INTERROG, OF_IND_INTERROG
from slinketPatterns import TO_clause1, TO_clause1_PERFECTIVE, TO_clause3, TO_clause3_PERFECTIVE, TO_clause5, TO_clause5_PERFECTIVE, TO_clause7 #TO_clause1, TO_clause2, TO_clause3, TO_clause4, TO_clause5, TO_clause6, TO_clause7
from slinketPatterns import IND_INTERROG_nonfin, OF_IND_INTERROG_nonfin
from slinketPatterns import ING_clause, ABOUT_ING_clause, AGAINST_ING_clause, AT_ING_clause, FOR_ING_clause, FROM_ING_clause, IN_ING_clause, OF_ING_clause, ON_ING_clause, TO_ING_clause, WITH_ING_clause
from slinketPatterns import ABOUT_NPev, AT_NPev, FOR_NPev, FROM_NPev, IN_NPev, OF_NPev, ON_NPev, OVER_NPev, TO_NPev, WITH_NPev, WITHOUT_NPev, PP_ABOUT
from slinketPatterns import NP_ev1, NP_ev2
from slinketPatterns import OBJCOMPL_pastPart, OBJCOMPL_adj
# BACKWARD patterns:
from slinketPatterns import Passive1, RelClauseExplic, RelClauseExplicPerfect
from slinketPatterns import NP_evAsSubj1, NP_evAsSubj2, NP_evAsSubj3
# REPORTING patterns:
from slinketPatterns import MAINsentence

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
    #ABILITY
    "ability" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #ACCEPTANCE
    #Refine: FActive depends on tense
    "acceptance" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                 [FACTIVE, FACTIVE])},
    "acceptances" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                  [FACTIVE, FACTIVE])},
    
    #ACCOMPLISHMENT
    "accomplishment" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "accomplishments" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},

    #ACHIEVEMENT
    "achievement" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "achievements" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},

    #ACQUISITION
    # Purpose clauses and more
    "acquisition" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "acquisitions" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},

    #ADOPTION
    #Purpose clauses and more
    "adoption" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "adoptions" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},

    #AGREEMENT
    "agreement" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause]],
                                [MODAL, MODAL])},    
    "agreements" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause]],
                                 [MODAL, MODAL])},    
    
    #APPOINTMENT
    #Purpose clauses so far, only. Missing NPs: "appointed CEO", etc.
    "appointment" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "appointments" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #APPROACH
    "approach" : {'forward' : ([[TO_NPev]], [FACTIVE])}, 
    "approaches" : {'forward' : ([[TO_NPev]], [FACTIVE])}, 

    #APPROVAL
    "approval" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_NPev]],
                               [MODAL, MODAL, MODAL])},      
    "approvals" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_NPev]],
                                [MODAL, MODAL, MODAL])},      
    
    #ASSERTION
    "assertion": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES]], [EVIDENTIAL])},
    "assertions": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES]], [EVIDENTIAL])},
    
    #ASSUMPTION
    "assumption" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    "assumptions" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},

    #ATTEMPT
    'attempt' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_NPev]],
                              [MODAL, MODAL, MODAL])},
    'attempted' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_NPev]],
                                [MODAL, MODAL, MODAL])},
    
    #AVOWAL
    "avowal" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3]], [FACTIVE, MODAL])},
    "avowals" : {'forward' : ([[OF_NPev], [TO_clause1, TO_clause3]], [FACTIVE, MODAL])},

    #BID
    #Purpose clauses and more
    "bid" : {'forward' : ([[FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "bids" : {'forward' : ([[FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    
    #BELIEF
    'belief': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    'beliefs': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    
    #BOOST
    "boost" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "boosts" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
                           
    #CALL
    'call' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'calls' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},

    #CANCELATION
    'cancelation' : {'forward' : ([[OF_NPev]], [COUNTER_FACTIVE])},
    'cancelations' : {'forward' : ([[OF_NPev]], [COUNTER_FACTIVE])},

    #CERTIFICATION
    "certification" : {'forward' : ([[THAT_clause_that], [OF_NPev]], [FACTIVE, FACTIVE])},
    "certifications" : {'forward' : ([[THAT_clause_that], [OF_NPev]], [FACTIVE, FACTIVE])},

    #CHALLENGE
    "challenge" : {'forward' : ([[TO_clause1, TO_clause3], [TO_NPev]], [MODAL, MODAL])},
    "challenges" : {'forward' : ([[TO_clause1, TO_clause3], [TO_NPev]], [MODAL, MODAL])},

    #CHANCE
    "chance" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [OF_ING_clause], [OF_NPev]], [MODAL])},
    "chances" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [OF_ING_clause], [OF_NPev]], [MODAL])},

    #CHANGE
    "change" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    "changes" : {'forward' : ([[OF_NPev]], [FACTIVE])},

    #CHARGE
    "charge" : {'forward' : ([[FOR_ING_clause], [OF_ING_clause, OF_NPev], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, MODAL, MODAL])}, 
    "charges" : {'forward' : ([[FOR_ING_clause], [OF_ING_clause, OF_NPev], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, MODAL, MODAL])}, 
    
    #CLAIM
    "claim" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [FOR_NPev] ],
                            [EVIDENTIAL, MODAL])},
    "claims" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [FOR_NPev] ],
                             [EVIDENTIAL, MODAL])},
    
    #CLEARANCE
    "clearance" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 

    #COMPLAINT
    "complaint" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},
    "complaints" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},

    #CONCERN
    "concern" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause]], [FACTIVE])},
    "concerns" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause]], [FACTIVE])},

    #CONFERENCE
    #Purpose clauses 
    "conference" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "conferences" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #CONFIRMATION
    "confirmation" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, 
                                     THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                    [OF_NPev]],
                                   [EVIDENTIAL, EVIDENTIAL])},
    "confirmations" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, 
                                      THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                     [OF_NPev]],
                                    [EVIDENTIAL, EVIDENTIAL])},
    
    #CONJECTURE
    "conjecture" : {'forward' : ([[ABOUT_NPev], [THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                 [FACTIVE, MODAL])},
    "conjectures" : {'forward' : ([[ABOUT_NPev], [THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                 [FACTIVE, MODAL])},
    
    #CONVERSATION
    "conversation" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause], [FOR_NPev, FOR_ING_clause]], [FACTIVE, MODAL])},
    "conversations" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause], [FOR_NPev, FOR_ING_clause]], [FACTIVE, MODAL])},

    #CREDIT
    "credit" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [THAT_clause_that]], [FACTIVE, FACTIVE, MODAL])},
    "credits" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [THAT_clause_that]], [FACTIVE, FACTIVE, MODAL])},

    #DECISION
    "decision" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                [AGAINST_ING_clause]],
                               [MODAL, MODAL, MODAL])},
    "decisions" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                 [AGAINST_ING_clause]],
                                [MODAL, MODAL, MODAL])},
    
    #DECLARATION
    "declaration" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                   [ABOUT_NPev, ABOUT_ING_clause]],
                                  [EVIDENTIAL, FACTIVE])},
    "declarations" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                    [ABOUT_NPev, ABOUT_ING_clause]],
                                   [EVIDENTIAL, FACTIVE])},
    
    #DELAY
    "delay" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    "delays" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    
    #DEMAND
    "demand" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [OF_NPev, OF_ING_clause]],
                             [MODAL, MODAL])},
    "demands" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [OF_NPev, OF_ING_clause]],
                              [MODAL, MODAL])},
    
    #DEMONSTRATION
    'demonstration' : {'forward' : ([[OF_NPev], [OF_IND_INTERROG]], [FACTIVE, FACTIVE])},
    'demonstrations' : {'forward' : ([[OF_NPev], [OF_IND_INTERROG]], [FACTIVE, FACTIVE])},

    #DESIRE
    "desire" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "desires" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #DESTRUCTION
    "destruction" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "destructions" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},

    #DEVELOP
    #Not sure about FACTIVE
    "development" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "developments" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},

    #DISCLOSE
    "disclose" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "discloses" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},

    #DISCOVERY
    "discovery" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "discoveries" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},

    #DISCUSSION
    #Not 100% sure about FACTIVE val. 
    "discussion" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [OF_NPev, ABOUT_NPev]], [MODAL, FACTIVE])},
    "discussions" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [OF_NPev, ABOUT_NPev]], [MODAL, FACTIVE])},

    #DOUBT
    "doubt" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},
    "doubts" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},

    #EFFORT
    # Purpose clause
    "effort" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "efforts" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #EXCUSE
    "excuse": {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])}, 
    "excuses": {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])}, 

    #EXPANSION
    "expansion" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "expansions" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},

    #EXPECTATION
    "expectation" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],
                                   [ABOUT_NPev, ABOUT_ING_clause, OF_NPev, OF_ING_clause]],
                                  [MODAL, MODAL, MODAL])},
    "expectations" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],
                                    [ABOUT_NPev, ABOUT_ING_clause, OF_NPev, OF_ING_clause]],
                                   [MODAL, MODAL, MODAL])},

    #EXTENSION
    "extension" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    "extensions" : {'forward' : ([[OF_NPev]], [FACTIVE])},

    #FAILURE
    "failure" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_ING_clause]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},

    #FEAR
    #Not sure about FACTIVE
    "fear" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3],
                            [OF_NPev, OF_ING_clause]],
                           [MODAL, MODAL, FACTIVE])},
    "fears" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3],
                             [OF_NPev, OF_ING_clause]],
                            [MODAL, MODAL, FACTIVE])},

    #FEELING
    "feeling" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_NPev, OF_ING_clause]],
                           [EVIDENTIAL, EVIDENTIAL])},
    "feelings" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_NPev, OF_ING_clause]],
                           [EVIDENTIAL, EVIDENTIAL])},

    #GUARANTEE
    "guarantee" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                              [MODAL, MODAL])},
    "guarantees" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                              [MODAL, MODAL])},

    #GOAL
    "goal" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_NPev, OF_ING_clause]], [MODAL, MODAL])}, 
    "goals" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_NPev, OF_ING_clause]], [MODAL, MODAL])}, 
    
    #HINT
    #Not sure
    "hint" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, MODAL])},
    "hints" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, MODAL])},

    #HOPE
    'hope': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                          [MODAL, MODAL])},
    'hopes': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                           [MODAL, MODAL])},

    #HYPOTHESIS
    "hypothesis" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, FACTIVE])},
    
    #IMPLICATION
    "implication" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "implications" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    
    #IMPOSITION
    'imposition' : {'forward' : ([[OF_NPev]], [MODAL])},
    'impositions' : {'forward' : ([[OF_NPev]], [MODAL])},

    #IMPROVEMENT
    "improvement" : {'forward' : ([[OF_NPev, NP_ev1, NP_ev2]], [FACTIVE])},
    "improvements" : {'forward' : ([[OF_NPev, NP_ev1, NP_ev2]], [FACTIVE])},
    
    #INCREASE
    "increase" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "increases" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    
    #INTENT
    "intent" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "intents" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #INTENT
    "intention" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_NPev, OF_ING_clause]], [MODAL, MODAL])},
    "intentions" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_NPev, OF_ING_clause]], [MODAL, MODAL])},
    
    #INTIMATION
    "intimation" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL])},
    "intimations" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL])},

    #INVESTIGATION
    "investigation" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    "investigations" : {'forward' : ([[OF_NPev]], [FACTIVE])},

    #INVITATION
    "invitation" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "invitations" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #LAUGH
    "laugh" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause]], [FACTIVE])},
    "laughs" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause]], [FACTIVE])},

    #MOVE
    "move" : {'forward' : ([[FROM_NPev, FROM_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "moves" : {'forward' : ([[FROM_NPev, FROM_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},

    #NEED
    "need" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL])},
    "needs" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL])},

    #NEGOTIATION
    "negotiation" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause], [OF_ING_clause, OF_NPev], [FOR_NPev, FOR_ING_clause], [TO_clause1]],
                                  [MODAL, MODAL, MODAL, MODAL])},
    "negotiations" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause], [OF_ING_clause, OF_NPev], [FOR_NPev, FOR_ING_clause], [TO_clause1]],
                                   [MODAL, MODAL, MODAL, MODAL])},
    
    #OFFER
    "offer" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "offers" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},

    #OPTION
    "option" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_ING_clause, OF_NPev]], [MODAL, MODAL])}, 
    "options" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [OF_ING_clause, OF_NPev]], [MODAL, MODAL])}, 

    #ORDER
    "order" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_ING_clause]],
                            [MODAL, MODAL, MODAL])},
    "orders" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2], [OF_ING_clause]],
                             [MODAL, MODAL, MODAL])},
    
    #ORGANIZE
    "organization" : {'forward' : ([[OF_NPev], [TO_clause1]], [MODAL, MODAL])},
    "organizations" : {'forward' : ([[OF_NPev], [TO_clause1]], [MODAL, MODAL])},

    #PERCEPTION
    "perception" : {'forward' : ([[THAT_clause_that], [OF_NPev, OF_ING_clause]], [FACTIVE, FACTIVE])}, 
    "perceptions" : {'forward' : ([[THAT_clause_that], [OF_NPev, OF_ING_clause]], [FACTIVE, FACTIVE])}, 

    #PLAN:
    "plan" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL])},
    "plans" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL])},

    #POSITION
    #For cases like: "he is in the poition..."
    "position" : {'forward' : ([[TO_clause1, TO_clause3], [OF_ING_clause,]], [MODAL, MODAL])}, 
    "position" : {'forward' : ([[TO_clause1, TO_clause3], [OF_ING_clause,]], [MODAL, MODAL])}, 

    #POWER
    "power" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "powers" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #PREDICTION
    "prediction" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},
    "predictions" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},


    #PREFERENCE
    "preference" : {'forward' : ([[FOR_ING_clause], [FOR_NPev]],
                                 [MODAL, MODAL])},    
    "preferences" : {'forward' : ([[FOR_ING_clause], [FOR_NPev]],
                                 [MODAL, MODAL])},    

    #PRESSURE
    "pressure" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "pressures" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},

    #PRESUMPTION
    "presumption" : {'forward' : ([[THAT_clause_that]], [MODAL])},
    "presumptions" : {'forward' : ([[THAT_clause_that]], [MODAL])},

    #PRETENCE
    "pretence" : {'forward' : ([[OF_NPev], [OF_ING_clause], [THAT_clause_that]],
                               [COUNTER_FACTIVE, COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "pretences" : {'forward' : ([[OF_NPev], [OF_ING_clause], [THAT_clause_that]],
                               [COUNTER_FACTIVE, COUNTER_FACTIVE, COUNTER_FACTIVE])},

    #PROHIBITION
    "prohibition" : {'forward' : ([[FROM_ING_clause, ON_ING_clause, AGAINST_ING_clause]], [MODAL])},
    "prohibitions" : {'forward' : ([[FROM_ING_clause, ON_ING_clause, AGAINST_ING_clause]], [MODAL])},

    #PROOF
    "proof" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "proofs" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    
    #PROMISE
    "promise" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[OF_ING_clause, OF_NPev]],
                              [MODAL, MODAL, MODAL])},
    "promises" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[OF_ING_clause, OF_NPev]],
                               [MODAL, MODAL, MODAL])},
    
    #PROPOSAL
    "proposal" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                [OF_NPev, OF_ING_clause]],
                               [MODAL, MODAL, MODAL])},
    "proposals" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                 [OF_NPev, OF_ING_clause]],
                                [MODAL, MODAL, MODAL])},
    #PUBLICATION
    "publication" : {'forward' : ([[OF_NPev]], [EVIDENTIAL])},
    "publications" : {'forward' : ([[OF_NPev]], [EVIDENTIAL])},

    #QUESTION
    "question" : {'forward' : ([[THAT_clause_if]], [MODAL])},
    "questions" : {'forward' : ([[THAT_clause_if]], [MODAL])},

    #RECOGNITION
    "recognition" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_NPev]], 
                                  [FACTIVE, FACTIVE])},
    "recognitions" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_NPev]], 
                                   [FACTIVE, FACTIVE])},

    #REFERENCE
    "reference" : {'forward' : ([[TO_NPev]], [FACTIVE])},
    "references" : {'forward' : ([[TO_NPev]], [FACTIVE])},

    #REGRET
    "regret" : {'forward': ([[AT_NPev, FOR_NPev]], [FACTIVE])},
    "regrets" : {'forward': ([[AT_NPev, FOR_NPev]], [FACTIVE])},

    #REJECTION
    #Careful with relType. Is it totally appropriate?
    "rejection" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    "rejections" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    
    #REMARK
    "remark"  : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [ON_NPev]],
                              [EVIDENTIAL, FACTIVE])},
    "remarks"  : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [ON_NPev]],
                              [EVIDENTIAL, FACTIVE])},

    #RENUNCIATION
    "renunciation" : {'forward' : ([[OF_NPev]], [COUNTER_FACTIVE])},
    "renunciations" : {'forward' : ([[OF_NPev]], [COUNTER_FACTIVE])},
    
    #RESPONSABILITY
    "responsability" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],
                                      [OF_NPev, OF_ING_clause, FOR_NPev, FOR_ING_clause]],
                                     [MODAL, MODAL])},
    "responsabilities" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],
                                        [OF_NPev, OF_ING_clause, FOR_NPev, FOR_ING_clause]],
                                       [MODAL, MODAL])},

    #STATEMENT
    "statement": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES]], [EVIDENTIAL])},
    "statements": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES]], [EVIDENTIAL])},
    
    #STRUGGLE
    "struggle"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL])},
    "struggles"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL])},

    #SUBJECT
    "subject" : {'forward' : ([[TO_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},

    #SUGGESTION
    "suggestion" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    "suggestions" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    
    #SUPPORT
    "support" : {'forward' : ([[FOR_NPev], [OF_NPev]], [MODAL, FACTIVE])},
    "support" : {'forward' : ([[FOR_NPev], [OF_NPev]], [MODAL, FACTIVE])},

    #SUSPICION
    "suspicion" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_ING_clause, OF_NPev]], [MODAL, MODAL])},
    "suspicions" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [OF_ING_clause, OF_NPev]], [MODAL, MODAL])},
    
    #TALK
    "talk" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    "talks" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    
    #UNDERSTANDING:
    "understanding" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    "understandings" : {'forward' : ([[OF_NPev]], [FACTIVE])},
    
    #USE
    # Purpose clause
    "use" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "uses" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #WISH
    "wish" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [FOR_NPev],
                           [THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that]],
                          [MODAL, MODAL, MODAL, COUNTER_FACTIVE, FACTIVE])},
    
    "wishes" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [FOR_NPev],
                           [THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that]],
                          [MODAL, MODAL, MODAL, COUNTER_FACTIVE, FACTIVE])},
    
    }




adjDict = {
    #ACCUSED
    "accused" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},

    #ABLE
    "able" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #AFRAID
    "afraid" : {"forward": ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [OF_NPev], [OF_ING_clause]], [MODAL, MODAL, FACTIVE, MODAL])},
    
    #ALLEGED:
    "alleged" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},

    #ANXIOUS
    "anxious" : {"forward": ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5], [ABOUT_NPev]],
                             [MODAL, MODAL, FACTIVE])},

    #AWARE
    "aware" : {'forward' : ([[THAT_clause_that], [OF_NPev]], [MODAL, FACTIVE])},
    

    #CERTAIN
    "certain" : {'forward': ([[THAT_clause_that]], [FACTIVE])},
    
    #CLEAR
    "clear" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE]),
               'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #CONCEIVABLE
    "conceivable" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                     'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #CONFIDENT
    "confident": {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [ABOUT_NPev, ABOUT_ING_clause]], [MODAL, MODAL])}, 
    
    #CRAZY
    "crazy" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                            [FACTIVE, MODAL, MODAL]),
               'backwards': ([[NP_evAsSubj3]], [FACTIVE])},
    
    #DUE
    "due" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #EAGER
    "eager" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #EVIDENT
    "evident" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE]),
                 'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #EXCITING
    "exciting" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                                  [FACTIVE, MODAL, MODAL]),
                  'backwards': ([[NP_evAsSubj3]], [FACTIVE])},
    #FALSE
    "false" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that]], [COUNTER_FACTIVE])},

    #IMMINENT
    "imminent" : {'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #IMPORTANT
    #Not sure about factive
    "important" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                                [FACTIVE, MODAL]),
                   'backwards': ([[NP_evAsSubj3]], [FACTIVE])},
    
    #IMPOSSIBLE
    "impossible" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                               [MODAL, MODAL]),
                    'backwards': ([[NP_evAsSubj3]], [MODAL])},
    
    #IMPROBABLE
    "improbable" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that],
                                  [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL]),
                    'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #INCONCEIVABLE
    "inconceivable" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                       'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #INTERESTING
    "interesting" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                                  [FACTIVE, MODAL, MODAL]),
                    'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #LIKELY
    "likely" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #LUCKY
    "lucky" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE])},

    #OBVIOUS
    "obvious" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE]),
                 'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #ODD
    "odd" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                          [FACTIVE, MODAL, MODAL]),
             'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #POSSIBLE
    "possible" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                               [MODAL, MODAL]),
                  'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #PROBABLE
    "probable" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                  'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #PROUD
    "proud" : {'forward' : ([[OF_ING_clause, OF_NPev], [TO_clause1_PERFECTIVE, TO_clause3_PERFECTIVE, TO_clause5_PERFECTIVE],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [FACTIVE, FACTIVE, MODAL])},

    #RELEVANT
    #Not sure about factive
    "relevant" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                                [FACTIVE, MODAL]),
                  'backwards': ([[NP_evAsSubj3]], [FACTIVE])},
    
    #RELUCTANT
    "reluctant" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #RESPONSABLE
    "responsable" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],
                                   [OF_NPev, OF_ING_clause, FOR_NPev, FOR_ING_clause]],
                                  [MODAL, MODAL])},
    #SORRY
    "sorry" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause]], [FACTIVE, FACTIVE])},

    #SAD
    "sad" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                              [FACTIVE, MODAL, MODAL])},

    #SIGNIFICANT
    "significant" : {'forward' : ([[THAT_clause_that]], [FACTIVE, MODAL]),
                     'backwards': ([[NP_evAsSubj3]], [FACTIVE])},
    
    #STRANGE
    "strange" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                                  [FACTIVE, MODAL, MODAL]),
                 'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #SURE
    "sure" : {'forward': ([[THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause], [TO_clause1, TO_clause3]], [FACTIVE, MODAL, MODAL])},
    
    #TRAGIC
    "tragic" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [THAT_clause_if]],
                             [FACTIVE, MODAL, MODAL])},
    #TRUE
    "true" : {'forward': ([[THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE]),
              'backwards': ([[NP_evAsSubj3]], [FACTIVE])},

    #UNFORTUNATE
    "unfortunate" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, FACTIVE])},
    #UNKNOWN
    "unknown" : {'forward' : ([[THAT_clause_if]], [MODAL])},

    #UNLIKELY
    "unlikely" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                  'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #URGENT
    "urgent" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL]),
                'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #VITAL
    "vital" : {'forward' : ([[THAT_clause_that]], [MODAL]),
               'backwards': ([[NP_evAsSubj3]], [MODAL])},

    #WELL-KNOWN
    "well-known" : {'forward' : ([[THAT_clause_that]], [FACTIVE])},
                    
    #WORTHWHILE
    "worthwhile" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #WILLING
    "willing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    }




verbDict = {
    #ACCEPT
    #Refine: FActive depends on tense
    "accept" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                              [TO_clause1, TO_clause3, TO_clause5]],
                             [FACTIVE, FACTIVE, MODAL])},
    "accepted" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [TO_clause1, TO_clause3, TO_clause5]],
                               [FACTIVE, FACTIVE, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "accepting" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                 [TO_clause1, TO_clause3, TO_clause5]],
                                [FACTIVE, FACTIVE, MODAL])},
    "accepts" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                               [TO_clause1, TO_clause3, TO_clause5]],
                              [FACTIVE, FACTIVE, MODAL])},
    
    
    #ACCOMPLISH
    "accomplish" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "accomplished" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "accomplishing" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "accomplishes" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},

    #ACCORDING
    # Problem: EVITA is not tagging this stem
    "according": {'forward' : ([[THAT_clause_NOT_that]], [EVIDENTIAL])},
    
    #ACCUSE
    "accuse" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    "accused" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    "accuses" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    "accusing" : {'forward' : ([[OF_NPev, OF_ING_clause]], [MODAL])},
    
    #ACHIEVE
    "achieve" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "achieved" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "achieves" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "achieving" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},

    #ACKNOWLEDE
    #Not totally sure about Factive value
    "acknowledge" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "acknowledged" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE]),
                      'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "acknowledges" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "acknowledging" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    
    #ACQUIRE
    # Purpose clauses and more
    "acquire" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "acquired" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "acquires" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "acquiring" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    
    #ADD
    "add" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
             'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "added" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "adding" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    "adds" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #ADMIT
    "admit" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "admitted" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "admitting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "admits" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    
    #ADOPT
    #Purpose clauses and more
    "adopt" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "adopted" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "adopts" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "adopting" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},

    #ADVOCATE
    "advocate" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "advocated" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "advocates" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "advocating" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    
    #AFFIRM
    "affirm" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                             [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "affirmed" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                               [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "affirming" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "affirms" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                              [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
        

    #AGREE
    "agree" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                            [MODAL, MODAL])},
    "agreed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                             [MODAL, MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "agreeing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                               [MODAL, MODAL])},
    "agrees" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that, THAT_clause_NOT_that]],
                             [MODAL, MODAL])},
    
    #AIM
    "aim" : {'forward' : ([[AT_ING_clause, AT_NPev]], [MODAL])}, 
    "aimed" : {'forward' : ([[AT_ING_clause, AT_NPev]], [MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "aiming" : {'forward' : ([[AT_ING_clause, AT_NPev]], [MODAL])}, 
    "aims" : {'forward' : ([[AT_ING_clause, AT_NPev]], [MODAL])}, 

    #ALLEGE
    "allege" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "alleged" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "alleging" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "alleges" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    
    #ALLOW
    'allow' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL, MODAL])},
    'allowed' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    'allowing' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause], [NP_ev1, NP_ev2]],
                               [MODAL, MODAL, MODAL])},
    'allows' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},
    
    #AMUSE
    "amuse" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]],
                            [FACTIVE]),
               'backwards' : ([[ING_clause]], [MODAL])},
    "amused" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [AT_NPev]],
                            [FACTIVE, FACTIVE]),
                'backwards' : ([[ING_clause]], [MODAL])},
    "amuses" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]],
                            [FACTIVE]),
                'backwards' : ([[ING_clause]], [MODAL])},
    "amusing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]],
                            [FACTIVE]),
                 'backwards' : ([[ING_clause]], [MODAL])},
    
    
    #ANNOUNCE
    "announce" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]],
                               [EVIDENTIAL, EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "announced" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]],
                                [EVIDENTIAL, EVIDENTIAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "announces" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]],
                                [EVIDENTIAL, EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "announcing" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]],
                                 [EVIDENTIAL, EVIDENTIAL])},

    #ANSWER
    "answer" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},    
    "answered" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},    
    "answering" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},    
    "answers" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},    
    
    #ANTICIPATE
    #Not sure about FACTIVE at past tense
    "anticipate" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},
    "anticipated" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},
    "anticipating" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},
    "anticipates" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},


    #APPEAR
    "appear" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "appeared" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that]],
                               [MODAL, MODAL])},
    "appearing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                                [MODAL, MODAL])},
    "appears" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL])},
    
    #APPOINT
    #Purpose clauses so far, only. Missing NPs: "appointed CEO", etc.
    "appoint" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "appointed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "appointing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "appoints" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #APPROACH
    "approach" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "approached" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "approaching" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "approaches" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 

    #APPROVE
    "approve" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    "approved" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "approves" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    "approving" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    
    #APPROACHING
    #Only FACTIVE?
    "approach" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "approached" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "approaches" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "approaching" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #ARGUE
    "argue" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "argued" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "argues" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "arguing" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    
    #ASCRIBE
    "ascribe" : {'forward' : ([[NP_ev1, NP_ev2], [TO_NPev]], [FACTIVE, MODAL])},
    "ascribed" : {'forward' : ([[NP_ev1, NP_ev2], [TO_NPev]], [FACTIVE, MODAL])},
    "ascribing" : {'forward' : ([[NP_ev1, NP_ev2], [TO_NPev]], [FACTIVE, MODAL])},
    "ascribes" : {'forward' : ([[NP_ev1, NP_ev2], [TO_NPev]], [FACTIVE, MODAL])},

    #ASK
    'ask' : {'forward' : ([[NP_ev1, NP_ev2, FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5],
                           [THAT_clause_if, IND_INTERROG]],
                          [MODAL, MODAL, MODAL])},
    'asked' : {'forward' : ([[NP_ev1, NP_ev2, FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5],
                             [THAT_clause_if, IND_INTERROG]],
                            [MODAL, MODAL, MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    'asking' : {'forward' : ([[NP_ev1, NP_ev2, FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5],
                              [THAT_clause_if, IND_INTERROG]],
                             [MODAL, MODAL, MODAL])},
    'asks' : {'forward' : ([[NP_ev1, NP_ev2, FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5],
                            [THAT_clause_if, IND_INTERROG]],
                           [MODAL, MODAL, MODAL])},
    
    #ASSERT
    "assert": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "asserted": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "asserting": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    "asserts": {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #ASSIST
    "assist" : {'forward' : ([[IN_NPev, IN_ING_clause]], [FACTIVE])},
    "assisted" : {'forward' : ([[IN_NPev, IN_ING_clause]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "assisting" : {'forward' : ([[IN_NPev, IN_ING_clause]], [FACTIVE])},
    "assists" : {'forward' : ([[IN_NPev, IN_ING_clause]], [FACTIVE])},
    
    #ASSUME
    "assume" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    "assumed" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    "assumes" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    "assuming" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [MODAL])},
    
    #ASSURE
    "assure" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "assured" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "assures" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "assuring" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    
    #ATTEMPT
    'attempt' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL])},
    'attempted' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                [MODAL, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    'attemptes' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                [MODAL, MODAL])},
    'attempting' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},
    
    #AUTHORIZE
    "authorize" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                [MODAL, MODAL])},
    "authorized" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "authorizes" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL])},
    "authorizing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                  [MODAL, MODAL])},
    
    #AVOID
    "avoid" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, COUNTER_FACTIVE])},
    "avoided" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, COUNTER_FACTIVE]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [COUNTER_FACTIVE])},
    "avoiding" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, COUNTER_FACTIVE])},
    "avoids" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, COUNTER_FACTIVE])},
    
    #AVOW
    "avow" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE])},
    "avowed" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE]),
                'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "avowing" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE])},
    "avows" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE])},

    #BECOME
    "become" : {'forward' : ([[NP_ev1, NP_ev2],[OBJCOMPL_pastPart]], [FACTIVE, FACTIVE])},
    "became" : {'forward' : ([[NP_ev1, NP_ev2],[OBJCOMPL_pastPart]], [FACTIVE, FACTIVE])},
    "becomes" : {'forward' : ([[NP_ev1, NP_ev2],[OBJCOMPL_pastPart]], [FACTIVE, FACTIVE])},
    "becoming" : {'forward' : ([[NP_ev1, NP_ev2],[OBJCOMPL_pastPart]], [FACTIVE, FACTIVE])},
    
    #BELIEVE
    'believe': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    'believed': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL])},
    'believes': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL])},
    'believing': {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3, TO_clause5]],
                               [MODAL, MODAL])},
    #BEMOAN
    "bemoan" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "bemoaned" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "bemoaning" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "bemoans" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
     
    #BID
    "bid" : {'forward' : ([[FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "bidding" : {'forward' : ([[FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "bids" : {'forward' : ([[FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    
    #BLOCK
    #Careful with relType value; is it totally appropriate?
    "block" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    "blocked" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [COUNTER_FACTIVE])},
    "blocking" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    "blocks" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    
    #BOOST
    "boost" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "boosted" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "boosting" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "boosts" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #BOTHER
    "bother" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "bothered" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "bothering" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "bothers" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    
    #CALCULATE
    "calculate" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_NOT_that], [THAT_clause_if]],
                            [FACTIVE, MODAL, MODAL])},
    "calculated" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_NOT_that], [THAT_clause_if]],
                              [FACTIVE, MODAL, MODAL])},
    "calculates" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_NOT_that], [THAT_clause_if]],
                              [FACTIVE, MODAL, MODAL])},
    "calculating" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_NOT_that], [THAT_clause_if]],
                               [FACTIVE, MODAL, MODAL])},
    #CALL
    'call' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'called' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'calling' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'calls' : {'forward' : ([[FOR_ING_clause, FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    
    #CANCEL
    'cancel' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    'cancelled' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    'cancelling' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    'canceled' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    'canceling' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    'cancels' : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},

    #CERTIFY
    "certify" : {'forward' : ([[THAT_clause_that]], [FACTIVE])},
    "certified" : {'forward' : ([[THAT_clause_that]], [FACTIVE])},
    "certifies" : {'forward' : ([[THAT_clause_that]], [FACTIVE])},
    "certifying" : {'forward' : ([[THAT_clause_that]], [FACTIVE])},

    #CHALLENGE
    "challenge" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [TO_NPev], [NP_ev1, NP_ev2]],
                                [MODAL, MODAL, FACTIVE])},
    "challenged" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [TO_NPev], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL, FACTIVE])},
    "challenging" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [TO_NPev], [NP_ev1, NP_ev2]],
                                  [MODAL, MODAL, FACTIVE])},
    "challenges" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [TO_NPev], [NP_ev1, NP_ev2]],
                                 [MODAL, MODAL, FACTIVE])},

    #CHANCE
    "chance" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "chanced" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "chancing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    "chances" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [FACTIVE])},
    
    #CHANGE
    "change" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "changed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "changing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "changes" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #CHARGE
    "charge" : {'forward' : ([[FOR_ING_clause], [WITH_ING_clause, WITH_NPev], [THAT_clause_that, THAT_clause_NOT_that]],
                             [FACTIVE, MODAL, MODAL])}, 
    "charged" : {'forward' : ([[FOR_ING_clause], [WITH_ING_clause, WITH_NPev], [THAT_clause_that, THAT_clause_NOT_that]],
                              [FACTIVE, MODAL, MODAL])}, 
    "charges" : {'forward' : ([[FOR_ING_clause], [WITH_ING_clause, WITH_NPev], [THAT_clause_that, THAT_clause_NOT_that]],
                              [FACTIVE, MODAL, MODAL])}, 
    "charging" : {'forward' : ([[FOR_ING_clause], [WITH_ING_clause, WITH_NPev], [THAT_clause_that, THAT_clause_NOT_that]],
                               [FACTIVE, MODAL, MODAL])}, 
    
    #CHECK
    "check" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG], [TO_clause1, TO_clause3]],
                            [MODAL, MODAL])}, 
    "checked" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG], [TO_clause1, TO_clause3]],
                            [MODAL, MODAL])}, 
    "checking" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG], [TO_clause1, TO_clause3]],
                            [MODAL, MODAL])}, 
    "checks" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG], [TO_clause1, TO_clause3]],
                            [MODAL, MODAL])}, 

    #CATCH
    "catch" : {'forward' : ([[ING_clause], [IND_INTERROG, NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])}, 
    "caught" : {'forward' : ([[ING_clause], [IND_INTERROG, NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])}, 
    "catching" : {'forward' : ([[ING_clause], [IND_INTERROG, NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])}, 
    "catches" : {'forward' : ([[ING_clause], [IND_INTERROG, NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])}, 

    #CHOOSE
    "choose" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "chooses" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "chose" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "chosen" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "choosing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #CITE
    "cite" : {'forward' : ([[THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "cited" : {'forward' : ([[THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [EVIDENTIAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "cites" : {'forward' : ([[THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [EVIDENTIAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "citing" : {'forward' : ([[THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [EVIDENTIAL])},
    
    #CLAIM
    "claim" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2], [FOR_NPev] ],
                            [EVIDENTIAL, MODAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "claimed" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2], [FOR_NPev] ],
                              [EVIDENTIAL, MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "claiming" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2], [FOR_NPev] ],
                               [EVIDENTIAL, MODAL, MODAL])},
    "claims" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2], [FOR_NPev] ],
                             [EVIDENTIAL, MODAL, MODAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #CLEAR
    "clear" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])}, 
    "cleared" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "clearing" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])}, 
    "clears" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])}, 
    
    #COMMENT
    #comment on
    "comment" : {'forward' : ([[ON_NPev], [THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [FACTIVE, EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "commented" : {'forward' : ([[ON_NPev], [THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [FACTIVE, EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "comments" : {'forward' : ([[ON_NPev], [THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [FACTIVE, EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "commenting" : {'forward' : ([[ON_NPev], [THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]], [FACTIVE, EVIDENTIAL])},
    
    #COMPLAIN
    "complain" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},
    "complained" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},
    "complaining" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},
    "complains" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [EVIDENTIAL, FACTIVE])},

    #COMPREHEND
    "comprehend" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "comprehended" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "comprehending" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "comprehends" : {'forward' : ([[THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},

    #CONCEDE
    "concede" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [NP_ev1]],
                              [FACTIVE, MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "conceded" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [NP_ev1]],
                               [FACTIVE, MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "concedes" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [NP_ev1]],
                              [FACTIVE, MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "conceding" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES], [NP_ev1]],
                              [FACTIVE, MODAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},


    #CONCERN
    "concern" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                 'backwards' : ([[THAT_clause_that, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "concerned" : {'forward' : ([[ABOUT_NPev, ABOUT_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, MODAL]),
                   'backwards' : ([[THAT_clause_that, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "concerning" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                    'backwards' : ([[THAT_clause_that, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},
    "concerns" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                  'backwards' : ([[THAT_clause_that, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE, FACTIVE])},

    #CONCLUDE
    "conclude" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "concluded" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "concluding" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "concludes" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    
    #CONFIRM
    "confirm" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                               [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "confirmed" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                 [NP_ev1, NP_ev2]],
                                [EVIDENTIAL, EVIDENTIAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "confirming" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                  [NP_ev1, NP_ev2]],
                                 [EVIDENTIAL, EVIDENTIAL])},
    "confirms" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [NP_ev1, NP_ev2]],
                               [EVIDENTIAL, EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #CONJECTURE
    "conjecture" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_SIMPLE, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                 [MODAL])},
    "conjectured" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_SIMPLE, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                  [MODAL])},
    "conjectures" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_SIMPLE, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                  [MODAL])},
    "conjecturing" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_SIMPLE, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                                   [MODAL])},

    #CONSIDER
    "consider": {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, MODAL])},
    "considered": {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "considering": {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, MODAL])},
    "considers": {'forward' : ([[NP_ev1, NP_ev2], [ING_clause]], [FACTIVE, MODAL])},
    
    #CONTEND
    "contend" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    "contended" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    "contending" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    "contends" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    
    #CREDIT
    "credit" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [IND_INTERROG]], [FACTIVE, MODAL])},
    "credited" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [IND_INTERROG]], [FACTIVE, MODAL])},
    "credits" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [IND_INTERROG]], [FACTIVE, MODAL])},
    "crediting" : {'forward' : ([[FOR_ING_clause, FOR_NPev], [IND_INTERROG]], [FACTIVE, MODAL])},

    #DARE
    "dare" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]], [MODAL])},
    "dared" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]], [MODAL])},
    "daring" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]], [MODAL])},
    "dares" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]], [MODAL])},

    #DECIDE
    # that clause may be signaling a sense change (towards a more 'assertive'-kind of verb)
    # Also missing: indirect questions
    "decide" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                              [AGAINST_ING_clause]],
                             [MODAL, MODAL, MODAL])},
    "decided" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                               [AGAINST_ING_clause]],
                              [MODAL, MODAL, MODAL])},
    "decides" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                               [AGAINST_ING_clause]],
                              [MODAL, MODAL, MODAL])},
    "deciding" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                [AGAINST_ING_clause]],
                               [MODAL, MODAL, MODAL])},
    
    #DECLARE
    "declare" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                               [ABOUT_NPev, ABOUT_ING_clause]],
                              [EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "declared" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [ABOUT_NPev, ABOUT_ING_clause]],
                               [EVIDENTIAL, FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "declaring" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                 [ABOUT_NPev, ABOUT_ING_clause]],
                                [EVIDENTIAL, FACTIVE])},
    "declares" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [ABOUT_NPev, ABOUT_ING_clause]],
                               [EVIDENTIAL, FACTIVE]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #DECLINE
    "decline" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "declined" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                               [COUNTER_FACTIVE, COUNTER_FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [COUNTER_FACTIVE])},
    "declines" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                               [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "declining" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    
    #DEDUCE:
    #Not sure about relTypes
    "deduce" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                              [MODAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [MODAL])},
    "deduced" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                              [MODAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [MODAL])},
    "deduces" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                              [MODAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [MODAL])},
    "deducing" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                              [MODAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [MODAL])},

    #DELAY
    "delay" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "delayed" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "delaying" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "delays" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},

    #DELIGHT
    "delight" : {'forward' : ([[THAT_clause_that]], [FACTIVE]),
                   'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "delighted" : {'forward' : ([[THAT_clause_that]], [FACTIVE]),
                   'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "delighting" : {'forward' : ([[THAT_clause_that]], [FACTIVE]),
                   'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "delights" : {'forward' : ([[THAT_clause_that]], [FACTIVE]),
                   'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    
    #DEMAND
    "demand" : {'forward' : ([[NP_ev1, NP_ev2],
                              [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]],
                             [MODAL, MODAL])},
    "demanded" : {'forward' : ([[NP_ev1, NP_ev2],
                                [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]],
                               [MODAL, MODAL])},
    "demanding" : {'forward' : ([[NP_ev1, NP_ev2],
                                 [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]],
                                [MODAL, MODAL])},
    "demands" : {'forward' : ([[NP_ev1, NP_ev2],
                               [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]],
                              [MODAL, MODAL])},
    #DEMONSTRATE
    "demonstrate" : {'forward' : ([[NP_ev1, NP_ev2], [IND_INTERROG_nonfin], [THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that]],
                                  [FACTIVE, FACTIVE, MODAL])}, 
    "demonstrated" : {'forward' : ([[NP_ev1, NP_ev2], [IND_INTERROG_nonfin], [THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that]],
                                   [FACTIVE, FACTIVE, MODAL])}, 
    "demonstrates" : {'forward' : ([[NP_ev1, NP_ev2], [IND_INTERROG_nonfin], [THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that]],
                                   [FACTIVE, FACTIVE, MODAL])}, 
    "demonstrating" : {'forward' : ([[NP_ev1, NP_ev2], [IND_INTERROG_nonfin], [THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that]],
                                    [FACTIVE, FACTIVE, MODAL])}, 
    
    #DENY
    "deny" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, NEG_EVIDENTIAL, NEG_EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "denied" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, NEG_EVIDENTIAL, NEG_EVIDENTIAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [NEG_EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "denies" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, NEG_EVIDENTIAL, NEG_EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "denying" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, NEG_EVIDENTIAL, NEG_EVIDENTIAL])},
    
    #DEPLORE
    "deplore" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])},
    "deplored" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])},
    "deploring" :{'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])},
    "deplores" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])},
    
    #DEPRIVE
    "deprive" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "deprived" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "deprives" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    "depriving" : {'forward' : ([[OF_NPev, OF_ING_clause]], [FACTIVE])},
    
    #DESCRIBE
    "describe" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL])}, 
    "described" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])}, 
    "describing" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL])}, 
    "describes" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])}, 
    
    #DESIGN
    # Purpose clause
    "design" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "designed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "designing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "designs" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #DESTROY
    "destroy" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "destroyed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "destroying" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "destroys" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #DETERMINE
    "determine" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2],
                                 [THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that]],
                                [MODAL, MODAL, MODAL])}, 
    "determined" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2],
                                  [THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that]],
                                 [MODAL, MODAL, MODAL]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "determines" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2],
                                  [THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that]],
                                 [MODAL, MODAL, MODAL])}, 
    "determining" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2],
                                   [THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that]],
                                  [MODAL, MODAL, MODAL])}, 

    #DEVELOP
    #Not sure about FACTIVE
    "develop" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "developed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "developing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "develops" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #DISCLOSE
    "disclose" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "disclosed" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "disclosing" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "discloses" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])}, 
    
    #DISCOVER
    "discover" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "discovered" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "discovering" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "discovers" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    
    #DISCUSS
    #Not 100% sure about FACTIVE val. 
    "discuss" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "discussed" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [NP_ev1, NP_ev2]], [MODAL, FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "discussing" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "discusses" : {'forward' : ([[IND_INTERROG, THAT_clause_if], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    
    #DIVULGE
    "divulge" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2], [IND_INTERROG]],
                              [EVIDENTIAL, FACTIVE, FACTIVE])},
    "divulged" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2], [IND_INTERROG]],
                              [EVIDENTIAL, FACTIVE, FACTIVE])},
    "divulges" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2], [IND_INTERROG]],
                              [EVIDENTIAL, FACTIVE, FACTIVE])},
    "divulging" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2], [IND_INTERROG]],
                              [EVIDENTIAL, FACTIVE, FACTIVE])},
    
    #DOUBT
    "doubt" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},
    "doubted" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},
    "doubting" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},
    "doubts" : {'forward' : ([[THAT_clause_that, THAT_clause_if], [ABOUT_NPev]],
                            [MODAL, MODAL])},
    

    #EASE
    "ease" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "eased" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "easing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "eases" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #EMPHASIZE
    "emphasize" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    "emphasized" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "emphasizing" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    "emphasizes" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #ENSURE
    "ensure" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "ensured" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "ensuring" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "ensures" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #ENTITLE
    "entitle" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    "entitled" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "entitling" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    "entitles" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    
    #ESTIMATE
    "estimate": {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                               [NP_ev1, NP_ev2]],
                              [MODAL, MODAL])}, 
    "estimated": {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [NP_ev1, NP_ev2]],
                               [MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "estimates": {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                [NP_ev1, NP_ev2]],
                               [MODAL, MODAL])}, 
    "estimating": {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES],
                                 [NP_ev1, NP_ev2]],
                                [MODAL, MODAL])}, 
    #EXCLAIM
    "exclaim": {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                              [EVIDENTIAL])}, 
    "exclaimed": {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                              [EVIDENTIAL])}, 
    "exclaiming": {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                              [EVIDENTIAL])}, 
    "exclaims": {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]],
                              [EVIDENTIAL])}, 
    
    #EXCUSE
    "excuse": {'forward' : ([[FOR_ING_clause, FOR_NPev], [FROM_ING_clause, FROM_NPev]],
                              [FACTIVE, MODAL])}, 
    "excused": {'forward' : ([[FOR_ING_clause, FOR_NPev], [FROM_ING_clause, FROM_NPev]],
                              [FACTIVE, MODAL])}, 
    "excuses": {'forward' : ([[FOR_ING_clause, FOR_NPev], [FROM_ING_clause, FROM_NPev]],
                              [FACTIVE, MODAL])}, 
    "excusing": {'forward' : ([[FOR_ING_clause, FOR_NPev], [FROM_ING_clause, FROM_NPev]],
                              [FACTIVE, MODAL])}, 

    #EXPAND
    "expand" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "expanded" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "expanding" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "expands" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #EXPECT
    "expect" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},
    "expected" : {'forward' : ([[TO_clause1, TO_clause3], [THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                               [MODAL, MODAL, MODAL]),
                  'backwards' : ([[RelClauseExplicPerfect], [Passive1, RelClauseExplic]], [FACTIVE, MODAL])},
    "expecting" : {'forward' : ([[TO_clause1, TO_clause3], [THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                                [MODAL, MODAL, MODAL])},
    "expects" : {'forward' : ([[TO_clause1, TO_clause3], [THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                              [MODAL, MODAL, MODAL])},

    #EXPLAIN
    "explain" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "explained" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "explaining" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "explains" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #EXPRESS
    "express" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    "expressed" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    "expressing" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    "expresses" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])}, 
    
    #EXPLORE
    # TO patterns: purpose clause
    "explore" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3], [IND_INTERROG]], [MODAL, MODAL, MODAL])}, 
    "explored" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3], [IND_INTERROG]], [MODAL, MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "exploring" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3], [IND_INTERROG]], [MODAL, MODAL, MODAL])}, 
    "explores" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3], [IND_INTERROG]], [MODAL, MODAL, MODAL])}, 
    
    #EXTENDED
    "extend" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "extended" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "extends" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "extending" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #FACE
    "face" : {'forward' : ([[NP_ev1, NP_ev2, WITH_NPev]], [FACTIVE])},
    "faced" : {'forward' : ([[NP_ev1, NP_ev2, WITH_NPev]], [FACTIVE]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "faces" : {'forward' : ([[NP_ev1, NP_ev2, WITH_NPev]], [FACTIVE])},
    "facing" : {'forward' : ([[NP_ev1, NP_ev2, WITH_NPev]], [FACTIVE])},
    
    #FAIL
    "fail" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [COUNTER_FACTIVE])},
    "failed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [COUNTER_FACTIVE])},
    "fails" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [COUNTER_FACTIVE])},
    "failing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [COUNTER_FACTIVE])},

    #FANCY
    "fancy" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ING_clause], [NP_ev1, NP_ev2], [ING_clause]],
                            [MODAL, MODAL, MODAL, MODAL, MODAL])},
    "fancied" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ING_clause], [NP_ev1, NP_ev2], [ING_clause]],
                            [MODAL, MODAL, MODAL, MODAL, MODAL])},
    "fancying" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ING_clause], [NP_ev1, NP_ev2], [ING_clause]],
                            [MODAL, MODAL, MODAL, MODAL, MODAL])},
    "fancies" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ING_clause], [NP_ev1, NP_ev2], [ING_clause]],
                              [MODAL, MODAL, MODAL, MODAL, MODAL])},

    #FASCINATE
    "fascinate" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]], [FACTIVE]),
                   'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "fascinated" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]], [FACTIVE]),
                    'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "fascinates" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]], [FACTIVE]),
                    'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    "fascinating" : {'forward' : ([[THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]], [FACTIVE]),
                     'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},    
    
    #FAVOR
    "favor" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "favored" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "favoring" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "favors" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    
    #FEAR
    #Not sure about FACTIVE
    "fear" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL, FACTIVE])},
    "feared" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, FACTIVE]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "fearing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL, FACTIVE])},
    "fears" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL, FACTIVE])},
    
    #FEEL
    "feel" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause], [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3,]],
                           [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "felt" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause], [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3,]],
                           [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "feeling" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause], [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3,]],
                           [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "feels" : {'forward' : ([[NP_ev1, NP_ev2], [ING_clause], [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3,]],
                           [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    
    
    #FIGURE
    "figure" : {'forward' : ([[THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "figured" : {'forward' : ([[THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    "figuring" : {'forward' : ([[THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    "figures" : {'forward' : ([[THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_that_QUOTES, THAT_clause_NOT_that, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},

    #FILE
    "file" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "filed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "files" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "filing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #FIND OUT
    #Risky: needs OUT
    "find" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that], [ABOUT_NPev, ABOUT_ING_clause], [IND_INTERROG_nonfin]],
                           [FACTIVE, FACTIVE, MODAL])},
    "found" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that], [ABOUT_NPev, ABOUT_ING_clause], [IND_INTERROG_nonfin]],
                           [FACTIVE, FACTIVE, MODAL])},
    "finding" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that], [ABOUT_NPev, ABOUT_ING_clause], [IND_INTERROG_nonfin]],
                           [FACTIVE, FACTIVE, MODAL])},
    "finds" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG, THAT_clause_NOT_that], [ABOUT_NPev, ABOUT_ING_clause], [IND_INTERROG_nonfin]],
                           [FACTIVE, FACTIVE, MODAL])},
    
    #FORBID
    "forbid" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "forbids" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "forbade" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "forbidding" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "forbidden" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},

    #FORCE
    "force" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    "forced" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "forces" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    "forcing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])}, 
    
    #FORECAST
    "forecast" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3]], [MODAL, MODAL])}, 
    "forecasted" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3]], [MODAL, MODAL])}, 
    "forecasting" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3]], [MODAL, MODAL])}, 
    "forecasts" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3]], [MODAL, MODAL])}, 

    #FORGET
    "forget" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, IND_INTERROG, THAT_clause_NOT_that],
                              [NP_ev1, NP_ev2, ABOUT_NPev], [TO_clause1, TO_clause3], [THAT_clause_if]],
                             [FACTIVE, FACTIVE, MODAL, MODAL])},
    "forgets" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, IND_INTERROG, THAT_clause_NOT_that],
                               [NP_ev1, NP_ev2, ABOUT_NPev], [TO_clause1, TO_clause3], [THAT_clause_if]],
                             [FACTIVE, FACTIVE, MODAL, MODAL])},
    "forgetting" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, IND_INTERROG, THAT_clause_NOT_that],
                                  [NP_ev1, NP_ev2, ABOUT_NPev], [TO_clause1, TO_clause3], [THAT_clause_if]],
                             [FACTIVE, FACTIVE, MODAL, MODAL])},
    "forgot" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, IND_INTERROG, THAT_clause_NOT_that],
                              [NP_ev1, NP_ev2, ABOUT_NPev], [TO_clause1, TO_clause3], [THAT_clause_if]],
                             [FACTIVE, FACTIVE, MODAL, MODAL])},
    "forgotten" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, IND_INTERROG, THAT_clause_NOT_that],
                                 [NP_ev1, NP_ev2], [TO_clause1, TO_clause3], [THAT_clause_if]],
                             [FACTIVE, FACTIVE, MODAL, MODAL])},     

    #FORGIVE
    "forgive" : {'forward' : ([[FOR_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "forgives" : {'forward' : ([[FOR_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "forgave" : {'forward' : ([[FOR_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "forgiven" : {'forward' : ([[FOR_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "forgiving" : {'forward' : ([[FOR_ING_clause], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},

    #FORSEE
    "forsee" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},
    "forseeing" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},
    "forseen" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},
    "forsaw" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL])},
    
    #GLOSS
    #Gloss OVER
    "gloss" : {'forward' : ([[OVER_NPev]], [FACTIVE])},
    "glossed" : {'forward' : ([[OVER_NPev]], [FACTIVE])},
    "glosses" : {'forward' : ([[OVER_NPev]], [FACTIVE])},
    "glossing" : {'forward' : ([[OVER_NPev]], [FACTIVE])},

    #GRANT
    "grant" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "granted" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "granting" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "grants" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    
    #GRASP
    "grasp" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "grasped" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "grasping" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},
    "grasps" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_that, THAT_clause_NOT_that]], [FACTIVE, FACTIVE])},

    #GUARANTEE
    "guarantee" : {'forward' : ([[TO_clause1, TO_clause3],
                                 [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                                [MODAL, MODAL, MODAL])},
    "guaranteed" : {'forward' : ([[TO_clause1, TO_clause3],
                                  [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                                 [MODAL, MODAL, MODAL])},
    "guaranteeing" : {'forward' : ([[TO_clause1, TO_clause3],
                                    [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                                   [MODAL, MODAL, MODAL])},
    "guarantees" : {'forward' : ([[TO_clause1, TO_clause3],
                                  [THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_SIMPLE, THAT_clause_NOT_that],[NP_ev1, NP_ev2]],
                                 [MODAL, MODAL, MODAL])},

    #GUESS
    #Not sure about that clause as modal
    "guess" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]],
                            [FACTIVE, MODAL])},
    "guessed" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]],
                              [FACTIVE, MODAL])},
    "guesses" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]],
                              [FACTIVE, MODAL])},
    "guessing" : {'forward' : ([[IND_INTERROG], [THAT_clause_that, THAT_clause_if, THAT_clause_NOT_that]],
                               [FACTIVE, MODAL])},

    #HAIL
    "hail" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "hailed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "hailing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "hails" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #HAPPEN
    "happen" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [FACTIVE, FACTIVE])},
    "happened" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [FACTIVE, FACTIVE])},
    "happens" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [FACTIVE, FACTIVE])},
    "happening" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                                [FACTIVE, FACTIVE])},
    
    
    #HEAR
    "hear" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "heard" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "hearing" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "hears" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, IND_INTERROG, THAT_clause_NOT_that], [ING_clause], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},

    #HELP
    "help" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]],
                           [MODAL])},
    "helped" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]],
                             [MODAL])},
    "helping" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]],
                              [MODAL])},
    "helps" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5, THAT_clause_NOT_tensed]],
                            [MODAL])},

    #HINT
    #Not sure
    "hint" : {'forward' : ([[THAT_clause_that], [AT_NPev]], [MODAL, MODAL])},
    "hinted" : {'forward' : ([[THAT_clause_that], [AT_NPev]], [MODAL, MODAL])},
    "hints" : {'forward' : ([[THAT_clause_that], [AT_NPev]], [MODAL, MODAL])},
    "hinting" : {'forward' : ([[THAT_clause_that], [AT_NPev]], [MODAL, MODAL])},
    
    #HOLDE
    'hold': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [NP_ev1, NP_ev2]],
                          [MODAL, MODAL, FACTIVE])},
    'held': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [NP_ev1, NP_ev2]],
                          [MODAL, MODAL, FACTIVE])},
    'holding': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [NP_ev1, NP_ev2]],
                          [MODAL, MODAL, FACTIVE])},
    'holds': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [NP_ev1, NP_ev2]],
                          [MODAL, MODAL, FACTIVE])},


    #HOPE
    'hope': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that]],
                          [MODAL, MODAL])},
    'hoped': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that]],
             [MODAL, MODAL])},
    'hopes': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that]],
             [MODAL, MODAL])},
    'hoping': {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that]],
                            [MODAL, MODAL])},
    
    #HYPOTHESIZE
    "hypothesize" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, FACTIVE])},
    "hypothesized" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, FACTIVE])},
    "hypothesizes" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, FACTIVE])},
    "hypothesizing" : {'forward' : ([[THAT_clause_that], [ABOUT_NPev]], [MODAL, FACTIVE])},
    
    #IGNORE
    "ignore" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                             [FACTIVE, FACTIVE])},
    "ignored" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                              [FACTIVE, FACTIVE])},
    "ignores" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                              [FACTIVE, FACTIVE])},
    "ignoring" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]],
                               [FACTIVE, FACTIVE])},
    #IMAGINE
    "imagine" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, IND_INTERROG], [NP_ev1, NP_ev2], [ING_clause]],
                                 [MODAL, MODAL, MODAL])},
    "imagined" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, IND_INTERROG], [NP_ev1, NP_ev2], [ING_clause]],
                                 [MODAL, MODAL, MODAL])},
    "imagining" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, IND_INTERROG], [NP_ev1, NP_ev2], [ING_clause]],
                                 [MODAL, MODAL, MODAL])},
    "imagines" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, IND_INTERROG], [NP_ev1, NP_ev2], [ING_clause]],
                                 [MODAL, MODAL, MODAL])},

    #IMPLEMENT
    "implement" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "implemented" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                     'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "implementing" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "implements" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    
    #IMPLY
    "imply" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "implied" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "implies" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    "implying" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [MODAL])},
    
    #IMPOSE
    'impose' : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'imposed' : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    'imposes' : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    'imposing' : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    
    #IMPROVE
    "improve" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "improved" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "improves" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "improving" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #INCREASE
    "increase" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "increased" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "increasing" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    "increases" : {'forward' : ([[NP_ev1, NP_ev2, ING_clause]], [FACTIVE])},
    
    #INDICATE
    "indicate" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    "indicated" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "indicates" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "indicating" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    
    #INSIST
    "insist" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "insisted" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "insisting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "insists" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #INTEND
    "intend" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "intended" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "intending" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "intends" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #INTIMATE
    "intimate" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "intimated" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "intimates" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "intimating" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #INVALIDATE
    #Not sure about Factive
    "invalidate" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "invalidated" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                     'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "invalidates" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "invalidating" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #INVESTIGATE
    "investigate" : {'forward' : ([[THAT_clause_if], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    "investigated" : {'forward' : ([[THAT_clause_if], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE]),
                      'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "investigates" : {'forward' : ([[THAT_clause_if], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    "investigating" : {'forward' : ([[THAT_clause_if], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    
    #INVITE
    "invite" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "invited" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "invites" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "inviting" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #JUSTIFY
    #Can be both modal and factive
    "justify" : {'forward' : ([[ING_clause]], [MODAL])},
    "justified" : {'forward' : ([[ING_clause]], [MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "justifies" : {'forward' : ([[ING_clause]], [MODAL])},
    "justifying" : {'forward' : ([[ING_clause]], [MODAL])},
    
    #KNOW
    "know" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that,  THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                            [IND_INTERROG_nonfin, TO_clause1]],
                           [FACTIVE, FACTIVE, MODAL])},
    "known" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that,  THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                             [IND_INTERROG_nonfin, TO_clause1]],
                            [FACTIVE, FACTIVE, MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "knew" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that,  THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                            [IND_INTERROG_nonfin, TO_clause1]],
                           [FACTIVE, FACTIVE, MODAL])},
    "knowing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that,  THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                               [IND_INTERROG_nonfin, TO_clause1]],
                              [FACTIVE, FACTIVE, MODAL])},
    "knows" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that,  THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                             [IND_INTERROG_nonfin, TO_clause1]],
                            [FACTIVE, FACTIVE, MODAL])},
    
    #LAUGH
    "laugh" : {'forward' : ([[AT_NPev]], [FACTIVE])},
    "laughed" : {'forward' : ([[AT_NPev]], [FACTIVE])},
    "laughing" : {'forward' : ([[AT_NPev]], [FACTIVE])},
    "laughs" : {'forward' : ([[AT_NPev]], [FACTIVE])},

    #LAST
    "last" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [FACTIVE])},
    "lasted" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [FACTIVE])},
    "lasting" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [FACTIVE])},
    "lasts" : {'backwards' : ([[NP_evAsSubj1, NP_evAsSubj2]], [FACTIVE])},

    #LEAD
    #Not sure about MODAL (FACTIVE?)
    "lead" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "led" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL]),
             'backwards' : ([[Passive1]], [FACTIVE])},
    "leading" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},
    "leads" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]], [FACTIVE, MODAL])},

    #LEARN
    "learn" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                             [IND_INTERROG_nonfin, TO_clause1]],
                            [FACTIVE, FACTIVE, MODAL])}, 
    "learned" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                               [IND_INTERROG_nonfin, TO_clause1]],
                              [FACTIVE, FACTIVE, MODAL])},
    "learning" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                                [IND_INTERROG_nonfin, TO_clause1]],
                               [FACTIVE, FACTIVE, MODAL])},
    "learns" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                              [IND_INTERROG_nonfin, TO_clause1]],
                             [FACTIVE, FACTIVE, MODAL])},
    "learnt" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                               [IND_INTERROG_nonfin, TO_clause1]],
                              [FACTIVE, FACTIVE, MODAL])},

    
    #LEAVE
    "leave" : {'forward' : ([[OBJCOMPL_pastPart, OBJCOMPL_adj]], [FACTIVE])},
    "left" : {'forward' : ([[OBJCOMPL_pastPart, OBJCOMPL_adj]], [FACTIVE])},
    "leaving" : {'forward' : ([[OBJCOMPL_pastPart, OBJCOMPL_adj]], [FACTIVE])},
    "leaves" : {'forward' : ([[OBJCOMPL_pastPart, OBJCOMPL_adj]], [FACTIVE])},
    
    #LET
    "let" : {'forward' : ([[THAT_clause_NOT_tensed]], [MODAL])},
    "letting" : {'forward' : ([[THAT_clause_NOT_tensed]], [MODAL])},
    "lets" : {'forward' : ([[THAT_clause_NOT_tensed]], [MODAL])},

    
    #LIKE
    "like" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "liked" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "liking" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "likes" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #LISTEN
    "listen" : {'forward' : ([[TO_NPev, TO_ING_clause]], [MODAL])},
    "listened" : {'forward' : ([[TO_NPev, TO_ING_clause]], [MODAL])},
    "listening" : {'forward' : ([[TO_NPev, TO_ING_clause]], [MODAL])},
    "listens" : {'forward' : ([[TO_NPev, TO_ING_clause]], [MODAL])},

    #LOOK:
    #(Look for, at)
    "look" : {'forward' : ([[FOR_NPev], [AT_NPev]], [MODAL, FACTIVE])},
    "looked" : {'forward' : ([[FOR_NPev], [AT_NPev]], [MODAL, FACTIVE])},
    "looking" : {'forward' : ([[FOR_NPev], [AT_NPev]], [MODAL, FACTIVE])},
    "looks" : {'forward' : ([[FOR_NPev], [AT_NPev]], [MODAL, FACTIVE])},
    
    #LOVE
    "love" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [ING_clause, NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "loved" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [ING_clause, NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "loving" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [ING_clause, NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},
    "loves" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_that], [ING_clause, NP_ev1, NP_ev2]], [MODAL, MODAL, MODAL])},

    #MAINTAIN
    "maintain" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "maintained" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "maintaining" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "maintains" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},


    #MEAN
    "mean" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [MODAL])},
    "meant" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [MODAL])},
    "means" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [MODAL])},
    "meaning" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [MODAL])},
    
    #MEET
    "meet" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "met" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
             'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])}, 
    "meeting" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "meets" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    
    #MENTION:
    "mention" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_if, IND_INTERROG], [ING_clause], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "mentioned"  : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_if, IND_INTERROG], [ING_clause], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "mentioning" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_if, IND_INTERROG], [ING_clause], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "mentions" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_if, IND_INTERROG], [ING_clause], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #MISS
    "miss" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2]], [COUNTER_FACTIVE, FACTIVE])},
    "missed" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2]], [COUNTER_FACTIVE, FACTIVE])},
    "missing" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2]], [COUNTER_FACTIVE, FACTIVE])},
    "misses" : {'forward' : ([[ING_clause], [NP_ev1, NP_ev2]], [COUNTER_FACTIVE, FACTIVE])},
    

    #MOVE
    "move" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "moved" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "moves" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    "moving" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, FACTIVE])},
    
    #NEED
    "need" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL])},
    "needed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "needing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL])},
    "needs" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL])},
    
    #NEGOTIATE
    "negotiate" : {'forward' : ([[NP_ev1, NP_ev2], [FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]],
                                [MODAL, MODAL, MODAL])},
    "negotiated" : {'forward' : ([[NP_ev1, NP_ev2], [FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]],
                                 [MODAL, MODAL, MODAL]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "negotiates" : {'forward' : ([[NP_ev1, NP_ev2], [FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]],
                                 [MODAL, MODAL, MODAL])},
    "negotiating" : {'forward' : ([[NP_ev1, NP_ev2], [FOR_NPev, FOR_ING_clause], [TO_clause1, TO_clause3, TO_clause5]],
                                  [MODAL, MODAL, MODAL])},
    
    #NOTED
    "note" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "noted" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "notes" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "noting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    
    #NOTICE
    "notice" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG]],
                             [FACTIVE])},
    "noticed" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG]],
                             [FACTIVE])},
    "noticing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG]],
                             [FACTIVE])},
    "notices" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG]],
                             [FACTIVE])},
    

    #NULLIFY
    "nullify" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "nullified" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "nullifying" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "nullifies" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #OBSERVE
    "observe" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, EVIDENTIAL])},
    "observed" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [NP_ev1, NP_ev2]],
                               [EVIDENTIAL, EVIDENTIAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "observes" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [NP_ev1, NP_ev2]],
                               [EVIDENTIAL, EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "observing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [NP_ev1, NP_ev2]],
                                [EVIDENTIAL, EVIDENTIAL])},
    

    #OFFER
    "offer" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "offered" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "offering" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "offers" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #OPPOSE
    #Ambiguos
    "oppose" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "opposed" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "opposes" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "opposing" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},

    #ORDER
    "order" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "ordered" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "ordering" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "orders" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #ORGANIZE
    "organize" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1]], [MODAL, MODAL])},
    "organized" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1]], [MODAL, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "organizes" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1]], [MODAL, MODAL])},
    "organizing" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1]], [MODAL, MODAL])},
    
    #PAY
    # Purpose clauses
    "pay" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "payed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])}, 
    "paid" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "paying" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "pays" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 

    #PERCEIVE
    "perceive" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])}, 
    "perceived" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])}, 
    "perceiving" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])}, 
    "perceives" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])}, 
    
    #PERMIT
    'permit' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},
    'permited' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause], [NP_ev1, NP_ev2]],
                               [MODAL, MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    'permiting' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause], [NP_ev1, NP_ev2]],
                                [MODAL, MODAL, MODAL])},
    'permits' : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL, MODAL])},
    
    #PERSUADE
    "persuade" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ABOUT_ING_clause]],
                               [MODAL, MODAL])},
    "persuaded" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ABOUT_ING_clause]],
                                [MODAL, MODAL])},
    "persuades" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ABOUT_ING_clause]],
                                [MODAL, MODAL])},
    "persuading" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ABOUT_ING_clause]],
                                 [MODAL, MODAL])},
    
    #PLAN:
    "plan" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL])},
    "planned" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "planning" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                               [MODAL, MODAL])},
    "plans" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL])},
    
    #PLEASE
    #    "please" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that],
    #                              [WITH_NPev]],
    #                [FACTIVE, FACTIVE, FACTIVE])}, 
    "pleased" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that],
                               [WITH_NPev]],
                              [FACTIVE, FACTIVE, FACTIVE])}, 
    #    "pleases" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that],
    #                               [WITH_NPev]],
    #                 [FACTIVE, FACTIVE, FACTIVE])}, 
    "pleasing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that],
                                [WITH_NPev]],
                               [FACTIVE, FACTIVE, FACTIVE])}, 
    
    #PLEDGE
    "pledge" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "pledged" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "pledges" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "pledging" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #POINT
    # Risky one. Needs to be followed by 'out'
    "point" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [EVIDENTIAL])},    
    "pointed" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [EVIDENTIAL])},    
    "pointing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [EVIDENTIAL])},    
    "points" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that]], [EVIDENTIAL])},    

    #POST
    "post" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL])},
    "posted" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL])},
    "posting" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL])},
    "posts" : {'forward' : ([[NP_ev1, NP_ev2]], [EVIDENTIAL])},
    
    #POSTULATE
    "postulate" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "postulated" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "postulates" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "postulating" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},

    #PREDICATE
    "predicate" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "predicated" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "predicates" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "predicating" : {'forward' : ([[THAT_clause_that]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #PREDICT
    "predict" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "predicted" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_NOT_that, THAT_clause_that]], [MODAL, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "predicting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "predicts" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #PREFER
    "prefer" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},    
    "prefered" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},    
    "prefering" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},    
    "prefers" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL, MODAL])},    

    #PREPARE
    "prepare" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL, MODAL])}, 
    "prepared" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])}, 
    "prepares" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL, MODAL])}, 
    "preparing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_ING_clause, FOR_NPev]], [MODAL, MODAL])}, 
    
    #PRESS
    "press" : {'forward' : ([[FOR_NPev]], [MODAL])},
    "pressed" : {'forward' : ([[FOR_NPev]], [MODAL])},
    "presses" : {'forward' : ([[FOR_NPev]], [MODAL])},
    "pressing" : {'forward' : ([[FOR_NPev]], [MODAL])},
    
    #PRESUME
    "presume" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that]], [MODAL, MODAL])},
    "presumed" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that]], [MODAL, MODAL])},
    "presumes" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that]], [MODAL, MODAL])},
    "presuming" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that]], [MODAL, MODAL])},

    #PRETEND
    "pretend" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "pretended" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "pretending" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},
    "pretends" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3]],
                              [COUNTER_FACTIVE, COUNTER_FACTIVE])},

    #PRICE
    "price" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "priced" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "prices" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "pricing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #PROHIBIT
    "prohibit" : {'forward' : ([[FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "prohibited" : {'forward' : ([[FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "prohibiting" : {'forward' : ([[FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "prohibits" : {'forward' : ([[FROM_ING_clause], [NP_ev1, NP_ev2]], [MODAL, MODAL])},

    #PROMISE
    "promise" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause]],
                              [MODAL, MODAL, MODAL, MODAL])},
    "promised" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause]],
                               [MODAL, MODAL, MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "promises" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause]],
                               [MODAL, MODAL, MODAL, MODAL])},
    "promising" : {'forward' : ([[TO_clause1, TO_clause3],[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause]],
                                [MODAL, MODAL, MODAL, MODAL])},
    
    #PROPOSE
    "propose" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                               [NP_ev1, NP_ev2], [ING_clause]],
                              [MODAL, MODAL, MODAL, MODAL])},
    "proposed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                [NP_ev1, NP_ev2], [ING_clause]],
                               [MODAL, MODAL, MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "proposes" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                [NP_ev1, NP_ev2], [ING_clause]],
                               [MODAL, MODAL, MODAL, MODAL])},
    "proposing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5],[THAT_clause_that, THAT_clause_NOT_that],
                                 [NP_ev1, NP_ev2], [ING_clause]],
                                [MODAL, MODAL, MODAL, MODAL])},
    
    #PROTECT
    "protect" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5], [FROM_NPev, FROM_ING_clause]],
                              [FACTIVE, MODAL, MODAL])},
    "protected" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5], [FROM_NPev, FROM_ING_clause]],
                                [FACTIVE, MODAL, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "protecting" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5], [FROM_NPev, FROM_ING_clause]],
                                 [FACTIVE, MODAL], MODAL)},
    "protects" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5], [FROM_NPev, FROM_ING_clause]],
                               [FACTIVE, MODAL, MODAL])},

    #PROVE
    "prove" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "proved" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE]),
                'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "proves" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "proven" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE]),
                'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "proving" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    
    #PROVIDE
    "provide" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "provided" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "provides" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "providing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    
    #PUBLISH
    "publish" :  {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                            [EVIDENTIAL])},
    "published" :  {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                            [EVIDENTIAL])},
    "publishing" :  {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                            [EVIDENTIAL])},
    "publishes" :  {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                            [EVIDENTIAL])},

    #QUESTION
    "question" : {'forward' : ([[THAT_clause_if], [ABOUT_ING_clause, ABOUT_NPev]], [MODAL, MODAL])},
    "questioned" : {'forward' : ([[THAT_clause_if], [ABOUT_ING_clause, ABOUT_NPev]], [MODAL, MODAL])},
    "questions" : {'forward' : ([[THAT_clause_if], [ABOUT_ING_clause, ABOUT_NPev]], [MODAL, MODAL])},
    "questioning" : {'forward' : ([[THAT_clause_if], [ABOUT_ING_clause, ABOUT_NPev]], [MODAL, MODAL])},

    #QUOTE
    "quote" : {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                            [EVIDENTIAL])},
    "quoted" : {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                             [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "quotes" : {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                             [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "quoting" : {'forward' : ([[THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_N_that_N_report, THAT_clause_that_NOT_report]],
                              [EVIDENTIAL])},

    #READ
    "read" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE])},
    "reading" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE])},
    "reads" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE])},

    #REALISE
    "realise" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realised" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realising" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realises" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    
    #REALIZE
    "realize" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realized" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realizing" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    "realizes" : {'forward' : ([[THAT_clause_that, THAT_clause_if, IND_INTERROG]],
                            [FACTIVE])},
    
    #REASSURE
    "reassure" : {'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},
    "reassured" : {'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},
    "reassures" : {'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},
    "reassuring" : {'backwards' : ([NP_evAsSubj1, NP_evAsSubj2], [FACTIVE])},
    
    #RECALL
    "recall" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG], [NP_ev1, NP_ev2,ING_clause]],
                             [FACTIVE, FACTIVE])},
    "recalled" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG], [NP_ev1, NP_ev2, ING_clause]],
                             [FACTIVE, FACTIVE])},
    "recalling" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG], [NP_ev1, NP_ev2, ING_clause]],
                                [FACTIVE, FACTIVE])},
    "recalls" : {'forward' : ([[THAT_clause_that,  THAT_clause_if, IND_INTERROG], [NP_ev1, NP_ev2, ING_clause]],
                              [FACTIVE, FACTIVE])},
    
    #RECKON
    "reckon" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ON_ING_clause, ON_NPev], [WITHOUT_NPev]],
                             [MODAL, MODAL, MODAL, FACTIVE])},
    "reckoned" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ON_ING_clause, ON_NPev], [WITHOUT_NPev]],
                             [MODAL, MODAL, MODAL, FACTIVE])},
    "reckoning" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ON_ING_clause, ON_NPev], [WITHOUT_NPev]],
                             [MODAL, MODAL, MODAL, FACTIVE])},
    "reckons" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3], [ON_ING_clause, ON_NPev], [WITHOUT_NPev]],
                             [MODAL, MODAL, MODAL, FACTIVE])},

    #RECOGNISE
    "recognise" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognised" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognises" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognising" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                  [FACTIVE, FACTIVE])},

    #RECOGNIZE
    "recognize" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognized" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognizes" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                [FACTIVE, FACTIVE])},
    "recognizing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that], [NP_ev1, NP_ev2]], 
                                  [FACTIVE, FACTIVE])},

    #REFER
    "refer" : {'forward' : ([[TO_NPev]], [FACTIVE])},
    "referred" : {'forward' : ([[TO_NPev]], [FACTIVE])},
    "referring" : {'forward' : ([[TO_NPev]], [FACTIVE])},
    "refers" : {'forward' : ([[TO_NPev]], [FACTIVE])},

    #REFRAIN
    "refrain" : {'forward' : ([[FROM_ING_clause]], [COUNTER_FACTIVE])},
    "refrained" : {'forward' : ([[FROM_ING_clause]], [COUNTER_FACTIVE])},
    "refrains" : {'forward' : ([[FROM_ING_clause]], [COUNTER_FACTIVE])},
    "refraining" : {'forward' : ([[FROM_ING_clause]], [COUNTER_FACTIVE])},

    #REGRET
    "regret" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "regretted" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "regretting" :{'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "regrets" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},

    #REJECT
    #Carful with relType. Is it totally appropriate?
    "reject" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "rejected" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "rejecting" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "rejects" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #REMARK
    "remark"  : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "remarked"  : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "remarks"  : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "remarking"  : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #REMEMBER
    "remember" : {'forward' : ([[THAT_clause_that,  THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                                [IND_INTERROG_nonfin, TO_clause1]],
                               [FACTIVE, FACTIVE, MODAL])},
    "remembered" : {'forward' : ([[THAT_clause_that,  THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                                [IND_INTERROG_nonfin, TO_clause1]],
                               [FACTIVE, FACTIVE, MODAL])},
    "remembering" : {'forward' : ([[THAT_clause_that,  THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                                [IND_INTERROG_nonfin, TO_clause1]],
                               [FACTIVE, FACTIVE, MODAL])},
    "remembers" : {'forward' : ([[THAT_clause_that,  THAT_clause_NOT_that, THAT_clause_if, IND_INTERROG], [ABOUT_NPev, ABOUT_ING_clause],
                                [IND_INTERROG_nonfin, TO_clause1]],
                               [FACTIVE, FACTIVE, MODAL])},

    #RENOUNCE
    "renounce" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    "renounced" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    "renouncing" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    "renounces" : {'forward' : ([[NP_ev1, NP_ev2]], [COUNTER_FACTIVE])},
    
    #REPLY
    "reply" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "replied" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                               [TO_clause1, TO_clause3, TO_clause5]],
                              [EVIDENTIAL, MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "replying" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                                [TO_clause1, TO_clause3, TO_clause5]],
                               [EVIDENTIAL, MODAL])},
    "replies" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                               [TO_clause1, TO_clause3, TO_clause5]],
                              [EVIDENTIAL, MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    

    #REPORT
    "report" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2], [OBJCOMPL_pastPart]],
                             [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "reported" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2], [OBJCOMPL_pastPart]],
                               [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "reporting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2], [OBJCOMPL_pastPart]],
                                [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "reports" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2], [OBJCOMPL_pastPart]],
                              [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #REQUIRE
    "require" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause],
                               [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL, MODAL, MODAL])},  
    "required" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause],
                                [TO_clause1, TO_clause3, TO_clause5]],
                               [MODAL, MODAL, MODAL, MODAL]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},  
    "requires" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause],
                                [TO_clause1, TO_clause3, TO_clause5]],
                               [MODAL, MODAL, MODAL, MODAL])},  
    "requiring" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that],[NP_ev1, NP_ev2], [ING_clause],
                                 [TO_clause1, TO_clause3, TO_clause5]],
                                [MODAL, MODAL, MODAL, MODAL])},  
    
    #RESENT
    "resent" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "resented" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "resenting" :{'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},
    "resents" : {'forward' : ([[THAT_clause_NOT_tensed, THAT_clause_that, THAT_clause_NOT_that, THAT_clause_SIMPLE], [NP_ev1, NP_ev2], [ING_clause]],
                             [FACTIVE, FACTIVE, FACTIVE])},

    #RESULT
    "result" : {'forward' : ([[THAT_clause_that], [IN_NPev, IN_ING_clause]],
                              [FACTIVE, FACTIVE])},  
    "resulted" : {'forward' : ([[THAT_clause_that], [IN_NPev, IN_ING_clause]],
                              [FACTIVE, FACTIVE])},  
    "results" : {'forward' : ([[THAT_clause_that], [IN_NPev, IN_ING_clause]],
                              [FACTIVE, FACTIVE])},  
    "resulting" : {'forward' : ([[THAT_clause_that], [IN_NPev, IN_ING_clause]],
                              [FACTIVE, FACTIVE])},  

    #REVEAL
    "reveal" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                             [EVIDENTIAL, FACTIVE])},
    "revealed" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                             [EVIDENTIAL, FACTIVE])},
    "revealing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                                [EVIDENTIAL, FACTIVE])},
    "reveals" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [IND_INTERROG]],
                             [EVIDENTIAL, FACTIVE])},
    
    #SAY:
    #- Only accounting for embedded THAT clauses.
    #- At present, not accounting for TO clauses or NP_ev.
    "said" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "say"  : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "saying" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},    
    "says" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #SCHEDULE
    "schedule" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "scheduled" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL]),
                   'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "schedules" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    "scheduling" : {'forward' : ([[FOR_NPev], [TO_clause1, TO_clause3, TO_clause5]], [MODAL, MODAL])},
    
    #SEE
    # - Missing sense of 'see' as intellectual perception.
    "see" : {'forward' : ([[ING_clause], [THAT_clause_NOT_tensed, THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "seen" : {'forward' : ([[ING_clause], [THAT_clause_NOT_tensed, THAT_clause_that], [NP_ev1, NP_ev2]],
                           [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL]),
              'backwards' : ([[Passive1, RelClauseExplic]], [EVIDENTIAL])},
    "saw" : {'forward' : ([[ING_clause], [THAT_clause_NOT_tensed, THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]],
                          [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "sees" : {'forward' : ([[ING_clause], [THAT_clause_NOT_tensed, THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]],
                           [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    "seeing" : {'forward' : ([[ING_clause], [THAT_clause_NOT_tensed, THAT_clause_NOT_that, THAT_clause_that], [NP_ev1, NP_ev2]],
                             [EVIDENTIAL,EVIDENTIAL,EVIDENTIAL])},
    

    #SEEK:
    "seek" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]],
                           [MODAL, MODAL])},
    "seeking" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL])},
    "seeks" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    "sought" : {'forward' : ([[NP_ev1, NP_ev2], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    
    #SELL
    #Purpose clauses
    "sell" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "sells" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "selling" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "sold" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #SEEM
    "seem" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                           [MODAL, MODAL])},
    "seemed" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "seeming" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                              [MODAL, MODAL])},
    "seems" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    
    #SET
    "set" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev]], [MODAL, MODAL])},
    "sets" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev]], [MODAL, MODAL])},    
    "setting" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev]], [MODAL, MODAL])},
    
    #SHOUT
    "shout" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "shouted" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "shouting" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "shouts" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    

    #SHOWN
    "show" : {'forward' : ([[NP_ev1, NP_ev2],[THAT_clause_NOT_that, THAT_clause_that],
                            [TO_clause1, TO_clause3, TO_clause5]],
                           [FACTIVE, FACTIVE, MODAL])}, 
    "showed" : {'forward' : ([[NP_ev1, NP_ev2],[THAT_clause_NOT_that, THAT_clause_that],
                              [TO_clause1, TO_clause3, TO_clause5]],
                             [FACTIVE, FACTIVE, MODAL])}, 
    "shown" : {'forward' : ([[NP_ev1, NP_ev2],[THAT_clause_NOT_that, THAT_clause_that],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [FACTIVE, FACTIVE, MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "shows" : {'forward' : ([[NP_ev1, NP_ev2],[THAT_clause_NOT_that, THAT_clause_that],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [FACTIVE, FACTIVE, MODAL])}, 
    "showing" : {'forward' : ([[NP_ev1, NP_ev2],[THAT_clause_NOT_that, THAT_clause_that],
                               [TO_clause1, TO_clause3, TO_clause5]],
                              [FACTIVE, FACTIVE, MODAL])},
    
    #SIGH
    "sigh" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "sighed" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "sighes" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
                'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "sighing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    

    #SOUND
    "sound" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_if]], [MODAL])},
    "sounded" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_if]], [MODAL])},
    "sounding" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_if]], [MODAL])},
    "sounds" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_if]], [MODAL])},

    #SPECULATE
    "speculate" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "speculated" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "speculates" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "speculating" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL])},
    
    #SPREAD
    "spread" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    "spreading" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},
    "spreads" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that]], [EVIDENTIAL])},

    #STALL
    "stall" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "stalled" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "stalling" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    "stalls" : {'forward' : ([[NP_ev1, NP_ev2]], [MODAL])},
    
    #STATE
    "state" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES], [IND_INTERROG]], [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "stated" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES], [IND_INTERROG]], [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "states" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES], [IND_INTERROG]], [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "stating" : {'forward' : ([[THAT_clause_that, THAT_clause_that_QUOTES], [IND_INTERROG]], [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #STRESS
    "stress"  : {'forward' : ([[THAT_clause_that,  THAT_clause_that_QUOTES], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "stressed"  : {'forward' : ([[THAT_clause_that,  THAT_clause_that_QUOTES], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "stressing"  : {'forward' : ([[THAT_clause_that,  THAT_clause_that_QUOTES], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE]),
                    'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "stresses"  : {'forward' : ([[THAT_clause_that,  THAT_clause_that_QUOTES], [NP_ev1, NP_ev2]], [EVIDENTIAL, FACTIVE]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},

    #STRUGGLE
    "struggle"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "struggled"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "struggling"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "struggles"  : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #SUGGEST
    "suggest" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                               [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [EVIDENTIAL, MODAL, MODAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "suggested" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                                 [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                [EVIDENTIAL, MODAL, MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "suggesting" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                                  [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                                 [EVIDENTIAL, MODAL, MODAL])},
    "suggests" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                                [TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                               [EVIDENTIAL, MODAL, MODAL]),
                  'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #SUPPORT
    "support" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "supported" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "supports" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "supporting" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #SUPPOSE
    "suppose" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "supposed" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [THAT_clause_NOT_that, THAT_clause_that]],
                             [MODAL, MODAL])},
    "supposing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},
    "supposes" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                             [MODAL, MODAL])},

    #SUSPECT
    "suspect" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_NOT_that, THAT_clause_that]], [MODAL, MODAL])},
    "suspected" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_NOT_that, THAT_clause_that]], [MODAL, MODAL])},
    "suspecting" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_NOT_that, THAT_clause_that]], [MODAL, MODAL])},
    "suspects" : {'forward' : ([[OF_NPev, OF_ING_clause], [THAT_clause_NOT_that, THAT_clause_that]], [MODAL, MODAL])},
    
    #SWEAR 
    "swear" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    "swearing" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    "swears" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    "swore" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},
    "sworn" : {'forward' : ([[THAT_clause_that, THAT_clause_NOT_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [MODAL, MODAL])},

    #SYMBOLIZE
    "symbolize" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "symbolized" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "symbolizing" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 
    "symbolizes" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])}, 

    #TALK
    "talk" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    "talked" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    "talking" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    "talks" : {'forward' : ([[ABOUT_NPev]], [MODAL])},
    
    #TELL
    "tell" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                            [TO_clause1, TO_clause3, TO_clause5],[PP_ABOUT]],
                           [EVIDENTIAL, MODAL, MODAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "telling" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                               [TO_clause1, TO_clause3, TO_clause5],[PP_ABOUT]],
                              [EVIDENTIAL, MODAL, MODAL])},
    "tells" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5],[PP_ABOUT]],
                            [EVIDENTIAL, MODAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "told" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                            [TO_clause1, TO_clause3, TO_clause5],[PP_ABOUT]],
                           [EVIDENTIAL, MODAL, MODAL]),
              'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #TESTIFY
    "testify" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "testified" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                   'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "testifying" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "testifies" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES]], [EVIDENTIAL]),
                 'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    
    #THANK
    "thank" : {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])},
    "thanked" : {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])},
    "thanks" : {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])},
    "thanking" : {'forward' : ([[FOR_ING_clause, FOR_NPev]], [FACTIVE])},

    #THINK
    "think" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]],
                            [MODAL])},
    "thinking" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]],
                               [MODAL])},
    "thinks" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]],
                             [MODAL])},
    "thought" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]],
                              [MODAL]),
                 'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    
    #TRY
    "try" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause]], [MODAL, MODAL])},
    "tried" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause]], [MODAL, MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "tries" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause]], [MODAL, MODAL])},
    "trying" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [ING_clause]], [MODAL, MODAL])},
 
    #TURN OUT
    #Risky: it needs OUT
    "turn" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                           [FACTIVE, FACTIVE])},
    "turned" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                           [FACTIVE, FACTIVE])},
    "turning" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                           [FACTIVE, FACTIVE])},
    "turns" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3, TO_clause5]],
                           [FACTIVE, FACTIVE])},

    #UNDERSTAND
    #Review: ambiguity issues here
    "understand" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    "understood" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE]),
                    'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "understands" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    "understanding" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that], [IND_INTERROG], [NP_ev1, NP_ev2]], [MODAL, FACTIVE, FACTIVE])},
    
    #URGE
    "urge" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "urged" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL]),
               'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "urges" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "urging" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #USE
    # Purpose clause
    "use" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "used" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "uses" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "using" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #VERIFY
    "verify" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "verified" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "verifies" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},
    "verifying" : {'forward' : ([[THAT_clause_that], [NP_ev1, NP_ev2]], [FACTIVE, FACTIVE])},

    #VOTE
    "vote" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "voted" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "votes" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    "voting" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])}, 
    
    #VOW
    "vow" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3]], [MODAL, MODAL])},
    "vowed" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3]], [MODAL, MODAL])},
    "vows" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3]], [MODAL, MODAL])},
    "vowing" : {'forward' : ([[THAT_clause_that], [TO_clause1, TO_clause3]], [MODAL, MODAL])},

    #WAIT
    "wait" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev, NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "waited" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev, NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "waiting" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev, NP_ev1, NP_ev2]], [MODAL, MODAL])},
    "waits" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [FOR_NPev, NP_ev1, NP_ev2]], [MODAL, MODAL])},
    
    #WANT 
    "want" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                           [MODAL, MODAL])},    
    "wanted" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                             [MODAL, MODAL])},    
    "wanting" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                              [MODAL, MODAL])},    
    "wants" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5], [NP_ev1, NP_ev2]],
                            [MODAL, MODAL])},

    #WARN
    "warn" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    "warned" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    "warning" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    "warns" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES, THAT_clause_SIMPLE]], [MODAL])},
    
    #WAIT
    "watch" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_NOT_tensed, IND_INTERROG], [ING_clause]],
                            [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "watched" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_NOT_tensed, IND_INTERROG], [ING_clause]],
                            [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "watching" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_NOT_tensed, IND_INTERROG], [ING_clause]],
                               [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},
    "watches" : {'forward' : ([[NP_ev1, NP_ev2], [THAT_clause_NOT_tensed, IND_INTERROG], [ING_clause]],
                              [EVIDENTIAL, EVIDENTIAL, EVIDENTIAL])},

    #WELCOME
    "welcome" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "welcomed" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE]),
                  'backwards' : ([[Passive1, RelClauseExplic]], [FACTIVE])},
    "welcomes" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},
    "welcoming" : {'forward' : ([[NP_ev1, NP_ev2]], [FACTIVE])},

    #WISH
    "wish" : {'forward': ([[THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that],
                           [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3]],
                          [COUNTER_FACTIVE, FACTIVE, MODAL, MODAL])},
    "wished" : {'forward': ([[THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that],
                             [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3]],
                            [COUNTER_FACTIVE, FACTIVE, MODAL, MODAL])},
    "wishing" : {'forward': ([[THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that],
                              [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3]],
                             [COUNTER_FACTIVE, FACTIVE, MODAL, MODAL])},
    "wishes" : {'forward': ([[THAT_clausePAST_that, THAT_clausePAST_NOT_that], [THAT_clausePERFECTIVE_NEG_that, THAT_clausePERFECTIVE_NEG_NOT_that],
                             [THAT_clause_that, THAT_clause_NOT_that], [TO_clause1, TO_clause3]],
                            [COUNTER_FACTIVE, FACTIVE, MODAL, MODAL])},
    
    #WILLING 
    "willing" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},

    #WONDER
    'wonder' : {'forward' : ([[THAT_clause_if, IND_INTERROG], [ABOUT_NPev], [THAT_clause_that, THAT_clause_NOT_that]],[MODAL, MODAL, FACTIVE, FACTIVE]),
                'reporting' : ([[MAINsentence]], [MODAL])},
    'wondered' : {'forward' : ([[THAT_clause_if, IND_INTERROG], [ABOUT_NPev], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL, FACTIVE, FACTIVE]),
                  'reporting' : ([[MAINsentence]], [MODAL])},
    'wondering' : {'forward' : ([[THAT_clause_if, IND_INTERROG], [ABOUT_NPev], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL, FACTIVE, FACTIVE]),
                   'reporting' : ([[MAINsentence]], [MODAL])},
    'wonders' : {'forward' : ([[THAT_clause_if, IND_INTERROG], [ABOUT_NPev], [THAT_clause_that, THAT_clause_NOT_that]], [MODAL, MODAL, FACTIVE, FACTIVE]),
                 'reporting' : ([[MAINsentence]], [MODAL])},

    #WORK
    #Purpose clauses
    "work" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "worked" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL]),
                'backwards' : ([[Passive1, RelClauseExplic]], [MODAL])},
    "working" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    "works" : {'forward' : ([[TO_clause1, TO_clause3, TO_clause5]], [MODAL])},
    
    #WORRY
    "worry" : {'forward' : ([[AT_NPev, AT_ING_clause], [THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause]], [MODAL, MODAL, FACTIVE])},
    "worried" : {'forward' : ([[AT_NPev, AT_ING_clause], [THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause]], [MODAL, MODAL, FACTIVE])},
    "worrying" : {'forward' : ([[AT_NPev, AT_ING_clause], [THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause]], [MODAL, MODAL, FACTIVE])},
    "worries" : {'forward' : ([[AT_NPev, AT_ING_clause], [THAT_clause_that], [ABOUT_NPev, ABOUT_ING_clause]], [MODAL, MODAL, FACTIVE])},

    #WRITE
    "write" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "writing" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "written" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "wrote" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES], [ABOUT_NPev]],
                            [EVIDENTIAL, FACTIVE]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},


    #YELL
    "yell" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "yelled" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "yelling" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},
    "yells" : {'forward' : ([[THAT_clause_NOT_that, THAT_clause_that, THAT_clause_that_QUOTES, THAT_clause_NOT_that_QUOTES],
                             [TO_clause1, TO_clause3, TO_clause5]],
                            [EVIDENTIAL, MODAL]),
               'reporting' : ([[MAINsentence]], [EVIDENTIAL])},


    }
