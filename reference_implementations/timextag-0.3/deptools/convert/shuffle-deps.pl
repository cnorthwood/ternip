#!/usr/bin/perl -w
# rules for modifying dependency structures coming from Penn

$depdir = $ENV{DEPDIR};
die "died: env. variable \$DEPDIR not defined\n" unless $depdir;
require "$depdir/lib/dep-utils.pl";

while (read_sentence(ARGV, \%sent)) {
    shuffle_dependencies(\%sent);
    output_sentence(STDOUT, \%sent);
}


sub shuffle_dependencies {
    local $sent = shift;

    ALL: {
    for my $h (sort keys %{$sent->{deps}}) {
        for my $rel (@{$sent->{deps}{$h}}) {
            if (is_have_gone($rel) or is_are_going($rel) or is_does_go($rel)) {
                #print_relation(STDERR, $rel);
                reverse_relation($rel, 'AUX');
                copy_relations($h, $rel->{dep}, 'AUX');
                substitute_dependent($h, $rel->{dep}, 'AUX');
                remove_relations($h, 'AUX');
                redo ALL;
            }
            if ($rel->{label} =~ /\|PP-LGS/) {
                $rel->{label} =~ s/-LGS//;
                for my $np (grep {$_->{label} =~ /\bNP\b/} @{$sent->{deps}{$rel->{dep}}}) {
                    $np->{label} =~ s/PP-LGS/PP/;
                    if ($np->{label} !~ /NP-LGS/) {
                        $np->{label} =~ s/\bNP\b/NP-LGS/;
                    }
                }
            }
        }
    }};

    for my $pos (keys %{$sent->{words}}) {
        next unless $sent->{tags}{$pos} eq 'POS';
        my $hd = max(keys %{$sent->{matrix}{$pos}});
        next unless defined $hd;
        #print STDERR "head $sent->{words}{$hd}\n";
        my ($head_rel) = grep {$_->{dep} eq $hd} @{$sent->{deps}{$pos}};
        my @other_rels = grep {$_->{dep} ne $hd} @{$sent->{deps}{$pos}};
        $_->{head} = $hd for @other_rels;
        push @{$sent->{deps}{$hd}}, @other_rels;
        @{$sent->{deps}{$pos}} = ($head_rel);
    }

}

sub max {
    my $res = shift;
    for (@_) {
        $res = $_ if greater_than($_, $res);
    }
    return $res;
}

sub greater_than {
    my ($x, $y) = @_;
    $x =~ s/\D//g;
    $y =~ s/\D//g;
    return $x > $y;
}
