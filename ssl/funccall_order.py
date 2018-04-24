"""NodeVisitor to determine order of function calls."""

from pycparser.c_ast import NodeVisitor

class FuncCallOrder(NodeVisitor):
    """Traverses the tree, determining the order that Function calls
    in each function definition."""

    def __init__(self):
        self.call_order = None
        self.current_function = None

    def visit_FuncDef(self, node): #pylint: disable=invalid-name
        """Create a new entry in the map for the function being visited."""
        name = node.decl.name
        self.call_order[name] = []
        self.current_function = name
        self.visit(node.body)
        self.current_function = None

    def visit_FuncCall(self, node): #pylint: disable=invalid-name
        """Simply appends the funccall to the current list."""
        # TODO: should we always ignore functions called in the arguments
        # of a function? Maybe its best to for OpenSSL purposes...
        self.call_order[self.current_function].append(node)

    def get_call_order(self, ast):
        """This is the only function that should be called publicly."""
        self.call_order = {}
        self.visit(ast)
        retval = self.call_order
        self.call_order = None
        self.current_function = None
        return retval
