"""Shared Utility Functions for c analyzers"""

import os
import subprocess
from collections import namedtuple
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
    sed_path = os.path.dirname(os.path.realpath(__file__)) \
               + r'/utils/include_preserve.sed'
    res = subprocess.run(['sed', '-i', '-rf', sed_path, path])
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
    subprocess.run(
        ['sed', '-i', '-rf', inserting_sed, path],
    )
    subprocess.run(
        ['sed', '-i', '-rf', deleting_sed, path],
    )

def preserve_include_find_end(node, start_index):
    """Find end of #pragma BEGIN include block and return index"""
    for i, child in enumerate(node.ext[start_index:]):
        if isinstance(child, pycparser.c_ast.Pragma) \
            and "END" in child.string:

            return i + start_index

    return -1
