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

# from pycparser.c_ast import Decl, UnaryOp, BinaryOp, Assignment, Compound, ID, PtrDecl
# from .type_helpers import get_type, add_identifier
from .node_transformer import NodeTransformer

class ThreePlaceOperations(NodeTransformer):
    """Transform that will reduce all arithmetic expressions to simple three
    place expressions."""
    def __init__(self, id_generator, environments):
        self.environments = environments
        self.envr = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Binop(self, node): #pylint: disable=invalid-name
        """For each operand of the binary operation that isn't a simple id,
        function call, or constant (or an id, function call, or constant wrapped
        by a Cast) simplify the computation recursively onto the previous lines,
        so that none of the lines have to be evaluated recursively"""
        return self.generic_visit(node)
