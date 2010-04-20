
while (<>) {
    s/replaced-dns\/NNS <repdns text="[^"]*" \/>//g;
    print;
}
