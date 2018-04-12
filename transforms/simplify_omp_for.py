"""
Wrap Ompfor in an extra compound block and lift any expressions
out of the for loop header. For example,

#pragma omp parallel for
for (int i = 0; i < a + b; i = i + (c + d)) {

}

might be transformed to
{
    int i;
    int censor01 = a + b;
    int censor02 = c + d;
    #pragma omp parallel for
    for (i = 0; i < censor01; i = i + censor02) {

    }
}
"""

from pycparser.c_ast import Assignment, DeclList, Compound, UnaryOp, BinaryOp
from pycparser.c_ast import ID
from .type_helpers import make_temp_value
from .node_transformer import NodeTransformer

class SimplifyOmpFor(NodeTransformer):
    """Transform to simplify the header of omp for loops."""
    def __init__(self, id_generator, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Compound(self, node): #pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.env
        self.env = self.environments[node]
        retval = self.generic_visit(node)
        self.env = parent
        return retval

    def visit_OmpFor(self, node):  #pylint: disable=invalid-name
        """Wrap Ompfor in an extra compound block and lift any expressions
        out of the for loop header."""
        loop = node.loops
        nodes = []

        # find the name of the variable of iteration, pull out the Decl if
        # there is one
        iter_var = None
        if isinstance(loop.init, Assignment) and \
            isinstance(loop.init.lvalue, ID):
            iter_var = loop.init.lvalue.name
        elif isinstance(loop.init, DeclList) and \
            len(loop.init.decls) == 1:
            decl = loop.init.decls[0]
            iter_var = decl.name
            nodes.append(decl)
            loop.init = Assignment("=", ID(iter_var), decl.init)
        else:
            raise Exception("Invalid OMP for loop init.")

        # pull out condition to evaluate it to a constant in advance
        bound_decl = None
        if isinstance(loop.cond.left, ID) and loop.cond.left.name == iter_var:
            bound_decl = make_temp_value(loop.cond.right,
                                         self.id_generator, self.env)
            loop.cond.right = ID(bound_decl.name)
        elif isinstance(loop.cond.right, ID) and \
            loop.cond.right.name == iter_var:
            bound_decl = make_temp_value(loop.cond.left,
                                         self.id_generator, self.env)
            loop.cond.left = ID(bound_decl.name)
        else:
            raise Exception("Invalid OMP for loop condition.")
        nodes.append(bound_decl)

        # if the iteration is not simple incrementation, pull out iteration
        # step size, evaluate it to a constant in advance

        if isinstance(loop.next, UnaryOp):
            nodes.append(node)
            return Compound(nodes)

        iter_decl = None
        if isinstance(loop.next, Assignment):
            if len(loop.next.op) == 2:
                binop = BinaryOp(loop.next.op[0], loop.next.lvalue,
                                 loop.next.rvalue)
                loop.next = Assignment("=", loop.next.lvalue, binop)

            binop = loop.next.rvalue
            if isinstance(binop.left, ID) and binop.left.name == iter_var:
                iter_decl = make_temp_value(binop.right,
                                            self.id_generator, self.env)
                binop.right = ID(iter_decl.name)
            elif isinstance(binop.right, ID) and binop.right.name == iter_var:
                iter_decl = make_temp_value(binop.left,
                                            self.id_generator, self.env)
                binop.left = ID(iter_decl.name)
        else:
            raise Exception("Invalid OMP for loop incrementation.")

        nodes.append(iter_decl)
        node.loops.stmt = self.generic_visit(node.loops.stmt)
        nodes.append(node)
        return Compound(nodes)
