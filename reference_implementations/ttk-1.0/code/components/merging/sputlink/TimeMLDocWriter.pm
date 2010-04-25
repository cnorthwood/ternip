package TimeMLDocWriter;

use strict;

my $TIMEML_VERSION = '1.2.1';

# All tags that are defined by TimeML
my @TIMEML_TAGS = qw ( TimeML TIMEX3 SIGNAL EVENT MAKEINSTANCE ALINK SLINK TLINK SYNTAX );

# Arrays that specify the order in which attributes are typically
# printed. Not strictly needed but makes it easier to compare output
# to input. Alphabetical order is used when no order is defined.
# NOTE: need to add attributes for some tags.
my @EVENT_TAGS = qw( eid class text stem sentID );
my @MAKEINSTANCE_TAGS = qw( eventID eiid tense aspect polarity cardinality pos nf_morph modality );
my @TIMEX3_TAGS  = qw( tid type value mod temporalFunction functionInDocument anchorTimeID sentID quant freq beginPoint endPoint );
my @SIGNAL_TAGS  = qw( sid sentID );
my @ALINK_TAGS  = qw( lid relType eventInstanceID relatedToEventInstance signalID );
my @TLINK_TAGS  = qw( lid relType eventInstanceID timeID relatedToEventInstance relatedToTime signalID );
my @SLINK_TAGS = qw( lid relType eventInstanceID subordinatedEventInstance signalID ); 
my @SYNTAX_TAGS = qw( linkID syntaxPattern);

# Tags that do not consume input
my @EMPTY_TAGS = qw ( MAKEINSTANCE SLINK TLINK ALINK SYNTAX );

my $DEBUGGING = 0;


# ------------------ NO EDITS NECESSARY BELOW THIS LINE ---------------------


# Hashes corresponding to the arrays above. For faster sorting.

my %TIMEML_TAGS = ();
my %EVENT_TAGS = ();
my %MAKEINSTANCE_TAGS = ();
my %TIMEX3_TAGS = ();
my %SIGNAL_TAGS = ();
my %ALINK_TAGS = ();
my %TLINK_TAGS = ();
my %SLINK_TAGS = ();
my %SYNTAX_TAGS = ();
my %EMPTY_TAGS = ();

# Fill the hashes.
&createHashes();

# Initial indent, for debugging purposes.
my $indent = '';


# ------------------ INITIALIZATION ----------------

sub new {
    my ($class, $timemldoc, $mode, $filehandle) = @_;
	my $objref = {};
	$objref->{_mode} = $mode;
	$objref->{_filehandle} = $filehandle ? $filehandle : *STDOUT;
	$objref->{_timemldoc} = $timemldoc;
    bless $objref;
    return $objref;
}


# ---------------- PUBLIC METHOD ----------------

# Write the contents of a list created by TimeMLDoc
sub write {
	my $self = shift;
	my $timemldoc = $self->{_timemldoc};
	$self->print('<?xml version="1.0" ?>' . "\n");
	foreach my $element (@$timemldoc) {
		$self->printDocElement($element);
	}
	$self->print("\n");
}


# ---------------- PRIVATE METHODS ----------------

sub printDocElement {
	my ($self,$element) = @_;
	if (ref($element) eq 'ARRAY') {
		my ($type,$hash) = @$element;
		$self->printTimeMLTag($type,$hash);
	} elsif ($element =~ /^<TimeML/) {
		$self->printTimemlHeader($element); 
	} else {
		$self->printOtherElement($element);
	}
}

sub printTimeMLTag {
	my ($self, $tagname, $hash) = @_;
	return if $self->tagIsDeleted($hash);
	$self->print("<$tagname");
	my @keys = &sortKeys($tagname,$hash);
	foreach my $key (@keys) {
		# not a timeml tag, so skip it
		next if $key eq 'sentID';
		$self->print(" $key=\"" . $hash->{$key} . '"');
	}
	$EMPTY_TAGS{$tagname} ? $self->print('/>') : $self->print('>');
}

sub printTimemlHeader {
	my ($self, $element) = @_;
	if ($element =~ /^<TimeML>/) {
		# Fill in default schema information if there was none
		# Should be done less hackish in TimeMLDoc.pm
		my $schema = "TimeML_$TIMEML_VERSION.xsd";
		$self->print('<TimeML' . "\n");
		$self->print('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' . "\n");
		$self->print('    xsi:noNamespaceSchemaLocation="http://timeml.org/timeMLdocs/' ."$schema\">\n");
	} else {
        $self->print($element);
	}
}

