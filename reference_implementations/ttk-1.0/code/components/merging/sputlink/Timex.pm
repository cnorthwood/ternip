package Timex;
use strict;


sub new {
	my ($class,$string) = @_;
	my $objref = {};
	# for now, only worry about these first five
	if ($string =~ /(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t/) {
		$objref->{_tid} = $1;
		$objref->{_sentid} = $2;
		$objref->{_text} = $3;
		$objref->{_type} = $4;
		$objref->{_value} = $5;
		$objref->{_funInDoc} = $7;
		$objref->{_wellformed} = 1; }
	else {
		$objref->{_wellformed} = 0; }
	bless $objref, $class; }

sub fromTimemlTags {
    my ($class, $timex) = @_;
    my $objref = {};
    $objref->{_tid} = $timex->{'tid'};
    $objref->{_sentid} = $timex->{'sentID'};
    $objref->{_text} = $timex->{'text'};
    $objref->{_type} = $timex->{'type'};
    $objref->{_value} = $timex->{'value'};
    $objref->{_funInDoc} = $timex->{'functionInDocument'};
    $objref->{_wellformed} = 1;
    bless $objref, $class; 
}

sub id { $_[0]->{_tid} }
sub tid { $_[0]->{_tid} }
sub sentid { $_[0]->{_sentid} }
sub text { $_[0]->{_text} }
sub type { $_[0]->{_type} }
sub value { $_[0]->{_value} }
sub funInDoc { $_[0]->{_funInDoc} }

sub type { return 'TIMEX3' }

# for use in iaa where offset was rolled into type & value
sub offset { return $_[0]->{_type} . '-' . $_[0]->{_value} }
sub offset { return $_[0]->{_type} }

sub isWellformed {
	my $self = $_[0];
	return $self->{_wellformed}; }

sub asString {
	my $self = $_[0];
	my $tid = $self->{_tid};
	my $sentid = $self->{_sentid};
	my $text = $self->{_text};
	my $type = $self->{_type};
	my $value = $self->{_value};
	return "$tid $sentid $text $type $value"; }

sub print_me {
	my $self = $_[0];
	my $tid = $self->{_tid};
	my $sentid = $self->{_sentid};
	my $text = $self->{_text};
	my $type = $self->{_type};
	my $value = $self->{_value};
	print "$tid $sentid $text $type $value\n"; }

1;
