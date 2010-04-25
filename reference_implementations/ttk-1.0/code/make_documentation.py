"""

Create manual pages with the docstrings for modules, classes and
functions. This latter functionality was added because pydoc breaks on
some of the tarsqi modules, most notably those that import the
treetagger.

NOTES:
- code creates potentially undesired documentation for the module
  components.preprocessing.wrapper, adding a couple of module-level
  functions that are not there in the code, but are imported
  functions.

"""

# not used yet, private methods are never printed
print_private_methods = True


import os
import sys
import inspect
from types import ClassType, FunctionType, MethodType

from modules import MODULES


javascript_code = \
"""<script language="JavaScript" type="text/JavaScript">
<!--

function view_code(id) {
  var newurl = "../functions/" + id + ".html";
  var w = window.open(newurl,"source code","width=770,height=600,scrollbars=yes,resizable=yes"); 
  w.xopener = window;
}

//-->
</script>
"""

FUNCTION_ID = 0

    
def print_module_documentation(module):
    filename = os.path.join('..', 'docs', 'code', 'modules', module.__name__+'.html')
    docfile = open(filename,'w')
    docfile.write("<html>\n<head>\n")
    docfile.write("")
    docfile.write('<link href="../css/module.css" rel="stylesheet" type="text/css">'+"\n")
    docfile.write(javascript_code)
    docfile.write("</head>\n<body>\n")
    docfile.write('<a href=../index.html>index</a>' + "\n\n")
    docfile.write('<div class="title">module ' + module.__name__ + "</div>\n\n")
    docstring = get_docstring(module)
    if docstring:
        docfile.write("<pre>\n" + docstring + "</pre>\n\n")
    print_function_documentation(docfile, get_functions(module))
    print_class_documentation(docfile, get_classes(module))

def print_class_documentation(docfile, classes):
    classes.sort(lambda x,y: cmp(str(x),str(y)))
    for class_object in classes:
        (module_name, class_name) = get_module_and_class_name(class_object)
        docfile.write("\n" + '<a name="' + class_name + '"/>')
        docfile.write('<div class="section">class ' + class_name + "</div>\n")
        docfile.write("<pre>\n")
        docstring = get_docstring(class_object)
        if docstring:
            docfile.write(docstring)
        for base_class in class_object.__bases__:
            (module_name, class_name) = get_module_and_class_name(base_class)
            ref = module_name + '.html#' + class_name
            docfile.write("\n\n<strong>Inherits from: <a href=%s>%s</a></strong>\n" % 
                          (ref, str(base_class)))
        docfile.write("</pre>\n\n")
        functions = get_functions(class_object)
        functions.sort(lambda x, y: cmp(x[0],y[0]))
        public_functions = get_public_functions(functions)
        private_functions = get_private_functions(functions)
        if public_functions:
            docfile.write("<h3>Public Functions</h3>\n")
            docfile.write("<blockquote>\n")
            for (name,fun) in public_functions:
                print_function(name, fun, docfile)
            docfile.write("</blockquote>\n")
        if private_functions and print_private_methods:
            docfile.write("<h3>Private Functions</h3>\n")
            docfile.write("<blockquote>\n")
            for (name,fun) in private_functions:
                print_function(name, fun, docfile)
            docfile.write("</blockquote>\n")

def print_function_documentation(docfile, functions):
    if functions:
        docfile.write("\n" + '<div class="section">functions</div>'+"\n")
    functions.sort(lambda x, y: cmp(x[0],y[0]))
    for (name, fun) in get_public_functions(functions):
        print_function(name, fun, docfile)

def get_classes(module):
    classes = []
    for (key, val) in module.__dict__.items():
        if type(val) == ClassType:
            if val.__dict__['__module__'] == module.__name__:
                classes.append(val)
    return classes

def get_functions(class_object):
    functions = []
    for (key, val) in class_object.__dict__.items():
        if type(val) == FunctionType:
            functions.append([key,val])
    return functions

def get_public_functions(functions):
    public_functions = []
    for (name, fun) in functions:
        if name.startswith('__') or not name.startswith('_'):
            public_functions.append((name,fun))
    return public_functions

