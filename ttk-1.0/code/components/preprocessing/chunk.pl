#!/usr/bin/perl

# ==================================================================
#  chunk.pl
# ==================================================================
#
#  Simple (and simplistic) chunker that takes tokenized and tagged
#  input (using Penn treebank tags) in one-sentence per line format,
#  and adds NG and VG chunks. It prints output to the standard output.
#
#  Usage
#
#    perl chunk.pl <input_file>
#
#  Example 
#
#    I/PP see/VBP dead/JJ people/NNS ./.
#    <NG>I/PP</NG> <VG>see/VBP</VG> <NG>dead/JJ people/NNS</NG> ./.
#
#  Wishlist:
#  - add adjective and adverb tags
#  - allow input with <s> and <lex> tags
#
#  Author:
#   Marc Verhagen
#   Brandeis University, May 2006
#   marc@cs.brandeis.edu
#
# ===================================================================

#use Data::Dumper;

$debug = 0;

# Removed CC from NP tags. Will incorrectly chunk "JJ CC JJ NN". May
# want to add it back in and deal with [NN and NN] by splitting it.
# Also removed DT, so "DT NN DT NN" is not one chunk, we could now
# miss things like "DT DT NN" (if they exist).

@beginsNP = qw( DT PRP$ CD JJ JJR JJS VBG NN NNS NNP NNPS VBN );
@inNP = qw( PRP$ EX CD JJ JJR JJS NN NNP NNPS NNS VBG VBN );
@endsNP = qw( NN NNS NNP NNPS );

@beginsVP = qw( TO MD VB VBD VBN VBP VBG VBZ );
@inVP = qw( RB RP VB VBD VBG VBN VBP VBZ );
@endsVP = qw ( VB VBD VBP VBG VBN VBZ );


# The following two are not yet used. 
$NP_ORDER = [['DT','PRP$'], 
             ['CD', 'JJ','JJR','JJS','CC','VBG','VBN'],
             ['NN','NNS','NNP','NNPS']];
$VP_ORDER = [['MD','RB','VB','VBD','VBG','VBN','VBZ'],
             ['VB','VBD','VBG','VBN', 'VBZ']];


my $startIndex;
my $endIndex;
my $startedNP;
my $startedVP;
my $closedNP;
my $closedVP;

my @sentence;

&readLists();

