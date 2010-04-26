#!/usr/bin/perl -w

# =========================================================================
#  scoreTLINKS.pl
# =========================================================================
#
#  Compare a candidate file to a reference file or all candidate files
#  in a directory to reference files in another directory. Calculate
#  precision, rcall and f-measure for the candidate file(s). 
#
#  Usage:
#
#      perl scoreFile [-(s|r)] <candidate_file> <reference_file>
#      perl scoreFile [-(s|r)] <candidate_dir> <reference_dir>
#
#      flags:
#
#         -s   use strict matching, a relation in a candidate tlink
#              matches the one in the reference tlink only if they are
#              identical, this is the default
#
#         -r   use relaxed matching, where matches are weighted
#
#  Candidate file and reference file have to be identical except for
#  the tlinks. In addition, both files can contain only one tlink per
#  line. If two directories are compared, then all files in the
#  candidate directory have to be in the reference directory.
#
#  Scores are written to standard output.
#
# =========================================================================


use strict;


my $DEBUG = 0;

### DEFINITIONS

# default setting for relation matching
my $strictMatching = 1;

# mapping of all relations to their inverses
my %REL_INVERSE = (
    'AFTER' => 'BEFORE',
    'BEFORE' => 'AFTER',
    'BEFORE-OR-OVERLAP' => 'OVERLAP-OR-AFTER',
    'OVERLAP-OR-AFTER' => 'BEFORE-OR-OVERLAP',
    'OVERLAP' => 'OVERLAP',
    'VAGUE' => 'VAGUE'
);


### MAIN LOOP

# read arguments
while ($ARGV[0] =~ /^-\w$/) { &parseOption(shift); }
my $candidateFile = shift;
my $referenceFile = shift;

# compare files or directories
if (-T $candidateFile and -T $referenceFile) {
    my $score = &scoreFile($candidateFile, $referenceFile);
    print $score;
} elsif (-d $candidateFile and -d $referenceFile) {
    my $score = &scoreDirectory($candidateFile, $referenceFile);
    print $score;
} else {
    die "INPUT ERROR: need to provide two files or two directories\n";
}


### FUNCTION DEFINITIONS

sub scoreFile
{
    # Main function that collects links, compares them, keeps score,
    # calculates P&R and dumps the results in a string which is returned.

    my ($candidateFile, $referenceFile) = @_;
    open CAN, "$candidateFile" or die "ERROR: cannot open '$candidateFile'\n";
    open REF, "$referenceFile" or die "ERROR: cannot open '$referenceFile'\n";

    my @referenceLinks = ();
    my %referenceLinks = ();
    my @candidateLinks = ();
    my %candidateLinks = ();

    while (<REF>) { &collectLink($_, \@referenceLinks, \%referenceLinks); }
    while (<CAN>) { &collectLink($_, \@candidateLinks, \%candidateLinks); }

    my $totalRef = scalar @referenceLinks;
    my $totalCan = scalar @candidateLinks;

    my $commonLinks = 0;
    my $correctLinks = 0;  # weighted sum for relaxed scoring case
    my $incorrectLinks = 0;

    foreach my $link (@candidateLinks) {
        my ($arg1, $arg2, $rel) = @$link;
        my $referenceRel = '';
        if ($referenceRel = $referenceLinks{"$arg1-$arg2"}) { ; }
        else {
            ($arg1, $arg2, $rel) = &swapArgs($arg1, $arg2, $rel);
            if ($referenceRel = $referenceLinks{"$arg1-$arg2"}) { ; }
        }
        if ($referenceRel) {
            $commonLinks++;    
            my $addToCorrect = &matchesReference($rel, $referenceRel);
            if ($DEBUG) { print STDERR "Adding to correct: $rel, $referenceRel, $addToCorrect\n"; }
            $correctLinks += $addToCorrect;
            if (! $addToCorrect) {
                if ($DEBUG) { print STDERR "Adding to incorrect\n"; }
                $incorrectLinks++;
            }
        }
    }
    
    # Compute PnR

#    my ($precision, $recall, $f) =  &calculate_PR(scalar(@candidateLinks), $correctLinks, $totalRef);
    my ($precision, $recall, $f) =  &calculate_PR($commonLinks, $correctLinks, $totalRef);
    &dumpResult($candidateFile, $referenceFile, $totalRef, $totalCan,
				$commonLinks, $correctLinks, $incorrectLinks, $precision, $recall, $f);
}

