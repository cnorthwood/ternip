"""

This module sets up the the MaxEnt Classifier for several platforms
and changes the settings.txt file.

Usage:

    python setup.py platform=linux|osx [flag=value]*

The platform flag is needed to determine what classifier executable to
use. This script will install the correct version given this setting
(currently, only Mac OSX and Linux are supported). All other flags
result in adding or changing lines to the settings.txt file. That file
is read when the toolkit starts up and all its settings are added to
the processing parameters. The only settings that make sense are those
processing parameters that are understood by the toolkit, see the
manual for a listing.

If settings.txt does not have a line like with a perl setting then it
will make a guess as to where the Perl executable lives. In most
cases, it will add

    perl=perl

but if setup.py can find an ActivePerl distribution it will use the
path to it, for example:

    perl=/usr/local/ActivePerl-5.8/bin/perl

Specifying a Perl flag overrides this.

"""

import sys
import os
import string

from ttk_path import TTK_ROOT
from utilities.file import read_settings, write_settings


CLASSIFIER_DIR = os.path.join(TTK_ROOT, 'components', 'classifier')

USAGE = "python setup.py platform=linux|osx [flag=value]*"



def setup_classifier(ostype):
    """Sets up the Classifier. It first cleans out old binaries and
    then unpacks new ones appropriate to the ostype. This method
    assumes that the classifier directory contains files
    mxtest.opt.OSTYPE and mxtrain.opt.OSTYPE."""
    os.chdir(CLASSIFIER_DIR)
    for file in ('mxtest.opt', 'mxtrain.opt'):
        if os.path.exists(file):
            os.remove(file)
    if ostype == 'osx':
        print "Setting up classifier for OSX"
        os.system("cp mxtest.opt.osx mxtest.opt")
        os.system("cp mxtrain.opt.osx mxtrain.opt")
    elif ostype == 'linux':
        print "Setting up classifier for Linux"
        os.system("cp mxtest.opt.linux mxtest.opt")
        os.system("cp mxtrain.opt.linux mxtrain.opt")
    else:
        print "Warning: ostype %s is not supported" % ostype
    os.chdir(TTK_ROOT)
    

def add_perl_path(settings):
    """Add a Perl path to the settings if there wasn't one yet."""
    if not settings.has_key('perl'):
        settings['perl'] = 'perl'
        path = get_active_state_perl()
        if path:
            settings['perl'] = path

def get_active_state_perl():
    """Return None or the path to the ActivePerl executable if it can find
    one. Looks for a directory starting with 'ActivePerl' inside of
    '/usr/local'. This method is designed to work only for OSX."""
    # NOTE: check whether this fails gracefully on Windows
    usr_local = os.path.join('/usr', 'local')
    if os.path.isdir(usr_local):
        for file in os.listdir(usr_local):
            if file.startswith('ActivePerl'):
                return os.path.join(usr_local, file, 'bin', 'perl')
    return None
        



if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.exit("\nMissing platform flag\nUsage: %s\n" % USAGE)

    args = sys.argv[1:]
    platform_flag = args.pop(0)
    try:
        (platform, ostype) = map(string.strip, platform_flag.split('='))
    except ValueError:
        sys.exit("\nUnexpected argument\nUsage: %s\n" % USAGE)
    if (platform != 'platform'):
        sys.exit("\nIllegal first flag.\nUsage: %s\n" % USAGE)
    if ostype in ('osx', 'linux'):
        setup_classifier(ostype)
    else:
        sys.exit("\nUnsupported os type\nUsage: %s\n" % USAGE)

    print "Updating settings.txt"
    flags = {}
    for arg in args:
        try:
            (flag, value) = map(string.strip, arg.split('='))
            flags[flag] = value
        except ValueError:
            sys.exit("\nUnexpected argument.\nUsage: %s\n" % USAGE)

    settings = read_settings('settings.txt')
    add_perl_path(settings)
    settings.update(flags)
    write_settings(settings, 'settings.txt')
