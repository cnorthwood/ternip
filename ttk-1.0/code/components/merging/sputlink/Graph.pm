package Graph;
use strict;

use Node;
use Edge;
use RelationType;
use Statistics;
use Set;

use Data::Dumper;

my $debugClosure = 0;


# GRAPH CREATION AND INITIALIZATION
# ---------------------------------

sub new {
    my ($class,$file) = @_;
    my $objref = { 
	_file => $file,
	_nodes => {},			# nodeID -> Node
	_edges => {},			# nodeID x nodeID -> Edge
	_table => {},			# rel x rel -> rel
	_doc => {},			# sentid -> Sentence
	_sentences => {},		# sentid -> list of nodeids
	#_nodelist => [],		# list of nodeids, sorted on text occurrence
	_DCT => undef,			# undef or string (a tid)
	_inconsistencyFound => 0,	# 0 or 1
	_simplePrecedenceAxioms => {},
	_simpleInclusionsAxioms => {} };
    bless $objref, $class; 
}


sub initialize 
{
    my ($self,$reader) = @_;
    $self->{_table} = $reader->table;
    $self->{_doc} = $reader->sentences;
    $self->initializeNodes($reader);
    $self->initializeEdges($reader);

    $self->{_in_nj_ij_axioms}->{'<'}{'<'} = '<';
    $self->{_in_nj_ij_axioms}->{'<'}{'m'} = '<';
    $self->{_in_nj_ij_axioms}->{'m'}{'<'} = '<';
    $self->{_in_nj_ij_axioms}->{'m'}{'m'} = '<';

    $self->{_in_nj_ij_axioms}->{'<'}{'di'} = '<';
    $self->{_in_nj_ij_axioms}->{'<'}{'si'} = '<';
    $self->{_in_nj_ij_axioms}->{'<'}{'fi'} = '<';
    $self->{_in_nj_ij_axioms}->{'m'}{'di'} = '<';
    $self->{_in_nj_ij_axioms}->{'m'}{'si'} = 'm';
    $self->{_in_nj_ij_axioms}->{'m'}{'fi'} = '<';

    $self->{_in_nj_ij_axioms}->{'di'}{'di'} = 'di';
    $self->{_in_nj_ij_axioms}->{'di'}{'si'} = 'di';
    $self->{_in_nj_ij_axioms}->{'di'}{'fi'} = 'di';
    $self->{_in_nj_ij_axioms}->{'si'}{'di'} = 'di';
    $self->{_in_nj_ij_axioms}->{'si'}{'si'} = 'si';
    $self->{_in_nj_ij_axioms}->{'si'}{'fi'} = 'di';
    $self->{_in_nj_ij_axioms}->{'fi'}{'di'} = 'di';
    $self->{_in_nj_ij_axioms}->{'fi'}{'si'} = 'di';
    $self->{_in_nj_ij_axioms}->{'fi'}{'fi'} = 'fi';

    $self->{_ni_nj_ij_axioms}->{'di'}{'<'} = '<';
    $self->{_ni_nj_ij_axioms}->{'fi'}{'<'} = '<';
    $self->{_ni_nj_ij_axioms}->{'si'}{'<'} = '<';
    $self->{_ni_nj_ij_axioms}->{'di'}{'m'} = '<';
    $self->{_ni_nj_ij_axioms}->{'fi'}{'m'} = '<';
    $self->{_ni_nj_ij_axioms}->{'si'}{'m'} = 'm';
}

sub initializeNodes { # also add them to the sentences hash
	my ($self,$reader) = @_;
	foreach my $event (values %{$reader->events}, values %{$reader->timexes}) {
		my $id = $event->id;
		my $node = Node->new($self,$event);
		$self->nodes->{$id} = $node;
		# add node to sentences hash
		push @{ $self->sentences->{$event->sentid} }, $id;
		# set the document creation time, if any
		if ($node->source->funInDoc eq 'CREATION_TIME') { $self->setDCT($id); }}
	# make sure that all sentences occur in the table, even if they
	# have no events or timexes in them
	foreach my $i (1 .. $self->sentenceCount) {
		unless ($self->sentences->{$i}) { $self->sentences->{$i} = []; }}
}

