package TLink;
use strict;


sub new {
	my ($class,$string) = @_;
	my $objref = {};
	if ($string =~ /(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)/) {	
		$objref->{_eiid1} = $1;
		$objref->{_eiid2} = $2;
		$objref->{_eid1} = $3;
		$objref->{_eid2} = $4;
		$objref->{_tid1} = $5;
		$objref->{_tid2} = $6;
		$objref->{_rel} = $7;
		$objref->{_sig} = $8;
		$objref->{_str1} = $9;
		$objref->{_str2} = $10;
		$objref->{_str3} = $11;
		$objref->{_wellformed} = 1; }
	else {
		$objref->{_wellformed} = 0; }
	bless $objref, $class; }

sub fromTimemlTags {
    my ($class, $tlink) = @_;
    my $objref = {};
    $objref->{_lid} = $tlink->{'lid'};
    $objref->{_eiid1} = $tlink->{'eventInstanceID'};
    $objref->{_eiid2} = $tlink->{'relatedToEventInstance'};
    $objref->{_eid1} = undef;
    $objref->{_eid2} = undef;
    $objref->{_tid1} = $tlink->{'timeID'};
    $objref->{_tid2} = $tlink->{'relatedToTime'};
    $objref->{_rel} = $tlink->{'relType'};
    $objref->{_sig} = $tlink->{'signalID'};
    $objref->{_str1} = undef;
    $objref->{_str2} = undef;
    $objref->{_str3} = undef;
    $objref->{_wellformed} = 1;
    bless $objref, $class;
}

sub fromClassifier_OLD {
    my ($class,$string) = @_;
    my $objref = {
	_eiid1 => undef,
	_eiid2 => undef,
	_eid1 => undef,
	_eid2 => undef,
	_tid1 => undef,
	_tid2 => undef,
	_rel => undef,
	_sig => undef,
	_str1 => undef,
	_str2 => undef,
	_str3 => undef };
    if ($string =~ /relType="(\S+)" eventInstanceID="(\S+)" relatedToEventInstance="(\S+)" confidence="(\S+)"/) {
	$objref->{_eiid1} = $2;
	$objref->{_eiid2} = $3;
	$objref->{_rel} = $1;
	$objref->{_conf} = $4;
	$objref->{_wellformed} = 1; }
    elsif ($string =~ /relType="(\S+)" eventInstanceID="(\S+)" relatedToTime="(\S+)" confidence="(\S+)"/) {
	$objref->{_eiid1} = $2;
	$objref->{_tid2} = $3;
	$objref->{_rel} = $1;
	$objref->{_conf} = $4;
	$objref->{_wellformed} = 1; }
    else {
	$objref->{_wellformed} = 0; }
    bless $objref, $class; 
}

sub fromClassifier {
    my ($class,$string) = @_;
    my $objref = {
	_eiid1 => undef,
	_eiid2 => undef,
	_eid1 => undef,
	_eid2 => undef,
	_tid1 => undef,
	_tid2 => undef,
	_rel => undef,
	_sig => undef,
	_str1 => undef,
	_str2 => undef,
	_str3 => undef };
    
    $objref->{_rel} = $1 if $string =~ /relType="(\S+)"/;
    $objref->{_eiid1} = $1 if $string =~ /eventInstanceID="(\S+)"/;
    $objref->{_eiid2} = $1 if $string =~ /relatedToEventInstance="(\S+)"/;
    $objref->{_conf} = $1 if $string =~ /confidence="(\S+)"/;
    $objref->{_tid2} = $1 if $string =~ /relatedToTime="(\S+)"/;
    
    if ($objref->{_rel}
        and $objref->{_eiid1}
        and ($objref->{_eiid2} or $objref->{_tid2})
        and $objref->{_conf})
    {
	$objref->{_wellformed} = 1;
    } else
    {
	$objref->{_wellformed} = 0;
    }

    #print STDERR "STRING: $string\n";
    bless $objref, $class; 
}

sub from_opening_tag
{
    # Similar to fromClassifier, only difference is that an origin
    # attribute was added and that this attribute was used to fill in
    # both a confidence and an origin filed, used for merge2.pl, needs
    # to be consolidated with the other creators
    
    my ($class,$string) = @_;
    my $objref = {
        _eiid1 => undef,
        _eiid2 => undef,
        _eid1 => undef,
        _eid2 => undef,
        _tid1 => undef,
        _tid2 => undef,
        _rel => undef,
        _sig => undef,
        _str1 => undef,
        _str2 => undef,
        _str3 => undef,
        _conf => undef,
        _origin => undef };
    
    $objref->{_rel} = $1 if $string =~ /relType="(\S+)"/;
    $objref->{_eiid1} = $1 if $string =~ /eventInstanceID="(\S+)"/;
    $objref->{_eiid2} = $1 if $string =~ /relatedToEventInstance="(\S+)"/;
    $objref->{_conf} = $1 if $string =~ /confidence="(\S+)"/;
    $objref->{_tid1} = $1 if $string =~ /timeID="(\S+)"/;
    $objref->{_tid2} = $1 if $string =~ /relatedToTime="(\S+)"/;
    $objref->{_origin} = $1 if $string =~ /origin="([^"]+)"/;

    # copy the confidence score from the origin tag, if there is one
    if ($objref->{_origin} =~ /CLASSIFIER (\d(.\d+)?)/) {
        $objref->{_conf} = $1;
    } else {
        # this is a hack that assigns maximum confidence to
        # non-classifier components
        $objref->{_conf} = 1;
    }
    
    if ($objref->{_rel}
        and $objref->{_eiid1}
        and ($objref->{_eiid2} or $objref->{_tid2})
        and $objref->{_origin})
    {
	$objref->{_wellformed} = 1;
    } else
    {
	$objref->{_wellformed} = 0;
    }

    #print STDERR "STRING: $string\n";
    bless $objref, $class; 
}

    
sub lid { $_[0]->{_lid} }
sub eiid1 { $_[0]->{_eiid1} }
sub eiid2 { $_[0]->{_eiid2} }
sub eid1 { $_[0]->{_eid1} }
sub eid2 { $_[0]->{_eid2} }
sub tid1 { $_[0]->{_tid1} }
sub tid2 { $_[0]->{_tid2} }
sub rel { $_[0]->{_rel} }
sub sig { $_[0]->{_sig} }
sub str1 { $_[0]->{_str1} }
sub str2 { $_[0]->{_str2} }
sub str3 { $_[0]->{_str3} }
sub confidence { $_[0]->{_conf} }

sub type { return 'TLINK' }

sub id1 {
	my $self = shift;
	$self->eiid1 ? $self->eiid1 : $self->tid1 }

sub id2 {
	my $self = shift;
	$self->eiid2 ? $self->eiid2 : $self->tid2 }

sub isWellformed {
	my $self = shift;
	return $self->{_wellformed}; }

sub print_me {
	my $self = shift;
	my $lid = $self->lid;
	my $id1 = $self->id1;
	my $id2 = $self->id2;
	my $str1 = $self->str1;
	my $rel = $self->rel;
	my $str2 = $self->str2;
	print "[$lid: $id1 $id2: $str1 $rel $str2]"; }

1;
