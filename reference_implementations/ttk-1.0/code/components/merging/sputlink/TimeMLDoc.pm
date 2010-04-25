#!/usr/bin/perl

use XML::Parser;
use TimeMLDocWriter;
use Data::Dumper;


package TimeMLDoc;

# put this one in an instance variable
$sentID = 0;


# PUBLIC METHODS-------------------------------------------------------

# constructor

# takes full filename and returns a TimeMLDoc object.
# optional second argument (boolean) turns on tokenization

sub parse {
    my $class = shift;
    my $inName = shift;
    local $tokenize = shift;
    my $self = {};

    my $parser = new XML::Parser();
    $parser->setHandlers(Start    => \&handle_start,
			 End      => \&handle_end,
			 Default  => \&handle_default,
			 XMLDecl  => \&handle_xmldecl);

    local $xmldec;
    local $root;
    local %EVENTs;
    local %TIMEX3s;
    local %SIGNALs;
    local %MAKEINSTANCEs;
    local %InstanceFromEvent;
    local @TLINKs;
    local @SLINKs;
    local @ALINKs;
    local @SYNTAXs;
    local @seeking;
    local @openedTags;
    local @DOCUMENT;
    local @FOOTER;
    local $docCounter = 0;
    local $textCounter = 0;
    local $timemlClosed;
    local $tagger;
    local $sentencizer;
    local $sentencizerTagger;
    local %SENTENCES;
    local %TOKENS;
    local $tagged;

    eval {$parse = $parser->parsefile($inName)};
    warn "WARNING: XML PARSING ERROR on file $inName $@ \n" if $@;
		
    $self->{TLINKS} = \@TLINKs;
    $self->{EVENTS} = \%EVENTs;
    $self->{TIMEXES} = \%TIMEX3s;
    $self->{SIGNALS} = \%SIGNALs;
    $self->{EVENTINSTANCES}= \%MAKEINSTANCEs;
    $self->{SLINKS} = \@SLINKs;
    $self->{ALINKS}= \@ALINKs;
    $self->{SYNTAXS}= \@SYNTAXs;
    $self->{TLINKSOURCES}= \%TLINKeiid;
    $self->{TLINKTARGS} = \%TLINKreiid;
    $self->{DOC} = \@DOCUMENT;
    $self->{TOKENS} = \%TOKENS;
    $self->{FOOTER} = \@FOOTER;
    $self->{ROOT} = $root;
    $self->{XMLDEC} = $xmldec;
    $self->{TAGGER} = $tagger;
    $self->{SENTENCIZER} = $sentencizer;
    $self->{SENTENCES} = \%SENTENCES;
    $self->{TAGGED} = $tagged;
    $self->{SENTAGGER} = $sentencizerTagger;
    $self->{INSTANCEFROMEVENT} = \%InstanceFromEvent;
    
    bless $self;
    return $self;
}


## ACCESSORS

sub document {
	my $self = shift;
	return @{ $self->{DOC} };
}

# gets the doctype declaration (no args)
sub declaration {
    my $self = shift;
    return $self->{XMLDEC};
}

# gets the root TimeML element (no args)
sub root {
    my $self = shift;
    return $self->{ROOT};
}

# These 4 return an array containing all the respective ids (no args).

sub eventIDs {
    my $self = shift;
    return keys %{ $self->{EVENTS} };
}

sub signalIDs {
    my $self = shift;
    return keys %{ $self->{SIGNALS} };
}

sub timeIDs {
    my $self = shift;
    return keys %{ $self->{TIMEXES} };
}

sub instanceIDs {
    my $self = shift;
    return keys %{ $self->{EVENTINSTANCES} };
}

# These all return an object--an array reference-- representing the
# respective elements (idString).

sub eventFromID {
    my ($self, $eid) = @_;
    return $self->{EVENTS}->{$eid};
}

sub signalFromID {
	my ($self, $sid) = @_;
    return $self->{SIGNALS}->{$sid};
}

sub timexFromID {
	my ($self, $tid) = @_;
    return $self->{TIMEXES}->{$tid};
}

sub instanceFromID {
    my ($self, $eiid) = @_;
    return $self->{EVENTINSTANCES}->{$eiid};
}

sub instanceFromEventID {
    my ($self, $eid) = @_;
    my $eiid = $self->{INSTANCEFROMEVENT}->{$eid};
    return $self->{EVENTINSTANCES}->{$eiid};
}

