
($ee, $et, $out) = @ARGV;


open EE, $ee;
open EE_REL, "$ee.REL";
open ET, $et;
open ET_REL, "$et.REL";
open OUT, "> $out";

print OUT "<TLINKS>\n";

while (<EE>) 
{
    /0eiid-((f\d+_)?ei\d+)/;
    $eiid1 = $1;
    /1eiid-((f\d+_)?ei\d+)/;
    $eiid2 = $1;
    $relLine = <EE_REL>;
    $relLine =~ /(\S+)/;
    $rel = $1;
    $relLine =~ /(\d.\d+)/;
    $confidence = $1;
    print OUT "<TLINK relType=\"$rel\" eventInstanceID=\"$eiid1\" relatedToEventInstance=\"$eiid2\" confidence=\"$confidence\" />\n";
}

while (<ET>) 
{
    /0eiid-((f\d+_)?ei\d+)/;
    $eiid1 = $1;
    /1tid-((f\d+_)?t\d+)/;
    $tid = $1;
    $relLine = <ET_REL>;
    $relLine =~ /(\S+)/;
    $rel = $1;
    $relLine =~ /(\d.\d+)/;
    $confidence = $1;
    print OUT "<TLINK relType=\"$rel\" eventInstanceID=\"$eiid1\" relatedToTime=\"$tid\" confidence=\"$confidence\" />\n";
}

print OUT "</TLINKS>\n";
