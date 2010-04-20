package Edge;

use HistoryElement;
use RelationType;
use strict;

my $debugClosure = 0;


# EDGE CREATION
# -------------

# Create an Edge from a TLink. Potentially, this is the reversed edge,
# so some values need to be reversed.
sub new {
    my ($class,$graph,$origin,$tlink) = @_;
    my ($lid,$id1,$id2,$sid,$tmlrel,$rel);
    # order is swapped for the inverted link
    if ($origin eq 'tlink') { 
	$lid = $tlink->lid;
	$sid = $tlink->sig;
	($id1,$id2) = ($tlink->id1, $tlink->id2);
        #print "$id1, $id2\n";
    }
    elsif ($origin eq 'tlinki') {
        ($id1,$id2) = ($tlink->id2, $tlink->id1); }
    else {
        warn "ERROR: unacceptable origin: $origin\n"; }
    # reverse relation type for inverted link/edge
    $tmlrel = $tlink->rel;
    $tmlrel = RelationType::reverseTimemlRel($tmlrel) if $origin eq 'tlinki';
    $rel = RelationType::timemlrel2basicrel($tmlrel),
    # and fill in the fields
    my $objref = {
        _name => "$id1-$id2",
        _lid => $lid,
        _sig => $sid,
        _node1 => $graph->nodeAt($id1),	# Node
        _node2 => $graph->nodeAt($id2),	# Node
        _timemlRel => $tmlrel,		# string
        _basicRels => $rel,		# string
        _origin => $origin,		# 'tlink' or 'tlinki'
        _history => [],			# list of HistoryElements
        _propagated => 0,		# 0 or 1
        _weight => 0,		    	# float
        _tlink => $tlink,		# TLink
        _graph => $graph };
    if ($tlink->confidence()) {
	$objref->{_confidence} = $tlink->confidence();
    }
    unless ($objref->{_node1} and $objref->{_node2}) {
        $objref->{_timemlRel} = undef;
        $objref->{_basicRels} = RelationType::unspecifiedRel;
        return 0;
    }
    bless $objref, $class;
}

# Create default edge between two nodes, only used by Graph::edgeAt
sub newDefault {
    my ($class,$graph,$id1,$id2) = @_;
    my $objref = {
        _name => "$id1-$id2",
        _node1 => $graph->nodeAt($id1),
        _node2 => $graph->nodeAt($id2),
        _timemlrel => undef,
        _basicRels => RelationType::unspecifiedRel,
        _origin => 'default',
        _history => [],
        _propagated => 0,
        _weight => 0,
        _tlink => undef,
        _graph => $graph };
    bless $objref, $class;
}


# TLINKS
# ------

sub asTlink
{
    my $self = shift;
    my $newHash = {};
    $newHash->{'lid'} = $self->{_lid} if $self->{_lid};
    $newHash->{'origin'} = $self->{_origin};
    if ($self->{_timemlRel}) {
	$newHash->{'relType'} = $self->{_timemlRel}; }
    else {
	$newHash->{'relType'} = RelationType::basicrel2timemlrel($self->{_basicRels}); }
#	$newHash->{'relType'} = $self->{_basicRels}; }
    my $name = $self->name;
    $name =~ /(.*)-(.*)/;
    my ($id1, $id2) = ($1, $2);
    if ($id1 =~ /^ei/) {
        $newHash->{'eventInstanceID'} = $id1; }
    else {
        $newHash->{'timeID'} = $id1; }
    if ($id2 =~ /^ei/) {
        $newHash->{'relatedToEventInstance'} = $id2; }
    else {
        $newHash->{'relatedToTime'} = $id2; }
    if ($self->{_sig}) {
        $newHash->{'signalID'} = $self->{_sig}; }
    return ['TLINK', $newHash];
}


# ACCESSORS
# ---------

sub name { $_[0]->{_name} }
sub node1 { $_[0]->{_node1} }
sub node2 { $_[0]->{_node2} }
sub timemlRel { $_[0]->{_timemlRel} }
sub basicRels { $_[0]->{_basicRels} }
sub origin { $_[0]->{_origin} }
sub history { $_[0]->{_history} }
sub propagated { $_[0]->{_propagated} }
sub weight { $_[0]->{_weight} }
sub tlink { $_[0]->{_tlink} }
sub graph { $_[0]->{_graph} }
sub confidence { $_[0]->{_confidence} }
sub basicRelsAsArray {
	return split / /, $_[0]->basicRels; }

sub setBasicRels {
	my ($self,$rels) = @_;
	#print "Setting rel of ", $self->asString, " to {$rels}\n";
	$self->{_basicRels} = $rels;
	$self->reaffirm if $self->basicRels ne RelationType::unspecifiedRel; }

sub setOrigin { $_[0]->{_origin} = $_[1]; }
sub setTimemlRel { $_[0]->{_timemlRel} = $_[1]; }
sub setPropagated { $_[0]->{_propagated} = $_[1]; }
sub setWeight { $_[0]->{_weight} = $_[1]; }

