package Sentence;
use strict;

sub new {
	my ($class,$id) = @_;
	my $objref = { _id => $id,
				   _tokens => [] };
	bless $objref, $class; }

sub id { $_[0]->{_id} }
sub tokens { $_[0]->{_tokens} }

sub addToken {
	my ($self, $line) = @_;
	$line =~ /(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*)/;
	#print "-$1-$2-$3-$4-$5-\n";
	push @{$self->tokens}, { _sentid => $1, _tokenid => $2, _text => $3, _type => $4, _id => $5 }; }

sub print_me {
	my ($self,$verbose) = @_;
	foreach my $token (@{$self->tokens}) {
		print '[', $token->{_sentid}, '-', $token->{_tokenid}, '] ' if $verbose;
		print $token->{_text}; }
	print "\n"; }

sub print_with_node {
	my ($self,$FH,$node) = @_;
	my $sentid = $self->id;
	my $nodeid = $node->type eq 'EVENT' ? $node->source->eid : $node->source->tid;
	print $FH "$sentid: ";
	foreach my $token  (@{$self->tokens}) {
		if ($nodeid eq $token->{_id}) { print $FH '__', uc $token->{_text}, '__'; }
		else { print $FH $token->{_text}; }}
	print $FH "\n"; }

1;