sub eventFromInstanceID {
    my ($self, $eiid) = @_;
    my $instance = $self->{EVENTINSTANCES}->{$eiid};
    return $self->{EVENTS}->{$instance->{'eventID'}};
}

sub eventIdFromInstanceID {
    my ($self, $eiid) = @_;
    my $e = $self->eventFromInstanceID($eiid);
    return $e->[2]{'eid'};
}

# Return an array of all links that contain an instanceID.
sub linksForInstanceID {
    my ($self, $eiid) = @_;
	my @links = ();
	foreach $link ($self->alinks(), $self->slinks(), $self->tlinks()) {
		push @links, $link if $self->linkContainsInstance($link, $eiid);
	}
	return @links;
}

sub linkContainsInstance {
    my ($self, $link, $eiid) = @_;
	my $relatedToEventInstance = $link->{'relatedToEventInstance'};
	my $subordinatedEventInstance = $link->{'subordinatedEventInstance'};
	if ($relatedToEventInstance) {
		return 1 if $relatedToEventInstance eq $eiid;
	} elsif ($subordinatedEventInstance) {
		return 1 if $link->{'subordinatedEventInstance'} eq $eiid;
	}
	return 0;
}


## REMOVING TAGS

# Remove the <EVENT> and </EVENT> tags from the DOC instance variable
# and add a __DELETED__ key to the object's attribute hash. Also
# removes an entry from the EVENTS and INSTANCEFROMEVENT hashes. Let
# removeInstanceWithID do the rest of the work.
sub removeEventWithID {
	my ($self, $eid, $log) = @_;
	my $eventObj = $self->eventFromID($eid);

	my $openingTag = $eventObj->[0];
	my $closingTag = $eventObj->[1];
	my $attrHash = $eventObj->[2];
	my $eiid = $self->{INSTANCEFROMEVENT}{$eid};

	delete $self->{DOC}[$openingTag];
	delete $self->{DOC}[$closingTag];
	$attrHash->{__DELETED__} = 1;
	delete $self->{EVENTS}->{$eid};
	delete $self->{INSTANCEFROMEVENT}{$eid};
	print "\tREMOVED EVENT ", &tagAsString($attrHash), "\n" if $log;
	$self->removeInstanceWithID($eiid, $log) if $eiid;
}

# Add a __DELETED__ key to the object's attribute hash. Also removes
# an entry from the EVENTINSTANCES hash. inally calls removeLink to
# get rid of all links that refer to the eiid.
sub removeInstanceWithID {
	my ($self, $eiid, $log) = @_;
	my $instanceObj = $self->instanceFromID($eiid);
	$instanceObj->{__DELETED__} = 1;
	delete $self->{EVENTINSTANCES}->{$eiid};
	print "\tREMOVED INSTANCE ", &tagAsString($instanceObj), "\n" if $log;
	foreach $link ($self->linksForInstanceID($eiid)) {
		$self->removeLink($link, $log); 
	}
}

# Mark a link to be deleted.
sub removeLink {
	my ($self, $link, $log) = @_;
	$link->{__DELETED__} = 1;
	print "\tREMOVED LINK ", &tagAsString($link), "\n" if $log;
}

sub tagAsString {
	my $tag = shift;
	my $str = "{ ";
	foreach my $att (keys %$tag) {
		next if $att eq '__DELETED__';
		$str .= $att . '="' . $tag->{$att} . '", ';
	}
	$str .= "}";
	return $str;
}


## Replacing tlinks with new set derived from closure and reduction

# Remove all TLINKs from the document, including the ones in the list.
sub clearTLINKs
{
    my $self = shift;
    my $firstTLINK = 0;
    my $lastTLINK = 0;
    my $currentOffset = 0;
    foreach my $docElement (@{$self->{DOC}}) {
        if (ref($docElement) eq 'ARRAY' and $docElement->[0] eq 'TLINK') {
            $firstTLINK = $currentOffset unless $firstTLINK;
            $lastTLINK = $currentOffset;
        }
        $currentOffset++;
    }
    my $size = $lastTLINK - $firstTLINK + 1;
    #print "$firstTLINK-$lastTLINK-$size\n";
    #print @{$self->{DOC}}[$firstTLINK..$lastTLINK];
    splice @{$self->{DOC}}, $firstTLINK, $size;
    $self->{TLINKS} = [];
}

