#!/usr/bin/env python

import ternip.formats
import tempfile
import sys
import os
import subprocess

# Pre-process the file for GUTime
with open(sys.argv[1]) as fd:
    doc = ternip.formats.tern(fd.read())
    doc.reconcile(doc.get_sents(), add_S='s', add_LEX='lex', pos_attr='pos')
(in_file, file_path) = tempfile.mkstemp()
in_file = os.fdopen(in_file, 'w')
in_file.write(str(doc)[22:])
in_file.close()

# Now run GUTime
subprocess.Popen(['perl', 'gutime.pl', file_path, file_path + '.output'], cwd='gutime').communicate()

# Post-process to strip LEX and S tags
with open(file_path + '.output') as fd:
    doc = ternip.formats.tern(fd.read())
    doc.strip_tag('s')
    doc.strip_tag('lex')

# Clean up temporary files
os.remove(file_path)
os.remove(file_path + '.output')

# Print output
print str(doc)