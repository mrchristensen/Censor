"""
Wrap Ompfor in an extra compound block and lift any expressions
out of the for loop header. For example,

#pragma omp parallel for
for (int i = 0; i < a + b; ++i) {

}

might be transformed to
{
    int i;
    int censor01 = a + b;
    #pragma omp parallel for
    for (i = 0; i < censor01; ++i) {

    }
}
"""

from pycparser.c_ast import Assignment, ID, DeclList
# from .type_helpers import make_temp_ptr
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

    def visit_Ompfor(self, node):  #pylint: disable=invalid-name
        """Wrap Ompfor in an extra compound block and lift any expressions
        out of the for loop header."""
        loop = node.loops

        # find the name of the variable of iteration
        iter_var = None
        loop.init.show()
        if isinstance(loop.init, Assignment) and \
            isinstance(loop.init.lvalue, ID):
            iter_var = loop.init.lvalue.name
        elif isinstance(loop.init, DeclList) and \
            len(loop.init.decls) == 1:
            iter_var = loop.init.decls[0].name
        else:
            raise Exception("Invalid OMP for loop init.")

        # pull out condition to evaluate it to a constant in advance
        ident = ID(self.id_generator.get_unique_id())
        cond = Assignment("=", ident, None)
        if isinstance(loop.cond.left, ID) and \
            loop.cond.left.name == iter_var:
            cond.rvalue = loop.cond.right
            loop.cond.right = ident
        elif isinstance(loop.cond.right, ID) and \
            loop.cond.right.name == iter_var:
            cond.rvalue = loop.cond.left
            loop.cond.left = ident
        else:
            raise Exception("Invalid OMP for loop condition.")

        # TODO: do something with the iterator?

        node.loops.stmt = self.generic_visit(node.loops.stmt)
        return [cond, node]
