#!/usr/bin/perl

# ========================================================================
# validate.pl
# ========================================================================
#
# Uses XML::Checker::Parser to validate TempEval files. Usage:
#
#      perl validate.pl <dir>
#
# Only files with tml extension will be validated. Script needs to
# run from the directory it is in. Results are printed to standard
# output.
#
# ========================================================================

use XML::Checker::Parser;

my $extension = 'tml';
my $DIR = shift @ARGV ;
my $tmp_file = "tmp_validation_file.tml";

opendir DIR , $DIR or die "Cannot open $DIR\n";
my @files = sort grep /$extension$/ , readdir DIR;
open(STDERR, ">&STDOUT");

foreach $file (@files)
{
	# Create temporay file so we can add the DOCTYPE line needed for DTD validation
	open TML1,"$DIR/$file";
	open TML2, "> $tmp_file" or die "Cannot write to $tmp_file\n";
	while (<TML1>) {
		print TML2;
		if (/^<\?xml version/) {
			print TML2 '<!DOCTYPE TempEval SYSTEM "tempeval.dtd">', "\n";
		}
	}
	close TML1;
	close TML2;

	print STDERR "\n\n==> $file\n\n";
	my $parser = new XML::Checker::Parser ( Handlers => { } );
	eval { $parser->parsefile($tmp_file); };
	if ($@) {
		print STDERR "\nPARSE FAILED\n";
		print $@;
	}
}

`rm $tmp_file`;
