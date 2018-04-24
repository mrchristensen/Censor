"""NodeVisitor to determine order of function calls."""

from pycparser.c_ast import NodeVisitor

class FuncCallOrder(NodeVisitor):
    """Traverses the tree, determining the order that Function calls
    in each function definition."""

    def __init__(self):
        pass

    def visit_FuncDef(self, node): #pylint: disable=invalid-name
        """Create a new entry in the map for the function being visited."""
        pass

    def visit_FuncCall(self, node): #pylint: disable=invalid-name
        """Simply appends the funccall to the current list."""
        pass