sub addTLink
{
    my ($self, $tlink) = @_;
    my $insertPoint = $self->tlinkInsertPoint;
    my @doc = $self->document();
    splice(@{ $self->{DOC} }, $insertPoint, 0, ($tlink, "\n"));
}

sub tlinkInsertPoint
{
    my $self = shift;
    my @doc = $self->document;
    my $point = $#doc;
    #print $#doc;
    #print $doc[$#doc];
    while ($point >= 0) {
	my $token = $doc[$point];
	return $point if $token eq '</TimeML>';
	$point--;
    }
}



## ACCESSORS

# Return all events, without the extra information like placement in
# DOC, but with text string.
sub events {
    my $self = shift;
    my @answer = ();
    foreach $id ($self->eventIDs()) {
		$eventplus = $self->eventFromID($id);
		$event = $eventplus->[2];
		$event->{'text'} = $self->textFromElement($eventplus);
		push @answer, $event;
    }
    return @answer;
}

# ... same with timexes
sub timexes {
    my $self = shift;
    my @answer = ();
    foreach $id ($self->timeIDs()) {
		$timexplus = $self->timexFromID($id);
		$timex = $timexplus->[2];
		$timex->{'text'} = $self->textFromElement($timexplus);
		push @answer, $timex;
    }
    return @answer;
}

# ... and with signals
sub signals {
    my $self = shift;
    my @answer = ();
    foreach $id ($self->signalIDs()) {
		$signalplus = $self->signalFromID($id);
		$signal = $signalplus->[2];
		$signal->{'text'} = $self->textFromElement($signalplus);
		push @answer, $signal;
    }
    return @answer;
}

# ... and with instances
sub instances {
    my $self = shift;
    my @answer = ();
    foreach $id ($self->instanceIDs()) {
		$instance = $self->instanceFromID($id);
		push @answer, $instance;
    }
    return @answer;
}



#these all return an array of objects representing links (no args)
sub slinks {
    my $self = shift;
    return @{$self->{SLINKS}};
}

sub tlinks {
    my $self = shift;
    return @{$self->{TLINKS}};
}

sub alinks {
    my $self = shift;
    return @{$self->{ALINKS}};
}

sub links {
    my $self = shift;
	return $self->alinks(), $self->slinks(), $self->tlinks();
}


# Returns the content of any content element (elementObj). Makes sure
# that tags are skipped.
sub textFromElement {
    my $self = shift;
    my $arrayOrHashRef = shift;
    if (ref($arrayOrHashRef) eq "HASH"){
        return "THIS ELEMENT HAS NO TEXT EXTENT";
    } else {
        my $start = $arrayOrHashRef->[0];
        my $end = $arrayOrHashRef->[1];
        my $text = "";
        for ($start+1..$end-1){
            my $chunk = $self->{DOC}->[$_];
			next if $chunk =~ /^</;
			next if ref($chunk) eq 'ARRAY';
            $text .= $chunk;
        }
        return $text;
    }
}

#returns n text nodes preceding an element (elementObj, n) 
sub backContext {
    my $self = shift;
    my $arrayRef = shift;
    my $noWanted = shift;
    my $noGot;
    my $context = "";
    my $pointer = $arrayRef->[0] - 1;
    while ($noGot < $noWanted) {
        my $node = $self->{DOC}->[$pointer];
        $node =~ s/\n/ /g;
        unless ($node =~ /^<.*>$/){
            $context = $node.$context;
            $noGot++;
        }
        $pointer--;
    }
    return $context;
}

#returns n text nodes following an element (elementObj, n)
sub foreContext {
    my $self = shift;
    my $arrayRef = shift;
    my $noWanted = shift;
    my $noGot;
    my $context = "";
    my $pointer = $arrayRef->[1] + 1;
    while ($noGot < $noWanted) {
        my $node = $self->{DOC}->[$pointer];
        $node =~ s/\n/ /g;
        unless ($node =~ /^<.*>$/){
            $context = $context.$node;
            $noGot++;
        }
        $pointer++;
    }
    return $context;
}