sub isDefault { return $_[0]->origin eq 'default'; }
sub isPropagated { $_[0]->isDefault or $_[0]->propagated; }
sub isUnknown { ($_[0]->timemlRel) ? ($_[0]->timemlRel eq 'UNKNOWN') : 0; }
		
sub containsDCT {
	my $self = shift;
	if ($self->graph->DCT) {
		if ( $self->node1->name eq $self->graph->DCT) { return 1; }
		if ( $self->node2->name eq $self->graph->DCT) { return 1; }}
	return 0; }

sub addHistory {
	my ($self,$historyElement) = @_;
	push @{ $self->history() }, $historyElement; }

# Reaffirmation inserts self into the edges table, this is done when a
# default edge receives a specific relation type.
sub reaffirm {
	my $self = $_[0];
	$self->graph->{$self->node1->name}{$self->node2->name} = $self; }

# cleanup by cleaning the history
sub cleanup {
	my $self = shift;
	$self->{_node1} = undef;
	$self->{_node2} = undef;
	$self->{_graph} = undef;
	foreach my $he (@{$self->history}) { $he->cleanup; }
	$self->{_history} = []; }


# WEIGHTS FOR SORTING
# -------------------

# Count all edges to node1 and all edges from node2, but do not
# include edges that are completely unspecified (that is, default
# edges and unknown edges).
sub scoreCount {
	my $self = $_[0];
	my $inlinks = scalar $self->node1->nonEmptyEdgesTo;
	my $outlinks = scalar $self->node2->nonEmptyEdgesFrom;
	$self->setWeight($inlinks + $outlinks);
	return $inlinks + $outlinks; }

# Count the weights on all non-trivial edges to node1 and from
# node2. Weights reflect the number of non-trivial edges that could be
# derived with the edge as the incoming or outgoing edge.
sub scoreWeight1 {
	my $self = $_[0];
	my ($scoreIn,$scoreOut) = (0,0);
	foreach my $in ( $self->node1->nonEmptyEdgesTo ) {
		$scoreIn += $self->graph->cardinality1->{_in}{$in->basicRels}; }
	foreach my $out ( $self->node2->nonEmptyEdgesFrom ) {
		$scoreOut += $self->graph->cardinality1->{_out}{$out->basicRels}; }
	$self->setWeight($scoreIn + $scoreOut);
	return $scoreIn + $scoreOut; }

# Like scoreWeight1, but weights depend on cardinality of the composed
# relations.
sub scoreWeight2 {
	my $self = $_[0];
	my ($scoreIn,$scoreOut) = (0,0);
	foreach my $in ( $self->node1->nonEmptyEdgesTo ) {
		$scoreIn += $self->graph->cardinality2->{_in}{$in->basicRels}; }
	foreach my $out ( $self->node2->nonEmptyEdgesFrom ) {
		$scoreOut += $self->graph->cardinality2->{_out}{$out->basicRels}; }
	$self->setWeight($scoreIn + $scoreOut);
	return $scoreIn + $scoreOut; }

	
# CLOSURE
# -------

sub propagateConstraints
{
	my $self = $_[0];

	# Do nothing if constraint was already propagated or if the
	# constraint is the unspecified relation (which occurs only on the
	# links marked default).
	return 1 if $self->propagated;
	$self->setPropagated(1);
	return 1 if $self->isDefault;
	#$self->print_me;	
	my $node_i = $self->node1;
	my $node_j = $self->node2;
    return unless ($node_i and $node_j);      
	#$node_j->print_me;	
	$self->dribble1($node_i,$node_j);

	foreach my $edge_k_i (values %{ $node_i->edgesTo }) {
		$self->propagateConstraint($edge_k_i,$self); }
	foreach my $edge_j_k (values %{ $node_j->edgesFrom }) {
		$self->propagateConstraint($self,$edge_j_k); }
}


sub propagateConstraint
{
	my ($self,$edge1,$edge2) = @_;

	return if $self->doNotPropagate($edge1,$edge2);
	my $node1 = $edge1->node1;
	my $node2 = $edge2->node2;
	my $edge3 = $self->graph->edgeAt($node1->name,$node2->name);
	$self->dribble2($edge1);

	# get the two relationtypes/constraints and get the composition,
	# abort if there is none (this resulted in huge time savings
	# compared to the composition operator return the unspecifiedRel)
	my $rel1 = $edge1->basicRels;
	my $rel2 = $edge2->basicRels;
	my $composedrel = $self->graph->compose($rel1,$rel2);
	return if not defined $composedrel;

	# intersect the composition with the existing relation
	my $relold = $edge3->basicRels;
	my $relnew = RelationType::intersectBasicRels($relold,$composedrel);
	$relnew = RelationType::sortRels($relnew);
	$self->dribble3($rel1,$rel2,$relold,$composedrel,$relnew);

	# check the new relation and how it compares to the old one
	if ($relnew eq '') {
		$self->closureInconsistency($edge1,$edge2,$edge3,$relold,$composedrel,$relnew); }
	elsif ($relnew eq $relold) {
		$self->closurePass(); }
	elsif ($relnew ne $relold) {
		$self->closureAddConstraint($edge1,$edge2,$edge3,$relold,$composedrel,$relnew); }
}

