package Node;
use strict;

sub new {
    my ($class,$graph,$source) = @_;
    my $objref = { _name => $source->id,
		   _type => $source->type,	# 'EVENT' or 'TIMEX3'
		   _source => $source,		# an Event or a Timex
		   _graph => $graph };
    bless $objref, $class; }


# ACCESSORS
# ---------

sub id { $_[0]->{_name} }
sub name { $_[0]->{_name} }
sub type { $_[0]->{_type} }
sub source { $_[0]->{_source} }
sub graph { $_[0]->{_graph} }
sub text { $_[0]->source->text }
	
# the next two routines return a hash of name->Edge pairs
sub edgesTo {
	my $self = $_[0];
	return $self->graph->edgesTo($self->name)};
sub edgesFrom {
	my $self = $_[0];
	return $self->graph->edgesFrom($self->name)};

# Return an array, do not include those edges that have unknown as a
# TimeML relation type. Used for weights.
sub nonEmptyEdgesTo {
	my ($self,$node) = @_;
	my @answer = ();
	foreach my $edge (values %{ $self->edgesTo }) {
		unless ($edge->isDefault or $edge->isUnknown) { push @answer, $edge }}
	return @answer; }
sub nonEmptyEdgesFrom {
	my ($self,$node) = @_;
	my @answer = ();
	foreach my $edge (values %{ $self->edgesFrom }) {
		unless ($edge->isDefault or $edge->isUnknown) { push @answer, $edge }}
	return @answer; }

sub cleanup {
	$_[0]->{_source} = undef;
	$_[0]->{_graph} = undef; }


# PRINTING
# --------

sub asString {
	my $self = $_[0];
	return "<" . $self->name . ' "' . $self->text . '">'; }

sub print_me {
	my ($self,$FH) = @_;
	unless (defined $FH) { $FH = *STDOUT; }
	print $FH $self->asString;
    print $FH "\n"; }

1;
