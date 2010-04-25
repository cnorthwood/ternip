
$depdir = $ENV{DEPDIR};
die "died: env. variable \$DEPDIR not defined\n" unless $depdir;
require "$depdir/lib/dep-utils.pl";


sub terminal ($) {
    die "$sent_id : $sent_text" unless defined $_[0]->{type};
    return $_[0]->{type} eq "TERM";
}

sub for_nonterms (&$) {
    my $f = shift;
    my $node = shift;

    return if terminal($node);
    $_ = $node;
    $f->($node);
    for my $d (@{$node->{daughters}}) {
        for_nonterms {&$f;} $d;
    }
    
}


sub for_nodes (&$) {
    my $f = shift;
    my $node = shift;

    $_ = $node;
    $f->($node);
    return if terminal($node);
    for my $d (@{$node->{daughters}}) {
        for_nodes {&$f;} $d;
    }
    
}


sub for_nonterms_bottom_up (&$) {
    my $f = shift;
    my $node = shift;

    return if terminal($node);
    
    for my $d (@{$node->{daughters}}) {
        for_nonterms_bottom_up {&$f;} $d;
    }
    $_ = $node;
    $f->($node);
    
}

sub for_nodes_bottom_up (&$) {
    my $f = shift;
    my $node = shift;

    if (not terminal($node)) {
        for my $d (@{$node->{daughters}}) {
            for_nodes_bottom_up {&$f;} $d;
        }
    }
    $_ = $node;
    $f->($node);
    
}


sub dump_sentence_wsj_1 {
    my $node = shift;
    
    if (terminal($node)) {
        print $fd "( $node->{pos}" . ($node->{ishead} ? '*' : '') . " $node->{word} ) ";
    } else {
        my $lexheads = "";
        if (defined $node->{lexheads}) {
            for my $h (@{$node->{lexheads}}) {
                $lexheads .= "_" . (ref($h->[0]) ? $h->[0]{word} : $h->[0]);
            }
        }
        print $fd "( " . 
                  ($node->{removed} ? "removed-$node->{removed}-" : '') . 
                  "$node->{label}" . 
                  ($node->{ishead} ? '*' : '') . 
                  $lexheads . 
                  " ";
        for my $d (@{$node->{daughters}}) {
            dump_sentence_wsj_1($d);
        }
        print $fd ") ";
    }
}


sub dump_sentence_wsj (*$) {
    local $fd = shift;
    my $sent = shift;
    dump_sentence_wsj_1($sent);
    print $fd "\n";
}

sub dump_sentence_grammar (*$) {
    my $fd = shift;
    my $sent= shift;

   for_nonterms {
       print $fd "$_->{label} ";
       for my $d (@{$_->{daughters}}) {
           if (terminal($d)) {
               print $fd $d->{pos};
           } else {
               my $lab = $d->{label};
               $lab =~ s/-[0-9]+//;
               print $fd $lab;
           }
           if ($d->{ishead}) {
               print $fd "'";
           }
           print $fd " ";
       }
       print $fd "\n";
   } $sent;
}
    
    
sub dump_sentence_dot_1 {
    my $node = shift;
    
    if (terminal($node)) {
        #print $fd "( $node->{pos}" . ($node->{ishead} ? '*' : '') . " $node->{word} ) ";
        print $fd "  node_$node->{global_id} [label=\"$node->{pos}\\n$node->{word}\"]\n";
        if ($node->{word} =~ /\*-([0-9]+)$/) {
            my $trace = $trace_targets[$1];
            print "  node_$node->{global_id} -> node_$trace_targets[$1]->{global_id} [style=dotted]\n";
        }
    } else {
        #my $lexheads = "";
        #if (defined $node->{lexheads}) {
        #    for my $h (@{$node->{lexheads}}) {
        #        $lexheads .= "_" . (ref($h->[0]) ? $h->[0]{word} : $h->[0]);
        #    }
        #}
        #print $fd "( " . 
        #          ($node->{removed} ? 'removed-' : '') . 
        #          "$node->{label}" . 
        #          ($node->{ishead} ? '*' : '') . 
        #          $lexheads . 
        #          " ";
        my $extra = "";
        if (exists $node->{options}) {
            $extra = "$node->{options}";
        }
        $extra .= ",style=dotted" if $node->{removed};
        print $fd "  node_$node->{global_id} [label=\"$node->{label}\"$extra]\n";
        for my $d (@{$node->{daughters}}) {
            print $fd "  node_$node->{global_id} -> node_$d->{global_id}";
            print $fd " [color=blue]" if $d->{ishead};
            print $fd "\n";
        }
        for my $d (@{$node->{daughters}}) {
            dump_sentence_dot_1($d);
        }
        #print $fd ") ";
    }
}


