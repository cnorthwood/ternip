#!/usr/bin/perl -w
# Find aligned tags in files

#######################################################################
## Comparing TIMEX2 Annotations
## ----------------------------
##
## score_timex2.pl compares two input files and reports differences in
## the tags occurring in these files. The default configuration is
## for TIMEX2 tags. score_timex2.pl accepts inline sgml format and
## APF (ACE Program Format), a standoff annotation format. If scoring
## APF, the source file must be present in the same directory as
## the APF.  score_timex2.pl will automatically detect which format 
## is being scored, and if APF, will attempt to find the source file
## based on the filename, with the assumption that the source will
## have an extension of .sgm, .sgml, .SGM, or .SGML).
##
## WARNINGS / INPUT ASSUMPTIONS
## ----------------------------
##  1. All open and close tags are paired (i.e. no <TAG /> at this time)
##  2. No text inside of text  <TEXT> ... <TEXT> ... </TEXT> ... </TEXT>
##     (That really means the TEXT tag. For other tags it is OK.)
##
## USAGE
## -----
## Invoke this script as follows (assuming perl is in your path):
##    perl score_timex2.pl [-t] <key file> <hypothesis file> [> <score_report>]
##
## <key file> and <hypothesis file> can be in inline SGML format or in
## APF (standoff) format. (One of each is also allowed.)
## In any case, it is assumed that the documents in each file are in
## the same format.
## 
## -t (optional) causes the entire document to be scored.
##    Else, the scorer defaults to comparing only those
##    portions within <TEXT>...</TEXT>.
##
## EXAMPLE
## -------
## In this example, the TIMEX2 tags in gold_standard.sgml are being
## compared to those of system_output.sgml, and the resulting report
## is being written out to a file named score_report.
##
##    perl score_timex2.pl gold_standard.sgml system_output.sgml > score_report
##
## OUTPUT
## ------
## The summary statistics are computed as follows:
## POS (Possible) = CORR + INCO + MISS
## ACT (Actual) = CORR + INCO + SPUR
## UND (Undergeneration) = MISS / POSS
## OVG (Overgeneration) = SPUR / ACT
## SUB (Substitution) = INCO / CORR + INCO
## ERR (Overall error rate) = INCO + SPUR + MISS / CORR + INCO + SPUR + MISS
## PREC(Precision) = CORR / ACT
## REC (Recall)  CORR/POSS
## F   (F-measure)
##
## KNOWN BUGS
## ---------
## Under certain conditions, the algorithm may generate a sub-optimal
## matching for ambiguous alignments. See comments for
## details. -wmorgan
##
## HISTORY
## ------
## score_timex2.pl was originally authored by George Wilson of the
## MITRE Corporation, and further upgraded by Susan Lubar
## and William Morgan of the MITRE Corporation.
##
## 7/2004 - 8/2004: modified by wmorgan of MITRE to the following
## ends:
## 1) new algorithm that does better (more robust) matching, and
##    allows for multiple tags of the same type to start at the same
##    position
## 2) files processed one document at a time rather than loading both
##    corpora completely into memory
## 3) massive code reorg and cleanup
##
## 10/2004: (re)added capability to limit scoring to tags within one
## tag-bounded region (e.g. <text>). --wmorgan
## 6/2005: added APF support. --wmorgan
## 9/2005: added -t parameter.  --wmorgan

#######################################################################

#######################################################################
###  Variables for user to modify
#######################################################################

## these are all case-insensitive
$DocTag          = "DOC";
$DocLabel        = "DOC_?ID";
$DocNo           = "DOCNO";

$TextTag         = "TEXT"; # only tags within this region will be
                           # scored. undefined this to score all tags.

$ScoreAllTags = 0; # as opposed to scoring just those tags in %ScoreTags - %IgnoreTags
$AmbiguousTagDebug = 0;

### Count only these tags and the specified attributes thereof. Set a
### tag to 1 to count and 0 to ignore. Attributes not specified here
### generate errors by default.
### USE ONLY UPPER-CASE.
%ScoreTags = ("TIMEX2" => { "TEXT"         => 1,
			     "VAL"          => 1,
			     "MOD"          => 1,
			     "SET"          => 1,
			     "GRANULARITY"  => 1,  # srl - obsolete
			     "NON_SPECIFIC" => 1,
			     "PERIODICITY"  => 1,  # srl - obsolete
			     "ANCHOR_DIR"   => 1,
			     "ANCHOR_VAL"   => 1,

			     "TYPE",        => 0,
			     "COMMENTS"     => 0,
			     "COMMENT"      => 0, },
##	       "TEXT"    => {},
	       "LEX"    => { "POS"          => 1, },
	      );

### these attributes are always reported during the tag-by-tag
### section, but may or may not be scored.
%ReportTags = ("TIMEX2" => { "COMMENTS"     => 1,
			     "COMMENT"      => 1, },
	       );


### Don't count these tags. This is only useful when $ScoreAllTags
### is true, in which every tag except these will be counted.
%IgnoreTags = (
	       "P" => 1,
	       "BR" => 1,
	      );

