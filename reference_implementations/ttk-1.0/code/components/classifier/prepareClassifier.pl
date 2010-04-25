use TimeMLDoc;
#use Data::Dumper;

$debug = 0;

($infile, $vector_file_EE, $vector_file_ET) = @ARGV;
my $DOC = TimeMLDoc->parse($infile);

%EID2VECTOR = ();
%TID2VECTOR = ();
&readVectors();

if ($debug) {
    foreach $id (sort keys %EID2VECTOR) { print "  $id  $EID2VECTOR{$id}\n"; }
    foreach $id (sort keys %TID2VECTOR) { print "  $id  $TID2VECTOR{$id}\n"; }
}

open IN, $infile or die;

@objects = &readText();
print "OBJECTS: @objects\n" if $debug;

open EE, "> $vector_file_EE";
open ET, "> $vector_file_ET";

# used to have -2, which does not work if there are only 2 objects
foreach $i (0..$#objects-1) {
    print "OBJ: $i\n" if $debug;
    &createVector($objects[$i], $objects[$i+1]);
    if ($i + 2 > $#objects) {
        &createVector($objects[$i], $objects[$i+2]);
    }
}

sub createVector
{
    my ($id1, $id2) = @_;
    $vector1 = &lookupVector($id1);
#    print "$id1 $vector1\n";
    $vector2 = &lookupVector($id2);
    if ($id1 =~ /e/ and $id2 =~/e/) {
	$vector1 =~ s/<INT>/0/g;
	$vector2 =~ s/<INT>/1/g;
	$vector1 =~ /0tense-(\S+)/;
	$t1 = $1;
	$vector2 =~ /1tense-(\S+)/;
	$t2 = $1;
	$shiftTense = ($t1 eq $t2) ? '0' : '1';
	$vector1 =~ /0aspect-(\S+)/;
	$a1 = $1;
	$vector2 =~ /1aspect-(\S+)/;
	$a2 = $1;
	$shiftAspect = ($a1 eq $a2) ? '0' : '1';
#	print "$t1 $t2 $a1 $a2\n";
#	print "UNKNOWN $vector1 $vector2 Signal-NONE shiftAspect-$shiftAspect shiftTen-$shiftTense\n";
	print EE "UNKNOWN $vector1 $vector2 Signal-NONE shiftAspect-$shiftAspect shiftTen-$shiftTense\n";
    }
    elsif ($id1 =~ /e/ and $id2 =~/t/) {
	$vector1 =~ s/<INT>/0/g;
	$vector2 =~ s/<INT>/1/g;
	print ET "UNKNOWN $vector1 $vector2 Signal-NONE\n";
    }
    elsif ($id1 =~ /t/ and $id2 =~/e/) {
	$vector2 =~ s/<INT>/0/g;
	$vector1 =~ s/<INT>/1/g;
	print ET "UNKNOWN $vector2 $vector1 Signal-NONE\n";
    }
}

sub lookupVector
{
    my $id = shift;
    if ($id =~ /e/) {
	return $EID2VECTOR{$id};
    } else {
	return $TID2VECTOR{$id};
    }
}

 
#open OUT, "> $vectorfile" or die; 

                                                                                                        
                                                                                                        
                                                                                                        
sub readVectors 
{ 

    # IBEFORE 0eid=e1 0Actualclass-OCCURRENCE 0aspect-NONE
    # 0modality-NONE # 0negation-NONE 0string-exploded 0te\nse-PAST
    # 0timeorevent-event # 0eid-e2 1Actualclass-OCCURRENCE
    # 1aspect-NONE 1modality-NONE # 1negation-NONE \1string-killing
    # 1tense-NONE 1timeorevent-event # Signal-NONE shiftAspect-0
    # shiftTen-1

    foreach $event (sort sort_by_id $DOC->events())
    {
	$eid = $event->{'eid'};
	$text = $event->{'text'};
	$class = $event->{'class'};
	$instance = $DOC->instanceFromEventID($eid);
	$eiid = $instance->{'eiid'};
	$tense = $instance->{'tense'};
	$aspect = $instance->{'aspect'};
	$polarity = $instance->{'polarity'};
	$modality = $instance->{'modality'};
	$pos = $instance->{'pos'};

	$modality = 'NONE' unless $modality;
	$polarity = 'NONE' unless $polarity eq 'NEG';

	$vector = "<INT>eid-$eid";
	$vector .= " <INT>eiid-$eiid";
	$vector .= " <INT>Actualclass-$class";
	$vector .= " <INT>aspect-$aspect";
	$vector .= " <INT>modality-$modality";
	$vector .= " <INT>negation-$polarity";
	$vector .= " <INT>string-$text";
	$vector .= " <INT>tense-$tense";
	$vector .= " <INT>timeorevent-event";

	$EID2VECTOR{$eid} = $vector;
	$vector =~ s/\b<INT>/0/gm;
	#print "$vector\n";
    }

    # INCLUDES 0Actualclass-OCCURRENCE 0aspect-NONE 0modality-NONE
    # 0negation-NONE 0string-killed 0tense-PAST 0timeorevent-event#
    # 1timeorevent-NONE 1string-Friday 1functionInDoc-false
    # 1temporalFunction-time 1type-DATE 1value-1998-08-07 Signal-NONE

    foreach $timex (sort sort_by_id $DOC->timexes())
    {
	$tid = $timex->{'tid'};
	$text = $timex->{'text'};
	$type = $timex->{'TYPE'};
	$value = $timex->{'VAL'};
	$fun = $timex->{'functionInDocument'};
	$fun = 'false' unless $fun;

	$vector = "<INT>tid-$tid";
	$vector .= " <INT>timeorevent-NONE";
	$vector .= " <INT>string-$text";
	$vector .= " <INT>functionInDoc-$fun";
	$vector .= " <INT>temporalFunction-time";
	$vector .= " <INT>type-$type";
	$vector .= " <INT>value-$value";

	$TID2VECTOR{$tid} = $vector;
	$vector =~ s/<INT>/0/gm;
	#print "$vector\n";
    }
}

sub sort_by_id 
{
    $a->{'eid'} =~ /e(\d+)/;
    $id1 = $1;
    $b->{'eid'} =~ /e(\d+)/;
    $id2 = $1;
    return $id1 <=> $id2;
}


sub readText
{
    @objects = ();
    while (<IN>) {
	#while (/ [et]id="([te]\d+)"/gm) {
	#    push @objects, $1;
	while (/ [et]id="([^"]+)"/gm) {
	    push @objects, $1;
	}
    }
    return @objects;
}