sub initializeEdges {
	my ($self,$reader) = @_;
	while ( my ($nodepair,$tlink) =  each %{$reader->tlinks}) {
		$nodepair =~ /(\w+)-(\w+)/;
		# put in the edge and its reversal, check if it was there already
		if ($self->edges->{$2}{$1}) {
			warn "WARNING: two tlinks between the same two node\n"; }
		my $e1 = Edge->new($self,'tlink',$tlink);
		my $e2 = Edge->new($self,'tlinki',$tlink);
        # skip edges that failed to be created
        # (possibly a result of non-existing nodes)
        if ($e1 and $e2) {
            $self->edges->{$1}{$2} = $e1;
            $self->edges->{$2}{$1} = $e2;
        }
		#$self->edges->{$1}{$2} = Edge->new($self,'tlink',$tlink);
		#$self->edges->{$2}{$1} = Edge->new($self,'tlinki',$tlink);
    }
}



# ACCESSORS
# ---------

sub file { $_[0]->{_file} }
sub nodes { $_[0]->{_nodes} }
sub edges { $_[0]->{_edges} }
sub table { $_[0]->{_table} }
sub doc { $_[0]->{_doc} }
sub sentences { $_[0]->{_sentences} }
sub nodelist { $_[0]->{_nodelist} }
sub DCT { $_[0]->{_DCT} }
sub inconsistencyFound { $_[0]->{_inconsistencyFound} }

sub setDCT { $_[0]->{_DCT} = $_[1] }
sub setInconsistencyFound { $_[0]->{_inconsistencyFound} = $_[1] }

sub sentenceCount {
	my $self = shift;
	return (sort {$b<=>$a} keys %{$self->doc})[0]; }


# ACCESSING NODES AND EDGES
# -------------------------

sub nodeAt {
	my ($self,$nodeID) = @_;
	$self->nodes->{$nodeID}; }

# Return edge between two nodes, identified by their names.
# Create default edge between the nodes if there was none before.
sub edgeAt {
	my ($self,$id1,$id2) = @_;
	my $edge = $self->edges->{$id1}{$id2};
	unless ($edge) {
		$edge = Edge->newDefault($self,$id1,$id2);
		$self->edges->{$id1}{$id2} = $edge; }
	return $edge; }

# Return a hashref of $toNode-$edge pairs, where $edge is an Edge from
# $fromNode to $toNode. Create empty hash if there were no edges
# leaving from $fromNode.
sub edgesFrom {
	my ($self,$fromNode) = @_;
	my $hashref = $self->edges->{$fromNode};
	defined $hashref ? $hashref : {}; }

# Return a hashref of $fromNode-$edge pairs, where $edge is an Edge from
# $fromNode to $toNode.
sub edgesTo {
	my ($self,$toNode) = @_;
	my $answer = {};
	foreach my $fromNode (keys %{ $self->edges }) {
		if ($self->edges->{$fromNode}{$toNode}) {
			$answer->{$fromNode} = $self->edges->{$fromNode}{$toNode}; }}
	return $answer; }

sub allNodes {
	return sort { $a->name cmp $b->name } values %{ $_[0]->nodes }; }

sub allEdges {
	my $self = shift;
	my @answer = ();
	my $edge;
	foreach my $n1 (sort keys %{ $self->edges }) {
		foreach my $n2 (sort keys %{ $self->edges->{$n1} }) {
			next if $n1 eq $n2;
			$edge = $self->edges->{$n1}{$n2};
			if (defined $edge & not $edge->isDefault) {
				push @answer, $edge; }}}
	return @answer; }

sub allNodePairs {
	my $self = shift;
	my @answer = ();
	foreach my $n1 ($self->allNodes) {
		foreach my $n2 ($self->allNodes) {
			my $n1Name = $n1->name;
			my $n2Name = $n2->name;
			next if $n1Name eq $n2Name;
			push @answer, [$n1,$n2]; }}
	return @answer; }

# Cleanup a graph by cleaning up all edges and deleting them.
sub cleanup {
	my $self = shift;
	my ($href,$n1,$n2,$edge);
	foreach my $node (values %{ $self->nodes }) { $node->cleanup; }
	$self->{_nodes} = undef;
	while (($n1,$href) = each (%{$self->edges})) {
		while (($n2,$edge) = each (%{$self->edges->{$n1}})) {
			$edge->cleanup;
			delete $self->edges->{$n1}{$n2}; }}}

			
