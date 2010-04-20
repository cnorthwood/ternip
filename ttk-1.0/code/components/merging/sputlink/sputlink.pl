#!/usr/bin/perl

use Reader;
use Graph;

$runClosure = 1;
$runReduction = 1;

$indir = 'DATA/IN';
$outdir = 'DATA/OUT';

$doc = 'ABC19980108.1830.0711.tml';
$doc = 'ABC19980114.1830.0611.tml';
#$doc = 'ABC19980304.1830.1636.tml';
#$doc = 'APW19980227.0489.tml';
#$doc = 'wsj_0006.tml';

$in = @ARGV ? shift @ARGV : "$indir/$doc";
$out = @ARGV ? shift @ARGV : "$outdir/$doc";

$compositions = 'rule_creation/compositions_short.txt';


if ((-d $in) and (-d $out)) { &processDir($in, $out); }
elsif (-f $in) { &processFile($in, $out); }
else { print "Warning: couldn't process $in\n"; }

sub processDir
{
    my ($indir, $outdir) = @_;
    opendir DIR, $indir or die "ERROR: cannot open directory $indir\n";
    foreach $file (readdir DIR) {
	next if $file eq 'ABC19980304.1830.1636.tml';
	next if $file eq 'APW19980213.1320.tml';
	next if $file eq 'APW19980227.0489.tml';
	&processFile("$indir/$file", "$outdir/$file") if (-f "$indir/$file");
    }
}

sub processFile 
{
    my ($infile, $outfile) = @_;
    print "$infile\n";
    my $debug = 1;
    
    $reader = Reader->new($infile, $compositions);
    $reader->readAnnotation();
    $reader->readCompositions();
    $graph = Graph->new($infile);
    $graph->initialize($reader);
    $reader->cleanup;

    $graph->pp(0,0,0) if $debug;
    print ">> GRAPH initialization       " if $debug;
    $graph->printStats if $debug;

    print ">> GRAPH closure              " if $debug;
    $graph->closeMe;
    if ($graph->inconsistencyFound) {
	print "INCONSISTENT GRAPH\n";
	return; }
    $graph->printStats if $debug;

    $graph->reduce;

    $reader->updateTLinks($graph->edges);
    $reader->printFile($outfile);
}
