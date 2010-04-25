#!/usr/bin/perl

# Version of the merger code made for the new tarsqi code of September
# 2007. Will not work as a standalone version since it only outputs a
# list of tlinks

use Reader;
use Graph;
use Edge;
use Data::Dumper;

$debug = 0;
$runClosure = 1;
$runReduction = 1;
$compositions = 'rule_creation/compositions_short.txt';

die "Not enough arguments" if @ARGV < 2;
&processFile(@ARGV);


sub processFile 
{
    # Reads the input file and creates a graph without edges as well
    # as a separate ordered list of edges. These edges are added to
    # the graph one by one, running closure after each addition to
    # check consistency. Reduce the graph after adding the edges and
    # print the tlinks to the output.
    
    my ($infile, $outfile) = @_;

    # initialize graph and list of edges
    $graph = &setup_graph($infile, $compositions);
    @edgeList = &readLinks($infile);

    # add edges one by one, running closure after each addition to
    # ensure consistency
    &add_edges($graph, @edgeList);

    # finally, reduce the graph and print the tlinks
    &reduce_graph($graph);
    &print_tlinks_to_file($graph, $outfile);
}




sub setup_graph
{
    # read the infile with all tlinks and create a reader and a graph
    my ($infile, $compositions) = @_;
    $reader = Reader->new($infile, $compositions);
    $reader->readAnnotation();
    $reader->readCompositions();
    $graph = Graph->new($infile);
    $graph->initialize($reader);
    
    # reset the dictionary of edges (tlinks) and cleanup the reader
    $graph->{_edges} = {};
    $reader->cleanup;

    # print stats etc, note that the graph should have no edges
    $graph->pp(0,1,1) if $debug;
    print "\n>> GRAPH after initialization\n\n" if $debug;
    $graph->printStats if $debug;

    return $graph;
}


sub readLinks
{
    # Create the sorted edge list that is going to be the input to
    # the merging procedure

    my ($infile) = @_;
    @edgeList = ();

    open IN, $infile or die "Cannot open input file $infile\n";
    @lines = <IN>;
    $lines = join "\n", @lines;
    @tlinks = split /<\/TLINK>/, $lines;

    foreach $tlink (@tlinks) {
        next unless $tlink =~ /TLINK/;
        $tlink =~ s/.*<TLINK/<TLINK/;
        print $tlink . "\n" if $debug;
        $tlink = TLink->from_opening_tag($tlink);
        #print Dumper($tlink);
        $e1 = Edge->new($graph,'tlink',$tlink);
        $e2 = Edge->new($graph,'tlinki',$tlink);
        #print $e1 . ' ' . $e2 . "\n";
        if ($e1 and $e2) {
            #print STDERR "e1: $e1 $tlink\n";
            #print STDERR Dumper($tlink);
            $e1->setOrigin($tlink->{_origin});
            $e2->setOrigin($tlink->{_origin} . ' i');
            push @edgeList, $e1;
            push @edgeList, $e2;
        }
    }

    # sort the list of tlinks on confidence score
    @edgeList = &sortEdges(@edgeList);

    &printEdges(@edgeList) if $debug;

    return @edgeList;
}




sub sortEdges
{
    @array = @_;
    return sort { $b->confidence() cmp $a->confidence() } @array;
}

sub printEdges
{
    my @edgeList = @_;
    print "EDGES: \n";
    my $count = 0;
    foreach my $edge (@edgeList) {
	$count++;
	print '  ', $count, ' ', $edge->confidence();
	$edge->print_me;
    }
}



sub add_edges
{
    my ($graph, @edgeList) = @_;
    $restore_debug = 0;
    
    # add edges one by one, running closure after each addition to
    # ensure consistency
    print "\n>> GRAPH adding edges\n\n" if $debug;
    foreach $edge (@edgeList) 
    {
        if ($debug) { print ' '; $edge->print_me(); } 
        last if $edge->confidence < 0.95;
        $comparison = $graph->characterizeNewEdge($edge);
        next if $comparison eq 'equal';
        next if $comparison eq 'inconsistent';
        $graph->storeState();
        if ($restore_debug) { print "   1 "; $graph->printStats; }
        $graph->addEdge($edge);
        if ($restore_debug) { print "   2 "; $graph->printStats; }
        $graph->closeMe();
        if ($restore_debug) { print "   3 "; $graph->printStats; }
        if ($graph->inconsistencyFound()) {
            $graph->restoreState();
            if ($restore_debug) { print "   4 "; $graph->printStats; }
        }
    }
    
    if ($debug) { print "\n"; $graph->printStats; $graph->pp(0,0,1); }
}





sub reduce_graph
{
    my $graph = shift;
    $graph->reduce;
    if ($debug) {
        print "\n>> GRAPH reduction\n\n";
        $graph->printStats; $graph->pp(0,0,1); }
}


sub print_tlinks_to_file
{
    my ($graph, $outfile) = @_;
    open OUT, "> $outfile" or die;
    print OUT "<TLINKS>\n";
    $edgesHash = $graph->edges;
    foreach my $id1 (keys %$edgesHash) {
        foreach my $id2 (keys %{ $edgesHash->{$id1} }) {
	    my $edge = $edgesHash->{$id1}{$id2};
	    my $tlink = $edge->asTlink;
            #print Dumper $tlink;
            print OUT "<TLINK";
            foreach $att (keys %{ $tlink->[1] }) {
                print OUT ' ' . $att . '="' . $tlink->[1]{$att} . '"';
            }
            print OUT "/>\n";
        }
    }
    print OUT "</TLINKS>\n";
}    
