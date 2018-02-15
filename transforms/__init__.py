"""AST source to source transformations"""

from .for_to_while import ForToWhile
from .omp_for import PragmaToOmpFor

def transform(ast):
    """Perform each transform in package"""
    transformers = [PragmaToOmpFor(), ForToWhile()]
    for transformer in transformers:
        ast = transformer.visit(ast)
    return ast
