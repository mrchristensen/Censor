"""Shared Utility Functions for c analyzers"""

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
