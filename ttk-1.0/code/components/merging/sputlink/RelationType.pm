package RelationType;
use strict;

# This package is not intended as a class, simply a bunch of data
# structures and routines that are relevant for relation types and
# that were clogging up the Edge class.


# Convenience
# -----------

sub unspecifiedRel { return '< m o fi di si = s d f oi mi >'; }


# Sorting
# -------

# Use default ordering of basic relations, following Freksa. This
# stuff is a time-hog, fighting for supremacy with intersect and
# propagateConstraint.

my $relorder = { '<' => 1, 'm' => 2, 'o' => 3, 'fi' => 4, 'di' => 5, 'si' => 6, '=' => 7,
				 's' => 8, 'd' => 9, 'f' => 10, 'oi' => 11, 'mi' => 12, '>' => 13 };

sub sortRels {
	my $rel = shift;
    join ' ',  sort { $relorder->{$a} <=> $relorder->{$b} } split(/ /, $rel); }


# Reversing
# ---------

my $reversedTimemlRel = { 'BEFORE' => 'AFTER', 'IBEFORE' => 'IAFTER',
						  'AFTER' => 'BEFORE', 'IAFTER' => 'IBEFORE',
						  'INCLUDES' => 'IS_INCLUDED', 'IS_INCLUDED' => 'INCLUDES',
						  'IDENTITY' => 'IDENTITY', 'SIMULTANEOUS' => 'SIMULTANEOUS',
						  'HOLDS' => 'HELD_BY', 'HELD_BY' => 'HOLDS', 'DURING' => 'DURING',
						  'BEGINS' => 'BEGUN_BY', 'BEGUN_BY' => 'BEGINS',
						  'ENDS' => 'ENDED_BY', 'ENDED_BY' => 'ENDS' };

my $reversedBasicRels = { '<' => '>', 'm' => 'mi', 'o' => 'oi',
						  's' => 'si', 'd' => 'di', 'f' => 'fi', '=' => '=',
						  'fi' => 'f', 'si' => 's', 'di' => 'd',
						  'oi' => 'o', 'mi' => 'm', '>' => '<' };
	
# Reversing TimeML relations
sub reverseTimemlRel {
	my ($rel) = @_;
	$reversedTimemlRel->{$rel}; }

# reversing basic relations
sub reverseBasicRels {
	my ($brel) = @_;
	my @brel = split / /, $brel;
	my @brelrev = ();
	foreach my $el (@brel) {
		# use unshift rather then push so we don't have to sort the result
		unshift @brelrev, $reversedBasicRels->{$el}; }
	return join ' ', @brelrev; }


# Translating
# -----------

my $tml2basic = { 'before' => '<', 'ibefore' => 'm', 'after' => '>', 'iafter' => 'mi',
		  'includes' => 'di', 'is_included' => 'd',
		  'identity' => '=', 'simultaneous' => '=',
		  'holds' => '=', 'held_by' => '=', 'during' => '=',
		  'begins' => 's', 'begun_by' => 'si', 'ends' => 'f', 'ended_by' => 'fi' };

my $basic2tml = { '<' => 'before', 'm' => 'ibefore','>' => 'after', 'mi' => 'iafter',
		  'di' => 'includes', 'd' => 'is_included',
		  '=' => 'simultaneous',
		  's' => 'begins', 'si' => 'begun_by', 'f' => 'ends', 'fi' => 'ended_by' };

sub timemlrel2basicrel {
    my $timemlrel = lc $_[0];
    return $tml2basic->{$timemlrel}; }

sub basicrel2timemlrel {
    my $basicrel = shift;
    return uc $basic2tml->{$basicrel}; }


# Generating
# ----------

my $int2rel = { 1 => '<', 2 => 'm', 3 => 'o', 4 => 'si', 5 => 'di', 6 => 'fi', 7 => '=',
		8 => 's', 9 => 'd', 10 => 'i', 11 => 'oi', 12 => 'mi', 13 => '>' };

# generating a random basic relation
sub generateRandomRel {
	my $i = sprintf "%d", rand 13;
	return $int2rel->{$i}; }

# Generate a relation type but take into account the frequencies of
# TimeML relations. That is, a basic relation (or better, the TimeML
# relations that it maps to) is more likely to be generated if it
# occurs more often in reality. The frequencies are taken from
# timebank (total number of tlinks is 5581). The only exception is the
# frequency for u, which is taken from a small experiment with
# user-prompting which showed that about 24% of prompts resulted in an
# unknown relation.
sub generateAdjustedRel {
	my $i = sprintf "%d", rand 7441;	# 5581 + 5581/3 
	if ($i < 1178) { return '<'; }		# 1178
	if ($i < 1211) { return 'm'; }		#   33
	if ($i < 1211) { return 'o'; }		#    0
	if ($i < 1460) { return 'fi'; }		#  249
	if ($i < 2038) { return 'di'; }		#  578
	if ($i < 2148) { return 'si'; }		#  110
	if ($i < 3656) { return '='; }		# 1508
	if ($i < 3729) { return 's'; }		#   73
	if ($i < 4714) { return 'd'; }		#  985
	if ($i < 4810) { return 'f'; }		#   96
	if ($i < 4810) { return 'oi'; }		#    0
	if ($i < 4842) { return 'mi'; }		#   32
	if ($i < 5581) { return '>'; }		#  739
	if ($i < 7441) { return 'u'; }		# 1860
	else { return 'u'; }}


# Intersection
# ------------

# Intersection of sets of basic relations, taken from code on the
# web that also gets the union.
sub intersectBasicRels {
	my ($array1,$array2) = @_;
	my @array1 = split / /, $array1;
	my @array2 = split / /, $array2;
	my @intersection = ();
	my %count = ();
	foreach my $element (@array1, @array2) { $count{$element}++ }
	foreach my $element (keys %count) {
		if ($count{$element} > 1) {
			push @intersection, $element; }}
	return join ' ', @intersection; }