# Prints the document to the specified filename. If no filename
# is specified, prints to standard output. Prints all tags
sub printOut
{
    my $self = shift;
    my $outName = shift;
    if ($outName) {
        open OUT, ">$outName" or die "can't open $outName for writing: $!";
    }
    my $FH = $outName ? *OUT : *STDOUT;
    my $docWriter = TimeMLDocWriter->new($self->{DOC},'max',$FH);
    $docWriter->write();
}


# Same as printOut, but prints TimeML tags only
sub printMin
{
    my $self = shift;
    my $outName = shift;
    if ($outName) {
        open OUT, ">$outName" or die "can't open $outName for writing: $!";
	}
	my $FH = $outName ? *OUT : *STDOUT;
	my $docWriter = TimeMLDocWriter->new($self->{DOC},'min',$FH);
	$docWriter->write();
}


# Same as printOut, but does not print <lex> tags
sub printNoLex
{
    my $self = shift;
    my $outName = shift;
    if ($outName) {
        open OUT, ">$outName" or die "can't open $outName for writing: $!";
	}
	my $FH = $outName ? *OUT : *STDOUT;
	my $docWriter = TimeMLDocWriter->new($self->{DOC},'no_lex',$FH);
	$docWriter->write();
}


#if tokenization was performed, returns the tokens contained
#in a content element (elementObject)
sub tokensFromElement {
    my $self = shift;
    die 'document not tokenized' unless $self->{TOKENS};
    my $arrayOrHashRef = shift;
    my $returnTags = shift;
    die 'document not tagged' if ($returnTags && !$self->{TAGGED});
    if (ref($arrayOrHashRef) eq "HASH"){
        return "THIS ELEMENT HAS NO TEXT EXTENT";
    } else {
        my $start = $arrayOrHashRef->[3];
        my $end = $arrayOrHashRef->[4];
        my @tokenArray;
        for ($start...$end){
            my $token;
            if ($returnTags) {
                $token = join('|', @{$self->{TOKENS}->{$_}}[0,2]);
            } else {
                $token = $self->{TOKENS}->{$_}->[0];
            }
            push @tokenArray, $token;
        }
        return @tokenArray;
    }
}

#gets the token numbers of the content of an element
sub tokenNumbersFromElement {
    my $self = shift;
    die 'document not tokenized' unless $self->{TOKENS};
    my $arrayOrHashRef = shift;
    if (ref($arrayOrHashRef) eq "HASH"){
        return "THIS ELEMENT HAS NO TEXT EXTENT";
    } else {
        my $start = $arrayOrHashRef->[3];
        my $end = $arrayOrHashRef->[4];
        return $start if $start == $end;
        return ($start...$end);
    }
}

#gets the token associated with a particular token number
sub getToken {
    my $self = shift;
    die 'document not tokenized' unless $self->{TOKENS};
    my $tokenNumber = shift;
    my $returnTags = shift;
    die 'document not tagged' if ($returnTags && !$self->{TAGGED});
    if ($returnTags) {
        return join('|', @{$self->{TOKENS}->{$tokenNumber}}[0,2]);
    } else {
        return $self->{TOKENS}->{$tokenNumber}->[0];
    }
}

#gets all the tokens in the document, in an array.
sub allTokens {
    my $self = shift;
    die 'document not tokenized' unless $self->{TOKENS};
    my $returnTags = shift;
    die 'document not tagged' if ($returnTags && !$self->{TAGGED});
    my @tokenArray;
    while (my ($k, $v) = each %{$self->{TOKENS}}) {
        if ($returnTags) {
            $tokenArray[$k] = join('|', @{$v}[0,2]);
        } else {
            $tokenArray[$k] = $v->[0];
        }
    }
    return @tokenArray;
}

#runs a sentencizer on the tokens of the doc
sub sentencizeTokens {
    my $self = shift;
    die "document not tokenized $!\n" unless my @allTokens = $self->allTokens;
    die "no sentencizer defined $!\n" unless my $sent = $self->{SENTENCIZER};
    my @arrayOfSentenceNumbers = &{$sent}(@allTokens);
    my $tokenCounter;
    my $tokenCount = @arrayOfSentenceNumbers;
    for (0...$tokenCount) {
        if ($_ < $tokenCount) {
            my $sentenceNo = $arrayOfSentenceNumbers[$_];
            $self->{TOKENS}->{$_}->[1] = $sentenceNo;
            unless (defined $self->{SENTENCES}->{$sentenceNo}->[0]) {
                $self->{SENTENCES}->{$sentenceNo}->[0] = $_;
            }
            unless (!$sentenceNo ||
                    defined $self->{SENTENCES}->{$sentenceNo-1}->[1]) {
                $self->{SENTENCES}->{$sentenceNo-1}->[1] = $_-1
            }
        } else {
            $self->{SENTENCES}->{$arrayOfSentenceNumbers[-1]}->[1] = $_-1;
        }
    }
}

