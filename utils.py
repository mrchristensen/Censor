"""Shared Utility Functions for c analyzers"""

import os
import platform
import subprocess
from collections import namedtuple
import re
import pycparser

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
    with open(path, 'r') as myfile:
        data = myfile.read()
    newdata = re.sub(
        r'(#include\s*<([:a-zA-Z0-9:]|/)+\.[:a-zA-Z:]>)',
        r'#pragma BEGIN \1\n\1\n#pragma END/',
        data)
    open(path, "w").write(newdata)

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

def semicolon(start_index, string):
    """if semicolon"""
    index = start_index
    while string[index].isspace():
        index += 1

    if string[index] == ';':
        index += 1
    else:
        return start_index

    return index

def volatile(start_index, string):
    """ finds end match of a paren ( returns that index,
        returns start_index if no paren found """
    index = start_index
    while string[index].isspace():
        index += 1

    if string[index:index+8] == 'volatile':
        index += 8
    else:
        return start_index

    return index

def remove_gcc_extentions(text):
    """ Run sed on source file to remove selected common gcc extentions
    """
    pattern = r'(asm)|(__restrict__)|(__inline__)|(__extension__)|(__attribute(__)*)|(\({)' #pylint: disable=line-too-long
    matches = re.finditer(pattern, text)
    if matches is None:
        return text
    replacements = []
    last_index = 0
    for match in matches:
        #match.group() start and end
        if match.start() < last_index:
            continue
        if match.group() == 'asm':
            end_index = volatile(match.end(), text)
            end_index = paren_match(end_index, text)
            if end_index == match.end():
                continue
            end_index = semicolon(end_index, text)
            replacements.append((match.start(), end_index, ''))
            last_index = end_index

        elif (match.group() == '__attribute__' or
              match.group() == '__attribute'):
            end_index = paren_match(match.end(), text)
            if end_index == match.end():
                continue
            replacements.append((match.start(), end_index, ''))
            last_index = end_index

        elif match.group() == '__inline__':
            replacements.append((match.start(), match.end(), 'inline'))
            last_index = end_index

        elif match.group() == '__restrict__' or '__extension__':
            replacements.append((match.start(), match.end(), ''))
            last_index = end_index
        elif match.group() == '({':
            end_index = paren_match(match.start(), text)
            if end_index == match.start():
                continue
            #before_semi_colon = end_index
            #end_index = semicolon(end_index, text)
            #if end_index == before_semi_colon:
            replacements.append((match.start(), end_index, '0'))
            #else:
            #    replacements.append((match.start(), end_index, '0;'))
            last_index = end_index

    altered_text = []
    index = 0
    for (begin, end, replace) in replacements:
        altered_text += text[index:begin] + replace
        index = end
    altered_text += text[index:]

    return "".join(altered_text)

def paren_match(start_index, string):
    """ finds end match of a paren ( returns that index,
    returns start_index if no paren found """
    index = start_index
    while string[index].isspace():
        index += 1
    if string[index] == '(':
        index += 1
    else:
        return start_index
    parencount = 1
    while parencount != 0:
        if string[index] == '(':
            parencount += 1
        elif string[index] == ')':
            parencount -= 1
        index += 1
    return index
