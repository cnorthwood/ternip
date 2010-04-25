package Statistics;
use strict;

# Statistics in this package are all for one document/graph.

sub new {
	my ($class,$graph) = @_;
	my $objref = { _linkspan => {},
				   _counts => {},
				   _graph => $graph };
	bless $objref, $class; }

sub graph { $_[0]->{_graph} }

sub cleanup { $_[0]->{_graph} = undef; }


# LINKSPAN

sub averageLinkSpan
{
	my ($self,$FH) = @_;

	# Link count, distance count and average. Numbers 1 are for all
	# links found, numbers 2 for all links except those including the
	# DCT and numbers 3 for all possible links.
	my @counts = qw( _lcount1 _dcount1 _av1 _lcount2 _dcount2 _av2 _lcount3 _dcount3 _av3 );
	foreach my $c (@counts) { $self->{_linkspan}{$c} = 0; }

	my $lspan = $self->{_linkspan};

	foreach my $edge ($self->graph->allEdges) {
		my $distance = nodeDistance($edge->node1,$edge->node2);
		$lspan->{_lcount1}++;
		$lspan->{_dcount1} += $distance;
		unless ($edge->containsDCT) {
			$lspan->{_lcount2}++;
			$lspan->{_dcount2} += $distance; }}

	# get the spans for all possible edges
	foreach my $pair ($self->graph->allNodePairs) {
		my $n1 = $pair->[0];
		my $n2 = $pair->[1];
		my $distance = nodeDistance($n1,$n2);
		$lspan->{_lcount3}++;
		$lspan->{_dcount3} += $distance; }
	
	$lspan->{_av1} = sprintf("%.2f", $lspan->{_dcount1} / $lspan->{_lcount1});
	$lspan->{_av2} = sprintf("%.2f", $lspan->{_dcount2} / $lspan->{_lcount2});
	$lspan->{_av3} = sprintf("%.2f", $lspan->{_dcount3} / $lspan->{_lcount3});
		
	# Write data to a tab delimited file
	my $sentences = $self->graph->sentenceCount;
	print $FH $self->graph->file;
	print $FH "\t$sentences";
	print $FH "\t$lspan->{_dcount1}\t$lspan->{_lcount1}\t$lspan->{_av1}";
	print $FH "\t$lspan->{_dcount2}\t$lspan->{_lcount2}\t$lspan->{_av2}";
	print $FH "\t$lspan->{_dcount3}\t$lspan->{_lcount3}\t$lspan->{_av3}\n";
}

sub nodeDistance {
	my ($node1,$node2) = @_;
	my $pos1 = $node1->source()->sentid();
	my $pos2 = $node2->source()->sentid();
	my $distance = $pos1 - $pos2;
	$distance =~ s/^-//;	# remove the sign
	return $distance; }


# BASIC STATISTICS

sub computeBasicStats
{
	my ($self,$TAB,$FIL) = @_;
	my @counts = qw( _nodesAll _edgesAll _edgesTLink _edgesGTag _edgesClassifier _edgesPrompt _edgesUnknown _edgesDefault
					 _edgesClosure _edgesClosureFine _edgesClosureCoarse );
	foreach my $c (@counts) { $self->{_counts}{$c} = 0; }
	my $cnts = $self->{_counts};
	# nodes
	foreach my $n ($self->graph->allNodes) {
		$cnts->{_nodesAll}++; }
	#subgraphs
	$cnts->{_subgraphsCount} = $self->graph->countSubgraphs;
	$cnts->{_subgraphsBiggest} = $self->graph->largestSubgraph;
	# edges
	my $nodes = $cnts->{_nodesAll};
	$cnts->{_edgesMax} = (($nodes * $nodes) - $nodes) / 2;
	foreach my $e ($self->graph->allEdges) {
		$cnts->{_edgesAll}++;
		if ($e->isUnknown) { $cnts->{_edgesUnknown}++; }
#		if ($e->origin =~ /^tlinki/) { $cnts->{_edgesTLink}++; }
		if ($e->origin =~ /^tlink/) { $cnts->{_edgesTLink}++; }
		if ($e->origin =~ /^gtag/) { $cnts->{_edgesGTag}++; }
		if ($e->origin =~ /^class/) { $cnts->{_edgesClassifier}++; }
		elsif ($e->origin =~ /^prompti/) { $cnts->{_edgesPrompt}++; }
		elsif ($e->origin =~ /^default/) { $cnts->{_edgesDefault}++; }
		elsif ($e->origin =~ /^closure/) {
			$cnts->{_edgesClosure}++;
			if ($e->basicRels =~ / /) { $cnts->{_edgesClosureFine}++; }
			else { $cnts->{_edgesClosureCoarse}++; }
		}
	}

	my $pctEdges = sprintf "%.2f%", ($cnts->{_edgesAll} / $cnts->{_edgesMax}) * 100;
	my $pctTLink = "n/a";
	my $pctGTag = "n/a";
	my $pctClass = "n/a";
	my $pctPrompt = "n/a";
	my $pctClosure = "n/a";
	if ($cnts->{_edgesAll}) {
	    $pctTLink = sprintf "%.2f%", ($cnts->{_edgesTLink} / $cnts->{_edgesAll}) * 100;
	    $pctGTag = sprintf "%.2f%", ($cnts->{_edgesGTag} / $cnts->{_edgesAll}) * 100;
	    $pctClass = sprintf "%.2f%", ($cnts->{_edgesClass} / $cnts->{_edgesAll}) * 100;
	    $pctPrompt = sprintf "%.2f%", ($cnts->{_edgesPrompt} / $cnts->{_edgesAll}) * 100;
	    $pctClosure = sprintf "%.2f%", ($cnts->{_edgesClosure} / $cnts->{_edgesAll}) * 100;
	}
	my $subgraphRatio = sprintf "%.2f", ($cnts->{_subgraphsBiggest} / $cnts->{_nodesAll});

	if ($TAB) {
		print $FIL $self->graph->file, "\n";
		#print $TAB "$cnts->{_edgesClosureFine} $cnts->{_edgesClosureCoarse} ";
		#print $TAB "$cnts->{_subgraphsCount}\t";
		print $TAB "n:$cnts->{_nodesAll}\t";
		print $TAB "sg:$cnts->{_subgraphsCount}|$cnts->{_subgraphsBiggest}|$subgraphRatio\t";
		print $TAB "t:$cnts->{_edgesTLink}\t$pctTLink\t";
		print $TAB "p:$cnts->{_edgesPrompt}\t$pctPrompt\tu:$cnts->{_edgesUnknown}\t";
		print $TAB "c:$cnts->{_edgesClosure}\t$pctClosure\te:$cnts->{_edgesAll}\t$pctEdges\tm:$cnts->{_edgesMax}\n"; }
}


