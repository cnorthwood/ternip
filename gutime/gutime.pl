#!/usr/bin/perl -w

# Wrapper script for TimeTag.pl and TempEx, very loosely based on
# GUTime-Evita.pl Seok Bae Jang - sbj3@georgetown.edu (June 2005)

# TempEx cannot deal with other tags than s and lex, so all other tags
# are stripped. This script does not attempt to put them back in,
# leaving that task to the Python code of the Tarsqi toolkit.


use English;

$/ = undef;

%options = ();
while ($ARGV[0] =~ /^-/) {
    $option = shift @ARGV;
    $value = shift @ARGV;
    $options{$option} = $value;
}

# use default text body tag or one supplied by user
$TextBodyTag = "TEXT";
if ($options{'-t'}) {
    $TextBodyTag = $options{'-t'};
}

$inputfile = shift;
$outputfile = shift;
$tmpfile = $inputfile . '.tmp';

$TextBodyStartTag = "<${TextBodyTag}[^>]*>";  # made more general (MV 070301)
$TextBodyEndTag = "<\/$TextBodyTag>";

open (IN, "$inputfile") or die "Cannot open $inputfile\n";
$text = <IN>;
close IN;
    
# Split apart front matter, main text and end matter, not needed when
# this script runs from the ttk, but need to keep track of material
# outside the text body tag if this is a standalone scirpt.
if ( $text =~ /($TextBodyStartTag)(.+?)($TextBodyEndTag)/s) {
    $opentag = $1;
    $closetag = $3;
    $vfront = $PREMATCH;
    $vbody = $2;
    $vback = $POSTMATCH;
    $body = $vbody;
    $vback =~ s/\n\n//g;
}

# Find a document creation time and add it as a TIMEX3 tag
$DateTime = &getDateTime($vfront, $text, $vback);
# $DCT = &create_DCT($DateTime);

# Prepare input for TimeTag and save to tmp file
# the second line is a hack to remove some tags that are not taken out by CleanUp
$body = CleanUp($body);
$body =~ s/<\/VG-VBG>//gm;  
$GUTimeTagSource = "<DOC>\n" . $DateTime . "\n" . $body . "</DOC>\n";
&saveToFile($GUTimeTagSource, $tmpfile);

# GUTime Tagging
#$output = `perl TimeTag.pl $tmpfile`;
$output = `perl TimeTag.pl $tmpfile | perl postTempEx.pl`;
$output =~ s/<DATE_TIME>.*?<\/DATE_TIME>\n//;
$output =~ s/<DOC>\n//;
$output =~ s/<\/DOC>\n//;
$output =~ s/^\n//;
$output =~ s/<TIMEX3 tid="t\d+">\n//g;
#&saveToFile($vfront.$opentag.$DCT.$output.$closetag.$vback, $outputfile);
&saveToFile($vfront.$opentag.$output.$closetag.$vback, $outputfile);
unlink($tmpfile);



sub CleanUp
{
    # Cleans up a source string to run GUTime, removes chunking tags,
    # Evita tags, and RTE3 tags. Should be more general.
    
    my $line1 = $_[0];

    @rte_tags = qw ( h t );
    @chunk_tags = qw( NG NX HEAD VG VX NGP POS VG-INF VG-VGB VG-VBN VNX INF VGX
                      RX RG AX-PRENOMINAL IN-MW );

    foreach $tag (@chunk_tags, @rte_tags) {
        $line1 =~ s/<$tag>//ig;
        $line1 =~ s/<\/$tag>//ig;
    }

    # remove evita tags
    $line1 =~ s/<EVENT[^>]+?>//ig;
    $line1 =~ s/<\/EVENT>//ig;
    $line1 =~ s/<MAKEINSTANCE[^>]+?\/>//ig;

    @atee_tags = qw (HandL Title Headline Para LeadPara TailParas
                     Byline Credit Contact Notes Copyright Art ELink);
    foreach $tag (@atee_tags) {
        $line1 =~ s/<$tag[^>]*>//ig;
        $line1 =~ s/<\/$tag>//ig;
    }
    
    return $line1;
}


#This function extracts information for <DATE_TIME> from document head.
#If a document head style is not defined, it should be defined in this file, or
#the <DATE_TIME> tag should be inserted in document head.