sub dump_sentence_dot (*$) {
    local $fd = shift;
    my $sent = shift;
    (my $sid = $sent_id) =~ s/[^a-zA-Z0-9]//g;
    print $fd "digraph wsj_$sid {\n";
    print $fd "  node [shape=plaintext height=.2]\n";
    print $fd "  edge [dir=none]\n";
    my $s = "$sent_id: $sent_text ";
    my $res_sent = "";
    while ($s) {
        if (not $s =~ /^(.{1,100})\s(.*)$/) {
            $s =~ /^(.*?)\s(.*)$/;
        }
        $res_sent .= "  $1\\l";
        $s = $2;
    }
    print $fd "  sentence [shape=box,label=\"$res_sent\"];\n";
    print $fd "  sentence -> node_$sent->{global_id};\n";
    local $node_id = 0;
    dump_sentence_dot_1($sent);
    print $fd "}\n";
}

sub dump_sentence_raw (*$) {
    local $fd = shift;
    my $sent = shift;
    my $tmp = $sent_text;
    $tmp =~ s/\S*(\*|-NONE-)\S*\s*//g;
    $tmp =~ s/\\//g;
    $tmp =~ s/-LRB-/\(/g;
    $tmp =~ s/-RRB-/\)/g;
    $tmp =~ s/-LCB-/\{/g;
    $tmp =~ s/-RCB-/\}/g;
    $tmp =~ s/-LSB-/\[/g;
    $tmp =~ s/-RSB-/\]/g;
    $tmp =~ s/ 0 +/ /g;
    print "$tmp\n";
}

    
    
sub dump_sentence_dep (*$) {
    local $fd = shift;
    my $wsj = shift;

    my $sent = {};

    $sent->{id} = $sent_id;
    $sent->{text} = $sent_text;
  
    for_nodes {
        my $node = $_;
        my $parent = $wsj->{parent}{$_->{global_id}};
        $parent = "top" unless defined $parent;
        if (terminal($_)) {
            $sent->{words}{$_->{id}} = $_->{word};
            $sent->{tags}{$_->{id}} = $_->{pos};
            push @{$sent->{phrases}{$parent}{children}}, {word=>$_->{id}};
            $sent->{word_phrases}{$_->{id}} = $parent;
        } else {
            my $phrase = {};
            $phrase->{id} = $node->{global_id};
            $phrase->{parent} = $parent;
            push @{$sent->{phrases}{$parent}{children}}, $phrase->{id};
            my $head = $node->{lexheads}[0][0]{id};
            $phrase->{head} = $head;
            $phrase->{start_word} = $node->{minid} if defined $node->{minid};
            $phrase->{end_word} = $node->{maxid} if defined $node->{maxid};
            $phrase->{type} = basic_label($node);
            $phrase->{text} = $node->{words};
            $sent->{phrases}{$phrase->{id}} = $phrase;
        }
    } $wsj;

    my $rel_id = 0;
    for_nonterms {
        my $parent = $_;
        my $parent_label = $parent->{label};
        $parent_label =~ s/([A-Za-z])[-=]\w.*$/$1/;
        my $head_found = 0;
        for my $child (@{$_->{daughters}}) {
            my $child_label = "";
            my %extra = ();
            if (terminal($child)) {
                $child_label = $child->{pos};
            } else {
                $child_label = $child->{label};
                if ($child->{removed}) {
                    $child_label = "removed-$child->{removed}-" . $child_label;
                    # skip removed nodes altogether
                    next;
                }
                if ($child->{empty}) {
                    $extra{trace} = "true";
                }
            }
            $child_label =~ s/[-=][0-9]+$//;
            if ($child->{ishead} and not $head_found) {
                # we will only allow multiple head children for S and VP
                # otherwise, only the first head child will be taken
                if ($parent_label !~ /\b(S|VP)\b/) {
                    $head_found = 1;
                }
            } else {
               # non-head or not first head
               my %visited_p_c = (); # visited parent-child pairs
               for my $hparent (@{$parent->{lexheads}}) {
                   for my $hchild (@{$child->{lexheads}}) {
                       die "bug in dump_sentence_dep\n" unless defined $hchild->[0];
                       next if exists $visited_p_c{$hparent->[0]->{id},$hchild->[0]->{id}};

                       my $rel = {};
                       $rel->{id}=$rel_id;
                       $rel_id++;
                       
                       if ($child->{ishead}) {
                           $rel->{label} = "COORD|$child_label";
                       } else {
                           $rel->{label} = "$parent_label|$child_label";
                       }
                       
                       $rel->{head} = $hparent->[0]->{id}; 
                       $rel->{dep} = $hchild->[0]->{id}; 
                       %{$rel->{options}} = %extra;
                       
                       push @{$sent->{deps}{$rel->{head}}}, $rel;
                       $child->{gf} = $rel->{label};
                       $sent->{phrases}{$child->{global_id}}{gf} = $rel->{label};
                   }
               }
            }
        }
    } $wsj;
    
    output_sentence($fd, $sent);
}
    

1;
