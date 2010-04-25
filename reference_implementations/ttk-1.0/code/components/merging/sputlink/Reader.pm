package Reader;
use strict;

use TimeMLDoc;
use Event;
use Timex;
use TLink;
use Sentence;
use Edge;
use RelationType;

use Data::Dumper;

my $debug = 0;


sub new {
    my ($class,$file1,$file2) = @_;
    my $objref = { 
	_file1 => $file1,	# document
	_file2 => $file2,	# compositions file
	_doc => undef,	    # parsed xml document
	_events => {},
	_timexes => {},
	_tlinks => {},
	_sentences => {},
	_table => {},
    };
    bless $objref, $class; }

sub events { $_[0]->{_events} }
sub timexes { $_[0]->{_timexes} }
sub tlinks { $_[0]->{_tlinks} }
sub sentences { $_[0]->{_sentences} }
sub table { $_[0]->{_table} }
sub DOC { $_[0]->{_doc} }


sub readAnnotation
{
    my $self = shift;
    $self->{_doc} = TimeMLDoc->parse($self->{_file1});
    my $DOC = $self->DOC;

    foreach my $tmlEvent ($DOC->events()) {
	my $tmlInstance = $DOC->instanceFromEventID($tmlEvent->{'eid'});
	my $event = Event->fromTimemlTags($tmlEvent, $tmlInstance);
	my $id = $event->id();
	$self->events->{$id} = $event;
    }

    foreach my $tmlTimex ($DOC->timexes()) {
	my $timex = Timex->fromTimemlTags($tmlTimex);
	my $id = $timex->id();
	$self->timexes->{$id} = $timex;
    }

    foreach my $tmlTLink ($DOC->tlinks()) {
	my $tlink = TLink->fromTimemlTags($tmlTLink);
	my $id1 = $tlink->id1();
	my $id2 = $tlink->id2();
	$self->tlinks->{"$id1-$id2"} = $tlink;
    }
}

sub readCompositions {
	my ($self) = @_;
	my $tableFile = $self->{_file2};
	open IN, $tableFile;
	while (<IN>) {
		chomp;
		my ($l1,$l2,$r) = split /\t/;
		$l1 = RelationType::sortRels($l1);
		$l2 = RelationType::sortRels($l2);
		$r = RelationType::sortRels($r);
		$self->table()->{$l1}{$l2} = $r; }}

sub cleanup {
	$_[0]->{_events} = undef;
	$_[0]->{_timexes} = undef;
	$_[0]->{_tlinks} = undef;
	$_[0]->{_sentences} = undef;
	$_[0]->{_table} = undef; }


sub updateTLinks 
{
    my ($self, $edgesHash) = @_;
    my $DOC = $self->DOC;
    #print Dumper $DOC;
    $DOC->clearTLINKs;
    foreach my $id1 (keys %$edgesHash) {
        foreach my $id2 (keys %{ $edgesHash->{$id1} }) {
	    my $edge = $edgesHash->{$id1}{$id2};
	    my $tlink = $edge->asTlink;
	    if ($debug) {
            $edge->print_me; print "\n";	    
            print Dumper $tlink; }
	    $DOC->addTLink($tlink);
        }
    }
    #print Dumper $DOC->{DOC};
}


sub printFile 
{
    my ($self, $file) = @_;
    $self->DOC->printOut($file);
    #$self->DOC->printMin($file);
    #print Dumper ($self->DOC);
}

sub print_me {
	my ($self) = @_;
	my $file = $self->{_file};
	print "BASEFILE: $file\n"; }

sub print_events { foreach my $event (values %{$_[0]->{_events}}) { $event->print_me(); } }
sub print_timexes { foreach my $timex (values %{$_[0]->{_timexes}}) { $timex->print_me(); } }
sub print_tlinks { foreach my $tlinks (values %{$_[0]->{_tlinks}}) { $tlinks->print_me(); } }

sub print_table {
	my ($self) = @_;
	foreach my $l1 (keys %{ $self->table() }) {
		foreach my $l2 (keys %{ $self->table()->{$l1} }) {
			my $r = $self->table()->{$l1}{$l2};
			print "$l1\t$l2\t$r\n"; }}}

1;