# INTER-ANNOTATOR AGREEMENT

sub iaa
{
	my ($class,$graph1,$graph2) = @_;
	my $iaa = {};
	#use Data::Dump qw(dump);
	
	# First the nodes, set one to key and other to response
	# Flipping key and response is not necessary because precision and
	# recall are identical when evened out over two annotators
	
	my @keyNodes = $graph1->allNodes;
	my @responseNodes = $graph2->allNodes;
	my %keyNodes = ();
	my %responseNodes = ();
	
	foreach my $node (@keyNodes) { $keyNodes{$node->source->offset} = 1; }
	foreach my $node (@responseNodes) { $responseNodes{$node->source->offset} = 1; }

	my $matches = 0;
	foreach my $id (keys %responseNodes) {
		$matches++ if $keyNodes{$id}; }

	my $precision = sprintf "%.2f", ($matches / scalar keys %keyNodes) * 100;
	my $recall = sprintf "%.2f", ($matches / scalar keys %responseNodes) * 100;

	$iaa->{_nodes} = { _precision => $precision,
					   _recall => $recall,
					   _matches => $matches,
					   _keySize => scalar keys %keyNodes,
					   _responseSize =>  scalar keys %responseNodes };

	# Now the edges
	
	my @keyEdges = $graph1->allEdges;
	my @responseEdges = $graph2->allEdges;
	my %keyEdges = ();
	my %responseEdges = ();

	foreach my $edge (@keyEdges) {
		my $off1 = $edge->node1->source->offset;
		my $off2 = $edge->node2->source->offset;
		$keyEdges{"$off1:$off2"} = $edge; }
	foreach my $edge (@responseEdges) {
		my $off1 = $edge->node1->source->offset;
		my $off2 = $edge->node2->source->offset;
		$responseEdges{"$off1:$off2"} = $edge; }

	my $matchesEntity = 0;
	my $matchesReltype = 0;
	my ($rel1,$rel2);
	foreach my $id (keys %keyEdges) {
		if ($responseEdges{$id}) {
			$matchesEntity++;
			$rel1 = $keyEdges{$id}->timemlRel;
			$rel2 = $responseEdges{$id}->timemlRel;
			if ($rel1 eq $rel2) {
				$matchesReltype++; }
			else {
				($rel1,$rel2) = sort ($rel1,$rel2);
				$iaa->{_mismatches}{"$rel1-$rel2"}++; }}}

	#print dump($iaa->{_mismatches});
	
	my $rE = sprintf "%.2f", ($matchesEntity / scalar keys %keyEdges) * 100;
	my $pE = sprintf "%.2f", ($matchesEntity / scalar keys %responseEdges) * 100;
	my $rR = sprintf "%.2f", ($matchesReltype / scalar keys %keyEdges) * 100;
	my $pR = sprintf "%.2f", ($matchesReltype / scalar keys %responseEdges) * 100;

	$iaa->{_edges} = { _pE => $pE, _rE => $rE, _matchesE => $matchesEntity,
					   _pR => $pR, _rR => $rR, _matchesR => $matchesReltype,
					   _keySize => scalar keys %keyEdges,
					   _responseSize =>  scalar keys %responseEdges };

	return $iaa;
}



# PRINTING

sub printBasicEdgeStats {
	my $self = $_[0];
	print "Edges: t:", $self->{_counts}{_edgesTLink};
	print " + g:", $self->{_counts}{_edgesGTag};
	print " + l:", $self->{_counts}{_edgesClassifier};
	print " + c:", $self->{_counts}{_edgesClosure};
	print " + d:", $self->{_counts}{_edgesDefault};
	print " = ", $self->{_counts}{_edgesAll};
	print '   (graphs ', $self->graph->countSubgraphs, ':', $self->graph->largestSubgraph, ")\n";

}

sub print_me {
	my ($self,$indent) = @_;
	print "$indent Counts:\n";
	foreach my $key (sort keys %{$self->{_counts}}) {
		printf "%s   %-20s %4d\n", ($indent, $key, $self->{_counts}{$key}); }}

1;