# Do not propagate if one of the edges is undefined (does that happen
# and, if so, why does that happen?) or if one of the edges is a
# default edge. May want to add check for the unknown relation. Also
# avoid checking i-j-i, which may cause a loop.
sub doNotPropagate {
	my ($self,$edge1,$edge2) = @_;
	return 1 if not defined $edge1;
	return 1 if not defined $edge2;
	return 1 if $edge1->isDefault;
	return 1 if $edge2->isDefault;
	#print "\n";
	#$edge1->print_me; print "\n";
	#$edge2->print_me; print "\n";
	#print $edge1->node1; print "\n";
	#print $edge2->node2; print "\n";
	return 1 if $edge1->node1->name eq $edge2->node2->name;
	return 0; }

sub closureInconsistency {
	my ($self,$edge1,$edge2,$edge3,$oldrel,$composedrel,$newrel) = @_;
	$self->graph->setInconsistencyFound(1);
	if (1) {
		#print "  **** INCONSISTENCY ****\n"; 
	}
	else {
		my $file = $self->graph->file;
		print "\n\n**** INCONSISTENCY in $file ****\n\n";
		print "#{$oldrel}\n";
		my $s1 = $edge3->node1->source->sentid;
		my $s2 = $edge3->node2->source->sentid ;
		print $edge3->asString(3), " \t($s1-$s2)\n\n";
		print "#{$composedrel}\n";
		$s1 = $edge1->node1->source->sentid;
		$s2 = $edge1->node2->source->sentid ;
		print $edge1->asString(3), " \t($s1-$s2)\n";
		$s1 = $edge2->node1->source->sentid;
		$s2 = $edge2->node2->source->sentid ;
		print $edge2->asString(3), " \t($s1-$s2)\n\n";
		$edge3->printWithHistory(0);
		$edge1->printWithHistory(0);
		$edge2->printWithHistory(0);
		print "\n"; }}

sub closurePass {
	if ($debugClosure) { print "         DOING NOTHING\n"; }}

sub closureAddConstraint {
	my ($self,$edge1,$edge2,$edge3,$oldrel,$composedrel,$newrel) = @_;
	if ($debugClosure) {
		print "         ADDING CONSTRAINT\n";
		print "            "; $edge3->print_me(); print " ==> "; }
	$edge3->setBasicRels($newrel);
	$edge3->setOrigin('closure');
	my $composition = '{' . $edge1->basicRels() . '} & {' . $edge2->basicRels() . "} => {$composedrel}";
	$edge3->addHistory(HistoryElement->new("{$oldrel}", $composition, $edge1, $edge2));
	if ($debugClosure) { $edge3->print_me(); print "\n"; } }



# DEBUGGING & PRINTING
# --------------------

sub dribble1 {
	my ($self,$node_i,$node_j) = @_;
	if ($debugClosure) {			
		print "\n", $self->asString(), "\n"; }}
		#print "  ", $node_i->asString(), " - ", $node_j->asString(), "\n"; }}

sub dribble2 {
	my ($self,$edge) = @_;
	if ($debugClosure) {
		print '    k_i: ', $edge->asString, "\n"; }}

sub dribble3 {
	my ($self,$rel1,$rel2,$oldrel,$composedrel,$newrel) = @_;
	my $unspec = RelationType::unspecifiedRel();
	$oldrel =~ s/$unspec/all/g;
	$composedrel =~ s/$unspec/all/g;
	$newrel =~ s/$unspec/all/g;
	$rel1 =~ s/$unspec/all/g;
	$rel2 =~ s/$unspec/all/g;
	if ($debugClosure) {
		print "         {$rel1} & {$rel2} ==> {$oldrel} INT {$composedrel} || {$newrel}\n"; }}


sub basicRelsPrintString {
	my $unspec = RelationType::unspecifiedRel;
	my $rels = $_[0]->basicRels;
	$rels =~ s/$unspec/all/g;
	return $rels;  }

sub asString {
	my ($self,$indent) = @_;
	$indent ||= 0;
	$indent = ' ' x $indent;
	my $propagationMarker = $self->isPropagated ? '+' : '';
	return
        "$indent <"
        . $self->name
        . " {"
        . $self->basicRelsPrintString
        . "} {"
        . $self->timemlRel
        . "} "
        . $self->origin
        . "} "
        . $self->{_tlink}->{_origin}
        . ">$propagationMarker"; }
	
sub print_me {
    my ($self,$FH) = @_;
    unless (defined $FH) { $FH = *STDOUT; }
    print $FH $self->asString();
    print $FH "\n"; }

sub printWithHistory {
	my ($self,$indent,$FH) = @_;
	my $newindent = $indent + 4;
	$indent = ' ' x $indent;
	unless (defined $FH) { $FH = *STDOUT; }
	my $marker = $self->origin() =~ /link/ ? '  ###' : '';
	print $FH $indent, $self->asString(), "$marker\n\n";
	foreach my $element (@{$self->history()}) {
		$element->print_me($newindent); }}

1;