#runs a tagger on the tokens of the doc.
sub tagTokens {
    my $self = shift;
    die "document not sentencized" unless my $sentenceCount = keys %{$self->{SENTENCES}};
    die "sentence tagger not defined" unless my $senttag = $self->{TAGGER};
    $self->{TAGGED} = 1;
    my @text;
    for (0...$sentenceCount) {
        my @sentence;
        my ($firstTokenNumber, $lastTokenNumber) = @{$self->{SENTENCES}->{$_}};
        for ($firstTokenNumber...$lastTokenNumber) {
            push @sentence, $self->{TOKENS}->{$_}->[0];
        }
        push @text, join(' ', @sentence);
    }
    my @tags = &{$senttag}(join("\n", @text));
    my $tagCounter = 0;
    for (@tags) {
        $self->{TOKENS}->{$tagCounter}->[2] = $_;
        $tagCounter++;
    }
}

sub getTag {
    my $self = shift;
    die 'document not tagged' unless $self->{TAGGED};
    my $tokenNumber = shift;
    return $self->{TOKENS}->{$tokenNumber}->[2];
}

sub getSentence {
    my $self = shift;
    die 'document not sentencized' unless $self->{SENTENCES};
    my $sentenceNumber = shift;
    my $returnTags = shift;
    die 'document not tagged' if ($returnTags && !$self->{TAGGED});
    my @arrayOfTokens;
    my ($firstTokenNo, $lastTokenNo) = @{$self->{SENTENCES}->{$sentenceNumber}};
    for ($firstTokenNo...$lastTokenNo) {
        my $token;
        if ($returnTags) {
            $token = join('|', @{$self->{TOKENS}->{$_}}[0,2]);
        } else {
            $token = $self->{TOKENS}->{$_}->[0];
        }
        push @arrayOfTokens, $token;
    }
    return join(' ', @arrayOfTokens);
}

sub getContextSentence {
    my $self = shift;
    die 'document not sentencized' unless $self->{SENTENCES};
    my $element = shift;
    my $elStart = $element->[3];
    my $elEnd = $element->[4];
    my $sentenceNo = $self->{TOKENS}->{$elStart}->[1];
    my ($sStart, $sEnd) = @{$self->{SENTENCES}->{$sentenceNo}};
    my $contextSentence;
    for ($sStart...$elStart-1) {
        $contextSentence .= " $self->{TOKENS}->{$_}->[0]";
    }
    $contextSentence = $contextSentence.' <<';
    for ($elStart...$elEnd) {
        $contextSentence .= " $self->{TOKENS}->{$_}->[0]";
    }
    $contextSentence = $contextSentence.' >>';
    for ($elEnd+1...$sEnd) {
        $contextSentence .= " $self->{TOKENS}->{$_}->[0]";
    }
    return $contextSentence;
}

sub getTokens {
    my $self = shift;
    die 'document not tokenized' unless $self->{TOKENS};
    my $tokenNumber = shift;
    my $wanted = shift;
    my $returnTags = shift;
    die 'document not tagged' if ($returnTags && !$self->{TAGGED});
    my $start = $wanted + $tokenNumber;
    my $pointer = $start;
    my @tokens;
    while ($pointer > $tokenNumber) {
        my $token;
        if ($returnTags) {
            $token = join('|', @{$self->{TOKENS}->{$pointer}}[0,2]);
        } else {
            $token = $self->{TOKENS}->{$pointer}->[0];
        }
        unshift @tokens, $token; 
        $pointer--;
    }
    while ($pointer < $tokenNumber) {
        if ($returnTags) {
            my $token = join('|', @{$self->{TOKENS}->{$pointer}}[0,2]);
        } else {
            my $token = $self->{TOKENS}->{$pointer}->[0];
        }
        push @tokens, $token;
        $pointer++;
    }
    return @tokens;
}

