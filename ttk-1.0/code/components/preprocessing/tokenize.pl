use Tokenize;

my $infile = shift;
my $outfile = shift;

&Tokenize::Tokenize_File($infile, $outfile);
#&Tokenize::Tokenize_File('DATA/IN/user_in','DATA/IN/user_in.spl');
