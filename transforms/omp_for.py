"""Pragma to OMP For Node transform"""

from .ast_transform import NodeTransformer

class PragmaToOmpFor(NodeTransformer): #pylint: disable=too-few-public-methods
    """Pragma to OMP For Node transform"""

    def __init__(self):
        pass

    def visit(self, node):
        raise NotImplementedError("Not implemented transform")
