package Tokenize;


# Tokenize.pm
# -----------

# Create output in one-sentence per line format and tokenize
# punctuation.
#
# Reads from standard input and writes to standard output. Use -s flag
# to suppress paragraph mode (the default). Paragraph mode and
# sentence mode are almost equivalent except for abbreviations at the
# end of a line.




# Main Loop 
# ---------

sub Tokenize_File
{
    # Variables 

    local $punctuation  =  '[.,!?\'\`\";:]';
    local $bracket      =  '[][(){}]';        # < and > removed (HTML tags)
    local $end_punct    =  '[.!?]';

    &Read_Abbrevs();

    # read arguments
    if ( $_[0] eq "-s" ) {
		shift @_; 
    } else { # paragraph mode
		$/ = ""; 	
	}
	
    my ($in_file,$out_file) = @_;
    open IN, $in_file or die "Cannot open $in_file\n";
    open OUT, "> $out_file" or die "Cannot open $out_file\n";

    while ( $line = <IN> ) {

    	$line =~ s/^\s+//;
    	$line =~ s/\s+$//;
		# keep paragraph markers, revisit this
    	if ( $line =~ /^<P>/ ) {
			$line =~ s/^<P>//;
			print OUT "\n<P>\n\n";
		}
    	@line = split /\s+/ , $line; # put tokens on array

    	for ( $i = 0 ; $i <= $#line ; $i++ ) {
			$token = $line[$i];
			if ( $token =~ /$punctuation|$bracket/ ) {
				$token = &Split_Punctuation($token);
				$token = &Restore_Abbrevs($token);
				$token = &Add_EOS_Marker($token,$i);
			} else { 
				$token .= " ";
			}
			$token = &Split_Contractions($token);
			print OUT $token;
		}
    	if ( $token =~ /\n/ ) {
			print OUT "\n";
		} else {
			print OUT "\n\n";
		}
    }
	
    $/ = "\n";	# reset input separator

    close IN; 
    close OUT; 
}



# Function Definitions
# --------------------


# Copy abbreviations and initial tokens from lists into hashes.

sub Read_Abbrevs
{
    foreach $abb ( @abbrevs ) { $abbrevs{$abb}++; }
    foreach $abb ( @end_abbrevs ) { $end_abbrevs{$abb}++; }
    foreach $tok ( @initial_tokens ) { $initial_tokens{$tok}++; }
}


# Split punctuation at beginning and end of token. Maximum of three
# punctuation marks at end of token is allowed. Possibly better not
# to split closing brackets if token contains corresponding closing
# bracket (but what about putting one word between brackets -->
# exception).

sub Split_Punctuation
{
    local ( $token ) = @_;
    $token =~ s/($punctuation|$bracket)$/ $&/;
    $token =~ s/($punctuation|$bracket) .$/ $&/;
    $token =~ s/($punctuation|$bracket) . .$/ $&/;
    $token =~ s/^($punctuation|$bracket)/$& /;
    $token =~ s/^. ($punctuation|$bracket)/$& /;
    $token =~ s/^. . ($punctuation|$bracket)/$& /;
    return $token;
}


# Restore abbreviations. If a period is preceded by a number of
# non-whitespace characters, then check whether those characters with
# the period are an abbreviation. If so, glue them back together.

sub Restore_Abbrevs
{
    local ( $token ) = @_;
    if ( $token =~ /(\S+) \./ ) {
		$tmp = "$1.";
		if ( &Abbrev($tmp) ) {
			$token =~ s/(\S+) \./$1\./;
		}
	}
    return $token;
}

# Abbreviation Lookup. A token is an abbreviation either if it is on
# the %abbrevs hash or if it matches the regular expression "(^[A-Z]\.)+",
# which encodes initials.

sub Abbrev
{
    local ( $token ) = @_;
    $abbrevs{$token} or $token =~ /^([A-Z]\.)+$/;
}


# Adding end-of-sentence markers (ie newlines).

# First check for a space followed by a period, exclamation mark or
# question mark. These may be followed by one other punctuation, which
# is either a quote or a closing bracket. Otherwise check whether the
# token is a possible sentence-final abbreviations followed by a
# possible sentence-intitial token. In other cases there will be no
# end-of-sentence.