sub printOtherElement {
	my ($self, $element) = @_;
	my $printIt = 1;
	if ($self->{_mode} eq 'min' and $element =~ /^<\/?(\S+)[ >]/) {
		my $tagname = $1;
		$printIt = 0 unless $self->isTimeMLTag($tagname);
	}
	if ($self->{_mode} eq 'no_lex' and $element =~ /^<\/?(\S+)[ >]/) {
		my $tagname = $1;
		$printIt = 0 if $tagname eq 'lex';
	}
	$self->print($element) if $printIt;
}

sub tagIsDeleted {
	my ($self, $hash) = @_;
    $hash->{__DELETED__} ? 1 : 0;
}

sub isTimeMLTag {
	my ($self, $tagname) = @_;
	return $TIMEML_TAGS{$tagname};
}

# Wrapper for all TimeML printing
sub print {
	my ($self, $string) = @_;
	my $FH = $self->{_filehandle};
	#print "*$string";
	print $FH $string if $string;
}


## Sorting

sub sortKeys {
	my ($tag, $atts) = @_;
	if ($tag eq 'EVENT') {
		return sort by_event_tag keys %$atts;
	} elsif ($tag eq 'TIMEX3') {
		return sort by_timex3_tag keys %$atts;
	} elsif ($tag eq 'SIGNAL') {
		return sort by_signal_tag keys %$atts;
	} elsif ($tag eq 'MAKEINSTANCE') {
		return sort by_makeinstance_tag keys %$atts;
	} elsif ($tag eq 'ALINK') {
		return sort by_alink_tag keys %$atts;
	} elsif ($tag eq 'SLINK') {
		return sort by_slink_tag keys %$atts;
	} elsif ($tag eq 'TLINK') {
		return sort by_tlink_tag keys %$atts;
	} elsif ($tag eq 'SYNTAX') {
		return sort by_syntax_tag keys %$atts;
	} else {
		return sort keys %$atts;
	}
}

sub by_event_tag {
	return $EVENT_TAGS{$a} <=> $EVENT_TAGS{$b}; }

sub by_timex3_tag {
	#print ":$a:$b:\n";
	return $TIMEX3_TAGS{$a} <=> $TIMEX3_TAGS{$b}; }

sub by_signal_tag {
	return $SIGNAL_TAGS{$a} <=> $SIGNAL_TAGS{$b}; }

sub by_makeinstance_tag {
	return $MAKEINSTANCE_TAGS{$a} <=> $MAKEINSTANCE_TAGS{$b}; }

sub by_alink_tag {
	return $ALINK_TAGS{$a} <=> $ALINK_TAGS{$b}; }

sub by_slink_tag {
	return $SLINK_TAGS{$a} <=> $SLINK_TAGS{$b}; }

sub by_tlink_tag {
	return $TLINK_TAGS{$a} <=> $TLINK_TAGS{$b}; }

sub by_syntax_tag {
	return $SYNTAX_TAGS{$a} <=> $SYNTAX_TAGS{$b}; }

sub createHashes {
	foreach my $tag (@EMPTY_TAGS) {
		$EMPTY_TAGS{$tag} = 1; }
	foreach my $tag (@TIMEML_TAGS) {
		$TIMEML_TAGS{$tag} = 1; }
	my $count = -9999;
	foreach my $att (@EVENT_TAGS) {
		$count++;
		$EVENT_TAGS{$att} = $count; }
	foreach my $att (@TIMEX3_TAGS) {
		$count++;
		$TIMEX3_TAGS{$att} = $count; }
	foreach my $att (@SIGNAL_TAGS) {
		$count++;
		$SIGNAL_TAGS{$att} = $count; }
	foreach my $att (@MAKEINSTANCE_TAGS) {
		$count++;
		$MAKEINSTANCE_TAGS{$att} = $count; }
	foreach my $att (@ALINK_TAGS) {
		$count++;
		$ALINK_TAGS{$att} = $count; }
	foreach my $att (@SLINK_TAGS) {
		$count++;
		$SLINK_TAGS{$att} = $count; }
	foreach my $att (@TLINK_TAGS) {
		$count++;
		$TLINK_TAGS{$att} = $count; }
	foreach my $att (@SYNTAX_TAGS) {
		$count++;
		$SYNTAX_TAGS{$att} = $count; }
}


## Debugging

sub indent {
	return unless $DEBUGGING;
	$indent .= '  '; }

sub outdent {
	return unless $DEBUGGING;
	$indent =~ s/^  //; }

sub debug {
	return unless $DEBUGGING;
	&indent;
	print STDERR $indent, $_[0], "\n"; }

1;