sub scoreDirectory
{
    # Like &scoreFile, but collects scores for all files in a directory

    my ($candidateDir, $referenceDir) = @_;
    opendir DIR, $candidateDir or die "ERROR: could not open '$candidateDir'\n";
    my @files = grep /^[^.]/, readdir DIR;

    my $allScores = '';
    foreach my $file (@files) {
		my $fileScore = &scoreFile("$candidateDir/$file", "$referenceDir/$file");
		$allScores .= $fileScore;
    }

    my $referenceLinks = 0;
    my $candidateLinks = 0;
    my $commonLinks = 0;
    my $correctLinks = 0;
    my $incorrectLinks = 0;

    foreach my $line (split /\n/, $allScores) {
		$referenceLinks += $1 if $line =~ / REFERENCE LINKS\s+(\d+)/;
		$candidateLinks += $1 if $line =~ / CANDIDATE LINKS\s+(\d+)/;
		$commonLinks += $1 if $line =~ / COMMON LINKS\s+(\d+)/;
		$correctLinks += $1 if $line =~ / CORRECT LINKS\s+(\d+)/;
		$incorrectLinks += $1 if $line =~ / INCORRECT LINKS\s+(\d+)/;
    }

    my ($precision, $recall, $f) =  &calculate_PR($commonLinks, $correctLinks, $referenceLinks);
    &dumpResult($candidateFile, $referenceFile, $referenceLinks, $candidateLinks,
				$commonLinks, $correctLinks, $incorrectLinks, $precision, $recall, $f);
}


sub parseOption 
{ 
    # Parse command line option, print warnings for unknown option

    my $option = shift;
    if ($option =~ /s/) {
		$strictMatching = 1; }
    elsif ($option =~ /r/) {
		$strictMatching = 0; }
    else {
		print STDERR "WARNING: ignored unknown option '$option'\n"; }
}


sub collectLink 
{
    # Pull the tlink out of a line, assumes that there is one tlink
    # per line

    my ($line, $arrayRef, $hashRef) = @_;
    if ($line =~ /(<TLINK[^>]+>)/) {
		my $tlink = $1;
		my ($arg1, $arg2, $rel) = &parseTLINK($tlink);
		$hashRef->{"$arg1-$arg2"} = $rel;
		push @$arrayRef, [$arg1, $arg2, $rel];  }
}


sub parseTLINK 
{
    # Extract the eiid or tid for both arguments of the link as well
    # as the relation type.

    my $tlink = shift;
    my ($rel, $id1, $id2);

    if ($tlink =~ /relType="([-_A-Z]+)"/) {
        $rel = $1;
    }
    if ($tlink =~ /eventID="([tei]+\d+)"/) {
        $id1 = $1;
    }
    if ($tlink =~ /relatedTo\w+="([tei]+\d+)"/) {
        $id2 = $1;
    }
    
    if ($rel and $id1 and $id2) {
        return ($id1, $id2, $rel);
    } else {
        print STDERR "WARNING: could not parse $tlink\n";
    }
}