sub Add_EOS_Marker
{
    local ( $token , $i ) = @_;
    if ( $token =~ / [.!?]( [\"\)])?$/ ) {
		$token .= "\n";
	} elsif ( $end_abbrevs{$token} 
			  and $i < $#line 
			  and $initial_tokens{$line[$i+1]} ) {
		$token .= "\n";
	} else {
		$token .= " ";
	}
    return $token;
}


# Splitting contractions.

sub Split_Contractions
{
    local ( $token ) = @_;
    $token =~ s/(\w+)\'re /$1 \'re /i;
    $token =~ s/(\w+)\'t /$1 \'t /i;
    $token =~ s/(\w+)\'ll /$1 \'ll /i;
    $token =~ s/(\w+)\'ve /$1 \'ve /i;
    $token =~ s/(\w+)\'d /$1 \'d /i;
    $token =~ s/(\w+)\'s /$1 \'s /i;
    $token =~ s/(\w+)\'m /$1 \'m /i;

    $token =~ s/(\S+)\'s /$1 \'s /; # hack for for possessive 's

    return $token;
}



# Abbreviation Lists
# ------------------

# Most abbreviations below are taken from the Brown2 corpus. The
# @end_abbrevs array contains abbreviations that can occur at the end of
# a sentence, they are a subset of the sentence-final abbreviations in
# Brown2 (intials and some other garbage abbreviations were deleted).

@months = 
    qw( Jan. Feb. Mar. Apr. Jun. Jul. Aug. Sep. Sept. 
		Oct. Nov Dec. );

@titles = 
    qw( Dr. Gen. Rep. JR. Jr. MD. Miss. Mr. Mrs. Ms. Prof. Sr. 
		dr. rep. jr. miss. mr. mrs. ms. prof. sr. );

@states = 
    qw( ALA. Ala. Ariz. CALIF. Cal. Calif. Colo. Conn. 
		Dak. Del. FLA. Fla. Ga. ILL. IND. Ill. Ind. Kan. Kans. Ky. 
		MICH. MISS. Mass. Mich. Minn. Miss. Mo. Mont. Nev. 
		Okla. Ore. Penna. TEX. Tenn. Tex. Va. Wash. Wis. );

@geo = 
    qw( Av. Ave. Bldg. Blvd. Rd. St. av. ave. pl. rd. sq. st. );

@measures =
	qw( 10-yr. LB. cent. cm. ft. hr. lb. lb./cu. lbs. 
		mil. min. mm. m.p.h. oz. sec. seq. yr. );

@other = 
    qw( Assn. Bros. Cir. Co. Corp. Ct. D-Ore. Dist. ED. Eng. 
		Inc. Kas. LA. La. Ltd. MD. MO. Md. O.-B. O.-C. 
		P.-T.A. Pa. Prop. R-N.J. SP. SS. Tech. Ter. USN. Yok. 
		a.m. al. dept. e.g. etc. gm. i.d. i.e. inc. kc. mos.
		p.m. post-A.D. pro-U.N.F.P. );


@abbrevs = ( @months, @titles, @states, @geo, @measures, @other );

# dr. as end abbrev??

@end_abbrevs =
    ( @months, @states, @geo, @measures,
      qw( A.D. A.M. Ass. B.C. Bldg. Blvd. Co. Corp. 
		  D.C. Dist. Eng. Esq. I.Q. I.R.S. Inc. Jr.
		  La. Md. N.C. N.J. N.Y. O.E.C.D. P.M. Pa. 
		  R.P.M. SS. Sr. St. Tech. U.N. U.S. U.S.A. U.S.S.R. 
		  a.m. al. av. ave. cm. dr. esq. etc. gm. hr. jr. kc. lbs.
		  mos. p.m. dr. D-Ore. ) );


# The tokens below are some of the most frequent tokens to start a
# sentence, about 4000 of 6000 sentences in one of the Brown2 files
# start with these tokens. Also, none of these tokens is likely to
# follow an abbreviation in a sentence. The tokens in the second 
# list are added manually.

@initial_tokens_brown =
    qw ( The In But Mr. He A It And For "The They As At That This 
	Some If "I One On "We I While When So These Many An Under
	Although It's To Last After Mrs. "It's There We With She
	Its However, Both Despite "This By "There Most Among All 
	According No Meanwhile, "If Still, "It Such New Even 
	Because Also, Since U.S. More Not His Terms Moreover, 
	Another You Those Other First "We're Each Yet "They 
	Separately, Several "You Instead, What Indeed, That's 
	Ms. Here Like "But Of About Then, Yesterday, During "When 
	"A Now "So Your From Also Two Now, Their ); 

@initial_tokens_rest =
    qw ( Without );

@initial_tokens = ( @initial_tokens_brown, @initial_tokens_rest );


1;
