package Set;
use strict;


sub new {
	my ($class,$field,@list) = @_;
	my $objref = { _data => {},
				   _size => 0,
				   _field => $field };
	foreach my $el (@list) {
		$objref->{_data}{$el->$field} = $el;
		$objref->{_size}++; }
	bless $objref, $class; }

sub isEmpty { $_[0]->{_size} == 0; }
sub notEmpty { $_[0]->{_size} != 0; }

sub pop {
	my $self = shift;
	return undef if $self->isEmpty;
	my @keys = keys %{ $self->{_data} };
	my $key = $keys[0];
	my $val = $self->{_data}{$key};
	# this gave weird errors:
	# my ($key,$val) = each %{ $self->{_data} };
	delete $self->{_data}{$key};
	$self->{_size}--;
	return $val; }

sub delete {
	my ($self,$key) = @_;
	if ($self->{_data}{$key}) {
		delete $self->{_data}{$key};
		$self->{_size}--; }}

sub print_me {
	my $self = shift;
	foreach my $key  (keys %{ $self->{_data} }) { print "$key "; }
	print "\n"; }

	
1;
