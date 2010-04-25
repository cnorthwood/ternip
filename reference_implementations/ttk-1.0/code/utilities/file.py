"""Module containing simple file utilities."""

import os
import string

def file_contents(filename):
    """Same as file_contents_as_string."""
    return file_contents_as_string(filename)

def file_contents_as_string(filename):
    """Returns the contents of a file as a string."""
    f = open(filename, 'r')
    content = '.'.join(f.readlines())
    f.close()
    return content

def file_contents_as_list(filename):
    """Returns the contents of a file as a list."""
    f = open(filename, 'r')
    content = f.readlines()
    f.close()
    return content


def write_text_to_file(text, filename):
    """Write a string to a file. If the file already exists, it will
    be overwritten.
    Arguments:
       text - a string
       filename - an absolute path
    Returns True if succesful, False otherwise."""
    try:
        f = open(filename, 'w')
        f.write(text)
        f.close()
        return True
    except:
        return False

def read_settings(filename):
    """Read the content of filename and put flags and values in a
    dictionary. Each line in the file is either an empty line, a line
    starting with '#' or a attribute-value pair separated by a '='
    sign. Returns the dictionary."""
    file = open(filename, 'r')
    settings = {}
    for line in file:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        (flag, value) = map(string.strip, line.split('='))
        settings[flag] = value
    file.close()
    return settings

def write_settings(settings, filename):
    """Write a dictionary to a file, with one line per entry and with the
    key and value separated by an '=' sign."""
    os.rename(filename, filename+'.org')
    file = open(filename, 'w')
    for (flag, value) in settings.items():
        file.write("%s=%s\n" % (flag, value))
    file.close()
