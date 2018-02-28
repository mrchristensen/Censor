"""Helper functions for instrumenting AST"""

import pycparser

def ensure_compound(node):
    """Wrap an AST node in a compound block if necessary"""
    if node is None:
        return pycparser.c_ast.Compound([])
    if isinstance(node, pycparser.c_ast.Compound):
        return node
    return pycparser.c_ast.Compound([node])