# CLOSURE
# -------

sub closeMe {
    my $self = $_[0];
    my $count = 0;
    #$self->print_me(0,0,0,0);
    while (not $self->isClosed) {
	$count++;
	print "\n\n", '-' x 20, "iteration $count ", '-' x 20, "\n" if $debugClosure;
	foreach my $edge ($self->allEdges) {
	    return if $self->inconsistencyFound;
	    $edge->propagateConstraints; }
	$self->pp(0,1) if $debugClosure; }
}

sub isClosed {
    my $self = $_[0];
    foreach my $edge ($self->allEdges) {
	if (not $edge->isPropagated) { return 0; }}
    return 1; 
}

# accessing the transitivity table
sub compose {
    my ($self,$rel1,$rel2) = @_;
    return $self->table->{$rel1}{$rel2}; 
}

sub characterizeNewEdge 
{
    # Compare a new edge to existing edge in graph, returns 'equal' if
    # the two are the same, 'consistent' if new edge is consistent
    # with graph and 'inconsistent' if new edge is not consistent with
    # graph. This is about local consistency, an edge could still be
    # inconsistent after closure.

    my ($self,$edge) = @_;
    my $debug = 0;
    my $name = $edge->name;
    $name =~ /(\S+)-(\S+)/;
    my ($id1, $id2) = ($1, $2);
    my $rels1 = $edge->basicRels;
    my $rels2 = $self->edgeAt($id1,$id2)->basicRels;
    if ($rels1 eq $rels2) {
	print "    {$rels1} equal {$rels2}\n" if $debug;
	return 'equal';
    } elsif (" $rels2 " =~ / $rels1 /) {
	print "    {$rels1} consistent {$rels2}\n" if $debug;
	return 'consistent';
    } else {
	print "    {$rels1} INCONSISTENT {$rels2}\n" if $debug;
	return 'inconsistent';
    }
}

sub addEdge {
    my ($self, $newEdge) = @_;
    my $name = $newEdge->name;
    $name =~ /(\S+)-(\S+)/;
    my ($id1, $id2) = ($1, $2);
    my $existingEdge = $self->edgeAt($id1, $id2);
    $existingEdge->setBasicRels($newEdge->basicRels);
    $existingEdge->setOrigin($newEdge->origin);
}


# Storing and retrieving state
# ----------------------------

sub storeState
{
    my $self = shift;
    foreach my $edge ($self->allEdges) {
	$edge->{_storedRels} = $edge->basicRels();
    }
}

sub restoreState
{
    my $self = shift;
    foreach my $edge ($self->allEdges) {
	my $storedRels = $self->{_storedRels};
	if ($storedRels) {
	    $edge->setBasicRels($edge->{_storedRels});
	} else {
	    $edge->setBasicRels(RelationType::unspecifiedRel);
	    $edge->setOrigin('default');
	}
    }
}


# Graph Reduction
# ---------------

sub reduce 
{
    my $self = shift;
    my $debug = 0;
    
    print ">> GRAPH remove disjunctions  " if $debug;
    $self->removeDisjunctions;
    $self->printStats if $debug;
    #$self->pp(0,0,1);

    print ">> GRAPH normalize edges      " if $debug;
    $self->normalizeEdges;
    $self->printStats if $debug;
    #$self->pp(0,0,1);

    print ">> GRAPH reverse closure      " if $debug;
    $self->openMe;
    #$self->pp(0,0,1);
    $self->printStats if $debug;

    print ">> GRAPH identity chains 1    " if $debug;
    $self->collapseRelsFromIdentityChains;
    $self->printStats if $debug;

    print ">> GRAPH identity chains 2    " if $debug;
    $self->collapseIdentityChains;
    $self->printStats if $debug;
}

sub removeDisjunctions
{
    my $self = shift;
    my $newEdges = {};
    foreach my $id1 (keys %{ $self->edges }) {
        foreach my $id2 (keys %{ $self->edges->{$id1} }) {
            my $edge = $self->edges->{$id1}{$id2};
            my $rel = $edge->basicRels;
            unless ($rel =~ / /) {
                $newEdges->{$id1}{$id2} = $edge; }
        }
    }
    $self->{_edges} = $newEdges;
}


