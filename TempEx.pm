# Variables and subroutines for tagging temporal expressions
# Copyright 2001 - The MITRE Corporation

use strict;

package      TempEx;
use vars     qw(@ISA @EXPORT @EXPORT_OK $VERSION);
require      Exporter;
@ISA       = qw(Exporter);
@EXPORT    = qw($TE_Loaded $TE_DEBUG $TE_HeurLevel
		TE_TagTIMEX TE_AddAttributes Date2ISO
		SetLexTagName printNonConsumingTIMEXes);
@EXPORT_OK = qw(Date2DOW Week2Date Word2Num
		%TE_Ord2Num %Month2Num $TEmonthabbr);
$VERSION   = 1.05;


########################################
## Global variable declarations for time expressions

use vars qw($TE_Loaded $TE_DEBUG $TE_HeurLevel);
use vars qw(%TE_Ord2Num %Month2Num $TEmonthabbr);

my($TEday, $TEmonth, $TERelDayExpr);
my($TEFixedHol, $TENthDOWHol, $TELunarHol, $TEDayHol);
my(%FixedHol2Date, %NthDOWHol2Date);
my(%Day2Num);
my(%TE_TimeZones, %TE_Season, %TE_Season2Month);
my(@TE_ML, @TE_CumML);
my(%TE_DecadeNums);
my($TEOrdinalWords, $TENumOrds, $OT, $CT);
my(%NumWords, @UnitWords, @EndUnitWords);
my($LexTagName, $OTCD, $OTNNP);

$TE_Loaded    = 1;
$TE_HeurLevel = 3;
$TE_DEBUG     = 0;

%TE_Season2Month = ("SP" => 4, "SU" => 6, "FA" => 9, "WI" => 12);


$OT = "(<[^\/][^>]*>)";
$CT = "(<\\\/[^>]*>)";

%NumWords
    = ("dozen" => 12,     "score" => 20,     "gross" => 144,
       "zero" => 0,       "oh" => 0,         "a"   =>  1, 
       "one" => 1,        "two" =>  2,       "three" =>  3, 
       "four" => 4,       "five" =>  5,      "six" =>  6,
       "seven" => 7,      "eight" =>  8,     "nine" =>  9,
       "ten" => 10,       "eleven" => 11,    "twelve" =>  12,
       "thirteen" => 13,  "fourteen" => 14,  "fifteen" =>  15, 
       "sixteen" => 16,   "seventeen" => 17, "eighteen" =>  18,
       "nineteen" => 19,  "twenty" => 20,    "thirty" =>  30,
       "forty" => 40,     "fifty" => 50,     "sixty" =>  60,
       "seventy" => 70,   "eighty" => 80,    "ninety" =>  90,
       "hundred" => 100,  "thousand" => 1000,"million" =>  1000000,
       "billion" => 1000000000, "trillion" => 1000000000000);

@UnitWords = qw(trillion billion million thousand hundred);
@EndUnitWords = qw(gross dozen score);


#################################
##  Variables for jfrank code  ##
#################################

my $useDurationChanges = 1;	#basically, if set to 0, none of the duration code does anything
my $printNCTs = 1;		# if set to 1, it will print out the non-consuming TIMEXES at the end of the printout


#wordtonum.pl variables

####

my $TE_Units = "(second|minute|hour|day|month|year|week|decade|centur(y|ie)|milleni(um|a))";

my %ordWord2Num = ("zeroeth" => 0,
		   "first" => 1,"second" => 2,"third" => 3,"fourth" => 4,"fifth" => 5,
		   "sixth" => 6,"seventh" => 7,"eighth" => 8,"ninth" => 9,"tenth" => 10,
		   "eleventh" => 11,"twelfth" => 12,"thirteenth" => 13,
		   "fourteenth" => 14,"fifteenth" => 15,"sixteenth" => 16,
		   "seventeenth" => 17,"eighteenth" => 18,"nineteenth" => 19,
		   "twentieth" => 20,"thirtieth" => 30,"fortieth" => 40,"fiftieth" => 50,
		   "sixtieth" => 60,"seventieth" => 70,"eightieth" => 80,"ninetieth" => 90,
		   "hundredth" => 100,"thousandth" => 1000,
		   "millionth" => 1000000,"billionth" => 1000000000,"trillionth" => 1000000000000);

#for getUniqueTID()
my $highestTID = 1;

# special variables relating to the beginPoint and endPoint values 
my $tiddef = 't99999';	#current default name for unspecified tids
my $tidDCT = 't0';	#current id for Document Creation Time

my $useUnspecTID = 1;	#if 1, we assign unspecified tids the value $tiddef
my $useDCT = 1;		#if 1 and $useUnspecTID = 1, then use 't0' instead of $tiddef 

my $unspecTIDVal = &getUnspecifiedTID();

# -if both tids exist, use them, i.e. "from 2002 until 2005"
# -if only one tid exists, use it, infer second time from duration value, then create non-consuming tid for it
# -if neither exists, use $tiddef as either beginPoint or endPoint, depending on the particular pattern...ignore
#  the other tid for now, since it can be easily inferred later anyway
#	-note that if $useUnspecTID = 0, we don't even create these non-consuming tids		


# some of these vars need to also be changed in: TimeTag.pl
my $valTagName = "VAL";
my $tidTagName = "tid";
my $tever = 2;	#TIMEX version


my @nonConsumingTIMEXes;
my $numNonConsumingTIMEXes = 0;

#################################
##   End of jfrank variables   ##
#################################



## Initialization
SetLexTagName("lex");

########################################
# Allows user to change name of POS tag
sub SetLexTagName {
    my($TagName);
    ($TagName) = @_;

    $LexTagName = $TagName;
    $OTCD = "<lex[^>]*pos=\\\"?CD[^>]*>";
    $OTNNP = "<lex[^>]*pos=\\\"?NNP?[^>]*>";
    
} # SetLexTagName


