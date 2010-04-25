#!/usr/bin/perl -w

# Convert WSJ-style bracketed sentences to dependency structures


#############################################################################################

$depdir = $ENV{DEPDIR};
die "died: env. variable \$DEPDIR not defined\n" unless $depdir;
require "$depdir/lib/wsjutils.pl";

#$noheads_fname = "$depdir/tmp/noheads";
#$noheads_lex_fname = "$depdir/tmp/noheads.lex";
#$empty_nonterms_fname = "$depdir/tmp/empty.nonterms";
$noheads_fname = "";
$noheads_lex_fname = "";
$empty_nonterms_fname = "";

use Getopt::Std;


$current_sentence = undef;
$n_nonterminals = 0;
$unassigned_heads = 0;
$empty_nonterminals = 0;
$n_sentences = 0;
$n_sentences_with_heads = 0;
$n_traces = 0;



sub for_nonterms(&$);
sub for_nonterms_bottom_up(&$);
sub for_nodes_bottom_up(&$);
sub for_nodes(&$);
sub terminal($);
sub label($);
sub basic_label($);

  

#open(NOHEADS, ">$noheads_fname") or die "Cannot open $noheads_fname\n";
#open(NOHEADS_LEX, ">$noheads_lex_fname") or die "Cannot open $noheads_lex_fname\n";
#open(EMPTY_NONTERMS, ">$empty_nonterms_fname") or die "Cannot open $empty_nonterms_fname\n";

$sent = "";
$sent_text = "";
$sent_start = "";
$sent_id = "";
@terminal_nodes = ();
$dump_trees = 0;
$dump_dots = 0;
$output_only_problems = 0;
$output_only_raw_text = 0;
$user_filter_routine = 0;

%opts = ();
getopts('tdprgxm', \%opts);
$dump_trees = $opts{t};
$dump_dots = $opts{d};
$dump_grammar = $opts{g};
$output_only_problems = $opts{p};
$output_only_raw_text = $opts{r};
$user_filter_routine = $opts{x};

