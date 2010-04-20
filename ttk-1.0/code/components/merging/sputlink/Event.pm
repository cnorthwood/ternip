package Event;

use strict;


sub new {
	my ($class,$string) = @_;
	my $objref = {};
	if ($string =~ /(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)/) {	
		$objref->{_eiid} = $1;
		$objref->{_eid} = $2;
		$objref->{_sentid} = $3;
		$objref->{_text} = $4;
		$objref->{_class} = $5;
		$objref->{_aspect} = $6;
		$objref->{_tense} = $7;
		$objref->{_wellformed} = 1; }
	else {
		$objref->{_wellformed} = 0; }
	bless $objref, $class; 
}

sub fromTimemlTags {
	my ($class, $event, $instance) = @_;
	my $objref = {};
	$objref->{_eiid} = $instance->{'eiid'};
	$objref->{_eid} = $event->{'eid'};
	$objref->{_sentid} = $event->{'sentID'};
	$objref->{_text} = $event->{'text'};
	$objref->{_class} = $event->{'class'};
	$objref->{_aspect} = $instance->{'aspect'};
	$objref->{_tense} = $instance->{'tense'};
	$objref->{_wellformed} = 1;
	bless $objref, $class; 
}

sub id { $_[0]->{_eiid} }
sub eiid { $_[0]->{_eiid} }
sub eid { $_[0]->{_eid} }
sub sentid { $_[0]->{_sentid} }
sub text { $_[0]->{_text} }
sub class { $_[0]->{_class} }
sub aspect { $_[0]->{_aspect} }
sub tense { $_[0]->{_tense} }
sub funInDoc { undef }

sub type { return 'EVENT' }

# for use in iaa where offset was rolled into t&a
sub offset { return $_[0]->{_aspect} . 'x' . $_[0]->{_tense} }
sub offset { return $_[0]->{_aspect} }

sub isWellformed {
	my $self = $_[0];
	return $self->{_wellformed}; }

sub print_me {
	my $self = $_[0];
	my $eiid = $self->{_eiid};
	my $eid = $self->{_eid};
	my $sentid = $self->{_sentid};
	my $text = $self->{_text};
	my $class = $self->{_class};
	my $aspect = $self->{_aspect};
	my $tense = $self->{_tense};
	print "$eiid $eid $sentid $text $class $aspect $tense\n"; }

1;