### Break up tags into classes. A tag is a member of a class if the
### corresponding function returns true.
## these are used by the subroutines above
$CalPointRe = "\\d{1,4}(-\\d\\d(-\\d\\d(T\\d\\d(:\\d\\d(:\\d\\d(\.\\d\\d)?)?([+-]nn|Z)?)?)?)?)?";
$WeekPointRe = "\\d{1,4}-W\\d\\d(-\\d)?";
$PeriodRe = "P((([\\d\\.]+Y)?([\\d\\.]+M)?([\\d\\.]+D)?(T([\\d\\.]+H)?([\\d\\.]+M)?([\\d\\.]+S)?)?)|([\\d\\.]+(W|DE|CD|ML|SP|SU|FA|WI|FY|Q\\d|H\\d|WE|MO|MI|AF|EV|NI|DT)))";
## set up the range regexp, which is a mite complicated...
$NonspecRe = "(" . $CalPointRe . "|" . $WeekPointRe .  "|" . $PeriodRe . ")";
$NonspecRe =~ s/(?<!\[)\\d/[\\dX]/go;
$NonspecRe =~ s/\[\\d\\\.\]/[\\d\\.X]/go;
#print STDERR "nonspecre $NonspecRe\n";

## now the classes
%TagClasses = (
  "TIMEX2" => {
    "calpoint" => sub { return match_val_re($CalPointRe, @_); },
    "weekpoint" => sub { return match_val_re($WeekPointRe, @_); },
    "period" => sub { return match_val_re($PeriodRe, @_); },
    "nonspec" => sub { return match_val_re($NonspecRe, @_) && !match_val_re($CalPointRe, @_) && !match_val_re($WeekPointRe, @_) && !match_val_re($PeriodRe, @_); },
    "prefixed" => sub { return match_val_re("(FY|BC|KA|MA|GA).*", @_); },
    "token" => sub { return match_val_re("PRESENT_REF|PAST_REF|FUTURE_REF", @_); },
    "noval" => sub {
      my $tag = shift;
      my $atts = shift;

      return (!exists $atts->{"VAL"}) || ($atts->{"VAL"} eq "");
    },
  },
);


#######################################################################
###  Nothing for user to modify below this
#######################################################################
$TagRe         = "<.*?>"; ## regex that defines a tag
$lab_format = "%-4s  %15s |  %30s |  %30s\n";

for(my $i = 0; $i <= $#ARGV; $i++) {
  if($ARGV[$i] eq "-t") {
    print STDERR "will ignore texttag\n";
    splice(@ARGV, $i, 1);
    undef($TextTag);
  }
}

exit print STDERR "Usage: perl score_timex2.pl <key file> <hypothesis file>\n" unless (@ARGV == 2);
exit main(@ARGV);

## here we go!
sub main {
  use strict;
  use vars qw($TextTag);

  my $keyfn = shift;
  my $txtfn = shift;

  open(KEY, $keyfn) or die qq(can't open "$keyfn");
  open(TXT, $txtfn) or die qq(can't open "$txtfn");

  my ($keyfunc, $txtfunc);

  if(is_xml_file(\*KEY)) {
    if(is_apf_file(\*KEY)) {
      print STDERR "key file is in APF format\n";
      my $sgmlfn = find_corresponding_sgml_file($keyfn);
      if(defined($sgmlfn)) {
	open(SGML, $sgmlfn) or die "can't open \"$sgmlfn\"";
	$keyfunc = sub {
	  return apf_next_doc(shift(), \*SGML);
	}
      }
      else {
	print STDERR "warning: can't find SGML file for $keyfn\n";
	$keyfunc = sub {
	  return apf_next_doc(shift(), undef);
	}
      }
    }
    else {
      die "key file is XML but i don't recognize it as APF";
    }
  }
  else {
    #print STDERR "key file is in inline format\n";
    $keyfunc = \&inline_next_doc;
  }

  if(is_xml_file(\*TXT)) {
    if(is_apf_file(\*TXT)) {
      print STDERR "hypothesis file is in APF format\n";
      my $sgmlfn = find_corresponding_sgml_file($txtfn);
      if(defined($sgmlfn)) {
	open(SGML2, $sgmlfn) or die "can't open \"$sgmlfn\"";
	$txtfunc = sub {
	  return apf_next_doc(shift(), \*SGML2);
	}
      }
      else {
	print STDERR "warning: can't find SGML file for $txtfn\n";
	$txtfunc = sub {
	  return apf_next_doc(shift(), undef);
	}
      }
    }
    else {
      die "hypothesis file is XML but i don't recognize it as APF";
    }
  }
  else {
    #print STDERR "hypothesis file is in inline format\n";
    $txtfunc = \&inline_next_doc;
  }

  my %total_scores;

  while(my ($keyid, $key) = &$keyfunc(\*KEY)) {
    my ($txtid, $txt) = &$txtfunc(\*TXT) or die qq(out of documents in "$keyfn");
#    die qq(mismatched key ($keyid) and text ($txtid) document ids) unless ($keyid eq $txtid);
    print "## document id: \"$keyid\"\n";

    my $scores = score($key, $txt);

    ## merge in all scores
    foreach my $class (keys %{$scores}) {
      foreach my $score (keys %{$scores->{$class}}) {
	for(my $i = 0; $i < 4; $i++) {
	  if(defined($scores->{$class}{$score}[$i])) {
	    $total_scores{$class}{$score}[$i] += $scores->{$class}{$score}[$i];
	  }
	}
      }
    }
  }

  print_scores(\%total_scores);
}

sub find_corresponding_sgml_file {
  my $keyfn = shift;
  my $ret = undef;

  my @extensions = qw(sgml sgm SGML SGM);

  my @parts = split(/\./, $keyfn);
  for(my $i = $#parts; $i >= 0; $i--) {
    my $name = join(".", @parts[0 .. $i]);
    foreach my $ext (@extensions) {
      my $fn = $name . "." . $ext;
      print STDERR "looking for $fn ...\n";
      if(-f $fn) {
	print STDERR "found it!\n";
	return $fn;
      }
    }
  }

  print STDERR "warning: can't decide on a corresponding SGML filename for APF file $keyfn\n";

  return undef;
}

sub is_xml_file {
  use strict;

  my $in = shift;

  while(defined ($_ = <$in>)) {
    last unless($_ =~ /^\s*$/);
  }

  seek($in, 0, 0);
  return(/\s*<?xml/i);
}

sub is_apf_file {
  use strict;

  my $in = shift;

  my $max = 50; # big hack
  while(defined ($_ = <$in>)) {
    next if(/^\s*$/);
    last if(($max <= 0) || /<!DOCTYPE/);
    $max--;
  }

  seek($in, 0, 0);
  return(/<!doctype source_file .* \"apf.*dtd">/i);
}

## class identification subroutine
sub match_val_re {
  use strict;

  my $re = shift;
  my $tag = shift;
  my $atts = shift;

  return (exists $atts->{"VAL"}) && ($atts->{"VAL"} =~ m/^($re)$/);
}

sub get_class {
  use strict;
  use vars qw(%TagClasses);

  my $tag = shift;
  my $atts = get_atts($tag->{"head"});

  my $class = undef;
  if(exists $TagClasses{$tag->{"type"}}) {
    my $subs = $TagClasses{$tag->{"type"}};

    foreach my $k (keys %{$subs}) {
      my $v = $subs->{$k};
      if(&$v($tag, $atts)) {
	$class = $k;
	last;
      }
    }
    $class = "unknown" unless defined $class;
  }

  return $class;
}

sub apf_next_doc {
  use strict;
  use vars qw($TextTag);

  my $in = shift;
  my $sgmlin = shift;
  $/ = ">";

  while(defined ($_ = <$in>)) {
    last if(m{^\s*<document}i);	# found a doc
  }

  return unless defined($_);	# no more documents, return nothing.
                                # (which, apparently, is the only
                                # thing that evaluates as false (as
                                # opposed to, say, undef).

  my $docid;
  if(/<document docid="(.*?)">/i) {
    $docid = $1;
  }
  else {
    die qq{can\'t parse APF "document" tag: got [$_]}
  }

  my ($textstart, $textend);
  if(defined $TextTag) {
    if(defined $sgmlin) {
      my $pos = 0;
      while(defined($_ = <$sgmlin>)) {
#	print "*** for $_ at " . tell($sgmlin) . "\n";

	my $atend = 0;
	if(/\s*(\S.*?)\s*<\/docid>/i) {
	  if(!($1 eq $docid)) {
	    print STDERR "warning: mismatched DOCIDs between APF and SGML files: $1 vs $docid\n";
	  }
	}
	elsif(/<\/doc>/i) {
	  last;
	}
	elsif(/<$TextTag/i) {
	  $textstart = $pos;
	}
	elsif(/<\/$TextTag/i) {
	  $atend = 1;
	}

	s/<.*?>//;
	$pos += length;
	if($atend) {
	  $textend = $pos;

	}
      }
    }
    else {
      print STDERR "warning: can't find SGML file, so $TextTag boundaries ignored\n";
    }
  }

#  print "*** decided text boundaries are $textstart $textend for $sgmlin and $TextTag ***\n";

  # i hate xml. i hate xml. i hate xml.
  my ($head, $start, $end);
  my $in_timex2 = 0;
  my $in_timex2_mention = 0;
  my $in_extent = 0;
  my $in_charseq = 0;
  my %dups;
  my @tags;
  $/ = ">";
  while(defined($_ = <$in>)) {
#    print "got $_\n";
    if(!$in_timex2 && /(<timex2 .*>)/mi) {
      $head = $1;
      $in_timex2 = 1;
#      print "in timex2 with $_\n";
    }
    elsif($in_timex2 && !$in_timex2_mention && /<timex2_mention/i) {
      $in_timex2_mention = 1;
#      print "in timex2_metion with $_\n";
    }
    elsif($in_timex2_mention && !$in_extent && /<extent/i) {
      $in_extent = 1;
#      print "in extent with $_\n";
    }
    elsif($in_extent && m,<charseq \s*start\s*=\s*"(.*?)" \s*end\s*=\s*"(.*?)">,i) {
      $start = $1;
      $end = $2;
      $in_charseq = 1;
    }
    elsif($in_charseq && m,(.*?)</charseq>,is) {
#      print "*** got $1\n";
      my $unique = "TIMEX2:$start:$end";
      my $body = $1;
      $body =~ s/[\r\n]+/ /g;
      my $tag = { start => $start, end => $end, type => "TIMEX2", head => $head, body => $body, unique => $unique };
      if (exists $dups{$unique}) { $tag->{"dup"} = 1; }
      else { $dups{$unique}++; }
#      print "start: $tag->{start}, end: $tag->{end}, type: $tag->{type}, head: $tag->{head}, body: $tag->{body}, unique: $tag->{unique}\n";
      push @tags, $tag unless defined($textend) && (($start > $textend) || ($end < $textstart));
      $in_charseq = 0;
    }

    elsif($in_extent && !$in_charseq && m,</extent,i) {
#      print "outside of extent with $_\n";
      $in_extent = 0;
    }
    elsif($in_timex2_mention && !$in_extent && m,</timex2_mention,i) {
      $in_timex2_mention = 0;
    }
    elsif($in_timex2 && !$in_timex2_mention && m,</timex2,i) {
      $in_timex2 = 0;
    }

    last if m{</document>}i;
  }

  @tags = sort { ($a->{"start"} <=> $b->{"start"}) || ($a->{"end"} <=> $b->{"end"}) } @tags;

  return $docid, \@tags;
}

## returns the next document from a stream, as a (docid, text) tuple
sub inline_next_doc {
  use strict;
  use vars qw($DocTag $DocLabel $DocNo $TextTag);

  my $in = shift;
  $/ = ">";

  while(defined ($_ = <$in>)) {
    last if(m{^\s*<$DocTag>}i);	# found a doc
    unless(m{^\s*$}) {
      ## feel free turn this off if it's too verbose -wmorgan
      print STDERR qq(warning: skipping extraneous text "$_" in quest for next <$DocTag> tag);
    }
  }

  return unless defined($_);	# no more documents, return nothing.
                                # (which, apparently, is the only
                                # thing that evaluates as false (as
                                # opposed to, say, undef)

  my $text = "";
  my $docid = undef;
  my $in_text_reg = (defined $TextTag ? 0 : 1);
  my $text_reg_count = (defined $TextTag ? 0 : 1);

  while(defined($_ = <$in>)) {
    if(m{\s*(\S+?)\s*</($DocLabel|$DocNo)>}i) {
      print STDERR qq(warning: multiple docid tags, using id "$1" instead of "$docid") if(defined $docid);
      $docid = $1;
    }

    if((defined $TextTag) && m{.*<$TextTag>$}is) {
      $in_text_reg = 1;
      $text_reg_count++;
    }
    elsif((defined $TextTag) && $in_text_reg && m{^(.*)</$TextTag>}is) {
      $text .= $1;
      $in_text_reg = 0;
    }
    else {
      $text .= $_ if $in_text_reg;
    }

    last if m{</$DocTag>}i;
  }

  print STDERR "warning: no docid found" unless $docid;
  print STDERR "warning: $text_reg_count <$TextTag> regions found in document $docid" unless ($text_reg_count == 1);
  return $docid, inline_get_tags($text);
}

## strip all sgml tags from a string, and compress whitespace
sub strmeat {
  use vars qw($TagRe);

  my $s = shift;
  $s =~ s/$TagRe//go;
  $s =~ s/\s+/ /go;
  return $s;
}

## return the first position where two strings differ, or the length
## of the strings if they're the same. neat hack eh? -wmorgan
sub string_diff { ($_[0] ^ $_[1]) =~ /^(\0*)/ && length($1); }

sub min { $_[0] < $_[1] ? $_[0] : $_[1] }
sub max { $_[0] > $_[1] ? $_[0] : $_[1] }
sub clamp { max(min($_[0], $_[1]), $_[2]) }

## the score function for deciding whether to align two tags or not.
## this should return values [0.0, 1.0]. 0.0 means the two tags
## shouldn't be aligned. 1.0 means they should. anything in between
## means maybe.

## current implementation simply calculates the extent overlap if the
## types match (otherwise 0).
sub score_alignment {
  my ($k, $t) = @_;

  my $ks = $k->{"start"};
  my $ke = $k->{"end"};

  my $ts = $t->{"start"};
  my $te = $t->{"end"};

  return 0.0 if($k->{"type"} ne $t->{"type"});
  my $overlap = (min($ke, $te) - max($ks, $ts)) / (max($ke, $te) - min($ts, $ks));
  return ($overlap < 0 ? 0.0 : $overlap);
}

### the various output functions. they return a string to be printed, and also
### update the scores appropriately.

### don't call these next two directly. they're just called by the
### other report_* functions.
sub report_key_atts_as {
  use strict;
  use vars qw($lab_format %ScoreTags %ReportTags);

  my $label = shift;
  my $type = shift;
  my $attrs = shift;

  my $ret = "";
  #while(my ($a, $v) = each %{$attrs}) { # we want to have a sorted list here so as to facilitate cross-platform comparisons
  foreach my $a (sort keys %{$attrs}) {
    my $v = $attrs->{$a};
    if((exists $ScoreTags{$type}{$a}) && $ScoreTags{$type}{$a}) {
      $ret .= sprintf($lab_format, "info", $a, $v, "");
    }
    elsif(exists $ReportTags{$type}{$a} && $ReportTags{$type}{$a}) {
      $ret .= sprintf($lab_format, "info", $a, $v, "");
    }
  }

  $ret;
}

sub report_txt_atts_as {
  use strict;
  use vars qw($lab_format %ScoreTags %ReportTags);

  my $label = shift;
  my $type = shift;
  my $attrs = shift;

  my $ret = "";
  #while(my ($a, $v) = each %{$attrs}) { # we want to have a sorted list here so as to facilitate cross-platform comparisons
  foreach my $a (sort keys %{$attrs}) {
    my $v = $attrs->{$a};
    if((exists $ScoreTags{$type}{$a}) && $ScoreTags{$type}{$a}) {
      $ret .= sprintf($lab_format, "info", $a, "", $v);
    }
    elsif((exists $ReportTags{$type}{$a}) && $ReportTags{$type}{$a}) {
      $ret .= sprintf($lab_format, "info", $a, "", $v);
    }
  }

  $ret;
}

## ok, now the "callable" reporting functions.
sub report_key_as_bad {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;

  $scores->{"overall"}{"$tag->{type}"}[1]++;
  $scores->{"overall"}{"$tag->{type}:TEXT"}[1]++;

  return sprintf($lab_format, "bad", $tag->{"bad"}, $tag->{"head"}, "") .
    (exists $tag->{"body"} ? sprintf($lab_format, "bad", "TEXT", $tag->{"body"}, "") : "") .
      report_key_atts_as("bad", $tag->{"type"},  get_atts($tag->{"head"}));
}

sub report_txt_as_bad {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;

  $scores->{"overall"}{"$tag->{type}"}[1]++;
  $scores->{"overall"}{"$tag->{type}:TEXT"}[1]++;

  return sprintf($lab_format, "bad", $tag->{"bad"}, "", $tag->{"head"}) .
    (exists $tag->{"body"} ? sprintf($lab_format, "bad", "TEXT", "", $tag->{"body"}) : "") .
      report_txt_atts_as("bad", $tag->{"type"}, get_atts($tag->{"head"}));
}

sub report_txt_as_spur {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;
  my $type = $tag->{"type"};
  my $class = get_class($tag);

  $scores->{"overall"}{$type}[3]++;
  $scores->{"overall"}{"$type:TEXT"}[3]++;

  if(defined $class) {
    $scores->{$class}{$type}[3]++;
    $scores->{$class}{"$type:TEXT"}[3]++; # srl track scores for TEXT attribute of scope errors
  }

  return sprintf($lab_format, "SPUR", "label", "", $type) .
    sprintf($lab_format, "SPUR", "text",  "", $tag->{"body"}) .
      report_txt_atts_as("SPUR", $tag->{"type"}, get_atts($tag->{"head"})) .
	(defined $class ? sprintf($lab_format, "info", "class", "", $class) : "");
}

## reports duplicate key tags as BAD
sub report_key_as_dup {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;
  my $type = $tag->{"type"};
  my $class = get_class($tag);

  return sprintf($lab_format, "bad", "dup_tag", $type, "") .
    sprintf($lab_format, "bad", "label", $type, "") .
      sprintf($lab_format, "bad", "text",  $tag->{"body"}, "") .
	report_key_atts_as("bad", $tag->{"type"}, get_atts($tag->{"head"})) .
	  (defined $class ? sprintf($lab_format, "info", "class", $class, "") : "");
}

## reports duplicate text tags as SPUR (plus one BAD)
sub report_txt_as_dup  {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;
  my $type = $tag->{"type"};
  my $class = get_class($tag);

  $scores->{"overall"}{$type}[3]++;
  $scores->{"overall"}{"$type:TEXT"}[3]++;

  if(defined $class) {
    $scores->{$class}{$type}[3]++;
    $scores->{$class}{"$type:TEXT"}[3]++; # srl track scores for TEXT attribute of scope errors
  }

  return sprintf($lab_format, "bad", "dup_tag", "", $type) .
    sprintf($lab_format, "SPUR", "label", "", $type) .
      sprintf($lab_format, "SPUR", "text",  "", $tag->{"body"}) .
	report_txt_atts_as("SPUR", $tag->{"type"}, get_atts($tag->{"head"})) .
	  (defined $class ? sprintf($lab_format, "info", "class", "", $class) : "");
}

sub report_key_as_miss {
  use strict;
  use vars qw($lab_format);

  my $tag = shift;
  my $scores = shift;
  my $type = $tag->{"type"};
  my $class = get_class($tag);

  $scores->{"overall"}{$type}[2]++;
  $scores->{"overall"}{"$type:TEXT"}[2]++; # srl track scores for TEXT attribute of scope errors

  if(defined $class) {
    $scores->{$class}{$type}[2]++;
    $scores->{$class}{"$type:TEXT"}[2]++; # srl track scores for TEXT attribute of scope errors
  }

  my $attrs = get_atts($tag->{"head"});

  return sprintf($lab_format, "MISS", "label", $type, "") .
    sprintf($lab_format, "MISS", "text",  $tag->{"body"}, "") .
      report_key_atts_as("MISS", $tag->{"type"}, get_atts($tag->{"head"})) .
	(defined $class ? sprintf($lab_format, "info", "class", $class, "") : "");
}

sub report_as_corr {
  use strict;
  use vars qw($lab_format);

  my $ktag = shift;
  my $ttag = shift;
  my $class = shift;
  my $scores = shift;

  $scores->{"overall"}{$ktag->{"type"}}[0]++;
  $scores->{"overall"}{"$ktag->{type}:TEXT"}[0]++; # srl track scores for TEXT attribute
  if(defined $class) {
    $scores->{$class}{$ktag->{type}}[0]++;
    $scores->{$class}{"$ktag->{type}:TEXT"}[0]++; # srl track scores for TEXT attribute
  }

  return sprintf($lab_format, "corr", "label", $ktag->{"type"}, $ttag->{"type"}) .
    sprintf($lab_format, "corr", "text", $ktag->{"body"}, $ttag->{"body"});
}

sub report_as_scope_error {
  use strict;
  use vars qw($lab_format);

  my $ktag = shift;
  my $ttag = shift;
  my $class = shift;
  my $scores = shift;

  $scores->{"overall"}{$ttag->{type}}[0]++;
  $scores->{"overall"}{"$ttag->{type}:TEXT"}[1]++;

  if(defined $class) {
    $scores->{$class}{$ttag->{type}}[0]++;
    $scores->{$class}{"$ttag->{type}:TEXT"}[1]++;
  }

  return "(scope error - $ktag->{unique} (len " . ($ktag->{"end"} - $ktag->{"start"}) . ") vs $ttag->{unique} (len " . ($ttag->{"end"} - $ttag->{"start"}) . "), score " . sprintf("%.5g", score_alignment($ktag, $ttag)) . ")\n" .
    sprintf($lab_format, "corr", "label", $ktag->{"type"}, $ttag->{"type"}) .
      sprintf($lab_format, "INCO", "text", $ktag->{"body"}, $ttag->{"body"});
}

## the alignment algorithm.
sub score {
    use strict;
    use vars qw($AmbiguousTagDebug %ScoreTags);

    my @key_tags = @{shift()};
    my @txt_tags = @{shift()};
    my %scores; # to be returned

    while(@key_tags || @txt_tags) { # main loop---while there are tags left to proess
      if(@key_tags == 0) { # no more key tags, drain text tags
	foreach my $t (@txt_tags) {
	  print report_txt_as_dup($t, \%scores) if exists $t->{"dup"};
	  print report_txt_as_bad($t, \%scores) if exists $t->{"bad"};
	  print report_txt_as_spur($t, \%scores);
	  print "\n";
	}
	@txt_tags = ();
      }

      elsif(@txt_tags == 0) { # no more text tags, drain key tags
	foreach my $k (@key_tags) {
	  print report_key_as_dup($k, \%scores) if exists $k->{"dup"};
	  print report_key_as_bad($k, \%scores) if exists $k->{"bad"};
	  print report_key_as_miss($k, \%scores) . "\n";
	}
	@key_tags = ();
      }

      else { # have at least one key and at least one text tag; align

	## here's how aligning will work:

	## we find the next set of key and text tags that overlap with
	## each other by at least one character. once we have these
	## tags, we'll do an n*m comparison and then greedily select
	## the best matches.

	## this is equivalent to greedy selection on the full n*m
	## scores, but quicker, as we assume that the score is always
	## 0 for tags that don't overlap, and thus don't have to deal
	## with these potential alignments.

	## this approach is not a great for several reasons (e.g. has
	## very poor worst-case performance; can can be tricked into
	## selecting the worst possible match, depending on the
	## scoring function), but it's at least not completely ad-hoc,
	## and will generate the same results if the tags are read in
	## reversed order, which is nice.

	## for example, in the following situation:
	##
	##       A |--------------|
        ##       B |------|
        ## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	##       C |--------------|
	##               D |------|
	##
	## if the scoring function is a monotonically increasing
	## function of the overlap extent (as it is in the current
	## code), the algorithm will always align A and C and say B is
	## spurious and D is missing, whereas it might be better,
	## depending on the specifics of scoring function, to align A
	## with D and B with C.

	## but these kinds of situations are kind of messed up to
	## begin with, so i say, merely, GIGO.

	## henderson claims that a guaranteed optimal solution that
	## works with any consistent scoring function requires linear
	## programming (and thus many horrific 60's fortran packages
	## whose original authors have all since died and which no one
	## really understands any more). one day i will write the
	## aligner to rule all aligners. but not today.

	## -wmorgan

	## our sets will be the tags in [0 .. $kmax) and [0 .. $tmax)
	my ($kmax, $tmax) = (0, 0);
	my $bound;

	## first, find the match sets
	if($key_tags[0]->{"start"} < $txt_tags[0]->{"start"}) {
	  $kmax = 1;
	  $bound = $key_tags[0]->{"end"};
	}
	else {
	  $tmax = 1;
	  $bound = $txt_tags[0]->{"end"};
	}

	my $added;
	do {
	  $added = 0;

	  if(($#key_tags >= $kmax) && ($key_tags[$kmax]->{"start"} < $bound)) {
	    $added = 1;
	    $bound = max($bound, $key_tags[$kmax]->{"end"});
	    $kmax++;
	  }

	  elsif(($#txt_tags >= $tmax) && ($txt_tags[$tmax]->{"start"} < $bound)) {
	    $added = 1;
	    $bound = max($bound, $txt_tags[$tmax]->{"end"});
	    $tmax++;
	  }
	} while($added);

#	print ">>> match sets: have key range [0, $kmax) of " . (scalar @key_tags) . " and txt range [0, $tmax) of " . (scalar @txt_tags) . "\n";

	## drop all bad and duplicate tags
	for(my $i = 0; $i < $kmax; $i++) {
	  if(exists $key_tags[$i]->{"bad"}) {
	    print report_key_as_bad($key_tags[$i], \%scores) . "\n";
	    splice(@key_tags, $i, 1);
	    $kmax--;
	  }
	  elsif(exists $key_tags[$i]->{"dup"}) {
	    print report_key_as_dup($key_tags[$i], \%scores) . "\n";
	    splice(@key_tags, $i, 1);
	    $kmax--;
	  }
	}

	for(my $i = 0; $i < $tmax; $i++) {
	  if(exists $txt_tags[$i]->{"bad"}) {
	    print report_txt_as_bad($txt_tags[$i], \%scores) . "\n";
	    splice(@txt_tags, $i, 1);
	    $tmax--;
	  }
	  elsif(exists $txt_tags[$i]->{"dup"}) {
	    print report_txt_as_dup($txt_tags[$i], \%scores) . "\n";
	    splice(@txt_tags, $i, 1);
	    $tmax--;
	  }
	}

	my $ambig = $AmbiguousTagDebug && (($tmax > 1) || ($kmax > 1) ? 1 : 0);

	if($ambig) {
	  print "#### ambiguous tag event\n";
	  print "#### i must match the following key tags: " .
	    (join(", ", map { $_->{"unique"} } @key_tags[0 .. $kmax - 1]) or "<none>") . "\n";
	  print "#### with the following text tags       : " .
	    (join(", ", map { $_->{"unique"} } @txt_tags[0 .. $tmax - 1]) or "<none>"). "\n"
	}

	## now greedily select the alignment to make
	my @match;
	do {
	  my $max_score = 0.0;
	  @match = ();

	  for(my $k = 0; $k < $kmax; $k++) {
	    for(my $t = 0; $t < $tmax; $t++) {
	      my $score = score_alignment($key_tags[$k], $txt_tags[$t]);
	      print "#### $key_tags[$k]->{unique} vs $txt_tags[$t]->{unique} has score $score\n" if $ambig;
	      if($score > $max_score) {
		$max_score = $score;
		@match = ($k, $t);
	      }
	    }
	  }

	  if(@match) {
	    my ($k, $t) = @match;

	    print "#### decided to match $key_tags[$k]->{unique} and $txt_tags[$t]->{unique}\n" if $ambig;
	    my $class = get_class($key_tags[$k]);

	    if($max_score == 1.0) { print report_as_corr($key_tags[$k], $txt_tags[$t], $class, \%scores); }
	    else { print report_as_scope_error($key_tags[$k], $txt_tags[$t], $class, \%scores); }

	    my $key_av = get_atts($key_tags[$k]->{"head"});
	    my $txt_av = get_atts($txt_tags[$t]->{"head"});

	    print score_atts($key_tags[$k], $txt_tags[$t], $key_av, $txt_av, $class, \%scores);

	    print sprintf($lab_format, "info", "class", $class, $class) if defined $class;
	    print "\n";

	    splice(@key_tags, $k, 1); $kmax--;
	    splice(@txt_tags, $t, 1); $tmax--;
	  }
	} while(($tmax > 0) && ($kmax > 0) && @match);

	## now we have zero or more key and text tags, all the
	## alignments of which have 0 scores. chew them up and spit
	## them out.
	print "#### can't do any more ambiguous matching\n" if $ambig;

	until($tmax == 0) {
	  print report_txt_as_spur($txt_tags[0], \%scores) . "\n";
	  shift @txt_tags; $tmax--;
	}

	until($kmax == 0) {
	  print report_key_as_miss($key_tags[0], \%scores) . "\n";
	  shift @key_tags; $kmax--;
	}
      }
    }

    return \%scores;
}

## given an aligned key tag and text tag, plow through all the
## attributes and complain accordingly. in contrast to the
## report_key_atts_as function above, this actually scores the
## attributes as well.
sub score_atts {
  use strict;
  use vars qw(%ScoreTags %ReportTags);

  my $k = shift;
  my $t = shift;
  my $type = $t->{"type"};

  my $kav = shift;
  my $tav = shift;

  my $class = shift;
  my $scores = shift;

  my $ret = ""; # we return a giant string

  ## first process all text a=v pairs
  foreach my $attr (sort keys %{$tav}) {
    if(exists $ScoreTags{$type}{$attr}) {
      if($ScoreTags{$type}{$attr}) {
	if(exists $kav->{$attr}) {
	  my $v1 = $tav->{$attr};
	  my $v2 = $kav->{$attr};

	  $v1 =~ s/[\s-]//go;
	  $v2 =~ s/[\s-]//go;
	  
	  if (lc($attr) eq 'val') {
	    # convert to ISO basic
	    $v1 =~ s/(-|:)//go;
	    $v2 =~ s/(-|:)//go;
	  }

	  if(lc($v1) eq lc($v2)) {
	    $ret .= sprintf($lab_format, "corr", $attr, $kav->{$attr}, $tav->{$attr});
	    $scores->{"overall"}{"$type:$attr"}[0]++;
	    $scores->{$class}{"$type:$attr"}[0]++ if defined $class;
	  }
	  else {
	    $ret .= sprintf($lab_format, "INCO", $attr, $kav->{$attr}, $tav->{$attr});
	    $scores->{"overall"}{"$type:$attr"}[1]++;
	    $scores->{$class}{"$type:$attr"}[1]++ if defined $class;
	  }
	}
	else { # spurious
	  $ret .= sprintf($lab_format, "SPUR", $attr, "", $tav->{$attr});
	  $scores->{"overall"}{"$type:$attr"}[3]++;
	  $scores->{$class}{"$type:$attr"}[3]++ if defined $class;
	}
      }
      ## otherwise, we ignore this tag, unless we're forcibly told to report it
      elsif((exists $ReportTags{$type}{$attr}) && $ReportTags{$type}{$attr}) {
	$ret .= sprintf($lab_format, "info", $attr, (exists $kav->{$attr} ? $kav->{$attr} : ""), $tav->{$attr});
      }
    }
    else {
      if(exists $kav->{$attr}) { # this is a tag that the key also
                                 # has, but we're not told to score
                                 # it, or even to ignore it. we'll
                                 # report it as a curiousity.
	$ret .= sprintf($lab_format, "info", $attr, (exists $kav->{$attr} ? $kav->{$attr} : ""), $tav->{$attr});
      }
      else { # key doesn't have it, and we're not ignoring it---so it's spurious
	$ret .= sprintf($lab_format, "SPUR", $attr, "", $tav->{$attr});
	$scores->{"overall"}{"$type:$attr"}[3]++;
	$scores->{$class}{"$type:$attr"}[3]++ if defined $class;
      }
    }
  }

  ## now all key a=v pairs which we didn't get to before
  foreach my $attr (sort keys %{$kav}) {
    if(exists $ScoreTags{$type}{$attr}) {
      if($ScoreTags{$type}{$attr}) {
	if(!exists $tav->{$attr}) {
	  $ret .= sprintf($lab_format, "MISS", $attr, $kav->{$attr}, "");
	  $scores->{"overall"}{"$type:$attr"}[2]++;
	  $scores->{$class}{"$type:$attr"}[2]++ if defined $class;
	}
      }
      elsif((exists $ReportTags{$type}{$attr}) && $ReportTags{$type}{$attr}) {
	$ret .= sprintf($lab_format, "info", $attr, $kav->{$attr}, "") unless exists $tav->{$attr};
      }
    }
    else { # key tag that we're not told to score or to ignore. we'll
           # report it as a curiousity.
      $ret .= sprintf($lab_format, "info", $attr, $kav->{$attr}, "") unless exists $tav->{$attr};
    }
  }

  return $ret;
}

## get attributes from a tag
sub get_atts {
    use strict;

    my $tag = shift;
    my %ret;

    unless($tag =~ /$TagRe/) {
      die qq(bad tag "$tag" passed to get_atts);
    }

    ## the following regexp won't work for unquoted values. i had to
    ## sacrifice that feature to make it work with equals signs and
    ## nested, non-escaped quotes. who ever decided to let callisto
    ## generate THAT needs to be beaten.)  -wmorgan
    my $identifier = "[\\w\\d_-]+";
    while($tag =~ /($identifier)\s*=\s*"(.*?)"(?=(\s*>|\s+($identifier)\s*=\s*"))/go) {
      my $att = $1;
      my $val = $2;
      $ret{uc($att)} = $val unless $val eq ""; # skip empty values
    }

    return \%ret;
}

##############################################
##  Finds all tags in a string
##  Takes one input: The string
##  Returns an array of hashes, one per tag
##  Array values are (TagContents, TaggedData)
##############################################

sub inline_get_tags {
  use strict;
  use vars qw(%ScoreTags %IgnoreTags $ScoreAllTags);

  my $string = shift;
  my @tags; # to be returned
  my %dups;

  my($type, $tag, $B4, $Aft, $Int, $TagHead);
  my($SPos, $EPos, $IntX, $key);
  my($tmp, $tmpB4);

  ## Get all tags!!!
  while ($string =~ /<\/(\w+)>/mo) { # srl - find an end tag
    $type = uc($1);
    $tag  = $&;
    $B4   = $`;
    $Aft  = $';

    if(($ScoreAllTags && exists $IgnoreTags{$type}) || (!$ScoreAllTags && !(exists $ScoreTags{$type}))) {
      # skip!
      $string = $B4 . $Aft;
    }

    elsif ($B4   =~ /(.*)(<$type[^>]*>)/mi) { # srl - else find matching start tag
      $B4    = $` . $1;
      $tmpB4 = $B4 . $2;
      $Int   = $';
      $TagHead = $2;
      $string = $B4 . $Int . $Aft;

      $tmp = $';
      while ($tmp =~ /(.*)(<$type[^>]*>)/mi) { #srl handle embedded tags
	$tmpB4 = $tmpB4 . $` . $1;
	$Int   = $';
	$TagHead = $2;
	$string = $tmpB4 . $Int . $Aft;
	$tmp = $';
	$B4 = $tmpB4;
      }

      $B4    =~ s/$TagRe//gmo;	# srl - get rid of tags
      $B4    =~ s/\s+//msog;	# srl - and whitespace
      $SPos  = length($B4);	# srl - start position
      $Int   = Tighten($Int);
      $IntX  = $Int;
      $IntX  =~ s/\s+//msog;
      $IntX  =~ s/$TagRe//msog;
      $EPos  = length($IntX) + $SPos; # srl - end position
      #	    print "startpos $SPos endpos $EPos $Int\n";

      my $unique = "$type:$SPos:$EPos";
      my $tag = { start => $SPos, end => $EPos, type => $type, head => $TagHead, body => $Int, unique => $unique };
      #	    $key   = sprintf("%07d:%07d:%s", $SPos, $EPos, uc($type));  # srl - key is startpos, endpos, tagtype  #srl upcase tag
      if (exists $dups{$unique}) { $tag->{"dup"} = 1; }
      else { $dups{$unique}++; }

      push @tags, $tag;
    }
    else {
      $SPos = length($B4);
      my $unique = "$type:$SPos:$SPos";
      push @tags, { start => $SPos, end => $SPos, type => $type, head => $TagHead, unique => $unique, bad => "UNMATCHED_CLOSE" };
      $string = $B4 . $Aft;
    }
  }

  @tags = sort { ($a->{"start"} <=> $b->{"start"}) || ($a->{"end"} <=> $b->{"end"}) } @tags;
  return(\@tags);
}

##############################################
##  sub Tighten
##  Formats text
##############################################

sub Tighten {
    use strict;
    my($string);
    use vars qw($TagRe);
    ($string) = @_;
    unless($string) { return(""); }

    $string =~ s/\n/ /goms;
    $string =~ s/$TagRe//goms;
    $string =~ s/\s\s+/ /goms;
    $string =~ s/\A\s+//oms;
    $string =~ s/\s+\Z//oms;

    return($string);
}

sub print_scoreblock {
  my $scores = shift;
  my $prefix = (@_ > 0 ? shift : "");
  my $Bad = 0;

  foreach my $s (sort keys %{$scores}) {
    if($s =~ /\ABAD_DATA/o) {
      $temp1 = $';
      if ($temp1 !~ /DUP_TAG/) {   #srl only skip bad tags that aren't dups
	$Bad++; next; 
      }
    }
    for($i=0; $i<4; $i++) {
      if(!defined($scores->{$s}[$i])) {
	$scores->{$s}[$i] = 0; }
    }
    $COR = $scores->{$s}[0];
    $INC = $scores->{$s}[1];
    $MIS = $scores->{$s}[2];
    $sPUR = $scores->{$s}[3];
    
    $POS = $COR + $INC + $MIS;
    $ACT = $COR + $INC + $sPUR;
    printf("%-20s%8s%8s |", "$prefix$s", $POS, $ACT);
    
    for($i=0; $i<4; $i++) {
      printf("%8d", $scores->{$s}[$i]); 
    }
    
    # srl added 3/29/04
    if ($POS) {$UND = $MIS / $POS;}
    else {$UND = 0;}
    # srl added 3/29/04
    if ($ACT) {$OVG = $sPUR / $ACT;}
    else {$OVG = 0;}
    # srl added 3/29/04
    if ($COR + $INC) {$sUB = $INC / ($COR+$INC);}
    else {$sUB = 0;}
    # srl added 3/29/04
    if ($COR + $INC + $sPUR + $MIS) {
      $ERR = ($INC + $sPUR + $MIS) / ($COR + $INC + $sPUR + $MIS);}
    else {$ERR = 0;}
    printf(" |   %5.3f   %5.3f   %5.3f   %5.3f", $UND, $OVG, $sUB, $ERR);
    
    if($ACT) { $Prec = $COR / $ACT; }
    else { $Prec = 0; }
    if($POS) { $Rec  = $COR / $POS; }
    else { $Rec = 0; }
    if($Prec + $Rec) { $F_Measure = (2 * $Prec * $Rec)/($Prec + $Rec); }
    else { $F_Measure = 0; }
    printf("    %5.3f   %5.3f   %5.3f\n", $Prec, $Rec, $F_Measure);
  }

  return $Bad;
}

sub print_sep {
    print "-------------------------------------+";
    print "---------------------------------+";
    print "---------------------------------------------------------\n";
}

## Print out summary statistics
sub print_scores {
    my $scores = shift;

    printf("%-20s%8s%8s |%8s%8s%8s%8s |%8s%8s%8s%8s%9s%8s%8s\n", "tag", "pos", "act",
	   "corr", "inco", "miss", "SPUR", "und", "ovg", "sub",
	   "err", "prec", "rec", "F");
    print_sep;
    print "  overall\n";
    print_sep;

    my $Bad = print_scoreblock($scores->{"overall"});

    foreach my $class (sort keys %{$scores}) {
      next if($class eq "overall");
      print_sep;
      print "  $class\n";
      print_sep;
      $Bad += print_scoreblock($scores->{$class});
    }
    print "\n";

    if($Bad) {
	print "*** Source Data Contained Errors ***\n";
	if(exists($scores->{"BAD_DATA_UNMATCHED_DOC_LENGTH"})) {
	    $temp = $scores->{"BAD_DATA_UNMATCHED_DOC_LENGTH"}[0];
	    print "Data contained $temp document pairs of unmatched lengths\n";
	}
	if(exists($scores->{"BAD_DATA_UNMATCHED_CLOSE"})) {
	    print "Source contained unmatched close tags\n";
	    $temp = ($scores->{"BAD_DATA_UNMATCHED_CLOSE"}[0]) || 0;
	    print "     Key: $temp\n";
	    $temp = ($scores->{"BAD_DATA_UNMATCHED_CLOSE"}[1]) || 0;
	    print "    Text: $temp\n";
	}
	if(exists($scores->{"BAD_DATA_DUP_TAG"})) {
	    print "Source contained duplicate tags\n";
	}
    }
}
