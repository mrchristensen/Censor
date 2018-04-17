""" AST transform: complex if chains, as in:

        if (cond1) {

        } else if (cond2) {

        } else {

        }

    into if-goto chains, like:

        if (cond1) {
            //...
            goto end;
        }
        if (cond2) {
            //...
            goto end;
        }
        // Else branch
        end:
"""

from pycparser.c_ast import If, Compound, Goto, Label
from .node_transformer import NodeTransformer
from .type_helpers import NO_OP
from .helpers import ensure_compound

class IfToIfGoto(NodeTransformer):
    """NodeTransformer to change if-else-if-else to if-goto"""

    def __init__(self, id_gen):
        self.id_gen = id_gen

    def visit_If(self, node): #pylint: disable=invalid-name
        """ Recursively modify If
        """
        node = self.generic_visit(node)
        node.iftrue = ensure_compound(node.iftrue)
        node.iffalse = ensure_compound(node.iffalse)
        if node.iffalse is None:
            return node

        end_label = self.id_gen.get_unique_id() + "_ENDIF"
        return self.mangle_if(node, end_label) + [Label(end_label, NO_OP)]

    def mangle_if(self, node, end_label):
        """ If rewrite
        """
        true_branch = ensure_compound(node.iftrue)
        true_branch.block_items.append(Goto(end_label))

        false_branch = ensure_compound(node.iffalse)
        if isinstance(false_branch, If):
            false_branch = self.mangle_if(false_branch, end_label)
            return [If(node.cond, true_branch, None), false_branch]
        elif isinstance(false_branch, Compound):
            return [If(node.cond, true_branch, None), false_branch]
        else:
            return [If(node.cond, true_branch, None), Compound([false_branch])]