$openbr = $closebr = 0;
$current_fname = "";
$n_sent_in_file = 0;
while (<>) {

    # convert WSJ bracketing to valid perl structure
    chomp;
    s{\(([^()\s]*)\)}{LBRACKET$1RBRACKET}g;
    s{'}{\\'}g;
    s{\(([^() ]+)\s+([^()]+)\)}{\{type=>'TERM',pos=>'$1',word=>'$2'\},}g;
    s{\(([^() ]*) ?}{\{type=>'NONTERM',label=>'$1',daughters=>[}g;
    s{\)}{]\},}g;
    s{LBRACKET(\S*)RBRACKET}{\($1\)}g;
                    
    
    $sent .= $_;

    s{'(\\'|[^'])*'}{}g;
    (my $openbr1 = $_) =~ s{[^\[]}{}g;
    (my $closebr1 = $_) =~ s{[^\]]}{}g;
    $openbr += length $openbr1;
    $closebr += length $closebr1;
    
    if ($openbr == $closebr and $sent =~ /\{/) {
        $openbr = $closebr = 0;
        if ($current_fname ne $ARGV) {
            $n_sent_in_file = 0;
            $current_fname = $ARGV;
        }
        $n_sent_in_file++;

        $sent_id = $current_fname;
        $sent_id =~ s{.*/}{};
        $sent_id =~ s{\D}{}g;
        $sent_id .= ".$n_sent_in_file";
        
        if ($sent !~ /\S/) {
            $sent = "";
            next;
        }
        $current_sentence = $sent;
        $sent =~ s{,\s+$}{};
        
        my @tmp = ($sent =~ /word=>'(.*?)'}/g);
        $sent_text = join ' ', @tmp;
        ($sent_start) = ($sent_text =~ /(^.{0,30})/);
       
        $sent = eval qq~$sent~;
        # discard outmost ((S...))
        $sent = $sent->{daughters}[0]; 
        @terminal_nodes = ();
        process_sentence($sent);
        cleanup($sent);
        $sent = "";
        next;
    }
}

#close NOHEADS;
#close NOHEADS_LEX;
#close EMPTY_NONTERMS;

print STDERR "Sentences: $n_sentences\n";
print STDERR "Sentences with all heads assigned: $n_sentences_with_heads\n";
print STDERR "Traces: $n_traces\n";
print STDERR "Nonterminals w/o heads: $unassigned_heads of $n_nonterminals ($noheads_fname" . 
             " $noheads_lex_fname)\n";
print STDERR "Empty non-terminals (default heads assigned): $empty_nonterminals ($empty_nonterms_fname)\n";

1;


sub cleanup {
    my $sent = shift;

    for_nodes_bottom_up {
        #if (exists $_->{trace}) {
        #    delete $_->{trace};
        #}
        %$_ = (); 
    } $sent
}

sub process_sentence {
    my $sent = shift;

    if ($output_only_raw_text) {
        dump_sentence_raw(STDOUT, $sent);
        return;
    }

    # first, index the terminal nodes, and also all nodes
    my $id = 0;
    my $global_id = 0;
    for_nodes {
        $_->{global_id} = $global_id++;
        if (terminal($_)) {
            $_->{id} = $id++;
            $terminal_nodes[$_->{id}] = $_;
            $_->{minid} = $_->{maxid} = $_->{id};
            $_->{words} = $_->{word};
        }
    } $sent;

    # mark empty nodes 
    for_nodes_bottom_up {
        if (terminal($_) and $_->{pos} eq '-NONE-') {
            $_->{empty} = 1;
        }
        if (not terminal($_)) {
            my $nonempty_found = 0;
            my $min = 1000000; my $max = -1000000;
            my @words = ();
            my $node_id = $_->{global_id};
            for my $d (@{$_->{daughters}}) {
                $sent->{parent}{$d->{global_id}} = $node_id;
                $nonempty_found = 1 unless $d->{empty};
                if (not $d->{empty}) {
                    $min = $d->{minid} if $d->{minid} < $min;
                    $max = $d->{maxid} if $d->{maxid} > $max;
                    push @words, $d->{words};
                }
            }
            $_->{empty} = 1 if not $nonempty_found;
            $_->{maxid} = $max if $max > -1000000;
            $_->{minid} = $min if $min < 1000000;
            $_->{words} = join(' ', @words);
        }
    } $sent;


    # detect traces and coindexed nodes
    @trace_targets = (); # trace id -> ancor node
    @trace_sources = (); # trace id -> list of references
    %nodes_to_remove = (); # id's of nodes to be removed from their original position
    for_nodes {
        if (not terminal($_) and $_->{label} =~ /-([0-9]+)$/) {
            # indexed node
            die "redefinition of trace target $1\nin sentence: $sent_text\n" if defined $trace_targets[$1];
            $trace_targets[$1] = $_;
            #print STDERR "trace target $1\n";
        }
        if (terminal($_) and $_->{pos} eq '-NONE-' and $_->{word} =~ /\*-([0-9]+)$/) {
            # trace 
            my $id = $1;
            $_->{trace_id} = $id;
            push @{$trace_sources[$id]}, $_;
            if ($_->{word} =~ /\*ICH\*|\*EXP\*|\*RNR\*/) {
                # the target node will be removed from its original position for:
                #  o "Interpret Constituent Here" traces
                #  o It-extraposition traces
                #  o Right Node Raising traces
                ($nodes_to_remove{$id} = $_->{word}) =~ s/[^A-Z]//g;
            }
            #print STDERR "trace source $1\n";
        }
    } $sent;

    # remove nodes planned for removing
    for (keys %nodes_to_remove) {
        die "Problem with removing in sentence: $sent_text\n" unless defined $trace_targets[$_];
        $trace_targets[$_]->{removed} = $nodes_to_remove{$_};
    }

    # resolve traces
    for (@trace_sources) {
        next unless defined $_;
        for (@$_) {
            if (not defined $trace_targets[$_->{trace_id}]) {
                print STDERR "unresolved trace $_->{trace_id}\n";
                $dump_trees = 1;
                dump_sentence(STDERR, $sent);
                exit 1;
            }
            $_->{trace} = $trace_targets[$_->{trace_id}];
            $n_traces++;
            #print STDERR "resolved trace $_->{trace_id}\n";
        }
    }

    # assign heads
    my $all_heads_assigned = 1;
    for_nonterms {
        $n_nonterminals++;
        if (not assign_head($_)) {
            $unassigned_heads++;
            #print NOHEADS nonterminal_to_cfgrule_basic($_) . "\n";
            #print NOHEADS_LEX nonterminal_to_cfgrule($_) . "\n";
            $all_heads_assigned = 0;
            mark_heads($_, -1);
        }
    } $sent;
    
    $n_sentences++;
    if ($dump_grammar) {
        dump_sentence_grammar(STDOUT, $sent);  
    } else {
        $n_sentences_with_heads++ if $all_heads_assigned;

        lexicalize_heads($sent);
        
        if ($output_only_problems) {
            dump_sentence(STDOUT, $sent) unless $all_heads_assigned;
        } else {
            if (not $user_filter_routine or x_routine($sent)) {
                dump_sentence(STDOUT, $sent);
            }
        }
    } 
    
    
}

# define if you want to do something special
sub x_routine {
    my $sent = shift;
    my $found = 0;

    for_nonterms {
        print "$_->{label}";
        if ($_->{ishead} or $_ == $sent) {
            print " *";
        }
        print "\n";
        #if ($_->{ishead} and $_->{label} =~ /[A-Z]-[A-Z]/) {
        #    print "$_->{label}\n";
        #    $found = 1;
        #    $_->{options} .= ",fontcolor=red";
        #}
    } $sent;

    #return $found;
    return 0;
}

sub dump_sentence {
    my ($fd, $sent) = @_;
    if ($dump_dots) {
        dump_sentence_dot($fd, $sent);
    } elsif ($dump_trees) {
        dump_sentence_wsj($fd, $sent);
    } else {
        dump_sentence_dep($fd, $sent);
    }
}

#-------------------------------------------------------
#--- Propagate heads upwards, make all heads lexical ---
#-------------------------------------------------------

sub lexicalize_heads {
    my $sent = shift;

    my @tracerefs = ();

    for_nodes_bottom_up {
        if (terminal($_)) {
            if ($_->{pos} eq '-NONE-' and $_->{word} =~ /\*-([0-9]+)$/) {
                # for now, take just trace number for traces
                my $ref = [$1, $_, $_];
                $_->{lexheads} = [$ref];
                push @{$tracerefs[$1]}, $ref;
            } else {
                $_->{lexheads} = [[$_, $_, $_]];
            }
            return;
        }
        
        # collect lexheads of all our heads
        my $hlist = $_->{lexheads} = [];
        for my $h (@{$_->{heads}}) {
            for my $hh (@{$h->{lexheads}}) {
                my $ref = [$hh->[0], $h, $_];
                if (not ref($hh->[0])) {
                    # our lexhead is a trace, resolve later
                    push @{$tracerefs[$hh->[0]]}, $ref;
                }
                push @$hlist, $ref;
            }
            last unless basic_label($_) =~ /\b(S|VP)\b/; # take only the first head for non-VP nodes
        }
            
    } $sent;

    # now propagate traces' lexheads
    my $unresolved_trace = 1;
    while ($unresolved_trace) {
        $unresolved_trace = 0;
        for (my $i = 0; $i < @tracerefs; $i++) {
            my $traceref = $tracerefs[$i];
            next unless defined $traceref;
            $unresolved_trace = 1;
            if (heads_are_lexicalized($trace_targets[$i])) {
                my @heads = @{$trace_targets[$i]->{lexheads}};
                # substitute "trace" lexhead with the first lexhead of the target 
                my $head = shift @heads;
                for my $ref (@$traceref) {
                    $ref->[0] = $head->[0];
                }
                # add all other target's lexheads to the end of our lexhead list
                for $head (@heads) {
                    for my $ref (@$traceref) {
                        push @{$ref->[2]->{lexheads}}, [$head->[0], $ref->[1], $ref->[2]];
                    }
                }
                undef $tracerefs[$i];
            } 
        }
    }
    
}

#---------------------------------------------------------------------------------
#--- Check whether all heads of the node are lexicalized (and traces resolved) ---
#---------------------------------------------------------------------------------
sub heads_are_lexicalized {
    my $node = shift;

    for my $h (@{$node->{lexheads}}) {
        return 0 unless ref($h->[0]);
    }
    
    return 1;
}

#----------------------------------------
#--- Assigning head to a non-terminal ---
#----------------------------------------

sub assign_head {
    my $n = shift;

    my @ids = ();
    for (my $i = 0; $i < @{$n->{daughters}}; $i++) {
        push (@ids, $i) unless exists $n->{daughters}[$i]{removed};
    }

    # skip labels only if there're more than one daughter
    if (@ids > 1) {
        @ids = grep {basic_label($n->{daughters}[$_]) !~ $always_skip_labels} @ids;
    }
    if (@ids > 1 and exists $skip_labels{basic_label($n)}) {
        @ids = grep {basic_label($n->{daughters}[$_]) !~ $skip_labels{basic_label($n)}} @ids;
    }
    if (@ids > 1 and basic_label($n) !~ /CONJP/ 
            and basic_label($n->{daughters}[$ids[0]]) =~ /CONJ|<CC>/) {
        shift @ids;
    }
    if (@ids > 1 and basic_label($n) !~ /CONJP/ 
            and basic_label($n->{daughters}[$ids[-1]]) =~ /CONJ|<CC>/) {
        pop @ids;
    }

    if (@ids == 1) {
        mark_heads($n, $ids[0]);
        return 1;
    }

    if (@ids == 0) {
        #print EMPTY_NONTERMS "empty non-terminal " . nonterminal_to_cfgrule($n) . "\n";
        #print STDERR $current_sentence . "\n";
        # simply mark first daughters as head
        mark_heads($n, 0);
        $empty_nonterminals++;
        return 1;
    }

    # try generic head table, if there's no conjunction
    if (not grep {($_ != 0) and (basic_label($n->{daughters}[$_]) =~ /<CC|CONJP/)} @ids 
            and exists $leftmost_heads{basic_label($n)}) {
        my ($id) = grep {label($n->{daughters}[$_]) =~ $leftmost_heads{basic_label($n)}} @ids;
        if (defined $id) {
            mark_heads($n, $id);
            return 1;
        }
    }

    # simplest conjunction: XP -> YP ZP XP* [,] ... YP XP* CC XP* (heads are with stars)
#    if (grep {basic_label($n->{daughters}[$_]) =~ /<CC>|CONJP/} @ids) {
#        my @separators = grep {basic_label($n->{daughters}[$_]) =~ /<CC>|CONJP|<,>/} @ids;
#        my @heads = map {$_ - 1} @separators;
#        push @heads, 
#    }
    

    # simple conjunction case: XP -> YP [,] CC ZP [,]
    my @tmp = grep {basic_label($n->{daughters}[$_]) ne '<,>'} @ids; 
    if (@tmp == 3 and basic_label($n->{daughters}[$tmp[1]]) =~ /<CC|CONJP/) {
                  #and basic_label($n->{daughters}[$tmp[0]]) eq label($n->{daughters}[$tmp[2]])) {
        mark_heads($n, $tmp[0], $tmp[2]);
        return 1;
    }
    
    # simple conjunction case: XP -> XP CC XP CC ... XP
    @tmp = grep {basic_label($n->{daughters}[$_]) ne '<,>'} @ids; 
    my $label = basic_label($n);
    if (grep {basic_label($n->{daughters}[$_]) =~ /<CC|CONJP/} @tmp and
            not grep {basic_label($n->{daughters}[$_]) !~ /^$label$|<CC|CONJP/} @tmp) {
        my @tmp1 = grep {basic_label($n->{daughters}[$_]) eq $label} @tmp;
        if (@tmp1) {
            mark_heads($n, @tmp1);
        } else {
            # strange case of only CCs/CONJPs
            mark_heads($n, $tmp[-1]);
        }
        return 1;
    }

    if (exists $head_assigners{basic_label($n)}) {
        return 1 if ($head_assigners{basic_label($n)}->($n, @ids));
    }

    return 0;
}


INIT {

%leftmost_heads = (
PP => qr/<IN|<TO|<VBG|<VBN|<NNP|PP/,  # NNP is for PP-TTL and -HLN
S => qr/^VP/,
VP => qr/<VB|<AUX/,  # AUX for Charniak's parser
SQ => qr/^S|^VP/,
SINV => qr/^S|^VP/,
SBARQ => qr/WHNP|WHADVP/,
ADJP => qr/ADJP/,
ADVP => qr/ADVP/,
PRN => qr/^VP/,
CONJP => qr/<IN/,
WHADVP => qr/<WRB/,
WHADJP => qr/<WRB/,
WHNP => qr/WHNP/,
);

$always_skip_labels = qr/<[.'`]|-TPC|PRN|INTJ/;

%skip_labels = (
NP => qr/PP|SBAR|<RB|<PDT|<[^A-Z,]/,
NX => qr/PP|SBAR/,
VP => qr/<TO|NP|PP|<MD|SBAR|ADVP|^S/,
SBAR => qr/^S($|[^B])|FRAG|<,|<``/,
SINV => qr/^S$/,
WHPP => qr/,|WHNP|PRN|^RB|ADVP/,  # PP is the head of WHPP (27.01.04, see 0001.115)
WHNP => qr/^(PP|<WP|<WDT|WHPP|<WRB|WHADJP)/, # WP$ if not a head of WHNP!!
PP => qr/,|^NP|PRN|^RB|ADVP/,
PRN => qr/,|:|''|<-LRB-|<-RRB-/,
ADJP => qr/<-NONE-|PP|^S/,
S => qr/<CC|CONJP|<[^A-Z]/,
UCP => qr/<CC|<,|CONJP/,
QP=>qr/<CC|<RB|<IN/,
ADVP=>qr/<CD/,
RRC=>qr/-(TMP|LOC|MNR)/,
);

%head_assigners = (

SINV => sub {
    return &{$head_assigners{S}}(@_);
},

WHNP => sub {
    return &{$head_assigners{NP}}(@_);
},

NP => sub {
    my $n = shift;

    # if the last child is POS -- it's the head
    if (basic_label($n->{daughters}[$_[-1]]) eq '<POS>') {
        mark_heads($n, $_[-1]);
        return 1;
    }

    # if there's no conjunction
    if (not grep {label($n->{daughters}[$_]) =~ /<CC|CONJP/} @_) {
        # last {NX, NN} daughter
        for my $label ('NX|<NN') {
            if (my @nns = grep {label($n->{daughters}[$_]) =~ /$label/} @_) {
                mark_heads($n, $nns[-1]);
                return 1;
            }
        }
        # first NP daughter
        my ($np) = grep {basic_label($n->{daughters}[$_]) eq 'NP'} @_;
        if (defined $np) {
            mark_heads($n, $np);
            return 1;
        }
        # last {QP, CD, JJ, ADJP} daughter
        for my $label ('QP', '<PRP', '<FW', '<CD|<JJ|ADJP|<VBG') {
            if (my @nns = grep {label($n->{daughters}[$_]) =~ /$label/} @_) {
                mark_heads($n, $nns[-1]);
                return 1;
            }
        }
    } else {
        # handle most common conjunction patterns
        # $npat is an element of NP conjunction. A little messy, eh?
        my $npat = '(?:(?:(?:<PRP\$>|<DT>|<JJ.?>|<VB[NG]>|NAC|QP|ADVP|ADJP|<CD>|<NN[A-Z]*>|NP)# )*((?:<CD>|NP|<PRP>|<NN[A-Z]*>|<JJ[A-Z]?>|<DT>|S|NX)#))';
        my @res = get_heads_in_conjunction($n, $npat, @_);
        if (@res) {
            mark_heads($n, @res);
            return 1;
        }

        # If does not work, simply take the last "good" daughter (it has to be after conjunction)
        for my $id (reverse @_) {
            last if basic_label($n->{daughters}[$id]) =~ /CONJ|<CC>/;
            if (basic_label($n->{daughters}[$id]) =~ /<CD>|NP|<PRP>|<NN[A-Z]*>|<JJ[A-Z]?>|<DT>|S/) {
                mark_heads($n, $id);
                return 1;
            }
        }
    }

    return 0;
},

NX => sub {
    my $n = shift;

    # if there's no conjunction
    if (not grep {label($n->{daughters}[$_]) =~ /<CC|CONJP/} @_) {
        if (basic_label($n->{daughters}[$_[-1]]) =~ /<NN|NX/) {
            mark_heads($n, $_[-1]);
            return 1;
        }
    } else {
        my $npat = '(?:(?:(?:<PRP\$>|<DT>|<JJ>|<NN[A-Z]*>)# )*((?:NX|<NN[A-Z]*>|<JJ[A-Z]?>)#))';
        my @res = get_heads_in_conjunction($n, $npat, @_);
        return 0 unless @res;
        mark_heads($n, @res);
        #print STDERR nonterminal_to_cfgrule($n) . join('.', @res) . "\n";
        return 1;
    }
    

    #print STDERR nonterminal_to_cfgrule($n) . "\n";
    return 0;
},

VP => sub {
    my $n = shift;

    # if there are VP daughters, all of them are heads
    if (my @vps = grep {label($n->{daughters}[$_]) eq 'VP'} @_) {
        mark_heads($n, @vps);
        return 1;
    }
    
    # now, if there are <VB.?> daughters, they are the heads
    if (my @vbs = grep {label($n->{daughters}[$_]) =~ /^<VB/} @_) {
        mark_heads($n, @vbs);
        return 1;
    }
 
    return 0;
},

QP => sub {
    my $n = shift;

    # QP -> ... TO ...   "2 hundred to 3 million"
    my $prev = 0;
    for my $to (@_) {
        if (basic_label($n->{daughters}[$to]) eq '<TO>') {
            mark_heads($n, $prev);
            return 1;
        }
        $prev = $to;
    }

    # QP -> ... {CD,NN.,JJ}
    if (basic_label($n->{daughters}[$_[-1]]) =~ /<CD>|<NNS?>|<JJR?>/) {
        mark_heads($n, $_[-1]);
        return 1;
    }

    return 0;
},

ADJP => sub {
    my $n = shift;

    # try JJ's as candidates for heads
    if (my @jjs = grep {basic_label($n->{daughters}[$_]) =~ /<JJ/} @_) {
        # it seems we don't have to care about conjunctions...
        mark_heads($n, @jjs);
        return 1;
    }

    # ADJP -> ... NN "((ADJP 5 %) interest)" 
    # ADJP -> ... VBN  or ADJP -> ... CD
    if (basic_label($n->{daughters}[$_[-1]]) =~ /<NN|VBN|VBG|<CD/) {
        mark_heads($n, $_[-1]);
        return 1;
    }

    # if there is RBR - take it
    if (my @rbrs = grep {basic_label($n->{daughters}[$_]) =~ /<RBR/} @_) {
        mark_heads($n, @rbrs);
        return 1;
    }

    # ADJP -> RB RB   "too early", "far enough"
    if (not grep {basic_label($n->{daughters}[$_]) !~ /<RB/} @_) {
        my $nonheads = qr/^(too|so|enough|as|even|not|.*ly|most|much|more|very)$/o;
        my @res = grep {$n->{daughters}[$_]{word} !~ $nonheads} @_;
        if (@res) {
            mark_heads($n, @res);
        } else {
            mark_heads($n, $_[-1]);
        }
        return 1;
    }

    # ADJP -> ... {all,...}
    if ($n->{daughters}[$_[-1]]{type} eq 'TERM' and  
        $n->{daughters}[$_[-1]]{word} =~ /^(all|any|another|every|some|other)$/) {
        mark_heads($n, $_[-1]);
        return 1;
    }

    # ADJP -> ... FW {foreign word}
    if (basic_label($n->{daughters}[$_[-1]]) =~ /<FW>/) {
        mark_heads($n, $_[-1]);
        return 1;
    }
    return 0;
},

ADVP => sub {
    my $n = shift;
   
    my $lex = nonterminal_to_string($n);
    # Check for fixed phrases
    if ($lex =~ /^(at\ least|at\ all|kind\ of|sort\ of|all\ but|of\ course|after\ all|
                   at\ best|at\ worst|so\ far|all\ of\ a\ sudden|later\ on|
                   all\ around|more\ than|above\ all|beter\ off|all\ along|
                   all\ the\ same|no\ doubt|let\ alone|quite\ the\ contrary|per\ se|
                   out\ there|a\ priori|above\ all|at\ first|pro\ bono|at\ most|in\ fact|
                   de\ facto|in\ effect|vice\ versa|in\ part|head\ to\ head|long\ since|
                   under\ way|to\ begin\ with)$/x) {
        mark_compound_heads($n, @_);
        return 1;
    }
    
    if ($lex =~ /^(en\ route|no\ matter|a\ la)($| )/x) {
        mark_compound_heads($n, $_[0], $_[1]);
        return 1;
    }

    # take all RBs
    if (my @rbs = grep {basic_label($n->{daughters}[$_]) =~ /<RB/} @_) {
        # if there's conjunction, mark all RBs as heads, otherwise mark only the last one
        if (grep {basic_label($n->{daughters}[$_]) =~ /<CC|CONJP/} @_) {
            mark_heads($n, @rbs); 
        } else {
            mark_heads($n, $rbs[-1]);
        }
        return 1;
    }

    # ADVP -> ... <IN|JJR>
    if (label($n->{daughters}[$_[-1]]) =~ /<(IN)\.(ago|before|out|up|down|behind|on)>|<JJ/) {
        mark_heads($n, $_[-1]);
        return 1;
    }

    # ADVP -> <IN> NP|PP|NN ...  ["up 5 %", "out of ..."]
    if (@_ >= 2 and basic_label($n->{daughters}[$_[0]]) =~ /<(IN|JJ|RP|VBN)/
               and basic_label($n->{daughters}[$_[1]]) =~ /^(NP|PP|S|NN)/) {
        mark_heads($n, $_[0]);
        return 1;
    }

    return 0;
},

S => sub {
    my $n = shift;

    # S -> NP NP...  or  S -> NP ADJP...
    if (@_ >= 2 and basic_label($n->{daughters}[$_[0]]) eq 'NP' 
                and basic_label($n->{daughters}[$_[1]]) =~ /NP|ADJP|PP/) {
        mark_heads($n, $_[1]);
        return 1;
    }

    # S -> ADJP-PRD NP-SBJ
    if (@_ == 2 and basic_label($n->{daughters}[$_[0]]) eq 'ADJP' 
                and basic_label($n->{daughters}[$_[1]]) eq 'NP') {
        mark_heads($n, $_[0]);
        return 1;
    }
    
    # S -> S* separated by punctuations and/or conjunctions, parentheticals, adjuncts 
    # all S's are heads
    if (not grep {label($n->{daughters}[$_]) !~ /^S|<CC|CONJP|IN|PRN|RB|PP|ADVP|[A-Z]+-(LOC|TMP|MNR|ADV)|<[^A-Z]/} @_) {
        my @heads =  grep {label($n->{daughters}[$_]) =~ /^S/} @_;
        if (@heads) {
            mark_heads($n, @heads);
        } else {
            mark_heads($n, $_[-1]);
        }
        return 1;
    }
    
    return 0;
},

PP => sub {
    my $n = shift;

    # PP -> <IN> and <IN> ...
    if (my @ins = grep {basic_label($n->{daughters}[$_]) =~ /<IN>/} @_) {
        mark_heads($n, @ins);
        return 1;
    }
    
    return 0;
},

SBAR => sub {
    my $n = shift;
    
    # SBAR -> ... <IN> S  (note that S has been filtered already)
    if (basic_label($n->{daughters}[$_[-1]]) eq '<IN>') {
        mark_heads($n, $_[-1]);
        return 1;
    }

    # SBAR -> ... <IN> <NN> S  (note that S has been filtered already) "in order ..."
    if (basic_label($n->{daughters}[$_[-2]]) eq '<IN>' and
        basic_label($n->{daughters}[$_[-1]]) eq '<NN>') {
        mark_heads($n, $_[-2], $_[-1]);
        return 1;
    }

    # minor fix: SBAR -> SBAR , SBAR  (commas has been filtered already)
    if (not grep {basic_label($n->{daughters}[$_]) ne 'SBAR'} @_) {
        mark_heads($n, @_);
        return 1;
    }

    return 0;
},

CONJP => sub {
    my $n = shift;
    mark_compound_heads($n, @_);
    return 1;
},

NAC => sub {
    my $n = shift;
    mark_heads($n, $_[0]);
    return 1;
},

FRAG => sub {
    my $n = shift;
    mark_heads($n, $_[-1]);
    return 1;
},

UCP => sub {
    my $n = shift;
    mark_heads($n, $_[-1]);
    return 1;
},

PRN => sub {
    my $n = shift;
    mark_heads($n, $_[0]);
    return 1;
},

);

}

###################################################

sub label ($) {
    if (terminal $_[0]) {
        return "<$_[0]->{pos}." . lc($_[0]->{word}) . ">";
    }
    return $_[0]->{label};
}

sub basic_label ($) {
    if (terminal $_[0]) {
        return "<$_[0]->{pos}>";
    }
    
    $_[0]->{label} =~ /^([^-=]*)/;
    return $1;
}

sub mark_heads {
    my $n = shift;

    $n->{heads} = [];
    $n->{headids} = [];
    
    @_ = (@_);
    for (@_) {
        if ($_ < 0) {
            $_ = @{$n->{daughters}} + $_;
        }
    }
    
    @_ = sort {$a <=> $b} @_;
    
    for (@_) {
        my $id = $_;
        push @{$n->{headids}}, $id;
        push @{$n->{heads}}, $n->{daughters}[$id];
        $n->{daughters}[$id]->{ishead} = 1;
    }
}
    

sub mark_compound_heads {
    my $n = shift;

    #print "*** " . join('-', map {label($n->{daughters}[$_])} @_) . "\n";
    # each co-head has a list of all co-heads
    my $ids = [map {$n->{daughters}[$_]{id}} @_];
    for (@{$n->{daughters}}) {
        $_->{coheads} = $ids;
    }
    
    # XXX
    mark_heads($n, @_);
}

# handle most common conjunction patterns (used for NPs and NXs)
sub get_heads_in_conjunction {    
        my $n = shift; 
        my $headpat = shift;
        
        my $pat = join " ", map {basic_label($n->{daughters}[$_]) . "-$_"} @_;
        
        my $id = '-[0-9]+';
        $headpat =~ s{#}{$id}g;
        
        # NP -> NP,..., NP CC NP
        if (my @res = ($pat =~ /^((?:$headpat (?:(?:<[,:]>|<CC>|CONJP)$id )+)*)$headpat (?:<[,:]>$id )?(?:<CC>|CONJP)$id $headpat(?: <[,:.]>$id)?$/)) {
            my @tmp = ($res[0] =~ /$headpat <[,:]>$id/g);
            shift @res; shift @res;
            unshift @res, @tmp;
            @res = map {s{\D}{}g; $_} @res;
            #print STDERR "$pat : " . join(".",@res) . "\n";
            return @res;
        }
        
        print STDERR "weird conjunction: /$pat/\n";
        return ();
        
}
        
sub nonterminal_to_string {    
    my $n = shift;
    my $str = "";

    foreach my $d (@{$_->{daughters}}) {
        my $tmp = label($d);
        $tmp =~ s{<[A-Z]+\.(.*)>}{$1};
        $str .= $tmp . " ";
    }
    $str =~ s{ $}{};
    return $str;
}

sub nonterminal_to_cfgrule_basic {    
    my $n = shift;
    my $str = "";

    $str .= basic_label($n);
    $str .= " -> ";
    foreach my $d (@{$_->{daughters}}) {
        $str .= basic_label($d);
        $str .= " ";
    }
    return $str;
}

sub nonterminal_to_cfgrule {    
    my $n = shift;
    my $str = "";

    $str .= label($n);
    $str .= " -> ";
    foreach my $d (@{$_->{daughters}}) {
        $str .= label($d);
        $str .= " ";
    }
    return $str;
}