sub ExDateTime
{
    my $line1 = $_[0];
    #clean existing TIMEX3 tags.
    $line1 =~ s/<TIMEX3.*?>//g;
    $line1 =~ s/<\/TIMEX3>//g;

    if ($line1 =~ /<DATE_TIME>(.*?)<\/DATE_TIME>/) {
        $tmpDate = $1;
        if ($tmpDate =~ /(\d\d\d\d)\s*-\s*(\d\d)\s*-\s*(\d\d)/) {
            $retVal = "<DATE_TIME>" . $2 . "/" . $3  . "/" . $1 . "</DATE_TIME>";
            return 	$retVal;
        }
        elsif ($tmpDate =~ /(\d\d)\s*-\s*(\d\d)\s*-\s*(\d\d\d\d)/) {
            $retVal  = "<DATE_TIME>" . $1 . "/" . $2  . "/" . $3  . "</DATE_TIME>";
            return 	$retVal;
        }
        elsif ($tmpDate =~ /(\d\d\d\d)\s*\/\s*(\d\d)\s*\/\s*(\d\d)/) {
            $retVal = "<DATE_TIME>" . $2 . "/" . $3  . "/" . $1 . "</DATE_TIME>";
            return 	$retVal;
        }
        elsif ($tmpDate =~ /(\d\d)\s*\/\s*(\d\d)\s*\/\s*(\d\d\d\d)/) {
            $retVal = "<DATE_TIME>" . $1 . "/" . $2  . "/" . $3  . "</DATE_TIME>";
            return 	$retVal;
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*CNN.*?<\/DOCNO>/s) {
        #CNN:
        #<DOCNO> CNN19980227.2130.0067 </DOCNO>
        #<bn_episode_trans program="CNN_Headline_News" air_date="19980227:2130">
        #<DOCNO> CNN19980126.1600.1104 </DOCNO>
        #<bn_episode_trans program="CNN_Headline_News" air_date="19980126:1600">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*CNN(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }    
    elsif ($line1 =~ /<DOCNO>\s*ea.*?<\/DOCNO>/) {
        #ABC_World_News_Tonight (ea):
        #<DOCNO> ea980120.1830.0456 </DOCNO>
        #<bn_episode_trans program="ABC_World_News_Tonight" air_date="19980120:1830">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*ea(\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*ABC.*?<\/DOCNO>/) {
        #<DOCNO> ABC19980108.1830.0711 </DOCNO>
        #<bn_episode_trans program="ABC_World_News_Tonight" air_date="19980108:1830">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*ABC(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*AP.*?<\/DOCNO>/) {
        #Associated Press (AP)
        #<DOCNO> AP900816-0139 </DOCNO>
        #<FILEID>AP-NR-08-16-90 2041EDT</FILEID>
        #<DOCNO> AP900815-0044 </DOCNO>
        #<FILEID>AP-NR-08-15-90 1337EDT</FILEID>
        if ($line1 =~ /<FILEID>\s*AP-\w\w-(\d\d)-(\d\d)-(\d\d)\s+.*?<\/FILEID>/) {
            return "<DATE_TIME>$1/$2/19$3</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*AP(\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*APW.*?<\/DOCNO>/) {
        #APW
        #<DOCNO> APW19980213.1310 </DOCNO>
        #<DATE_TIME> 02/13/1998 14:26:00 </DATE_TIME>
        #<DOCNO> APW19980213.1380 </DOCNO>
        #<DATE_TIME> 02/13/1998 15:44:00 </DATE_TIME>
        if ($line1 =~ /(<DATE_TIME>.*?<\/DATE_TIME>)/) {
            return $1;
        }
        elsif ($line1 =~ /<DOCNO>\s*APW(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }    
    elsif ($line1 =~ /<DOCNO>\s*WSJ.*?<\/DOCNO>/) {
        #wsj
        #<DOCNO> WSJ891102-0161 </DOCNO>
        #<DD> = 891102 </DD>
        #<DD> 11/02/89 </DD>
        #<DOCNO> WSJ891102-0032 </DOCNO>
        #<DD> = 891102 </DD>
        #<DD> 11/02/89 </DD>
        if ($line1 =~ /<DD>\s*(\d\d)\/(\d\d)\/(\d\d)\s*<\/DD>/) {
            return "<DATE_TIME>$1/$2/$3</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*WSJ(\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*VOA.*?<\/DOCNO>/) {
        #VOA
        #<DOCNO> VOA19980331.1700.1533 </DOCNO>
        #<bn_episode_trans program="VOA" air_date="19980331:1700">
        #<DOCNO> VOA19980303.1600.2745 </DOCNO>
        #<bn_episode_trans program="VOA" air_date="19980303:1600">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*VOA(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*PRI.*?<\/DOCNO>/) {
        #PRI
        #<DOCNO> PRI19980205.2000.1998 </DOCNO>
        #<bn_episode_trans program="PRI_The_World" air_date="19980205:2000">
        #<DOCNO> PRI19980115.2000.0186 </DOCNO>
        #<bn_episode_trans program="PRI_The_World" air_date="19980115:2000">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*PRI(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*NYT.*?<\/DOCNO>/) {
        #NYT
        #<DOCNO> NYT19980206.0460 </DOCNO>
        #<DATE_TIME> 02/06/1998 22:19:00 </DATE_TIME>
        #<DOCNO> NYT19980402.0453 </DOCNO>
        #<DATE_TIME> 04/02/1998 22:52:00 </DATE_TIME>
        if ($line1 =~ /(<DATE_TIME>.*?<\/DATE_TIME>)/) {
            return $1;
        }
        elsif ($line1 =~ /<DOCNO>\s*NYT(\d\d\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }    
    elsif ($line1 =~ /<DOCNO>\s*ed.*?<\/DOCNO>/) {
        #ed
        #CNN_Headline_News
        #<DOCNO> ed980111.1130.0089 </docno>
        #<bn_episode_trans program="CNN_Headline_News" air_date="">
        if ($line1 =~ /<bn_episode_trans.*air_date=\"(\d\d\d\d)(\d\d)(\d\d):\d\d\d\d\">/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        elsif ($line1 =~ /<DOCNO>\s*ed(\d\d)(\d\d)(\d\d).*?<\/DOCNO>/) {
            return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
        }
        else {
            return "Error: cannot find <DATE_TIME>";
        }
    }
    elsif ($line1 =~ /<DOCNO>\s*\D+?(\d\d)(\d\d)(\d\d).*?<\/DOCNO>/s) {
        #<DOCNO>
        #WSJ910225-0066
        #</DOCNO>
        return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
    }
    elsif ($line1 =~ /<PUBDATE>\s*?(\d\d)(\d\d)(\d\d)\s*?<\/PUBDATE>/s) {
        #<PUBDATE> 911203 <PUBDATE>
        return "<DATE_TIME>$2/$3/$1</DATE_TIME>";
    }
    
    else {
        return "NULL";
    }
}



sub saveToFile
{
    my ($text, $filename) = @_;
    open (OUT, "> $filename") or die "Could not save to $filename\n";
    print OUT $text;
    close OUT;
}


sub getDateTime
{
    my ($vfront, $line, $vback) = @_;

    #Generate Time Tagging Source.
    $vfront_tmp = $vfront;
    $vfront_tmp =~ s/<lex[^<]*>//ig;
    $vfront_tmp =~ s/<\/lex>//ig;

    # added use of command line option to enter the DCT
    if ($options{'-dct'}) {
        $DateTime = '<DATE_TIME>' . $options{'-dct'} . '</DATE_TIME>';
    } else {
        $DateTime = &ExDateTime($vfront_tmp);
        $DateTime = &ExDateTime($line) if $DateTime eq "NULL";
        $DateTime = &ExDateTime($vback) if $DateTime eq "NULL";
    }
    
    if ($DateTime eq "NULL") {
        #print STDERR "Warning: no document date found, using current date\n";
        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
        $year = $year + 1900;
        $year =~ /\d\d(\d\d)/;
        $year = $1;
        $DateTime = sprintf "<DATE_TIME>%02d/%02d/%02d</DATE_TIME>", $year,$mon+1,$mday;
    }

    return $DateTime;
}


sub create_DCT
{
    my $DateTime = shift;
    my $creation_time = '';
    
    # Create CreationTime tag Default tid for CREATION_TIME is t100 to
    # avoid a loading error in TANGO, since t0 is not allowed in
    # TANGO. If there are more than 100 temporal expressions, you
    # need to modify t100.

    if ($DateTime =~ /<DATE_TIME>\s*(\d\d)\/(\d\d)\/(\d\d)\s*<\/DATE_TIME>/) {
        $creation_time = "<TIMEX3 functionInDocument=\"CREATION_TIME\" tid=\"t100\" VAL=\"19$3$1$2\"\/>";
    }
    elsif ($DateTime =~ /<DATE_TIME>\s*(\d\d)\/(\d\d)\/(\d\d\d\d)\s*<\/DATE_TIME>/) {
        $creation_time = "<TIMEX3 functionInDocument=\"CREATION_TIME\" tid=\"t100\" VAL=\"$3$1$2\"\/>";
    }
    elsif ($DateTime =~ /<DATE_TIME>\s*(\d\d\d\d\d\d\d\d)\s*<\/DATE_TIME>/) {
        $creation_time = "<TIMEX3 functionInDocument=\"CREATION_TIME\" tid=\"t100\" VAL=\"$1\"\/>";
    }
    else {
        print STDERR "WARNING (GUTime-Evita.pl): cannot generate <Creation_Time> tag\n";
    }

    return $creation_time;
}


sub moveMakeinstanceTagsToEnd
{
    my ($body, $vback) = @_;

    # only move them if there is a closing TimeML tag 
    if ($vback =~ /<\/TimeML>/) {
        my $MAKEINSTANCE = "";
        while ($body =~ /(<MAKEINSTANCE[^>]+?>)/) {
            $MAKEINSTANCE .= $1 . "\n";
            $body =~ s/<MAKEINSTANCE[^>]+?>//;
        }
        $vback =~ s/<\/TimeML>/\n$MAKEINSTANCE\n<\/TimeML>/;
    }

    return ($body, $vback);
}