sub getTags {
    my $self = shift;
    die 'document not tagged' unless $self->{TAGGED};
    my $tokenNumber = shift;
    my $wanted = shift;
    my $start = $wanted + $tokenNumber;
    my $pointer = $start;
    my @tags;
    while ($pointer > $tokenNumber) {
        unshift @tags, $self->{TOKENS}->{$pointer}->[2]; 
        $pointer--;
    }
    while ($pointer < $tokenNumber) {
        push @tags, $self->{TOKENS}->{$pointer}->[2];
        $pointer++;
    }
    return @tags;
}


sub setSentencizer {
    my $self = shift;
    $self->{SENTENCIZER} = shift;
}



sub setTagger {
    my $self = shift;
    $self->{TAGGER} = shift;
}


#Class Methods

sub attributes {
    my $class = shift;
    my $arrayOrHashRef = shift;
    if (ref($arrayOrHashRef) eq "HASH"){
        return $arrayOrHashRef;
    } else {
        return $arrayOrHashRef->[2];
    }
}

sub tokenize {
    my $class = shift;
    my $textNode = shift;
    return tokenizeTextNode($textNode);
}

##PRIVATE STUFF----------------------------------------------------------

#Handlers

sub handle_start { #pass start tags off to functions based on their type

  local $expat = shift;
  local $tag = shift;
  if ($tag eq 'MAKEINSTANCE') {
      procMI(@_);
  } elsif ($tag eq 's') {
      procSentence(@_);
  } elsif ($tag eq 'EVENT') {
      procEvent(@_);
  } elsif($tag eq 'TLINK') {
      procTlink(@_);
  } elsif ($tag eq 'TIMEX3') {
      procTimex3(@_);
  } elsif ($tag eq 'SIGNAL') {
      procSignal(@_);
  } elsif ($tag eq 'SLINK') {
      procSlink(@_);
  } elsif ($tag eq 'ALINK') {
      procAlink(@_);
  } elsif ($tag eq 'SYNTAX') {
      procSyntax(@_);
  } elsif ($tag eq 'TimeML') {
      procTimeML(@_);
  } else {
      procMisc(@_);
  }
  $docCounter++;
}

sub handle_end {
    local $expat = shift;
    local $tag = shift;
    return 0 if $tag =~ /^(MAKEINSTANCE|SLINK|TLINK|ALINK)$/;
#    return 0 if $tag =~ /^(DOCNO|DOCTYPE|ACCESS|ACTION|DESCRIPT|CAPTION|DOCID|HL|DD|AN)/;
#	print "TAG" if not $tag;
#	print "TAG: $tag\n" if not $seeking[0];
    if ($tag =~ /^(EVENT|TIMEX3|SIGNAL)$/) {
	#print Dumper(\@openedTags);
	$openingTag = pop @openedTags;
	if ($openingTag and $tag eq $openingTag->[0]) {
	    $id = $openingTag->[1];
	    if ($tag eq 'EVENT') {
		$eid = $openingTag->[1];
		$EVENTs{$id}->[4] = $textCounter-1;
		$EVENTs{$id}->[1] = $docCounter;
		#print Dumper($EVENTs{$id}); 
	    } elsif ($tag eq 'TIMEX3') {
		$TIMEX3s{$id}->[4] = $textCounter-1;
		$TIMEX3s{$id}->[1] = $docCounter;
		#print Dumper($TIMEX3s{$id}); 
	    } elsif ($tag eq 'SIGNAL') {
		$SIGNALs{$id}->[4] = $textCounter-1;
		$SIGNALs{$id}->[1] = $docCounter;
		#print Dumper($SIGNALs{$id}); 
	    } else { warn "tried to index invalid end tag: $!";}
	}
    }
    $DOCUMENT[$docCounter] = $expat->original_string();
    if ($tag eq 'TimeML') {
        $timemlClosed = 1;
    } else {
        $docCounter++;
    }
}


sub handle_default { 
	# handles text, entities, comments, and <? directives 
    my $expat = shift;
    my $string = shift;
	if ($timemlClosed) {
        push @FOOTER, $string;
    } else {
        unless ($string =~ /^<.*>$/) {
            if ($tokenize) {
                $string =~ s/\n/ /g;
                my @tokens = tokenizeTextNode($string);
                for (@tokens) {
                    $TOKENS{$textCounter}->[0] = $_;
                    $textCounter++;
                }
            }
        }
        $DOCUMENT[$docCounter] = $string;
        $docCounter++;
    }
}