while (<>) 
{
    next if /^\#/;
    @sentence = split;
    &initTags($#sentence);

    $index = 0;
    while ($index <= $#sentence) 
    {
        $tag = &getTag($index,\@sentence);
        print STDERR "$index:$pair\n" if $debug;
        
        if ($beginsNP{$tag}) {
            $newIndex = &readConstituent('NP', $index);
            if ($newIndex > $index) {
                $index = $newIndex;
                next; }
        }

        if ($beginsVP{$tag}) {
            $newIndex = &readConstituent('VP', $index);
            if ($newIndex > $index) {
                $index = $newIndex;
                next; }
        }

        if ($tag eq 'PRP' or $tag eq 'PP') {
            &setTags('NP', $index, $index);
            print STDERR "  standalone PRP/PP tag\n" if $debug;
            $index++;
            next;
        } 

        $index++;
    }

    &importChunks();
    &fixCommonErrors();
    &printChunks();

    if ($debug) {
        print STDERR "\n\@npOpen = @npOpen\n";
        print STDERR "\@npClose = @npClose\n";
        print STDERR "\@vpOpen = @vpOpen\n";
        print STDERR "\@vpClose = @vpClose\n";
        print STDERR "\@sentence = @sentence\n\n";
    }
}


sub readConstituent
{
    # Read constituent of class $class, starting at index
    # $index. Returns $index if no constituent could be read, returns
    # the index after the end of the consitutent otherwise.
    
    my ($class, $index) = @_;
    my ($beginIndex, $endIndex, $pair, $tag);

    print STDERR "  $index started $class\n" if $debug;

    # store first index of consitituent and get tag
    $beginIndex = $index;  
    $tag = &getTag($index,\@sentence);

    # check whether current tag can end the constituent
    if (&endingTag($class, $tag)) {
        $endIndex = $index;
        print STDERR "  $index can end $class\n" if $debug;
    }

    # skip first token (we already know it starts a constituent of
    # class $class) and get new tag
    $index++;
    $tag = &getTag($index,\@sentence);
    
    while (&constituentTag($class, $tag)) {
        print STDERR "  $index in $class\n" if $debug;
        if (&endingTag($class, $tag)) {
            $endIndex = $index;
            print STDERR "  $index can end $class\n" if $debug;
        }
        # move to next tag
        $index++;
        $tag = &getTag($index,\@sentence);
    }

    if (defined $endIndex) {
        # constituent found, set tags and return index after end
        &setTags($class, $beginIndex, $endIndex);
        return $endIndex + 1;
    } else {
        # no constituent found, return first index
        return $beginIndex;
    }
}


sub constituentTag
{
    # Check whether tag $tag can occur inside a constituent of class
    # $class.

    my ($class, $tag) = @_;
    if ($class eq 'NP') {
        return $inNP{$tag};
    } elsif ($class eq 'VP') {
        return $inVP{$tag};
    } else {
        print STDERR "Warning (constituenTag): unknown tag class $class\n";
    }

}

sub endingTag
{
    my ($class, $tag) = @_;
    if ($class eq 'NP') {
        return $endsNP{$tag};
    } elsif ($class eq 'VP') {
        return $endsVP{$tag};
    } else {
        print STDERR "Warning (endingTag): unknown tag class $class\n";
    }
}


sub setTags
{
    my ($class, $beginIndex, $endIndex) = @_;
    if ($class eq 'NP') {
        $npOpen[$beginIndex] = '<NG>';
        $npClose[$endIndex] = '</NG>';
    } elsif ($class eq 'VP') {
        $vpOpen[$beginIndex] = '<VG>';
        $vpClose[$endIndex] = '</VG>';
    } else {
        print STDERR "Warning (setTags): unknown tag class $class\n";
    }
}


sub getTag
{
    my ($index, $sentence) = @_;
    my $pair = $sentence->[$index];
    $pair =~ /\/(\S+)$/;
    my $tag = $1;
    return $tag;
}


sub initTags 
{
    my $i = shift;
    foreach $i (0 .. $i) {
        $npOpen[$i] = '-';
        $npClose[$i] = '-';
        $vpOpen[$i] = '-';
        $vpClose[$i] = '-';
    }
}


sub readLists
{
    # Create hashes from list with definition of VP and NP tags

    foreach $x (@inNP) { $inNP{$x}++; }
    foreach $x (@beginsNP) { $beginsNP{$x}++; }
    foreach $x (@endsNP) { $endsNP{$x}++; }
    foreach $x (@inVP) { $inVP{$x}++; }
    foreach $x (@beginsVP) { $beginsVP{$x}++; }
    foreach $x (@endsVP) { $endsVP{$x}++; }
}


sub importChunks
{
    @chunkedSentence = ();    $npChunk = 0;
    $vpChunk = 0;

    foreach $i (0..$#sentence) 
    {
        if ($npOpen[$i] ne '-') {
            $npChunk = 1;
            @currentNP = ($sentence[$i]);
            if ($npClose[$i] ne '-') {
                $npChunk = 0;
                &addChunk('NG', @currentNP);
            }
        } 

        elsif ($npClose[$i] ne '-') {
            $npChunk = 0;
            push @currentNP, $sentence[$i];
            &addChunk('NG', @currentNP);
        }

        elsif ($vpOpen[$i] ne '-') {
            $vpChunk = 1;
            @currentVP = ($sentence[$i]);
            if ($vpClose[$i] ne '-') {
                $vpChunk = 0;
                &addChunk('VG', @currentVP);
            }
        }

        elsif ($vpClose[$i] ne '-') {
            $vpChunk = 0;
            push @currentVP, $sentence[$i];
            &addChunk('VG', @currentVP);
        }

        elsif ($npChunk) {
            push @currentNP, $sentence[$i];
        }

        elsif ($vpChunk) {
            push @currentVP, $sentence[$i];
        }

        else {
            push @chunkedSentence, ['lex', [$sentence[$i]]];
        }
        
    }
}


sub addChunk
{
    my ($class, @chunk) = @_;
    push @chunkedSentence, [$class, \@chunk];
}


sub printChunks
{
    foreach $i (0..$#chunkedSentence) {
        my $chunk = $chunkedSentence[$i];
        my $tag = $chunk->[0];
        my @tokens = @{$chunk->[1]};
        if ($tag eq 'lex') {
            print "$tokens[0] ";
        } else {
            print "<$tag>";
            foreach $j (0..$#tokens-1) {
                print "$tokens[$j] ";
            }
            print "$tokens[$#tokens]</$tag> ";
        }
    }
    print  "\n\n";
}



sub fixCommonErrors
{
    # Phase 2 of processing. Fix some common errors.

    &fixVBGs();

    # other candidates:
    #
    #   [DT NN DT NN] ==> [DT NN] [DT NN]
    #   (not needed any more, DT is never inside an NG)
    #
    #   [VBD VBD]==> [VBD] [VBD]
    #
    #   [DT NNP NNP CC DT NNP NNP NNP] ==> [DT NNP NN]P CC [DT NNP NNP NNP]
    #   eg: the World Bank and the International Monetary Fund
    #   (not needed anymore, a CC is never in an NG)
}


sub fixVBGs
{
    # Is a VBG and adjective or a gerund? This is to rewrite sequences like 
    # "[see/VBP sleeping/VBG] [men/NNS]" into "[see/VBP] [sleeping/VBG men/NNS]"

    my @matches = &findVBGs();
    foreach my $match (@matches) {
        &moveVBGfromVBtoNG($match->[0], $match->[1]);
    }
}


sub findVBGs
{
    # Find all occurrences of VGs followed by NGs where: (i) the VG
    # ends in VBG, (ii) the NG starts with one of NN, NNS, NNP, NNPS,
    # and (iii) the verb before the VBG is not a form of "be".
    
    my $BE = "(be)|(is)|(was)|(are)|(am)";
    my @matchingChunks = ();

    foreach $i (0..$#chunkedSentence - 1)
    {
        $j = $i + 1;
        $chunk = $chunkedSentence[$i];
        $nextChunk = $chunkedSentence[$j];

        # check chunk class
        $chunkTag = $chunk->[0];
        $nextChunkTag = $nextChunk->[0];
        next unless $chunkTag eq 'VG' and $nextChunkTag eq 'NG';

        @chunkTokens = @{$chunk->[1]};
        $lastOfChunk = $chunkTokens[$#chunkTokens];
        @nextChunkTokens = @{$nextChunk->[1]};
        $firstOfNextChunk = $nextChunkTokens[0];

        # check tokens in chunk
        if ($lastOfChunk =~ /VBG/ and
            $firstOfNextChunk =~ /(NNS?)|(NNPS?)/)
        {
            # skip forms of be
            $tokenBeforeVBG = $chunkTokens[$#chunkTokens-1];
            if ($tokenBeforeVBG) {
                if ($tokenBeforeVBG =~ /^$BE/) {
                    next; }}
            
            #print STDERR "  CHUNK $i: @chunkTokens\n";
            #print STDERR "  NEXT $j:  @nextChunkTokens\n\n";
            push @matchingChunks, [$i,$j];
        }
    }

    #print STDERR Dumper(\@matchingChunks);
    return @matchingChunks;
}


sub moveVBGfromVBtoNG
{
    my ($i, $j) = @_;
    my @chunk1 = @{$chunkedSentence[$i]->[1]};
    my @chunk2 = @{$chunkedSentence[$j]->[1]};

    $vbg = pop @chunk1;
    unshift @chunk2, $vbg;
    #print STDERR "  MOVING $vbg\n";
    #print STDERR "  @chunk1\n";
    #print STDERR "  @chunk2\n";

    $chunkedSentence[$i]->[1] = \@chunk1;
    $chunkedSentence[$j]->[1] = \@chunk2;
}
