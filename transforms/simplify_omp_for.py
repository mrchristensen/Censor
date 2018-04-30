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

        iter_var = self.get_iter_var(loop, nodes)
        bound_decl = self.pull_condition(loop, iter_var)
        if bound_decl is not None:
            nodes.append(bound_decl)

        # if the iteration is not simple incrementation, pull out iteration
        # step size, evaluate it to a constant in advance
        if isinstance(loop.next, UnaryOp):
            nodes.append(node)
            return Compound(nodes)
        else:
            iter_decl = self.pull_incrementation(loop, iter_var)
            nodes.append(iter_decl)
            node.loops.stmt = self.generic_visit(node.loops.stmt)
            nodes.append(node)
            return Compound(nodes)

    def get_iter_var(self, loop, nodes): #pylint: disable=no-self-use
        """"find the name of the variable of iteration, pull out the Decl if
        there is one."""
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
        return iter_var

    def pull_condition(self, loop, iter_var):
        """pull out condition to evaluate it to a constant in advance."""
        bound_decl = None
        if isinstance(loop.cond.left, ID) and isinstance(loop.cond.right, ID):
            return bound_decl
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
        return bound_decl

    def pull_incrementation(self, loop, iter_var):
        """Pull out iteration step size, evaluate it to a constant
        in advance."""
        iter_decl = None
        if isinstance(loop.next, Assignment):
            if len(loop.next.op) == 2:
                # Naive version of removing compound assignment. We don't need
                # to worry about side effects of the lvalue because "It is
                # unspecified whether, in what order, or how many time any side
                # effects within the lb, b, or incr expressions occur."
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
        return iter_decl