sub handle_xmldecl {
    my %atts;
    my ($expat, $version, $encoding, $standalone) = @_;
    $atts{'version'} = $version if $version;
    $atts{'encoding'} = $encoding if $encoding;
    $atts{'standalone'} = "yes" if $standalone;
    $xmldec = \%atts;
}

#functions that process that process start tags-------------------

sub procMisc { #processes non-TimeML starts.
    $DOCUMENT[$docCounter] = $expat->original_string();
}

sub procTimeML {
    my $atts = getAtts(@_);
    $root = $atts;
	$DOCUMENT[$docCounter] = $expat->original_string();
}

sub procSentence {
	$sentID++;
	$DOCUMENT[$docCounter] = $expat->original_string();
}

sub procEvent {
    my $atts = getAtts(@_);
	$atts->{'sentID'} = $sentID;
    push @openedTags,  ['EVENT', $atts->{'eid'}];
	my $obj = [$docCounter, $docCounter, $atts, $textCounter];
    $EVENTs{$atts->{'eid'}} = $obj;
#	print Dumper($obj);
	# Put a reference in the DOC attribute. As a result, any changes
	# to the EVENT will update the one in DOC immediately. Same trick
	# is used for other tags.
	$DOCUMENT[$docCounter] = ['EVENT',$atts];
}

sub procMI {
    my $atts = getAtts(@_);
	my $eiid = $atts->{'eiid'};
    $MAKEINSTANCEs{$eiid} = $atts;
	$InstanceFromEvent{$atts->{'eventID'}} = $eiid;
	$DOCUMENT[$docCounter] = ['MAKEINSTANCE',$atts];
}

sub procTimex3 {
    my $atts = getAtts(@_);
    $atts->{'sentID'} = $sentID;
    push @openedTags,  ['TIMEX3', $atts->{'tid'}];
	my $obj = [$docCounter, $docCounter, $atts, $textCounter];
#	print Dumper($obj);
    $TIMEX3s{$atts->{'tid'}} = $obj;
    $DOCUMENT[$docCounter] = ['TIMEX3',$atts];
}

sub procSignal {
    my $atts = getAtts(@_);
    $atts->{'sentID'} = $sentID;
    push @openedTags,  ['SIGNAL', $atts->{'sid'}];
	my $obj = [$docCounter, $docCounter, $atts, $textCounter];
#	print Dumper($obj);
    $SIGNALs{$atts->{'sid'}} = $obj;
    $DOCUMENT[$docCounter] = ['SIGNAL',$atts];
}

sub procAlink {
    my $atts = getAtts(@_);
    push @ALINKs, $atts;
    $DOCUMENT[$docCounter] = ['ALINK',$atts];
}

sub procSlink {
    my $atts = getAtts(@_);
    push @SLINKs, $atts;
    $DOCUMENT[$docCounter] = ['SLINK',$atts];
}

sub procTlink {
    my $atts = getAtts(@_);
    push @TLINKs, $atts;
    $DOCUMENT[$docCounter] = ['TLINK',$atts];
}

sub procSyntax {
    my $atts = getAtts(@_);
    push @SYNTAXs, $atts;
    $DOCUMENT[$docCounter] = ['SYNTAX',$atts];
}



#utility functions-----------------------------------

