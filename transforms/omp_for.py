"""Pragma to OMP For Node transform"""

from .ast_transform import ASTTransform

class PragmaToOmpFor(ASTTransform): #pylint: disable=too-few-public-methods
    """Pragma to OMP For Node transform"""

    def __init__(self):
        pass

    def transform(self, node):
        raise NotImplementedError("Not implemented transform")
