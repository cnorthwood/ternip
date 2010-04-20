package HistoryElement;

use strict;
use Edge;

sub new
{
	my ($class,$oldrel,$composition,$edge1,$edge2) = @_;
	my $comp = $composition;
	my $unspec = RelationType::unspecifiedRel();
	$oldrel =~ s/$unspec/all/g;
	$composition =~ s/$unspec/all/g;
	my $objref = { _oldrel => $oldrel,
				   _composition => $composition,
				   _edge1 => $edge1,
				   _edge2 => $edge2,
				   _edge1Rel => $edge1->basicRels,
				   _edge2Rel => $edge2->basicRels };
	bless $objref, $class;
}


sub oldrel { $_[0]->{_oldrel}} ;
sub composition { $_[0]->{_composition}} ;
sub edge1 { $_[0]->{_edge1}} ;
sub edge2 { $_[0]->{_edge2}} ;
sub edge1Rel { $_[0]->{_edge1Rel}} ;
sub edge2Rel { $_[0]->{_edge2Rel}} ;

# clenaup by removing the edges (don't clean them, that would get you
# into a loop)
sub cleanup {
	$_[0]->{_edge1} = undef;
	$_[0]->{_edge2} = undef; }

sub asString {
	my ($self,$indent) = @_;
	my $str1 = $indent . $self->composition . "\n";
	my $str2 = $indent . $self->edge1->asString . "\n";
	my $str3 = $indent . $self->edge2->asString . "\n";
	return $str1 . $str2 . $str3; }

sub print_me {
	my ($self,$indent,$FH) = @_;
	my $newindent = $indent;
	$indent = ' ' x $indent;
	unless (defined $FH) { $FH = *STDOUT; }
	print $indent, $self->composition, "\n\n";
	$self->edge1->printWithHistory($newindent,$FH);
	$self->edge2->printWithHistory($newindent,$FH); }

1;