sub tokenizeTextNode {
    my $textNode = shift;
    #space before period if it's followed by a space and a capital
    $textNode =~ s/\.(\s+[A-Z])/ \.$1/g;
    #space before period if it's after a lower-case and at the end of a node
    $textNode =~ s/([a-z])\./$1 \./g;
    #space around colon or comma or backslash if it's not surrounded by numbers
    $textNode =~ s/([^0-9])\:([^0-9])/$1 \: $2/g;
    $textNode =~ s/([^0-9])\,([^0-9])/$1 \, $2/g;
    $textNode =~ s/\,( |$)/ \, /g;    
    $textNode =~ s/([^0-9])\/([^0-9])/$1 \, $2/g;
    
    # put space before any other punctuation
    $textNode =~ s/([^ ])\!/$1 \!/g;
    $textNode =~ s/([^ ])\?/$1 \?/g;
    $textNode =~ s/([^ ])\;/$1 \;/g;
    $textNode =~ s/([^ ])\"/$1 \"/g;
    $textNode =~ s/([^ ])\`/$1 \`/g;
    $textNode =~ s/([^ ])\'/$1 \'/g;
    $textNode =~ s/([^ ])\)/$1 \)/g;
    $textNode =~ s/([^ ])\(/$1 \(/g;
    
    
    # put space after any other punctuation
    $textNode =~ s/\!([^ ])/\! $1/g;
    $textNode =~ s/\?([^ ])/\? $1/g;
    $textNode =~ s/\;([^ ])/\; $1/g;
    $textNode =~ s/\"([^ ])/\" $1/g;
    #$textNode =~ s/\`([^ ])/\` $1/g;
    #$textNode =~ s/\'([^ ])/\' $1/g;
    $textNode =~ s/\(([^ ])/\( $1/g;
    $textNode =~ s/\)([^ ])/\) $1/g;
    
    
    #put spaces around special symbols
    $textNode =~ s/([^ ])\%/$1 \%/g;
    $textNode =~ s/([^ ])\$/$1 \$/g;
    $textNode =~ s/([^ ])\+/$1 \+/g;
    #s/([^ ])\-/$1 \-/g;
    $textNode =~ s/([^ ])\#/$1 \#/g;
    $textNode =~ s/([^ ])\*/$1 \*/g;
    $textNode =~ s/([^ ])\[/$1 \[/g;
    $textNode =~ s/([^ ])\]/$1 \]/g;
    $textNode =~ s/([^ ])\{/$1 \{/g;
    $textNode =~ s/([^ ])\}/$1 \}/g;
    $textNode =~ s/([^ ])\>/$1 \>/g;
    $textNode =~ s/([^ ])\</$1 \</g;
    #$textNode =~ s/([^ ])\_/$1 \_/g;
    $textNode =~ s/([^ ])\\/$1 \\/g;
    $textNode =~ s/([^ ])\|/$1 \|/g;
    $textNode =~ s/([^ ])\=/$1 \=/g;
    $textNode =~ s/([^ ])\&/$1 \&/g;
    
    $textNode =~ s/\%([^ ])/\% $1/g;
    $textNode =~ s/\$([^ ])/\$ $1/g;
    $textNode =~ s/\+([^ ])/\+ $1/g;
    #$textNode =~ s/\-([^ ])/\- $1/g;
    $textNode =~ s/\#([^ ])/\# $1/g;
    $textNode =~ s/\*([^ ])/\* $1/g;
    $textNode =~ s/\[([^ ])/\[ $1/g;
    $textNode =~ s/\]([^ ])/\] $1/g;
    $textNode =~ s/\}([^ ])/\} $1/g;
    $textNode =~ s/\{([^ ])/\} $1/g;
    $textNode =~ s/\\([^ ])/\\ $1/g;
    $textNode =~ s/\|([^ ])/\| $1/g;
    #$textNode =~ s/\_([^ ])/\_ $1/g;
    $textNode =~ s/\<([^ ])/\< $1/g;
    $textNode =~ s/\>([^ ])/\> $1/g;
    $textNode =~ s/\=([^ ])/\= $1/g;
    $textNode =~ s/\&([^ ])/\& $1/g;
    
    
    ## remove leading whitespace
    $textNode =~ s/^\s+//;
    return split(/[\s]+/, $textNode);
}

sub getAtts {
    my %atts;
    while (@_) {
        my $att = shift;
        my $value = shift;
        $atts{$att} = $value;
    }
    return \%atts;
}

sub attString {
    my $attString;
    my $hashref = shift;
    while (my ($att, $value) = each %{$hashref}) {
        $attString=$attString."$att=\"$value\" ";
    }
    return $attString;
}

sub declarationString {
    unless ($xmldec) {
        my %atts;
        $atts{'version'} = '1.0';
        $xmldec = \%atts;
    }
    my $decString = '<?xml ';
    $decString = $decString.attString($xmldec);
    $decString = $decString."?>\n";
    return $decString;
}

sub startString {
    my $startString;
    my $tag = shift;
    my $attHashref = shift;
    $startString = "<$tag ";
    $startString = $startString.attString($attHashref);
    $startString = $startString.'>';
    return $startString;
}


return 1;