########################################
sub TE_TagTIMEX (\$) {

    my($string);
    ($string) = @_;
    
    my($temp1, $temp2, $temp3, $temp4);
    my($rest, $Count, $MCount, $year, $Nyear, $testyear);
    my($TE1, $TE2, $Tag2, $MixedCase);
    my($mid1, $mid2, $b4, $copy);
   
    ###########################################
    ###  Code added by jfrank - July-August 2004  ###
    ###########################################

    # ADD DURATIONS TAGS AND ADD ATTRIBUTES TO DURATION TAGS #	

    $string = &deliminateNumbers($string);

#    my $numString = '(a? (few|couple))?$OT\+ (\d+|NUM_START.*?NUM_END)';  #will match either a numeric or word/based number
    my $numString = '(\d+|NUM_START.*?NUM_END)';  #will match either a numeric or word/based number
    my $numOrdString = '(((\d*)(1st|2nd|3rd|[4567890]th))|NUM_ORD_START.+?NUM_ORD_END)';


    my $curDurValue;
    my $curPhrase;

    #ADD NEW DURATION PATTERNS HERE
    #Note: each added pattern here requires an added pattern in the expressionToDuration and expressionToPoints functions

    my @matchPatterns;   

    #Do substitutions
    my $curPattern;

    foreach $curPattern (@matchPatterns){
EACHPAT: while ($string =~ /$curPattern/g){
		$curPhrase = $1;

		my $bef = $`;

		my $helper = "";
		if ($bef =~ /<TIMEX$tever[^>]*>(.*?)$/){
			$helper = $1;	#helper var is everything between current pattern and immediately-preceding TIMEX tag
		}

		if (($helper =~ /<\/TIMEX$tever>/) || ($helper eq "")){	# so we don't embed tags ### CHECK ON THIS ########################
			unless ($curPhrase =~ /^<TIMEX$tever[^>]*TYPE=\"DURATION\"[^>]*>/){   #already has duration tag
				$curDurValue = &expressionToDuration($curPhrase);
				my $pointsString = &expressionToPoints($curPhrase);

				my $bp = "";
				my $ep = "";
				if ($pointsString =~ /([^:]*):([^:]*)/){
					$bp = $1;
					$ep = $2;
				}

				my $beginString = "";
				my $endString = "";

				if ($bp ne ""){$beginString = " beginPoint=\"$bp\"";}   	
				if ($ep ne ""){$endString = " endPoint=\"$ep\"";}   					

				#deal with nonconsuming TIMEXes here
				my $curNCTIMEX = "";
				my $curBPTID = "";
				my $curEPTID = "";
				if (($beginString eq "") && ($endString ne "")){  #endPoint defined, not beginPoint
					$curBPTID = &getUniqueTID();
					$beginString = " beginPoint=\"$curBPTID\"";
					$curNCTIMEX = "<TIMEX$tever $tidTagName=\"$curBPTID\">";	#still need to add VAL
					$nonConsumingTIMEXes[$numNonConsumingTIMEXes] = $curNCTIMEX;
					$numNonConsumingTIMEXes++;
				} elsif (($endString eq "") && ($beginString ne "")){  #beginPoint defined, not endPoint
					$curEPTID = &getUniqueTID();
					$endString = " endPoint=\"$curEPTID\"";
					$curNCTIMEX = "<TIMEX$tever $tidTagName=\"$curEPTID\">";	#still need to add VAL
					$nonConsumingTIMEXes[$numNonConsumingTIMEXes] = $curNCTIMEX;
					$numNonConsumingTIMEXes++;
				}


				#make actual duration changes
				if ($useDurationChanges == 1){
					$string =~ s/$curPhrase/<TIMEX$tever TYPE=\"DURATION\"$beginString$endString $valTagName=\"$curDurValue\">$curPhrase<\/TIMEX$tever>/gi;
				}
			} 
 		}
   	}
    }



    #get rid of number delimiters  ###  NEED TO MAKE SURE THIS WORKS AT BEGINNING AND END
    $string =~ s/NUM_START//g;
    $string =~ s/NUM_END//g;
    $string =~ s/NUM_ORD_START//g;
    $string =~ s/NUM_ORD_END//g;


    ###########################################
    ########  End of code by jfrank  ##########
    ###########################################

##
## End of jfrank additions ##
    
    # ---------------------
    # Clean up tags

    # Clean up sentence tags
#    while($string =~ s/(<TIMEX[^>]*>)(<s>)/$2$1/oi) {}
#    while($string =~ s/(<\/s>)(<\/TIMEX[^>]*>)/$2$1/oi) {}
    
    # ---------------------
    # merge timex tags here

    #########################
    ###  added by jfrank  ###
    #########################

    #insert tids into TIMEX3 tags
    $string = &addTIDs($string);    


    ##########################
    ### end of jfrank code ###
    ##########################

    return($string);

} # TE_TagTIMEX


########################################
sub TE_AddAttributes {
    
    my($string, $RefTime, $TE, $output);
    my($temp1, $temp2, $temp3, $temp4, $temp5, $temp6, $temp7);
    my($Attributes, $Dir, $b4, $EndTag, $lead, $STag);
    my($Comment, $Tag, $AorP, $Offset);
    my($Hour, $Min, $twelve, $DorS, $Zone, $TimeZone);
    my($format, $RTday, $RTmonth);
    my($POS, $POS2, $VB, $verb2, $RelDir, $textDir);
    my($test, $offset, $Reason);
    my($Y, $M, $D, $YM, $Day, $Year, $RefM);
    my($DOW, $DOM, $RefDOM, $RefDOW);
    my($Month, $NMonth);
    my($Season, $hol);
    my($W_b4, $W_aft, $trail, $trailtext);
    my($next_word, $preceding_word);
    my($Exact, $Unit, $Extra, $junk);
    my($Val, $Val1, $FoundVal);
    my($Type, $orig_string, $TEstring);
    
    ($string, $RefTime) = @_;

    $output = "";
    $orig_string = $string;

    while($string =~ /(<\/TIMEX$tever>)/io) {
	$Attributes = "";
	
	$b4     = $`;
	$EndTag = $1;
	$string = $';

	if($b4 =~ /(.*)(<TIMEX$tever[^>]*>)/sio) {
	    $lead     = $1;
	    $output  .= $1;
	    $STag     = $2;
	    $TE = $';
	} else {
	    print STDERR "** ERROR ** - No beginning TIMEX tag!\n";
	    #print STDERR "   --Original string--\n$orig_string\n-----\n";
	    #print STDERR "   --B4--\n$b4\n--string--\n$string\n-----\n";
	    
	}

	$STag =~ /TYPE=\"(\w+)\"/oi;
	$Type = lc($1);
	
	# find the string
	$TEstring = $TE;
	$TEstring =~ s/<[^>]+>//go;
	$TEstring =~ s/\n/ /go;
	if($TE_DEBUG) { $Attributes .= " TEXT=\"$TEstring\""; }

	# find preceding, next word 
	if($output =~ /.*$OT+(\w+)$CT+/os) {
	    $junk  = $';
	    $preceding_word = lc($2);
	    if($junk =~ /\"/o) { $preceding_word = ""; }
	} else { $preceding_word = ""; }

	if($string =~ /$OT+(\w+)$CT+/os) {
	    $junk  = $`;
	    $next_word = lc($2);
	    if($junk =~ /\"/o) { $next_word = ""; }
	} else { $next_word = ""; }

	$FoundVal = 0;

	# type=date
	if($Type eq "date") {
	    
	    # Now rules requiring RefTime
	    if($RefTime && ($RefTime =~ /\d\d\d\d/o)) {
		# yesterday, today, tomorrow, tonight
		# this (morning|afternoon|evening)
		# Friday the 13th

		# Handle relative expressions requiring relative direction
		if(!$FoundVal && ($TE_HeurLevel > 1)) {
		    $Reason = "";
		    $verb2  = "";
		    $POS2   = "";
		    
		    # find the relevant verb and POS
		    if($lead   =~
		       /.*<LexTagName[^>]*pos=\"?(VBP|VBZ|VBD|MD)[^>]*>(\'?\w+)/sio) {
			$POS = $1; $VB  = lc($2);
			$' =~ /pos=\"(VB[A-Z]?)\"[^>]*>(\w+)/;
			$POS2 = $1; $verb2 = $2;
		    } elsif($string =~
			    /<$LexTagName[^>]*pos=\"?(VBP|VBZ|VBD|MD)[^>]*>(\'?\w+)/io) {
			$POS = $1; $VB  = lc($2);
			$' =~ /pos=\"?(VB[A-Z]?)\"[^>]*>(\w+)/;
			$POS2 = $1; $verb2 = $2;
		    } elsif($output =~
			    /.*<$LexTagName[^>]*pos=\"?(VBP|VBZ|VBD|MD)[^>]*>(\'?\w+)/sio) {
			$POS = $1; $VB = lc($2);
			$' =~ /pos=\"?(VB[A-Z]?)[^>]*>(\w+)/;
			$POS2 = $1; $verb2 = $2;
		    } else {
			$POS = "X"; $VB  = "NoVerb";
		    }

		    if(($POS =~/(VBP|VBZ|MD)/io) &&
		       (($output =~ /$OT+going$CT+\s+$OT+to$CT+/sio) ||
			($string =~ /$OT+going$CT+\s+$OT+to$CT+/sio))) {
			$POS = "MD"; $VB  = "going_to";
		    }
		    
		    if($TE_DEBUG > 1) {
			$Attributes .= " verb=\"$VB:$POS\"";
			if($POS eq "MD") {
			    $Attributes .= " verb2=\"$verb2:$POS2\""; }
		    }

		    $RelDir = 0;
		    if($POS eq "VBD") {
			$RelDir = -1;
			$Reason = "$POS";
		    }
		    elsif($POS eq "MD") {
			if($VB =~ /(will|\'ll|going_to)/io) {
			    $RelDir = 1;
			    $Reason = "$POS:$VB";
			}
			elsif($verb2 eq "have") {
			    $RelDir = -1;
			    $Reason = "$POS:$VB";
			}
			elsif(($VB =~ /((w|c|sh)ould|\'d)/o)
			      && ($POS2 eq "VB")) {
			    $RelDir = 1;
			    $Reason = "$POS:$VB";
			}
			
		    }

		    # Heuristic Level > 2
		    if(($TE_HeurLevel > 2) && ($RelDir == 0)) {
			# since / until
			if($preceding_word eq "since") {
			    $RelDir = -1;
			    $Reason = "since";
			} elsif($preceding_word eq "until") {
			    $RelDir = 1;
			    $Reason = "until";
			}
			    
		    } # if($TE_HeurLevel > 2)

		    
		    # We found a Relative direction
		    if($RelDir) {

			# Month name present
			if($TEstring =~ /\b($TEFixedHol|$TEmonth|$TEmonthabbr)\b/io) {
			    $1 =~ /(\w{3})/;
			    $M = $Month2Num{lc($1)};
			    $RefTime =~ /((\d{4})\d{4})/o;
			    $RefTime = $1;
			    $Y = $2;

			    # Is numeric day or week of present? 
			    if($TEstring =~ /($TEOrdinalWords|$TENumOrds)\s+week(end)?\s+(of|in)/io) {
				$temp1 = lc($1);
				if($temp1 =~ /\d+/o) { $temp2 = $&; }
				else { $temp2 = $TE_Ord2Num{$temp1}; }
				if($temp2 > 4) { $Attributes .= " ERROR=\"BadWeek\""; }
				if($TEstring =~ /weekend/io) { $D = ($temp2*7)-5; }
				else { $D = ($temp2*7)-3; }
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				$test = $RefTime;
			    }
			    elsif($TEstring =~ /(\d\d?)/o) {
				$D = $1;
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				$test = $RefTime;
			    }
			    # Ordinal day given
			    elsif($TEstring =~ /($TEOrdinalWords)/io) {
				$D = $TE_Ord2Num{lc($1)};
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				$test = $RefTime;
			    }
			    elsif($TEstring =~ /\bides\b/io) {
				if(($M == 3) || ($M == 5) ||
				   ($M == 7) || ($M == 10)) { $D = 15; }
				else { $D = 13; } 
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				$test = $RefTime;
			    }
			    elsif($TEstring =~ /\bnones\b/io) {
				if(($M == 3) || ($M == 5) ||
				   ($M == 7) || ($M == 10)) { $D = 7; }
				else { $D = 5; } 
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				$test = $RefTime;
			    }
			    # Fixed Holiday
			    elsif($TEstring =~ /($TEFixedHol)/io) {
				$hol = lc($1);
				$hol =~ s/\s+//go;
				$FixedHol2Date{$hol} =~ /(\d\d)(\d\d)/o;
				$M = $1;
				$D = $2;
				$format = "%4d%02d%02d";
				$Val = sprintf($format, $Y, $M, $D);
				if($TEstring =~ /(eve)/io) {
				    $Val = &OffsetFromRef($Val, -1);
				    $Val =~ /(\d\d\d\d)(\d\d)(\d\d)/o;
				    $Y = $1;
				    $M = $2;
				    $D = $3;
				}
				$test = $RefTime;
			    }
			    # just a month
			    else {
				$format = "%4d%02d";
				$Val = sprintf($format, $Y, $M);
				$RefTime =~ /(\d{6})/o;
				$test = $1;
			    }
			    
			    if(($RelDir > 0) && ($test > $Val)) {
				$Y++;
			    } elsif(($RelDir < 0) && ($test < $Val)) {
				$Y--;
			    }
			    $Val = sprintf($format, $Y, $M, $D);

			    if(($TEstring =~
				/the\s+(\w+\s+)?week(end)?\s+(of|in)/io) && $D) {
				$Val = &Date2Week($Val);
				if($TEstring =~ /weekend/io) { $Val .= "WE"; }
			    }

			    if($TEstring =~ /$TEFixedHol/io) {
				$Attributes .= " ALT_VAL=\"$Val\"";
			    } else { $Attributes .= " $valTagName=\"$Val\""; }
			    if(($TE_DEBUG > 1) && $Reason) {
				$Attributes .= " reason=\"$Reason\""; }
			    $FoundVal = 1;
			    
			} # if month name present

			# Nth DOW Hol
			elsif($TEstring =~ /($TENthDOWHol)/io) {
			    $temp1 = $NthDOWHol2Date{lc($1)};
			    $temp1 =~ /(\d\d?)-(\d)-(\d)/o;
			    $M = $1;
			    $temp2 = $2;
			    $temp3 = $3;
			    $RefTime =~ /\d{4}/o;
			    $Y = $&;
			    $D = NthDOW2Date($M, $temp2, $temp3, $Y);
			    $Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    $RefTime =~ /\d{8}/o;
			    $test = $&;
			    if(($RelDir > 0) && ($test > $Val)) {
				$Y++;
				$D = NthDOW2Date($M, $temp2, $temp3, $Y);
			    } elsif(($RelDir < 0) && ($test < $Val)) {
				$Y--;
				$D = NthDOW2Date($M, $temp2, $temp3, $Y);
			    }
			    $Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    $Attributes .= " ALT_VAL=\"$Val\"";
			    $FoundVal = 1;
			}
			
			elsif($TEstring =~ /\b$TELunarHol\b/io) {
			    $RefTime =~ /\d{4}/o;
			    $Y = $&;
			    $Val = EasterDate($Y);
			    if($TEstring =~ /\bgood\s+friday\b/io) {
				$Val = &OffsetFromRef($Val, -3); }
			    elsif($TEstring =~ /\b(shrove\s+tuesday|mardis\s+gras)\b/io) {
				$Val = &OffsetFromRef($Val, -47); }
			    elsif($TEstring =~ /\bash\s+wednesday\b/io) {
				$Val = &OffsetFromRef($Val, -46); }
			    elsif($TEstring =~ /\bpalm\s+sunday\b/io) {
				$Val = &OffsetFromRef($Val, -7); }

			    $RefTime =~ /\d{8}/o;
			    $test = $&;
			    if(($RelDir > 0) && ($test > $Val)) {
				$Y++;
				$Val = EasterDate($Y);
				if($TEstring =~ /\bgood\s+friday\b/io) {
				    $Val = &OffsetFromRef($Val, -3); }
				elsif($TEstring =~ /\b(shrove\s+tuesday|mardis\s+gras)\b/io) {
				    $Val = &OffsetFromRef($Val, -47); }
				elsif($TEstring =~ /\bash\s+wednesday\b/io) {
				    $Val = &OffsetFromRef($Val, -46); }
				elsif($TEstring =~ /\bpalm\s+sunday\b/io) {
				    $Val = &OffsetFromRef($Val, -7); }
			    } elsif(($RelDir < 0) && ($test < $Val)) {
				$Y--;
				$Val = EasterDate($Y);
				if($TEstring =~ /\bgood\s+friday\b/io) {
				    $Val = &OffsetFromRef($Val, -3); }
				elsif($TEstring =~ /\b(shrove\s+tuesday|mardis\s+gras)\b/io) {
				    $Val = &OffsetFromRef($Val, -47); }
				elsif($TEstring =~ /\bash\s+wednesday\b/io) {
				    $Val = &OffsetFromRef($Val, -46); }
				elsif($TEstring =~ /\bpalm\s+sunday\b/io) {
				    $Val = &OffsetFromRef($Val, -7); }
			    }
			    $Attributes .= " ALT_VAL=\"$Val\"";
			    $FoundVal = 1;
			}
			# Day of week, no month
			elsif($TEstring =~ /($TEday)/io) {
			    $temp1 = lc($');
			    $DOW = $Day2Num{lc($1)};

			    $RefDOW = &Date2DOW($RefTime);
			    $offset = $DOW - $RefDOW;
			    if(($RelDir > 0) && ($offset < 0)) {
				$offset += 7; }
			    if(($RelDir < 0) && ($offset > 0)) {
				$offset -= 7; }
			    $Val = &OffsetFromRef($RefTime, $offset);
			    if($temp1 =~ /morning/io) { $Val .= "MO"; }
			    elsif($temp1 =~ /afternoon/io) { $Val .= "AF"; }
			    elsif($temp1 =~ /evening/io) { $Val .= "EV"; }
			    elsif($temp1 =~ /night/io) { $Val .= "TNI"; }
			    
			    $Attributes .= " $valTagName=\"$Val\"";

			    $FoundVal = 1;
			}
			# (the|this) weekend
			elsif($TEstring =~ /weekend/io) {
			    $RefDOW = &Date2DOW($RefTime);
			    # val1 = saturday
			    if($RelDir > 0) {
				$Val1 = &OffsetFromRef($RefTime, -1*$RefDOW+6);
			    } elsif($RelDir < 0) {
				$Val1 = &OffsetFromRef($RefTime, -1*$RefDOW-1);
			    }
			    $Val = &Date2Week($Val1);
			    $Attributes .= " $valTagName=\"${Val}WE\"";
			    $FoundVal = 1;
			}

		    } # if($RelDir)

		    # assume dates near the reftime are this year
		    elsif(($TE_HeurLevel > 2) &&
			  ($TEstring =~ /\b($TEFixedHol|$TEmonth|$TEmonthabbr|$TENthDOWHol|$TELunarHol)\b/io)) {
			$RefTime =~ /((\d{4})(\d\d)(\d\d))/o;
			$RefTime = $1;
			$RTmonth = $3;
			$RTday   = $4;
			$Y = $2;
			$D = 0;
			$Val = "";

			if(($TEstring =~ /\b($TEmonth|$TEmonthabbr)\b/io) &&
			   ($TEstring !~ /\b(fool|may\s+day)/io)) {
			    $1 =~ /(\w{3})/;
			    $M = $Month2Num{lc($1)};
			} elsif($TEstring =~ /\b$TELunarHol\b/io) {
			    $Val = EasterDate($Y);
			    if($TEstring =~ /\bgood\s+friday\b/io) {
				$Val = &OffsetFromRef($Val, -3); }
			    elsif($TEstring =~ /\b(shrove\s+tuesday|mardis\s+gras)\b/io) {
				$Val = &OffsetFromRef($Val, -47); }
			    elsif($TEstring =~ /\bash\s+wednesday\b/io) {
				$Val = &OffsetFromRef($Val, -46); }
			    elsif($TEstring =~ /\bpalm\s+sunday\b/io) {
				$Val = &OffsetFromRef($Val, -7); }
			    $Val =~ /\d\d\d\d(\d\d)(\d\d)/o;
			    $M = $1;   $D = $2;
			} elsif($TEstring =~ /$TEFixedHol/io) {
			    $hol = lc($1);
			    $hol =~ s/\s+//go;
			    $FixedHol2Date{$hol} =~ /(\d\d)(\d\d)/o;
			    $M = $1;
			    $D = $2;
			    if($TEstring =~ /\beve\b/io) {
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
				$offset = -1;
				$Val = &OffsetFromRef($Val, $offset);
				$Val =~ /\d\d\d\d(\d\d)(\d\d)/o;
				$M = $1;
				$D = $2;
			    }
			} elsif($TEstring =~ /($TENthDOWHol)/io) {
			    $temp1 = $NthDOWHol2Date{lc($1)};
			    $temp1 =~ /(\d\d?)-(\d)-(\d)/o;
			    $M = $1;
			    $temp2 = $2;
			    $temp3 = $3;
			    $RefTime =~ /\d{4}/o;
			    $Y = $&;
			    $D = NthDOW2Date($M, $temp2, $temp3, $Y);
			    $Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			}

			if((abs($M - $RTmonth) < 2) ||
			   (abs($M - $RTmonth) == 11))  {
			    # guess nearby instance of date

			    # fix year if needed
			    if(($M - $RTmonth) == 11) { $Y--; }
			    elsif(($RTmonth - $M) == 11) { $Y++; }

			    # Is numeric day present?
			    if($Val) {1;}
			    elsif($TEstring =~ /($TEOrdinalWords|$TENumOrds)\s+week(end)?\s+(of|in)/io) {
				$temp1 = lc($1);
				if($temp1 =~ /\d+/o) { $D = $&; }
				else { $D = $TE_Ord2Num{$temp1}; }
				if($D > 4) { $Attributes .= " ERROR=\"BadWeek\""; }
				if($TEstring =~ /weekend/io) { $D = ($D*7)-5; }
				else { $D = ($D*7)-3; }
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    } elsif($TEstring =~ /(\d\d?)/o) {
				$D = $1;
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    }
			    # Ordinal day given
			    elsif($TEstring =~ /($TEOrdinalWords)/io) {
				$D = $TE_Ord2Num{lc($1)};
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    }
			    elsif($TEstring =~ /\bides\b/io) {
				if(($M == 3) || ($M == 5) ||
				   ($M == 7) || ($M == 10)) { $D = 15; }
				else { $D = 13; } 
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    }
			    elsif($TEstring =~ /\bnones\b/io) {
				if(($M == 3) || ($M == 5) ||
				   ($M == 7) || ($M == 10)) { $D = 7; }
				else { $D = 5; } 
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D);
			    }

			    elsif($D) {
				$Val = sprintf("%4d%02d%02d", $Y, $M, $D); }
			    else {
				$Val = sprintf("%4d%02d", $Y, $M); }

			    if(($TEstring =~ /the\s+(\w+\s+)?week(end)?\s+(of|in)/io) && $D) {
				$temp1 = $Val;
				$Val = &Date2Week($Val);
				if($TEstring =~ /weekend/io) { $Val .= "WE"; }
			    }
			    if($TEstring =~ /($TEFixedHol|$TENthDOWHol|$TELunarHol)/io) {
				$Attributes .= " ALT_VAL=\"$Val\""; }
			    else { $Attributes .= " $valTagName=\"$Val\""; }
			    if($TE_DEBUG > 1) {
				$Attributes .= " reason=\"near_reftime\""; }

			    
			} # abs($M - $RTmonth) < 2
		    } # dates near the reftime

		    else {
			# Handle generics
			if($TEstring =~ /($TEday)/io) {
			    $DOW = $Day2Num{lc($1)};
			    unless($DOW) { $DOW += 7; }
			    $Val = sprintf("-W-%d", $DOW)
			    }
		    }
		    
		}  # (!$FoundVal && ($TE_HeurLevel > 1))
		
	    } # if($RefTime)
	}  # if type=date

	# type=time
	elsif($Type eq "time") {

	    if($TEstring =~ /(exact|precise|sharp|on\s+the\s+dot)/io) {
		$Exact = 1; }
	    elsif($output =~ /(exactly|precisely)/io) { $Exact = 1; }
	    else { $Exact = 0; }

	    
	    # AM/PM
	    if($TEstring =~ /(\d\d?)(:(\d\d))?\s*([ap])\.?\s*m\.?/oi) {
		$Hour = $1;
		$Min  = $3;
		$AorP = lc($4);

		if($TEstring =~ /half\s+past/io) { $Min = 30; }
		elsif($TEstring =~ /quarter\s+after/io) { $Min = 15; }
		elsif($TEstring =~ /quarter\s+(of|before|to)/io) {
		    $Min = 45;    $Hour--;
		}
		elsif($TEstring =~ /(\d+|\w+(-\w+)?)\s+(minutes?\s+)?(before|after|past|of|to|until)/io) {
		    $Min = Word2Num(lc($1));
		    $temp1 = $4;
		    if($temp1 =~ /(of|before|to|until)/io) {
			$Min = 60 - $Min;  $Hour--; }
		}

		if(($AorP eq "p") && ($Hour < 12)) { $Hour += 12; }
		if(($AorP eq "a") && ($Hour == 12)) { $Hour = 0; }
		if(defined($Min)) { $Val = sprintf("%02d%02d", $Hour, $Min); }
		elsif($Exact) { $Val = sprintf("%02d00", $Hour); }
		else { $Val = sprintf("%02d", $Hour); }
		$Attributes .= " $valTagName=\"T$Val$TimeZone\"";
		if(($Hour>24) || (defined($Min) && ($Min>59))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		if(($AorP eq "a") && ($Hour>12)) {
		    $Attributes .= " ERROR=\"Inconsistent\""; }
		$FoundVal = 1;
	    }
	    elsif($TEstring =~ /(\w+\s+)?(\w+\s+)?([\w\-]+)\s+([ap])\.?\s*m\.?/oi) {
		undef $Min;
		$AorP = lc($4);
		$temp1 = $1; $temp2 = $2; $temp3 = $3;
		if(defined($temp1) && Word2Num($temp1) &&
		   defined($temp2) && Word2Num($temp2) &&
		   Word2Num($temp3)) {
		    $Hour = Word2Num($temp1);
		    $Min  = Word2Num($temp2 . $temp3);
		} elsif(defined($temp1) && Word2Num($temp1) &&
			!defined($temp2)) {
		    $Hour = Word2Num($temp1);
		    $Min  = Word2Num($temp3);
		} else { $Hour = Word2Num($temp3); }

		if($TEstring =~ /half\s+past/io) { $Min = 30; }
		elsif($TEstring =~ /quarter\s+after/io) { $Min = 15; }
		elsif($TEstring =~ /quarter\s+(of|before|to|until)/io) {
		    $Min = 45;    $Hour--;
		}
		elsif($TEstring =~ /(\d+|\w+(-\w+)?)\s+(minutes?\s+)?(before|after|past|of|to|until)/io) {
		    $temp1 = $4;
		    $Min = Word2Num(lc($1));
		    if($temp1 =~ /(of|before|to|until)/io) {
			$Min = 60 - $Min;  $Hour--; }
		}
		
		if(($AorP eq "p") && ($Hour < 12)) { $Hour += 12; }
		if(($AorP eq "a") && ($Hour == 12)) { $Hour = 0; }
		
		if(defined($Min)) { $Val = sprintf("%02d%02d", $Hour, $Min); }
		elsif($Exact) { $Val = sprintf("%02d00", $Hour); }
		else { $Val = sprintf("%02d", $Hour); }
		$Attributes .= " $valTagName=\"T$Val$TimeZone\"";
		if(($Hour>24) ||
		   ((defined($Min)) && ($Min > 59)) ||
		   (($AorP eq "a")  && ($Hour > 12))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		$FoundVal = 1;
	    }

	    # in the (morning|evening)
	    elsif($TEstring =~
		  /(\d\d?)(:(\d\d)|\s+o\'clock)?\s+(in\s+the\s+(morning|afternoon|evening)|at\s+night)/oi) {
		$Hour = $1;
		$Min  = $3;
		$AorP = lc($4);
		if(($AorP =~ /(afternoon|evening|night)/io) && ($Hour < 12)) {
		    $Hour += 12; }
		if(($AorP =~ /morning/io) && ($Hour == 12)) { $Hour = 0; }
		if($TEstring =~ /half\s+past/io) { $Min = 30; }
		elsif($TEstring =~ /quarter\s+after/io) { $Min = 15; }
		elsif($TEstring =~ /quarter\s+(of|before|to)/io) {
		    $Min = 45;    $Hour--;
		}
		elsif($TEstring =~ /(\d+|\w+(-\w+)?)\s+minutes?\s+(before|after|past|of|to|until)/io) {
		    $Min = Word2Num(lc($1));
		    $temp1 = $3;
		    if($temp1 =~ /(of|before|to|until)/io) {
			$Min = 60 - $Min;  $Hour--; }
		}

		if($Min) { $Val = sprintf("%02d%02d", $Hour, $Min); }
		elsif($Exact) { $Val = sprintf("%02d00", $Hour); }
		else { $Val = sprintf("%02d", $Hour); }
		$Attributes .= " $valTagName=\"T$Val\"";
		if(($Hour>24) || (defined($Min) && ($Min>59))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		if(($AorP =~ /morning/io) && ($Hour>11)) {
		    $Attributes .= " ERROR=\"Inconsistent\""; }
		$FoundVal = 1;
	    }
	    
	    elsif(($TEstring =~
		   /([a-z]+)(\s+o\'clock)?\s+(in\s+the\s+(morning|afternoon|evening)|at\s+night)/oi) &&
		  ($temp1 = Word2Num($1)) && ($temp1 < 13)) {
		$Hour = $temp1;
		$AorP = lc($3);
		if(($AorP =~ /(afternoon|evening|night)/io) && ($Hour <12)) {
		    $Hour += 12; }
		if(($AorP =~ /morning/io) && ($Hour == 12)) { $Hour = 0; }
		$Val = sprintf("%02d", $Hour);
		if($TEstring =~ /half\s+past/io) { $Val .= "30"; }
		elsif($TEstring =~ /quarter\s+after/io) { $Val .= "15"; }
		elsif($TEstring =~ /quarter\s+(of|before|to)/io) {
		    $Hour--; $Val = sprintf("%02d45", $Hour);  }
		elsif($TEstring =~ /(\d+|\w+(-\w+)?)\s+minutes?\s+(before|after|past|of|to|until)/io) {
		    $Min = Word2Num(lc($1));
		    $temp1 = $3;
		    if($temp1 =~ /(of|before|to|until)/io) {
			$Min = 60 - $Min;  $Hour--;
		    }
		    $Val = sprintf("%02d%02d", $Hour, $Min);
		}

		$Attributes .= " $valTagName=\"T$Val\"";
		if($Hour>24) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		if(($AorP =~ /morning/io) && ($Hour>11)) {
		    $Attributes .= " ERROR=\"Inconsistent\""; }
		$FoundVal = 1;
	    }
	    
	    #     o\'clock      - No AM/PM clue
	    # OR  the hour of  - No AM/PM clue
	    elsif((($TEstring =~ /(\w+)\s+o\'clock/oi) &&
		   ($temp1 = Word2Num($1)) && ($temp1 < 13)) ||
		  (($TEstring =~ /the\s+hour\s+of\s+(\w+)/oi) &&
		   ($temp1 = Word2Num($1)) && ($temp1 < 13)) ||
		  (($TEstring =~ /(\w+(-\w+)?)\s+(minutes?\s+)?(before|after|past|of|to|until)\s+(\w+)/oi) &&
		   ($temp2 = Word2Num($1)) &&
		   ($temp1 = Word2Num($5)) && ($temp1 < 13))
		  ) {
		undef $Min;
		$Tag = "ALT_VAL";
		$Comment = " COMMENT=\"No AM/PM info\"";

		$Hour = $temp1;
		$Val = sprintf("%02d", $Hour);
		if($TEstring =~ /half\s+past/io) { $Val .= "30"; }
		elsif($TEstring =~ /quarter\s+after/io) { $Val .= "15"; }
		elsif($TEstring =~ /quarter\s+(of|before|to)/io) {
		    $Hour--; $Val = sprintf("%02d45", $Hour);  }
		elsif($TEstring =~ /(\w+(-\w+)?)\s+(minutes?\s+)?(before|after|past|of|to|until)/io) {
		    $Min = Word2Num(lc($1));
		    $temp1 = $4;
		    if($temp1 =~ /(of|before|to|until)/io) {
			$Min = 60 - $Min;  $Hour--;
		    }
		    $Val = sprintf("%02d%02d", $Hour, $Min);
		}

		# Search for broader context
		if(($orig_string =~/morning/io) &&
		   ($orig_string !~/(afternoon|evening|night)/io)) {
		    $Tag = "VAL"; $Comment = "";
		} elsif(($orig_string !~/morning/io) &&
			($orig_string =~/(afternoon|evening|night)/io)) {
		    $Tag = "VAL"; $Comment = "";
		    $Hour += 12;
		    if(defined($Min)) {
			$Val = sprintf("%02d%02d", $Hour, $Min); }
		    else { $Val = sprintf("%02d", $Hour); }
		}

		$Attributes .= " $Tag=\"T$Val\"";
		$Attributes .= $Comment;
		if($Hour>24) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		$FoundVal = 1;
	    }  # No AM/PM clue

	    # military type time
	    elsif($TEstring =~ /(\d\d):?(\d\d)/oi) {
		$Hour = $1;
		$Min  = $2;
		$Val = sprintf("%02d%02d", $Hour, $Min);
		$Attributes .= " $valTagName=\"T$Val$TimeZone\"";
		if(($Hour>24) || (defined($Min) && ($Min>59))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		$FoundVal = 1;
	    }
	    elsif($TEstring =~ /(\d\d)(\d\d)\s+h(ou)rs?/oi) {
		$Hour = $1;
		$Min  = $2;
		$Val = sprintf("%02d%02d", $Hour, $Min);
		$Attributes .= " $valTagName=\"T$Val$TimeZone\"";
		if(($Hour>24) || (defined($Min) && ($Min>59))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		$FoundVal = 1;
	    }
	    elsif($TEstring =~ /\b(\d\d?)\s+hours?(\s+(\d\d?)\s+minutes?)?/oi) {
		$Hour = $1;
		$Min  = $3;
		if($Min) { $Val = sprintf("%02d%02d", $Hour, $Min); }
		else { $Val = sprintf("%02d", $Hour); }
		$Attributes .= " $valTagName=\"T$Val$TimeZone\"";
		if(($Hour>24) || (defined($Min) && ($Min>59))) {
		    $Attributes .= " ERROR=\"Bad Time\""; }
		$FoundVal = 1;
	    }
	    
	} # if type=time


	##############################
	###  Code added by jfrank  ###
	##############################

	# type=duration
	elsif($Type eq "duration") {



	}

	##############################
	###   end of jfrank code   ###
	##############################


	else {
	    print STDERR "Bad type assigned!! $Type\n";
	}

	# Add  MOD\'s
	if($TEstring =~ /\b(late|end)\b/io) {
	    $Attributes .= " MOD=\"LATE\"";
	}elsif($TEstring =~ /\bno\s+more\s+than\b/io){
	    $Attributes .= " MOD=\"EQUAL_OR_LESS\"";
	}elsif($TEstring =~ /\bmore\s+than\b/io){ 
	    $Attributes .= " MOD=\"MORE_THAN\"";
	} elsif($TEstring =~ /\b(early|start|beginning|dawn of)\b/io) {
	    $Attributes .= " MOD=\"EARLY\"";
	} elsif($TEstring =~ /\bmid(dle)?\b/io) {
	    $Attributes .= " MOD=\"MID\"";
	} elsif($TEstring =~ /\bat\s+least\b/io){
	    $Attributes .= " MOD=\"EQUAL_OR_MORE\"";
	}	
	if($TEstring =~ /(about|around|some)/io) {
	    $Attributes .= " MOD=\"APPROX\""; }

	$STag     =~ s/>/$Attributes>/;
	$output  .= "$STag$TE$EndTag";

    }  # While

    $output .= $string;

#####
#$output =~ s/<lex[^>]*>//g;
#$output =~ s/<\/lex>//g;
#####

    return($output);
    
} # TE_AddAttributes




########################################
## Purely internal subroutines
########################################



######################################## 
sub MonthLength {
    my($Month, $Year, $ML);
    ($Month, $Year) = @_;

    if(($Month == 2) && (IsLeapYear($Year))) { $ML = 29; }
    else { $ML = $TE_ML[$Month]; }
    return($ML);
} # End of subroutine MonthLength

######################################## 
sub DayOfYear {
    my($Month, $Year, $Day, $ISO, $DOY);
    ($ISO) = @_;

    if($ISO =~ /\A(\d\d\d\d)(\d\d)(\d\d)/o) {
	$Year = $1; $Month = $2; $Day = $3;
	$DOY = $TE_CumML[$Month - 1] + $Day;
	if(IsLeapYear($Year) && ($Month > 2)) { $DOY++; }
	return($DOY);
    } else { return(0); }

} # End of subroutine DayOfYear


######################################## 
sub Week2Date {
    # Returns the date of the Thursday in the specified week.
    my($ISOin, $ISOout, $DOY, $Week, $Year);
    my($Month, $Day, $ML);
    ($ISOin) = @_;

    if($ISOin =~ /(\d\d\d\d)W(\d\d)/o) {
	$Year = $1;
	$Week = $2;
	$DOY  = $Week*7 - 3;

	$Month = 1;
	$ML = MonthLength($Month, $Year);
	while($DOY > $ML) {
	    $Month++;
	    if($Month > 12) { return "00000002";}
	    $DOY -= $ML;
	    $ML = MonthLength($Month, $Year);
	}
	$ISOout = sprintf("%04d%02d%02d", $Year, $Month, $DOY);
	return($ISOout);
    } else { return "00000001"; }

}  # End of subroutine Week2Date


########################
## jfrank subroutines ##
########################

sub printNonConsumingTIMEXes{
	foreach my $curNCT (@nonConsumingTIMEXes){
		print "$curNCT\n";
	}
}

# -For input string, adds TIDS to TIMEX2 tags, then returns updated string
# -Uses global variable $highestID

sub addTIDs{
	my $string = shift;
	my $currentTID;

	#while ($string =~ /((<TIMEX$tever)([^>]*>))/g){
	#	my $curTag = $1;
	#	my $firstPart = $2;
	#	my $secondPart = $3;
	#
	#	unless ($curTag =~ / $tidTagName=/i){	#unless tag already has a TID
	#		$currentTID = &getUniqueTID();
	#		my $newTag = $firstPart . " $tidTagName=\"$currentTID\"" . $secondPart;
	#		$string =~ s/$curTag/$newTag/;
	#	}
	#}
	return $string;
}

sub getUniqueTID{
	my $curIDNum = $highestTID;
	$highestTID++;
	my $retVal = "t$curIDNum";
	return $retVal;
}

# Takes in an expression assumed to be a duration expression and returns a 
#   duration value, such as P3D for "3 days".  Other things assumed about 
#   the expressions:
#	-they may have POS tags, assuming opening tags are of the form <lex ...>
#	 and closing tags are of the form </lex>
#	-if they have numbers written out in words, i.e. "thirty seven", then
#	 the words have been tagged using deliminateNumbers(), thus, discluding
#	 POS tags, "thirty seven" would be tagged "NUM_STARTthirty sevenNUM_END" 

# Duration Format: PnYnMnDTnHnMnS


sub expressionToDuration{
	my $phrase = shift;
	my $multiplier = 1;  #only changes for special words like "decade", "week", etc..

	#note - some of the incorrect spelling in this hash is due to the generalized matching which will match things like "centurys"
	my %abbToTimeUnit = ("years" => "yr","year" => "yr","yrs" => "yr","yr" => "yr",
			     "months" => "mo","month" => "mo","mo" => "mo","mos" => "mo",
			     "days" => "da", "day" => "da",
			     "hours" => "hr", "hour" => "hr", "hrs" => "hr", "hr" => "hr",
			     "minutes" => "mi","minute" => "mi","mins" => "mi","min" => "mi",
			     "seconds" => "se","second" => "se","secs" => "se","sec" => "se",
			     "weeks" => "wk","week" => "wk","wks" => "wk","wk" => "wk",
			     "decades" => "de","decade" => "de","decs" => "de","dec" => "de",
			     "centurys" => "ct","century" => "ct","centuries" => "ct","centurie" => "ct",
			     "millenias" => "ml","millenia" => "ml","milleniums" => "ml","millenium" => "ml");

	#get rid of POS tags
	$phrase =~ s/<lex[^>]*>//g;
	$phrase =~ s/<\/lex>//g;

	#get rid of opening and closing tags
	$phrase =~ s/^$OT+//;
	$phrase =~ s/$CT+$//;


#####
#print STDERR "phrase is: $phrase\n";
#####


	#change number-words into actual numbers
	while ($phrase =~ /(NUM_START(.*?)NUM_END)/g){
		my $curPart = $1;
		my $curWordNum = $2;
		my $curNumNum = &wordToNumber($curWordNum);
		$phrase =~ s/$curPart/$curNumNum/;
	}
	while ($phrase =~ /(NUM_ORD_START(.*?)NUM_ORD_END)/g){
		my $curPart = $1;
		my $curWordNum = $2;
		my $curNumNum = &wordToNumber($curWordNum);
		$phrase =~ s/$curPart/$curNumNum/;
	}


	my %durVals = ("yr" => -1,"mo" => -1, "da" => -1, "hr" => -1, "mi" => -1, "se" => -1);
	my $curUnit;
	my $curVal;


	#i.e. "3 month", "6-day-old"
	if ($phrase =~ /^(\d*)[-\s]$TE_Units([-\s]old)?$/){
		$curVal = $1;
		$curUnit = $2;

	#i.e. "the past 3 months"
	} elsif ($phrase =~ /the\s([pl]ast|next)\s(\d*)\s($TE_Units(s)?)/){
		$curVal = $2;
		$curUnit = $4;
	#jbp i.e. "no more than"
	} elsif ($phrase =~ /^no\smore\sthan\s(\d*)\s$TE_Units(s)?$/i){
		$curVal = $1;
		$curUnit = $2;
	#jbp i.e. "more than" 	
	} elsif ($phrase =~ /^more\sthan\s(\d*)\s$TE_Units(s)?$/i){
		$curVal = $1;
		$curUnit = $2;
	#jbp i.e. "at least.. " 	
	} elsif ($phrase =~ /^at\sleast\s(\d*)\s$TE_Units(s)?$/i){
		$curVal = $1;
		$curUnit = $2;
	#i.e. "another thirteen months"
	} elsif ($phrase =~ /^another\s(\d*)\s$TE_Units(s)?$/){
		$curVal = $1;
		$curUnit = $2;

	############  NEED TO FIX THIS SO A NP OR VP COMES AT END
	#i.e. "for ten minutes following"
#        } elsif ($phrase =~ /^(the|for)\s(\d+)\s($TE_Units)(s)?\s(since|after|following|before|prior\sto|previous\sto)$/){ 
        } elsif ($phrase =~ /^the\s(\d+)\s($TE_Units)(s)?$/){ 
		$curVal = $1;
		$curUnit = $2;

	###########  NEED TO FIX THIS SO THAT SOMETHING COMES AFTER "OF"  ###############
	#i.e. "the first six months of", "the last 7 minutes of"
#	} elsif ($phrase =~ /^the\s(1|last|final)\s(\d+)\s$TE_Units(s)?\sof$/){
	} elsif ($phrase =~ /^the\s(1|last|final)\s(\d+)\s$TE_Units(s)?$/){
		$curVal = $2;
		$curUnit = $3;

	#i.e. "the eighth consecutive day in a row"
	} elsif ($phrase =~ /^the\s(\d+)\s(straight|consecutive)\s($TE_Units)(\s(in\sa\srow|consecutively))?$/){
		$curVal = $1;
		$curUnit = $3;

	#i.e. "the twenty ninth day straight"	
	} elsif ($phrase =~ /^the\s(\d*)\s($TE_Units)\s(straight|consecutively|in\sa\srow)$/){
		$curVal = $1;
		$curUnit = $2;

	#i.e. "four minutes"
	} elsif ($phrase =~ /^(\d+)\s($TE_Units)(s)?$/){
		$curVal = $1;
		$curUnit = $2;

	#i.e. "a decade", "a couple years"
        } elsif ($phrase =~ /^a\s((few|couple|couple\sof)\s)?($TE_Units(s)?)$/){
		$curVal = $1;
		$curUnit = $3;
		if (defined($curVal)){
			$curVal = "X"; 	#for underspecified values
		}else{
			$curVal = 1;
		}

	} else{
		print STDERR 'Unrecognized pattern in expressionToDuration';
		die "\n   Processed (POS tags removed and number words converted) pattern is: $phrase\n";
	}
	


	if ($curUnit =~ /\.$/) {chop($curUnit);}  #remove trailing period (in abbreviations)
	$curUnit = $abbToTimeUnit{$curUnit};

	#deal with special cases - week, decade, century, millenium
	if ($curUnit eq "wk"){
		$multiplier = 7;
		$curUnit = "da";
	} elsif ($curUnit =~ "de"){
		$multiplier = 10;
		$curUnit = "yr";
	} elsif ($curUnit =~ "ct"){
		$multiplier = 100;
		$curUnit = "yr";
	} elsif ($curUnit =~ "ml"){
		$multiplier = 1000;
		$curUnit = "yr";
	}
	if ($curVal =~ /^\d*$/){
		$curVal = $curVal * $multiplier;
	}

	$durVals{$curUnit} = $curVal;		
	


	
	my $durString = "P";
	unless ($durVals{"yr"} =~ /^-1$/){
		$durString = $durString . $durVals{"yr"} . "Y";
	}
	unless ($durVals{"mo"} =~ /^-1$/){
		$durString = $durString . $durVals{"mo"} . "M";
	}
	unless ($durVals{"da"} =~ /^-1$/){
		$durString = $durString . $durVals{"da"} . "D";
	}

	$durString .= "T";

	unless ($durVals{"hr"} =~ /^-1$/){
		$durString = $durString . $durVals{"hr"} . "H";
	}
	unless ($durVals{"mi"} =~ /^-1$/){
		$durString = $durString . $durVals{"mi"} . "M";
	}
	unless ($durVals{"se"} =~ /^-1$/){
		$durString = $durString . $durVals{"se"} . "S";
	}

	#if $durString ends in T
	if ($durString =~ /T$/){chop($durString);}

	return $durString;
}

#returns tids for the begin and endpoints of an expression in the format "btid:etid"
sub expressionToPoints{
	my $phrase = shift;
	my $beginPoint = "";
	my $endPoint = "";
	

	#get rid of POS tags
	$phrase =~ s/<lex[^>]*>//g;
	$phrase =~ s/<\/lex>//g;

	#get rid of opening and closing tags
	$phrase =~ s/^$OT+//;
	$phrase =~ s/$CT+$//;

	#change number-words into actual numbers
	while ($phrase =~ /(NUM_START(.*?)NUM_END)/g){
		my $curPart = $1;
		my $curWordNum = $2;
		my $curNumNum = &wordToNumber($curWordNum);
		$phrase =~ s/$curPart/$curNumNum/;
	}
	while ($phrase =~ /(NUM_ORD_START(.*?)NUM_ORD_END)/g){
		my $curPart = $1;
		my $curWordNum = $2;
		my $curNumNum = &wordToNumber($curWordNum);
		$phrase =~ s/$curPart/$curNumNum/;
	}


	#i.e. "3 month", "6-day-old"
	if ($phrase =~ /^(\d*)[-\s]$TE_Units([-\s]old)?$/){
		## not doing anything yet

	#i.e. "the past 3 months"
	} elsif ($phrase =~ /the\s([pl]ast|next)\s\d*\s($TE_Units(s)?)/){
		my $curOp1 = $1;
		if ($curOp1 =~ /[pl]ast/){
			$endPoint= $unspecTIDVal;
		} elsif ($curOp1 =~ /next/){
			$beginPoint= $unspecTIDVal;
		}

	#i.e. "another thirteen months"
	} elsif ($phrase =~ /^another\s\d*\s$TE_Units(s)?$/){
		$beginPoint= $unspecTIDVal;

	} elsif ($phrase =~ /^no\smore\sthan\s\d*\s$TE_Units(s)?$/i){
		$beginPoint= $unspecTIDVal;
	} elsif ($phrase =~ /^more\sthan\s\d*\s$TE_Units(s)?$/i){
		$beginPoint= $unspecTIDVal;
	} elsif ($phrase =~ /^at\sleast\s\d*\s$TE_Units(s)?$/i){
		$beginPoint= $unspecTIDVal;
	#i.e. "for ten minutes following"
#        } elsif ($phrase =~ /^(the|for)\s\d+\s($TE_Units)s?\s(since|after|following|before|prior\sto|previous\sto)$/){ 
        } elsif ($phrase =~ /^the\s(\d+)\s($TE_Units)(s)?$/){ 

		my $curOp1 = $3;
		if ($curOp1 =~ /(since|after|following)/){
			$beginPoint= $unspecTIDVal;
		} elsif ($curOp1 =~ /(before|prior to|previous to)/){
			$endPoint= $unspecTIDVal;
		}

	###########  NEED TO FIX THIS SO THAT SOMETHING COMES AFTER "OF"  ###############
	#i.e. "the first six months of", "the last 7 minutes of" - note that "first" gets translated to "1"
#	} elsif ($phrase =~ /^the\s(1|last|final)\s(\d+)\s$TE_Units(s)?\sof$/){
	} elsif ($phrase =~ /^the\s(1|last|final)\s(\d+)\s$TE_Units(s)?$/){

		## not doing anything yet - pattern is too vague

	#i.e. "the eighth consecutive day in a row"
	} elsif ($phrase =~ /^the\s(\d+)\s(straight|consecutive)\s($TE_Units)(\s(in\sa\srow|consecutively))?$/){
		$endPoint= $unspecTIDVal;

	#i.e. "the twenty ninth day straight"	
	} elsif ($phrase =~ /^the\s(\d*)\s($TE_Units)\s(straight|consecutively|in\sa\srow)$/){
		$endPoint= $unspecTIDVal;

	#i.e. "four minutes","a decade"
	} elsif ($phrase =~ /^(\d+)\s($TE_Units)(s)?$/){
		## not doing anything yet - pattern is too vague

        } elsif ($phrase =~ /^a\s((few|couple|couple\sof)\s)?($TE_Units(s)?)$/){
		## not doing anything yet - pattern is too vague

	} else{
		print STDERR 'Unrecognized pattern in expressionToPoints';
		die "\n   Processed (POS tags removed and number words converted) pattern is: $phrase\n";
	}

	my $retVal = $beginPoint . ":" . $endPoint;
	return $retVal;

}

sub getUnspecifiedTID{
	my $retval = "";
	if ($useUnspecTID == 1){			
		$retval= $tiddef;
		if ($useDCT == 1){$retval = $tidDCT;}
	}
	return $retval;
}

###############################
## end of jfrank subroutines ##
###############################






# End of internal subroutines
###############################################

1;
# Copyright 2001 - The MITRE Corporation

__END__
The rest of this is to provide documentation through perldoc.

= pod Begin TempEx Documentation

=head1 Module TempEx

 Title:          Temporal Expressions
 Version:        1.05
 Purpose:        Tagging temporal expressions
 Author:         Dr. George Wilson
 Organization:   The MITRE Corporation
 email:          gwilson@mitre.org
 Date:		 Dec-2001

=head1 B<Copyright Notice>

=item Copyright 2001 The MITRE Corporation

=item Use of this code is subject to a licensing agreement.

=item

Better documentation is planned, but
right now you are stuck with this.

 Usage

 There are two main functions and two variables to control behaviour.
 
 Function: TE_TagTIMEX
    The input is assumed to be a sentence that has been tagged
    with part-of-speech tags. The output is the same sentence
    with additional tags to mark time expressions. The part of
    speech tagging is assumed to be compatible with the current
    version of the prelembic tagger that comes with the alembic
    distribution.

 Function: TE_AddAttributes
    The function takes two input arguments: a sentence and a
    reference time. The sentence is assumed to be a string that
    has been tagged with part-of-speech tags and for time expressions.
    The reference time is a string in the format YYYYMMDDHHMM.
    The output is the same sentence with attributes added to the time
    tags. Which rules are used and the extent of the attributes are
    controlled by the variables TE_DEBUG and TE_HeurLevel.

 Function: Date2ISO
    The function takes a single string as an input arguement
    and attempts to reformat it into an ISO date. This may
    be useful for making driver programs.
    
 Variable: Debug flag
   TE_DEBUG = 0          means only required output (default)
                         This will be the TYPE and VAL if applicable.
   TE_DEBUG = 1          include TEXT=XXX attribute
   TE_DEBUG = 2          all output - right now, that includes
			 information about rules used and interpretation
			 of verbs.

 Variable: Heuristic Level
   TE_HeurLevel = 0      only absolute dates are used (RefTime not used)
   TE_HeurLevel = 1      Allow rules based on strong linguistics markers
   TE_HeurLevel = 2      also use solid verb rules
   TE_HeurLevel = 3      additional heuristics (default)


=cut


v
