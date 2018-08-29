"""Shared Utility Functions for c analyzers"""

import os
import platform
import subprocess
from collections import namedtuple
import pycparser
import pickle

Function = namedtuple('Function', ['funcDef'])

Thread = namedtuple('Thread', ['function', 'init_store'])

State = namedtuple('State', ['loc', 'store'])

def find_main(ast):
    """Examines the AST for a unique main function."""
    mains = [child for child in ast.ext if is_main(child)]
    if len(mains) == 1:
        return Function(mains[0])
    else:
        raise Exception("No main function found")

def is_main(ext):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(ext, pycparser.c_ast.FuncDef) and ext.decl.name == 'main'

def sanitize(ast):
    """ Strip fake includes from preprocessed ast.
    """
    from transforms.helpers import NodeTransformer
    class Sanitizer(NodeTransformer):
        """Sanitizing NodeTransformer"""
        def visit_FileAST(self, node): #pylint: disable=invalid-name, no-self-use
            """Visit the FileAST and remove typedefs included by fake libc"""
            marks = []
            for i, child in enumerate(node):
                if isinstance(child, pycparser.c_ast.Pragma) \
                    and "BEGIN" in child.string:

                    end = preserve_include_find_end(node, i)
                    if end == -1:
                        raise RuntimeError("Could not find ending Pragma!")

                    marks.append((i+1, end+1))

            diff = 0
            for (begin, end) in marks:
                begin -= diff
                end -= diff
                del node.ext[begin:end]
                diff += end - begin

    Sanitizer().visit(ast)

def preserve_include_preprocess(path):
    """ Run sed on source file to preserve includes through gcc preprocessing
    """
    sed_path = os.path.dirname(os.path.realpath(__file__)) \
               + r'/utils/include_preserve.sed'
    res = run_sed_file(sed_path, path)
    if res.returncode != 0:
        raise RuntimeError('Could not perform include preserve preprocessing!')

def preserve_include_postprocess(path):
    """ Run sed on transformed source file to remove fake_libc_includes and
        replace them with the original includes.
    """
    inserting_sed = os.path.dirname(os.path.realpath(__file__)) \
                    + r'/utils/insert_includes.sed'
    deleting_sed = os.path.dirname(os.path.realpath(__file__)) \
                   + r'/utils/remove_fake_includes.sed'
    run_sed_file(inserting_sed, path)
    run_sed_file(deleting_sed, path)

def run_sed_file(sed, path):
    """ Runs the custom preprocessing on the files based on the sed version """
    if platform.system() == 'Darwin':
        return subprocess.run(['sed', '-Ef', sed, path])
    else:
        return subprocess.run(['sed', '-i', '-rf', sed, path])

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

def preserve_include_find_end(node, start_index):
    """Find end of #pragma BEGIN include block and return index"""
    for i, child in enumerate(node.ext[start_index:]):
        if isinstance(child, pycparser.c_ast.Pragma) \
            and "END" in child.string:

            return i + start_index

    return -1

def find_dependencies(path_to_makefile="./", name_of_makefile="Makefile"):
    '''Returns a list of Strings of all of the depenencies of a makefile.
    Currently extracts each "example.c" in all instances of "make -dn"
    outputting a "Considering target file 'example.c'."'''
    command = 'make -dn -C ' + path_to_makefile
    command += ' -f ' + name_of_makefile
    c_file = "\'.*\\.c\'"
    consider = "Considering target file " + c_file + "\\."
    not_found = "File " + c_file + " does not exist."
    grep = ' | grep "' + consider + "\\|" + not_found + '"'
    command += grep
    command += ' | cut -f2 -d "\'"'
    pipe = subprocess.PIPE
    out = subprocess.STDOUT
    popen = subprocess.Popen(command, shell=True, stdout=pipe, stderr=out)
    output = popen.communicate()[0]
    output = output.decode('ascii').split('\n')
    output = [path_to_makefile + item for item in output if len(item) is not 0]
    dependencies = []
    index = 0
    while index < len(output):
        if index == len(output) - 1:
            dependencies.append(output[index])
        elif output[index] != output[index + 1]:#check to see if file exists
            dependencies.append(output[index])
        else:
            index += 1 # skip duplicate and don't add either
        index += 1
    return dependencies
