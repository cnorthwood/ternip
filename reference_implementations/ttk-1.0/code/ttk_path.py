"""Provides root directory and adds utilities directory to path

Get the directory the script runs from and add the directories with
ttk modules to the Python search path, inserting them after the
current directory. This script needs to be in the same directory as
ttk.py, the main python TTK script. I would really like this to be
done in the main tarsqi.py script.

Other modules can use the following to get at the root directory:

    from ttk_path import TTK_ROOT

Extending the path used to be how all imports were done, which was
rather moronic. The only holdout is the utilities directory. This is
because all FSA's in patterns were compiled while using the old
system, need to keep it until all FSA are recompiled.

"""

__author__ = 'marc@cs.brandeis.edu (Marc Verhagen)'
__date__ = 'July 16th, 2007'


import sys
import os

# This MUST be done differently, using os.getcwd(). The way it's done
# now makes it hard to run tarsqi from the python command line since
# we now get the current directory using sys.argv, which is empty
# when running tarsqi from the python prompt.
scriptName = sys.argv[0]
scriptPath = os.path.abspath(scriptName)
TTK_ROOT = os.path.dirname(scriptPath)

# need to get rid of this by recompiling all FSA's
sys.path[1:1] = [ os.path.join(TTK_ROOT,'utilities') ]