sub matchesReference
{
    # Compare the relation type of the candidate links and the
    # reference link, return true of they match, false otherwise. Use
    # strict or relaxed matching.

    my ($rel, $referenceRel) = @_;
    if ($referenceRel eq $rel) {
        return 1;
    } else {
        if ($strictMatching) {	

            return 0;
        } else {
            
            if ( (($rel eq "BEFORE") && ($referenceRel eq "BEFORE-OR-OVERLAP")) ||
                 (($rel eq "OVERLAP") && ($referenceRel eq "BEFORE-OR-OVERLAP")) ||
                 (($rel eq "OVERLAP") && ($referenceRel eq "OVERLAP-OR-AFTER")) ||
                 (($rel eq "AFTER") && ($referenceRel eq "OVERLAP-OR-AFTER")) ||
                 (($rel eq "BEFORE-OR-OVERLAP") && ($referenceRel eq "BEFORE")) ||
                 (($rel eq "BEFORE-OR-OVERLAP") && ($referenceRel eq "OVERLAP")) ||
                 (($rel eq "BEFORE-OR-OVERLAP") && ($referenceRel eq "OVERLAP-OR-AFTER")) ||
                 (($rel eq "OVERLAP-OR-AFTER") && ($referenceRel eq "OVERLAP")) ||
                 (($rel eq "OVERLAP-OR-AFTER") && ($referenceRel eq "AFTER")) ||
                 (($rel eq "OVERLAP-OR-AFTER") && ($referenceRel eq "BEFORE-OR-OVERLAP")) )  {
                
                return 0.5;
            } 
            if ( (($rel eq "BEFORE") && ($referenceRel eq "VAGUE")) ||
                 (($rel eq "OVERLAP") && ($referenceRel eq "VAGUE")) ||
                 (($rel eq "AFTER") && ($referenceRel eq "VAGUE")) ||
                 (($rel eq "VAGUE") && ($referenceRel eq "BEFORE")) ||
                 (($rel eq "VAGUE") && ($referenceRel eq "OVERLAP")) ||
                 (($rel eq "VAGUE") && ($referenceRel eq "AFTER")) )  {
                
                return 0.33;
            } 
            if ( (($rel eq "BEFORE-OR-OVERLAP") && ($referenceRel eq "VAGUE")) ||
                 (($rel eq "OVERLAP-OR-AFTER") && ($referenceRel eq "VAGUE")) ||
                 (($rel eq "VAGUE") && ($referenceRel eq "BEFORE-OR-OVERLAP")) ||
                 (($rel eq "VAGUE") && ($referenceRel eq "OVERLAP-OR-AFTER")) )  {
                
                return 0.67;
            }
            
            return 0;
        }
    }
}


sub swapArgs 
{
    # Swap relations and give the onverse of the relation
    my ($arg1, $arg2, $rel) = @_;
    return ($arg2, $arg1, $REL_INVERSE{$rel});
}


sub calculate_PR 
{
    # Calculate precision, recall and f-measure

    my ($commonLinks, $correctLinks, $totalRef) = @_;
    my ($precision, $recall, $f);
    if ($commonLinks) {
        $precision = $correctLinks / $commonLinks; }
    if ($totalRef) {
        $recall = $correctLinks / $totalRef; }
    if ($commonLinks and $totalRef) {
        $f = $precision + $recall;
        if ($f > 0)  {
            $f = (2 * $precision * $recall) / $f;
        } else {
            $f = 0; }}
    return ($precision, $recall, $f);
}


sub dumpResult
{
    # Dump results in string and return it

    my ($candidateFile, $referenceFile, $totalRef, $totalCan,
	$commonLinks, $correctLinks, $incorrectLinks, $precision, $recall, $f) = @_;
    
    my $result = '';
    open RESULT, '>', \$result; 
    print RESULT "\n>> CANDIDATE FILE: $candidateFile";
    print RESULT "\n>> REFERENCE FILE: $referenceFile\n\n";
    printf RESULT "  REFERENCE LINKS  %5d\n", $totalRef;
    printf RESULT "  CANDIDATE LINKS  %5d\n", $totalCan;
    printf RESULT "  COMMON LINKS     %5d\n", $commonLinks;
    printf RESULT "  CORRECT LINKS    %5s\n", $strictMatching ? $correctLinks : sprintf("%.2f", $correctLinks);
    printf RESULT "  INCORRECT LINKS  %5d\n\n", $incorrectLinks;
    printf RESULT "  PRECISION  =  %s\n", &toString($precision);
    printf RESULT "  RECALL     =  %s\n", &toString($recall);
    printf RESULT "  F-MEASURE  =  %s\n\n", &toString($f);
    return $result;
}


sub toString 
{
   # Return the measure as a floating point with precision 2, if
   # undefined, return 'N/A'
    my $measure = shift;
    $measure ? return sprintf("%.3f", $measure) : return ' N/A';
}