sub collapseRelsFromIdentityChains
{
    my $self = shift;
    my @chains = $self->findIdentityChains;
    foreach my $chain (@chains) {
        $self->collapseRelsFromIdentityChain($chain);
    }
}

sub collapseIdentityChains
{
    my $self = shift;
    my @chains = $self->findIdentityChains;
    foreach my $chain (@chains) {
        $self->collapseIdentityChain($chain);
    }
}

sub findIdentityChains
{
    my $self = shift;
    #$self->print_ic_subgraphs;
    my @id_chains = $self->ic_findSubgraphs;
    return @id_chains;
}

sub collapseRelsFromIdentityChain
{
    my ($self, $chain) = @_;
    return if $#$chain == 0;
    my %ids = ();
    my $debug = 0;

    print "CHAIN @$chain\n" if $debug;
    my $representative = $chain->[0];
    foreach my $node (@$chain) { $ids{$node}++; }

    foreach my $node (@$chain[1..$#$chain]) 
    {
        print " $node\n" if $debug;

        foreach my $edgesHash ($self->nodeAt($node)->edgesFrom) {
            foreach my $id (keys %$edgesHash) {
                next if $ids{$id}; # node is in same chain
                $edgesHash->{$id}->print_me if $debug;
		delete $self->{_edges}{$node}{$id};
	    }
        }
        foreach my $edgesHash ($self->nodeAt($node)->edgesTo) {
            foreach my $id (keys %$edgesHash) {
                next if $ids{$id}; # node is in same chain
                $edgesHash->{$id}->print_me if $debug;
		delete $self->{_edges}{$id}{$node};
	    }
        }
    }
}


sub collapseIdentityChain
{
    my ($self, $chain) = @_;
    next if $#$chain == 0;
    my $debug = 0;
    my %pairs = ();

    print "CHAIN @$chain\n" if $debug;
    foreach my $i (0..$#$chain-1) {
        my $id1 = $chain->[$i];
        my $id2 = $chain->[$i+1];
        $pairs{"$id1:$id2"}++; }
    foreach my $id1 (@$chain) {
        foreach my $id2 (@$chain) {
	    next if $id1 eq $id2;
            my $edge = $self->{_edges}{$id1}{$id2};
            next unless $edge;
            $edge->print_me if $debug;
	    unless ($pairs{"$id1:$id2"}) {
		print "  deleting $id1:$id2\n" if $debug;
		delete $self->{_edges}{$id1}{$id2};
            }
        }
    }
}



sub normalizeEdges
{
    # Only keep the edges with relation type <, m, di, fi, si and =.
    # Includes removing all disjunctions, but in most (all?) case that
    # was already done or there were never disjunctions to begin with.

    my $self = shift;
    my $normalizedEdges = {};
    my %allowedRels = ( '<'=>1, 'm'=>1, 'di'=>1, 'fi'=>1, 'si'=>1, '='=>1 );
    foreach my $id1 (keys %{ $self->edges }) {
        foreach my $id2 (keys %{ $self->edges->{$id1} }) {
            my $edge = $self->edges->{$id1}{$id2};
            my $rel = $edge->basicRels;
            if ($allowedRels{$rel}) {
                $normalizedEdges->{$id1}{$id2} = $edge; }
        }
    }
    $self->{_edges} = $normalizedEdges;
}

sub openMe 
{
    my $self = shift;
    foreach my $id1 (keys %{ $self->edges }) {
        foreach my $id2 (keys %{ $self->edges->{$id1} }) {
            my $edge = $self->edges->{$id1}{$id2};
            if ($self->isDerivable($edge)) {
		# mark them first, so you do not delete edges that 
		# could be used to derive other edges
		$self->edges->{$id1}{$id2}{_isDeleted} = 1; }
        }
    }
    foreach my $e ($self->allEdges) {
	delete $self->{_edges}{$e->node1->name}{$e->node2->name} if $e->{_isDeleted};
    }
}


sub isDerivable 
{
    my ($self, $edge) = @_;
    my $debug = 0;
    $edge->print_me if $debug; 
    my $i = $edge->node1->id;
    my $j = $edge->node2->id;
    my $node_i = $edge->node1;
    my $node_j = $edge->node2;
    my @edges_i_n = values %{ $node_i->edgesFrom };
    my @edges_n_j = values %{ $node_j->edgesTo };
    foreach my $edge_i_n (@edges_i_n) {
        foreach my $edge_n_j (@edges_n_j) {
            if ($edge_i_n->node2->id eq $edge_n_j->node1->id) {
                my $rel1 = $edge_i_n->{_basicRels};
                my $rel2 = $edge_n_j->{_basicRels};
                my $rel3 = $edge->{_basicRels};
                if ($debug) {
                    print "  $rel1 & $rel2 ==> $rel3\n"; }
                return 0 if $rel1 eq '=' and $rel2 eq '=';
                if ($self->compose($rel1, $rel2) eq $rel3) {
                    if ($debug) {
                        print "  $rel3 is derivable\n";
                        print "    "; $edge_i_n->print_me;
                        print "    "; $edge_n_j->print_me; }
                    if ($node_i->name eq $node_j->name) {
                        print "   WARNING: cycle\n";
                    }
                    return 1;
                }
            }
        }
    }    
    return 0;
}


sub isDerivable
{
    my ($self, $edge) = @_;
    my $debug = 0;
    $edge->print_me if $debug; 

    my $i = $edge->node1->name;
    my $j = $edge->node2->name;
    my $rel = $edge->{_basicRels};
    return 0 if $rel eq '=';

    my ($node, $n, $edge1, $edge2, $rel1, $rel2);

    foreach $node ($self->allNodes) 
    {
	$n = $node->name;

	# Rin & Rnj -> Rij
	$edge1 = $self->{_edges}{$i}{$n};
	$edge2 = $self->{_edges}{$n}{$j};
	if ($edge1 and $edge2) {
	    if ($debug) {
		print " "; $edge1->print_me;
		print " "; $edge2->print_me; }
	    $rel1 = $edge1->{_basicRels};
	    $rel2 = $edge2->{_basicRels};
	    return 1 if $self->{_in_nj_ij_axioms}{$rel1}{$rel2} eq $rel;
	}

	# Rni & Rnj -> Rij
	$edge1 = $self->{_edges}{$n}{$i};
	$edge2 = $self->{_edges}{$n}{$j};
	if ($edge1 and $edge2) {
	    if ($debug) {
		print " "; $edge1->print_me;
		print " "; $edge2->print_me; }
	    $rel1 = $edge1->{_basicRels};
	    $rel2 = $edge2->{_basicRels};
	    return 1 if $self->{_ni_nj_ij_axioms}{$rel1}{$rel2} eq $rel;
	}
    }

    return 0;
}



# Identity Chains
# ---------------

sub ic_dfs {
    my ($self,$nodeName,$subgraph) = @_;
    unless ($subgraph->{$nodeName}) {
	$subgraph->{$nodeName} = 1;
	my $edgesHash = $self->edgesFrom($nodeName);
	foreach my $n (keys %$edgesHash) {
            #$edgesHash->{$n}->print_me;
	    # skip empty default edges and unknown edges
	    next if $edgesHash->{$n}->isDefault;
	    next if $edgesHash->{$n}->isUnknown;
            # only follow = links
            next unless $edgesHash->{$n}->{_basicRels} eq '=';
	    $self->ic_dfs($n,$subgraph); }}
    return $subgraph; 
}

sub ic_findSubgraphs {
    my $self = shift;
    my @subgraphs = ();
    my $nodes = Set->new('name',$self->allNodes);
    while ($nodes->notEmpty) {
	my $node = $nodes->pop;
	my @subgraph = keys %{ $self->ic_dfs($node->name,{}) };
	foreach my $element (@subgraph) {
	    $nodes->delete($element); }
	push @subgraphs, \@subgraph; }
    return @subgraphs; 
}


# Subgraphs
# ---------

sub dfs {
	my ($self,$nodeName,$subgraph) = @_;
	unless ($subgraph->{$nodeName}) {
		$subgraph->{$nodeName} = 1;
		my $edgesHash = $self->edgesFrom($nodeName);
		foreach my $n (keys %$edgesHash) {
			# skip empty default edges and unknown edges
			next if $edgesHash->{$n}->isDefault;
			next if $edgesHash->{$n}->isUnknown;
			$self->dfs($n,$subgraph); 
		}
		$edgesHash = $self->edgesTo($nodeName);
		foreach my $n (keys %$edgesHash) {
			# skip empty default edges and unknown edges
			next if $edgesHash->{$n}->isDefault;
			next if $edgesHash->{$n}->isUnknown;
			$self->dfs($n,$subgraph); 
		}
	}
	return $subgraph; }

sub findSubgraphs {
	my $self = shift;
	my @subgraphs = ();
	my $nodes = Set->new('name',$self->allNodes);
	while ($nodes->notEmpty) {
		my $node = $nodes->pop;
		my @subgraph = keys %{ $self->dfs($node->name,{}) };
		foreach my $element (@subgraph) {
			$nodes->delete($element); }
		push @subgraphs, \@subgraph; }
	return @subgraphs; }

sub countSubgraphs {
	return scalar $_[0]->findSubgraphs; }

sub largestSubgraph {
	my $self = shift;
	my $max = 0;
	foreach my $sg ($self->findSubgraphs) {
		my $size = scalar @$sg;
		if ($size > $max) { $max = $size; }}
	return $max; }


		
# DEBUGGING & PRINTING
# --------------------

sub dribble1 {
	my ($self,$edge,$rel) = @_;
	my $node1 = $edge->node1;
	my $node2 = $edge->node2;
	print "\n", uc $node1->text, '  {', $edge->basicRels, '}  ', uc $node2->text;
	print "  ==>  $rel\n"; }

sub pp {
    my ($self, $printSubs, $printNodes, $printEdges) = @_;
    $self->print_me();
    $self->print_subgraphs() if $printSubs;
    $self->print_nodes() if $printNodes;
    $self->print_edges() if $printEdges;
}    

sub print_me {
	my $self = shift;
	my $filename = $self->file;
	print "\n<< TIMEML_GRAPH >> \n   DOC: $filename\n";
	if ($self->DCT) {
		print "   DCT: ", $self->nodeAt($self->DCT)->asString, "\n\n"; }}

sub print_sentences {
	my $self = shift;
	print "\nSENTENCES:\n\n";
	foreach my $id (sort {$a <=> $b} keys %{ $self->sentences }) {
		my $num = ($id eq '**nil**') ? 0 : $id;
		print "  $num: ", join(' ', @{$self->sentences->{$id}}), "\n"; }
	print "\n"; }
		
sub print_nodes {
	my $self = shift;
	print "   NODES:\n";
	my $nodecount = 0;
	foreach my $id ( sort keys %{$self->nodes}) {
		$nodecount++;
		printf "    %3d  ", $nodecount;
		$self->nodes()->{$id}->print_me(); }
    print "\n"; }

sub print_edges {
	my $self = shift;
	print "   EDGES:\n";
	my $edgecount = 0;
	foreach my $id1 ( sort keys %{$self->edges}) {
		foreach my $id2 ( sort keys %{ $self->edges()->{$id1} }) {
			my $edge = $self->edges()->{$id1}{$id2};
			next if $edge->isDefault();
			$edgecount++;
			printf "   %4d  %s\n", $edgecount, $edge->asString(); }}
			#foreach my $element (@{$edge->history()}) {
			#	print "          ", $element->asString(), "\n"; }
    print "\n"; }

sub print_subgraphs {
	my $self = shift;
    print "   SUBGRAPHS:\n";
    my @subgraphs = $self->findSubgraphs;
    foreach my $sg (@subgraphs) {
        print "      {" . (join ' ', sort @$sg), "}\n"; }
    print "\n"; }

sub print_ic_subgraphs {
	my $self = shift;
    print "   SUBGRAPHS:\n";
    my @subgraphs = $self->ic_findSubgraphs;
    foreach my $sg (@subgraphs) {
        print "      {" . (join ' ', sort @$sg), "}\n"; }
    print "\n"; }

sub print_table {
	my $self = shift;
	print "\nTABLE:\n";
	foreach my $l1 (keys %{ $self->table() }) {
		foreach my $l2 (keys %{ $self->table()->{$l1} }) {
			my $r = $self->table()->{$l1}{$l2};
			printf "%-27s   &    %-27s   ==>    %-s\n", ($l1,$l2,$r); }}}

sub printStats {
    my $self = shift;
    my $stats = Statistics->new($self);
    $stats->computeBasicStats;
    print "  ";
    $stats->printBasicEdgeStats;
    #$stats->print_me('   '); 
}


1;
