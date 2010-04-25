
%deputils_options  = (
    output_format => 'cxml',
);

sub string2opthash {
    my $str = shift;

    my $options = {};
    while ($str =~ /(\w+)=(['"])(.*?)\2/) {
        $options->{$1} = $3;
        $str =~ s/.*?\w+=(['"]).*?\1\s*//;
    }
    die "option string '$str'" if $str;
    return $options;
}

# Read sentence with dependencies from an XML file
# Args: FILEHANDLE, \%text, \%words, \%tags, \%deps
#   or: FILEHANDLE, \%sent
# Returns: $sentence_id
sub read_sentence {

    my ($fd, $text, $words, $tags, $deps, $word_options, $matrix, $maxid) = @_;
    my $sent = undef;
    my $text_start_tmp = "";
    my $text_start = \$text_start_tmp;

    if (not defined $words) {
        $sent = $text;
        delete $sent->{$_} for (keys %$sent);
        $sent->{id} = undef;
        $sent->{nid} = undef;
        $text = \($sent->{text});
        $text_start = \($sent->{start});
        $words = \%{$sent->{words}};
        $tags = \%{$sent->{tags}};
        $deps = \%{$sent->{deps}};
        $heads = \%{$sent->{heads}};
        $word_options = \%{$sent->{word_options}};
        $rels = \%{$sent->{rels}};
        $matrix = \%{$sent->{matrix}};
        $invmatrix = \%{$sent->{invmatrix}};
        $maxid = \($sent->{maxid});
        $minid = \($sent->{minid});
        $max_rel_id = \($sent->{max_rel_id});
        $phrases = \%{$sent->{phrases}};
        $phrase_layers = \%{$sent->{phrase_layers}};
    }
    
    my $sent_id = undef;
    my $sent_options = undef;
    $$text = "";
    $$text_start = "";
    %$words = ();
    %$tags = ();
    %$deps = ();
    %$word_options = ();
    %$matrix = ();
    %$invmatrix = ();
    $$maxid = -1;
    $$minid = 0;
    $$max_rel_id = -1;

    $global_rel_id = 0;

    while (defined($_ = <$fd>) and !/<sentence (.*)>/) {}
    return undef if eof($fd);
    /<sentence (.*)>/;
    $sent_options = string2opthash($1);
    $sent_id = $1;
    
    my @phrase_ids = ();

    while (defined($_ = <$fd>) and !/<\/sentence>/) {
        if (/<\/phrase>/) {
            pop @phrase_ids;
        }
        if (/<text>(.*)$/) {
            $$text = $1;
            unless ($$text =~ s/<\/text>.*//) {
                while (defined($_ = <$fd>) and !/<\/text>/) {
                    $$text .= $_;
                }
                die "End of file while looking for </text>\n" if eof($fd);
            }
            ($$text_start) = ($$text =~ /^(.{0,30})/);
        } elsif (/<phrase (.*)\/?>/) {
            my $options = $1;
            $options = string2opthash($options);
            $phrases->{$options->{id}} = $options;
            if ($options->{layer}) {
                $phrase_layers->{$options->{layer}}{$options->{id}} = $options;
            }
            my $parent = $phrase_ids[-1];
            $parent = "top" unless defined $parent;
            push @{$sent->{phrases}{$parent}{children}}, $options->{id};
            push @phrase_ids, $options->{id} unless /<\/phrase>/;
        } elsif (/<word ([^>]*)>(.*)<\/word>/) {
            my $word = $2;
            my $opts = string2opthash($1);
            #$opts->{id} =~ s/[^0-9]+/-/g;
            $words->{$opts->{id}} = $word;
            $tags->{$opts->{id}} = ($opts->{pos} or $opts->{tag});
            #delete $opts->{id};
            #delete $opts->{tag};
            for my $opt (keys %$opts) {
                $word_options->{$opts->{id}}{$opt} = $opts->{$opt};
            }
            my $parent = $phrase_ids[-1];
            if (defined $parent) {
                push @{$sent->{phrases}{$parent}{children}}, {word=>$opts->{id}};
                $sent->{word_phrases}{$opts->{id}} = $parent;
            }
        } elsif (/<(dependency|rel) ?([^>]*)>\s*(.*<\/rel>\s*)?$/) {
            my $options = $2;
            my $closed = $3;
            my $label = "generic";
            my @heads = ();
            my @deps = ();

            $options = string2opthash($options);
            $label = $options->{label} if defined $options->{label};
            delete $options->{label};
           
            if ($closed) {
                push @heads, $options->{head};
                push @deps, $options->{dep};
                delete $options->{head};
                delete $options->{dep};
            } else {
                while (defined($_ = <$fd>) and !/<\/(dependency|rel)>/) {
                    if (/<label>(.*)<\/label>/) {
                        $label = $1;
                    }
                    if (/<head ([^>]*)>(.*)<\/head>/) {
                        my $word = $2;
                        my $opts = string2opthash($1);
                        #$opts->{id} =~ s/[^0-9]/-/g;
                        $words->{$opts->{id}} = $word;
                        $tags->{$opts->{id}} = ($opts->{pos} or $opts->{tag});
                        push @heads, $opts->{id};
                        for my $opt (keys %$opts) {
                            $word_options->{$opts->{id}}{$opt} = $opts->{$opt} unless $opt =~ /^(pos|id)$/;
                        }
                    }
                    if (/<dep ([^>]*)>(.*)<\/dep>/) {
                        my $word = $2;
                        my $opts = string2opthash($1);
                        #$opts->{id} =~ s/[^0-9]/-/g;
                        $words->{$opts->{id}} = $word;
                        $tags->{$opts->{id}} = ($opts->{pos} or $opts->{tag});
                        push @deps, $opts->{id};
                        for my $opt (keys %$opts) {
                            $word_options->{$opts->{id}}{$opt} = $opts->{$opt} unless $opt =~ /^(pos|id)$/;
                        }
                    }
                }
                die "End of file while looking for </dependency>\n" if eof($fd);
            }
           
            my $rel_id = $options->{id};
            if (defined $rel_id) {
                delete $options->{id};
            } else {
                $rel_id = $global_rel_id++;
            }
            
            my $dep_struct = {
                id => $rel_id,
                head  => $heads[0],
                dep   => $deps[0],
                label => $label,
                options => $options,
            };
            if (@heads > 1 or @deps > 1) {
                $dep_struct->{compound} = 1;
            }
            $dep_struct->{heads} = [@heads];
            $dep_struct->{deps} = [@deps];
            $rels->{$rel_id}= $dep_struct;
            (my $tmp = $rel_id) =~ s/\D//g;
            $$max_rel_id = $tmp if $$max_rel_id < $tmp;
           
            # XXX: only first head and dependent 
            for my $h ($heads[0]) {
                for my $d ($deps[0]) {
                    if ($d eq $h and @deps > 1) {
                        $d = $deps[1];
                    }
                        
                    $dep_struct->{dep} = $d;
                    push @{$deps->{$h}}, $dep_struct;
                    push @{$heads->{$d}}, $dep_struct;
                    if (not exists $matrix->{$h}{$d}
                        or exists $matrix->{$h}{$d}{options}{layer}) {
                        $matrix->{$h}{$d} = $dep_struct;
                        $invmatrix->{$d}{$h} = $dep_struct;
                    }
                    if ($d =~ /^[0-9]+$/) {
                        $$maxid = $d if ($d > $$maxid);
                        $$minid = $d if ($d < $$minid);
                    }
                    if ($h =~ /^[0-9]+$/) {
                        $$maxid = $h if ($h > $$maxid);
                        $$minid = $h if ($h < $$minid);
                    }
                }
            }
        }
    }
    die "End of file while looking for </sentence>\n" if defined($_) and !/<\/sentence>/;

    if (defined $sent) {
        $sent->{id} = $sent_id;
        ($sent->{nid} = $sent_id) =~ s/^.*\D(\d)/$1/;
        $sent->{options} = $sent_options;
    }

    return $sent_id;
}


# used to give XML node options a "natural" order
sub compare_opt_names {
    return -1 if $a eq 'id';
    return 1 if $b eq 'id';
    return -1 if $a eq 'type';
    return 1 if $b eq 'type';
    return -1 if $a eq 'tag';
    return 1 if $b eq 'tag';
    return -1 if $a eq 'start';
    return 1 if $b eq 'start';
    return -1 if $a eq 'end';
    return 1 if $b eq 'end';
    return -1 if $a eq 'start_word';
    return 1 if $b eq 'start_word';
    return -1 if $a eq 'end_word';
    return 1 if $b eq 'end_word';
    return $a cmp $b;
}

sub opthash2string {
    my $options = shift;
    my $res = "";
    if (defined $options) {
        for my $opt (sort compare_opt_names keys %$options) {
            next if ref $options->{$opt};
            my $quote = "\"";
            if ($options->{$opt} =~ /$quote/) {
                $quote = "'";
                die "bad attribute value: $options->{$opt}" if $options->{$opt} =~ /$quote/;
            }
            $res .= " $opt=$quote$options->{$opt}$quote";
        }
    }
    return $res;
}


# Output sentence with dependencies to an XML file
# Args: FILEHANDLE, $sentence_id, \%text, \%words, \%tags, \%deps
#   or: FILEHANDLE, \%sent
sub output_sentence {
    my ($fd, $sent_id, $text, $words, $tags, $deps, $word_options) = @_;
    my $sent = undef;

    if (not defined $text) {
        $sent = $sent_id;
        $sent_id = $sent->{id};
        $text = \($sent->{text});
        $words = \%{$sent->{words}};
        $tags = \%{$sent->{tags}};
        $deps = \%{$sent->{deps}};
        $word_options = \%{$sent->{word_options}};
    } else {
        die "output_sentence: should be used with two args only";
    }

    if ($deputils_options{output_format} eq 'cxml') {
        return output_sentence_cxml($fd, $sent);
    }
    
    my $sent_opts = opthash2string($sent->{options});
    print $fd "<sentence$sent_opts>\n";
    if ($text) {
        $$text =~ s/"/'/g;
        print $fd "  <text>\n$$text  </text>\n";
    }

    if ($sent->{phrases}) {
        for my $ph (sort {$a<=>$b} keys %{$sent->{phrases}}) {
            my $text = $sent->{phrases}{$ph}{text};
            delete $sent->{phrases}{$ph}{text};
            my $opts = opthash2string($sent->{phrases}{$ph});
            print "  <phrase$opts>$text</phrase>\n";
        }
    }

    for my $w (sort {"$a$b" =~ /\D/ ? 0 : ($a<=>$b)} keys %$words) {
            my $opts = opthash2string($word_options->{$w});
            print "  <word id=\"$w\" tag=\"$tags->{$w}\"$opts>$words->{$w}</word>\n";
    }
    
    my %seen_compounds = ();
    if (defined $deps) {
        
        for my $h_id (keys %$deps) {
            for my $d (@{$deps->{$h_id}}) {
                my $dep_options = opthash2string($d->{options});
                if (not $d->{compound}) {
                    my $d_id = $d->{dep};
                    $d->{id} = ++$sent->{max_rel_id} unless defined $d->{id};
                    print $fd "  <rel id=\"$d->{id}\" label=\"$d->{label}\"$dep_options";
                    #print $fd "     <label>$d->{label}</label>\n";
                    print $fd " head=\"$h_id\" dep=\"$d_id\">";
                    #print $fd "     <dep id=\"$d_id\" pos=\"$tags->{$d_id}\"$d_options>" .
                    #                "$words->{$d_id}</dep>\n";
                    print $fd "$sent->{words}{$h_id} : $sent->{words}{$d_id}";
                    print $fd "</rel>\n";
                } else {
                    warn "warning: compound deps not implemented (sentence \"$sent->{start}...\")";
                    next if exists $seen_compounds{$d};
                    $seen_compounds{$d} = 1;
                    print $fd "  <dependency>\n";
                    print $fd "     <label$dep_options>$d->{label}</label>\n";
                    for my $hid (sort @{$d->{heads}}) {
                        my $h_options = opthash2string($word_options->{$hid});
                        print $fd "     <head id=\"$hid\" pos=\"$tags->{$hid}\"$h_options>" . 
                                        "$words->{$hid}</head>\n";
                    }
                    for my $did (sort @{$d->{deps}}) {
                        my $d_options = opthash2string($word_options->{$did});
                        print $fd "     <dep id=\"$did\" pos=\"$tags->{$did}\"$d_options>" . 
                                        "$words->{$did}</dep>\n";
                    }
                    print $fd "  </dependency>\n";
                    
                }
            }
        }
    }
    print $fd "</sentence>\n";
}

sub word2xml {
    my ($sent, $w, $xmltag) = @_;

    $xmltag = "word" unless $xmltag;
    
    $sent->{word_options}{$w}{id} = $w;
    $sent->{word_options}{$w}{tag} = $sent->{tags}{$w};
    my %options = %{$sent->{word_options}{$w}};
    $options{id} = "w".$options{id} unless $options{id} =~ /w/;
    my $opts = opthash2string(\%options);
    my $t = $sent->{words}{$w};
    $t =~ s/\&(?!\w+;)/\&amp;/g;
    $t =~ s/</&lt;/g;
    return "<$xmltag$opts>$t</$xmltag>\n";
}

sub phrase2xml {
    my ($sent, $phrase, $prefix) = @_;

    if (not defined $phrase->{start}) {
        $phrase->{start} = $sent->{word_options}{$phrase->{start_word}}{start}; 
    }
    if (not defined $phrase->{end}) {
        $phrase->{end} = $sent->{word_options}{$phrase->{end_word}}{end}; 
    }
    my %opts = %$phrase;
    delete $opts{text};
    delete $opts{start_word};
    delete $opts{end_word};
    delete $opts{parent};
    $opts{id} = ("p" . $opts{id}) unless $opts{id} =~ /p/;
    $opts{headword} = $sent->{words}{$opts{head}};
    $opts{head} = ("w" . $opts{head}) unless $opts{head} =~ /w/;
    my $opts = opthash2string(\%opts);
    my $res = "$prefix<phrase$opts>\n";
    for my $id (@{$phrase->{children}}) {
        if (ref $id) {
            $res .= "$prefix  " . word2xml($sent, $id->{word});
            next;
        }
        $res .= phrase2xml($sent, $sent->{phrases}{$id}, $prefix."  ");
    }
    $res .= "$prefix</phrase>\n";

    return $res;
}

sub output_sentence_cxml {
    my ($fd, $sent) = @_;

    $sent->{options}{id} = $sent->{id} unless defined $sent->{options}{id};
    $sent->{options}{cxmlLocalBase} = "text" unless defined $sent->{options}{cxmlLocalBase};
    my $sent_opts = opthash2string($sent->{options});
    print $fd "<sentence$sent_opts>\n";
    my $text = "";
    my $textlen = 0;
    my $words_xml = "";
            
    for my $w (sort {my ($x,$y)=($a,$b); $x=~s/\D//g; $y=~s/\D//g; ($x<=>$y)} keys %{$sent->{words}}) {
        if (1) {#($w =~ /^\d+$/) {
            $sent->{word_options}{$w}{start} = $textlen;
            $textlen += length($sent->{words}{$w});
            $sent->{word_options}{$w}{end} = $textlen-1;
            $textlen++;
            $text .= "$sent->{words}{$w} ";
        }
    }
    
    print $fd "  <text>$text</text>\n";

    if ($sent->{phrases}{top}) {
        print $fd phrase2xml($sent, $sent->{phrases}{$_}, "  ") for @{$sent->{phrases}{top}{children}};
    } 
    
    for my $w (sort {$sent->{word_options}{$a}{start} <=> $sent->{word_options}{$b}{end}} keys %{$sent->{words}}) {
        if (not exists $sent->{word_phrases}{$w}) {
            print $fd "  ".word2xml($sent, $w);
        }
    }

    my %seen_compounds = ();
    if (defined $sent->{deps}) {
        
        for my $h_id (keys %{$sent->{deps}}) {
            for my $d (@{$sent->{deps}{$h_id}}) {
                my $dep_options = opthash2string($d->{options});
                if (not $d->{compound}) {
                    my $d_id = $d->{dep};
                    $d->{id} = ++$sent->{max_rel_id} unless defined $d->{id};
                    next unless defined $d_id;
                    $d_id = "w$d_id" unless $d_id =~ /w/;
                    $h_id = "w$h_id" unless $h_id =~ /w/;
                    my $rel_id = $d->{id};
                    $rel_id = "r$rel_id" unless $rel_id =~ /r/;
                    my $h_word = $sent->{words}{$d->{head}};
                    $h_word = "XXX$d->{head}" unless defined $h_word;
                    my $d_word = $sent->{words}{$d->{dep}};
                    $d_word = "XXX$d->{dep}" unless defined $d_word;
                    print $fd "  <rel id=\"$rel_id\" label=\"$d->{label}\" head=\"$h_id\" " . 
                                     "dep=\"$d_id\"$dep_options>" . 
                                     "$h_word : $d_word" . 
                                     "</rel>\n";
                    #print $fd "    ", word2xml($sent, $d->{head}, 'head');
                    #print $fd "    ", word2xml($sent, $d->{dep}, 'dep');
                    #print $fd "  </rel>\n";
                } else {
                    die "warning: compound deps not implemented (sentence \"$sent->{start}...\")";
                }
            }
        }
    }
    print $fd "</sentence>\n";
}


# Normalize dependencies: remove some func. labels (e.g. 'NP-SBJ-2|DT' -> 'NP|DT')
# The justification of this is questionable
sub normalize_sentence {
    for my $sent (@_) {
        for my $h (keys %{$sent->{deps}}) {
            for my $dep (@{$sent->{deps}{$h}}) {
                $dep->{label} = normalize_label($dep->{label});
                if (defined $dep->{options}{correct}) {
                    $dep->{options}{correct} = normalize_label($dep->{options}{correct});
                }
            }
        }
    }
}

sub normalize_label {
    my $lab = shift;

    # remove functional tags of the "head" part of the label
    $lab =~ s/-.*\|/\|/;

    # remove trace counters
    $lab =~ s/-[0-9]+//g;

    return $lab;
}


# returns the list of nodes below $id in the sentence, excluding nodes from @exclude
sub get_phrase_below {
    my ($sent, $id, @exclude) = @_;

    my $seen = {$id => 1};
    my @active = ($id);
    
    my %exclude = ();
    $exclude{$_} = 1 for @exclude;
    
    while (@active) {
        $id = shift @active;
        #next if $exclude{$id};
        my @conj = ();
        #if (not $exclude{$id}) {
        #    for my $cc (@{$sent->{deps}{$id}}) {
        #        push @conj, keys %{$sent->{invmatrix}{$cc->{dep}}};
        #    }
        #}
        my @next = keys %{$sent->{matrix}{$id}};
        @next = grep {not exists $exclude{$_}} @next;
        for my $dep (@next, @conj) {
            if (not defined $seen->{$dep}) {
                push @active, $dep;
                $seen->{$dep} = 1;
            }
        }
    }

    return sort {$a <=> $b} keys %$seen;
}

# Various operations on relations

sub remove_relation {
    my $rel = shift;
    my $h = $rel->{head};
    my $d = $rel->{dep};
    my $label = $rel->{label};

    my $id = undef;
    #print STDERR " --- ";
    #print_relation(STDERR, $rel);
    for (my $i = 0; $i < @{$sent->{deps}{$h}}; $i++) {
        #print STDERR " === ";
        #print_relation(STDERR, $sent->{deps}{$h}[$i]);
        if ($sent->{deps}{$h}[$i] == $rel) {
            $id = $i;
            last;
        }
    }
    
    die "bug in remove_relation" unless defined $id;

    splice @{$sent->{deps}{$h}}, $id, 1;
}

sub add_relation {
    my ($label, $h, $d, $hl, $dl) = @_;

    push @{$sent->{deps}{$h}}, { head  => $h,
                                 dep   => $d,
                                 label => $label,
                                 heads => $hl,
                                 deps => $dl };
}

sub reverse_relation {
    my $rel = shift;
    my $label = shift;

    if (not defined $label) {
        $label = 'inv-' . $rel->{label};
    }

    remove_relation($rel);
    add_relation($label, 
                 $rel->{dep}, $rel->{head},
                 $rel->{deps}, $rel->{heads});
}


sub remove_relations {
    my ($head, $skip) = @_;

    my @deps = grep {$_->{label} =~ /$skip/} @{$sent->{deps}{$head}};
    $sent->{deps}{$head} = [@deps];

}

sub copy_relations {
    my ($from, $to, $skip) = @_;

    my @deps = grep {$_->{label} !~ /$skip/} @{$sent->{deps}{$from}};
    my @newdeps = ();
    
    for my $dep (@deps) {
        $newdep = {%$dep};
        $newdep->{head} = $to;
        push @{$sent->{deps}{$to}}, $newdep; 
    }
    
}

sub substitute_dependent {
    my ($old, $new, $skip) = @_;

    for my $h (sort keys %{$sent->{deps}}) {
        for my $rel (@{$sent->{deps}{$h}}) {
            next unless $rel->{dep} eq $old;
            next if $rel->{label} =~ /$skip/;
            $rel->{dep} = $new;
        }
    }

}

sub print_relation {
    my ($fd, $rel) = @_;

    print $fd ($sent->{words}{$rel->{head}} . "_" . $sent->{tags}{$rel->{head}} . " -- " .
               $rel->{label} . " -> " .
               $sent->{words}{$rel->{dep}} . "_" . $sent->{tags}{$rel->{dep}} . "\n");
}


sub find_shortest_path {
    my ($sent, $head, $dep, $restrictor) = @_;

    my %seen = ();
    my %active = ($head => [{start=>$head, end=>$dep}]);
    
    while (1) {
        last if scalar(keys %active) == 0 or defined $active{$dep};

        for my $n (keys %active) {
            $seen{$n} = 1;
            for my $rel (@{$sent->{deps}{$n}}) {
                next if $restrictor and not &$restrictor($sent, $rel);
                next if exists $rel->{options}{removed};
                next if exists $seen{$rel->{dep}};
                next if exists $active{$rel->{dep}};
                @{$active{$rel->{dep}}} = @{$active{$n}};
                push @{$active{$rel->{dep}}}, {dep=>$rel};
            }
            for my $rel (@{$sent->{heads}{$n}}) {
                next if $restrictor and not &$restrictor($sent, $rel);
                next if exists $rel->{options}{removed};
                next if exists $seen{$rel->{head}};
                next if exists $active{$rel->{head}};
                @{$active{$rel->{head}}} = @{$active{$n}};
                push @{$active{$rel->{head}}}, {head=>$rel};
            }
            delete $active{$n};
            last if defined $active{$dep};
        }
    }

    return undef if not exists $active{$dep};

    return $active{$dep};
}

sub path2string {
    my ($sent, $path) = @_;

    return "nil" unless defined $path;

    #my $res = "$sent->{words}{$path->[0]{start}}";
    my $res = "";

    die "bug" unless @$path;
    
    for my $i (@$path) {
        next if exists $i->{start};
        if (exists $i->{head}) {
            #$res .= " >$i->{head}{label}> $sent->{words}{$i->{head}{head}}";
            $res .= "_>$i->{head}{label}>";
        } elsif (exists $i->{dep}) {
            #$res .= " <$i->{dep}{label}< $sent->{words}{$i->{dep}{dep}}";
            $res .= "_<$i->{dep}{label}<";
        } else {
            die "bug";
        }
    }

    return $res . "_";
}

# Check various classes of words and relations

sub is_have_gone {
    my $rel = shift;
    my $h = $rel->{head};
    my $d = $rel->{dep};
    my $label = $rel->{label};

    return 0 unless is_have($h);
    return 0 unless $label =~ /^VP.*\|VP/;
    return 0 unless $sent->{tags}{$d} =~ /VB[NP]/;
    return 1;
}

sub is_have {
    my $n = shift;
    return ($sent->{tags}{$n} =~ /^VB|^AUX/ and
            $sent->{words}{$n} =~ /^(have|Have|has|Has|had|Had|having|Having|'ve|'d|'s)$/);
}

sub is_are_going {
    my $rel = shift;
    my $h = $rel->{head};
    my $d = $rel->{dep};
    my $label = $rel->{label};

    return 0 unless is_be($h);
    return 0 unless $label =~ /^VP.*\|VP/;
    return 0 unless $sent->{tags}{$d} =~ /VBG/;
    return 1;
}

sub is_does_go {
    my $rel = shift;
    my $h = $rel->{head};
    my $d = $rel->{dep};
    my $label = $rel->{label};

    return 0 unless is_do($h);
    return 0 unless $label =~ /^VP.*\|VP/;
    return 0 unless $sent->{tags}{$d} =~ /^VB$/;
    return 1;
}

sub is_be {
    my $n = shift;
    return ($sent->{tags}{$n} =~ /^VB|^AUX/ and
           $sent->{words}{$n} =~ /^(am|Am|'m|is|Is|'s|are|Are|'re|was|Was|were|Were|be|Be|been|Been|being|Being)$/);
}

sub is_do {
    my $n = shift;
    return ($sent->{tags}{$n} =~ /^VB|^AUX/ and
           $sent->{words}{$n} =~ /^(do|Do|does|Does|did|Did|doth|Doth)$/); # Note: no 'done'
}

1;