def get_private_functions(functions):
    private_functions = []
    for (name, fun) in functions:
        if name.startswith('_') and not name.startswith('__'):
            private_functions.append((name,fun))
    return private_functions

def print_function(name, fun, docfile):
    global FUNCTION_ID
    funname = get_function_name(fun)
    docstring = get_docstring(fun)
    docfile.write("<pre>\n")
    docfile.write("<div class=function>%s</div>\n" % funname)
    docfile.write(docstring)
    FUNCTION_ID += 1
    id = "%04d" % FUNCTION_ID
    if docstring:
        docfile.write("\n\n")
    docfile.write("<a href=javascript:view_code(\"%s\")>view source</a>" % id)
    funname = get_function_name(fun)
    print_function_code(id, funname, fun)
    docfile.write("</pre>\n")
    
def get_function_name(fun):
    try:
        firstline = inspect.getsourcelines(fun)[0][0]
    except IOError:
        # needed for some imports, like "from string import lower"
        firstline = ''
        print 'WARNING: could not get source lines of', fun
    firstline = firstline.strip()
    firstline = firstline[4:-1]
    return firstline
    
def print_function_code(id, name, fun):
    filename = os.path.join('..', 'docs', 'code', 'functions', "%s.html" % id)
    funfile = open(filename, "w")
    funfile.write("<html>\n<head>\n")
    funfile.write('<link href="../css/function.css" rel="stylesheet" type="text/css">'+"\n")
    funfile.write("</head>\n<body>\n")
    #funfile.write("<h3>%s</h3>\n" % name)
    funfile.write('<pre>')
    code = "".join(inspect.getsourcelines(fun)[0])
    code = trim(code, 0)
    funfile.write(code)
    funfile.write('</pre>')

def get_docstring(object):
    docstring = ''
    if object.__doc__:
        docstring = object.__doc__
    return trim(protect(docstring))

def print_docstring(object, docfile, prefix=''):
    docstring = get_docstring(object)
    docfile.write("<pre>\n" + docstring)
    if type(object) == FunctionType:
        global FUNCTION_ID
        FUNCTION_ID += 1
        id = "%04d" % FUNCTION_ID
        if docstring:
            docfile.write("\n\n")
        #docfile.write("<a href=\"functions/%s.html\">view source</a>\n" % id)
        docfile.write("<a href=javascript:view_code(\"%s\")>view source</a>" % id)
        funname = get_function_name(object)
        print_function_code(id, funname, object)
    docfile.write("</pre>\n")
    
def protect(docstring):
    docstring = docstring.replace('<', '&lt;')
    docstring = docstring.replace('>', '&gt;')
    docstring = docstring.strip()
    return docstring

def get_module_and_class_name(base_class):
    class_string = str(base_class)
    components = class_string.split('.')
    module_name = '.'.join(components[:-1])
    class_name = components[-1]
    return (module_name, class_name)

def trim(docstring, linenum=1):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count for
    # docstrings):
    indent = sys.maxint
    for line in lines[linenum:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)



if __name__ == '__main__':

    # use this if user specified just a set of modules, only create
    # documentation for those modules (this will by the way screw up
    # the numbering for functions, so it should only be used to
    # quickly check updated documentation for a module, documentation
    # for other modules may be off)
    if sys.argv[1:]:
        for module_name in sys.argv[1:]:
            module = eval(module_name)
            analyse_module(module)
            print_module_documentation(module)
        sys.exit()

    # otherwise, do everything
    filename = os.path.join('..', 'docs', 'code', 'index.html')
    indexfile = open(filename,'w')
    indexfile.write("<html>\n<head>\n")
    indexfile.write("<link rel=\"stylesheet\" href=\"css/list.css\"> \n")
    indexfile.write("</head>\n<body>\n")
    indexfile.write("<h3>Tarsqi Toolkit Module Documentation</h3>\n")
    indexfile.write("<ul>\n")
    for module in MODULES:
        name = module.__name__
        indexfile.write("<li><a href=modules/%s.html>%s</a>\n" % (name, name))
        print_module_documentation(module)
    indexfile.write("</ul>\n</body>\n</html>\n")
