"""
Transform that will reduce all arithmetic expressions to simple three place
expressions like
a = b + c;
that involve a single binary operation and a simple assignment (no compound
assignment). This will make it easy for the interpreter to evaluate each
line without needing to parse it recursively. Intermediate calculations
will be placed on previous lines, the order not being important because
order of evaluation of subexpressions is undefined.

For example,
int x = (int)((float)(1 + 3) + (4.5 + (float)(7 - 2)));

will be transformed to something like

int censor03 = 7 - 2;
float censor02 = 4.5 + (float)censor03;
float censor01 = 1 + 3;
int x = (int)(censor01 + censor02);

"""
from pycparser.c_ast import Cast, ID, FuncCall, Constant, BinaryOp, UnaryOp
from pycparser.c_ast import Decl, ArrayRef #, Assignment, Compound, PtrDecl
from .node_transformer import NodeTransformer
from .type_helpers import get_type, add_identifier

class ThreePlaceOperations(NodeTransformer):
    """Transform that will reduce all arithmetic expressions to simple three
    place expressions."""
    def __init__(self, id_generator, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Make sure self.env is up to date with the current scope."""
        parent = self.env
        self.env = self.environments[node]
        retval = self.generic_visit(node)
        self.env = parent
        return retval

    def visit_Decl(self, node): #pylint: disable=invalid-name
        """Decompose assignment expression in Decl"""
        if node.init is None:
            return node
        stmts = [node]
        self.recursively_simplify(node.init, stmts)
        stmts.reverse()
        return stmts

    def visit_Assignment(self, node): #pylint: disable=invalid-name
        """Decompose complex expressions in both the lvalue and the rvalue."""
        stmts = [node]
        self.recursively_simplify(node.lvalue, stmts)
        self.recursively_simplify(node.rvalue, stmts)
        stmts.reverse()
        return stmts

    def visit_Binop(self, node): #pylint: disable=invalid-name
        """For each operand of the binary operation where
        is_primitive(operand) == False (see function below), simplify the
        computation recursively onto the previous lines,so that none of the
        lines have to be evaluated recursively"""
        pass

    def recursively_simplify(self, node, new_lines):
        """Accumulates new lines to be inserted, in reverse order, and
        does the recursion."""
        # print("--recursively simplifying: "); node.show()
        if is_primitive(node):
            pass
        elif isinstance(node, Cast):
            self.recursively_simplify(node.expr, new_lines)
        elif isinstance(node, BinaryOp):
            if not is_primitive(node.left):
                stmt = self.make_new_decl(node.left)
                new_lines.append(stmt)
                self.recursively_simplify(node.left, new_lines)
                node.left = ID(stmt.name)
            if not is_primitive(node.right):
                stmt = self.make_new_decl(node.right)
                new_lines.append(stmt)
                self.recursively_simplify(node.right, new_lines)
                node.right = ID(stmt.name)
        elif isinstance(node, UnaryOp):
            if not is_primitive(node.expr):
                stmt = self.make_new_decl(node.expr)
                new_lines.append(stmt)
                self.recursively_simplify(node.expr, new_lines)
                node.expr = ID(stmt.name)
        else:
            raise NotImplementedError("")

    def make_new_decl(self, expr):
        """takes in an expression, makes a new Decl that declares a temp
        variable and initializes it using the given expression"""
        new_id = self.id_generator.get_unique_id()
        typ = get_type(expr, self.env)
        add_identifier(typ, new_id)
        stmt = Decl(new_id, [], [], [], typ, expr, None)
        return stmt

def is_primitive(node):
    """Returns a bool stating whether or not the given node is a basic unit of
    computation that can't be simplified."""
    while isinstance(node, Cast):
        node = node.expr
    return isinstance(node, (ID, Constant, FuncCall, ArrayRef))
