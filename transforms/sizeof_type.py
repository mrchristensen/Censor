"""SizeofType Transform"""

from .node_transformer import NodeTransformer
from .type_helpers import get_type

class SizeofType(NodeTransformer):
    """
    Transform to replace 'sizeof(var_name) with 'sizeof(type_name)'
    so that future transforms can safely move UnaryOps around
    without worrying if identifiers will be undeclared.

    Example:
    struct node *n = (struct node*)malloc(sizeof(n));
    will become
    struct node *n = (struct node*)malloc(sizeof(struct node));

    For now this transform is only being applied in Decl nodes
    where identifiers are most commonly used unitialized
    """
    class ReplaceIDWithType(NodeTransformer):
        """Replace id with type in sizeof"""
        def __init__(self, envr):
            self.envr = envr

        def visit_UnaryOp(self, node): # pylint: disable=invalid-name
            """Replace sizeof(var) with sizeof(type)"""
            if node.op != 'sizeof':
                return node
            node.expr = get_type(node.expr, self.envr)
            return node

    def __init__(self, environments):
        self.environments = environments
        self.envr = self.environments["GLOBAL"]

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Change environment"""
        envr = self.envr
        self.envr = self.environments[node]
        retval = self.generic_visit(node)
        self.envr = envr
        return retval

    def visit_Decl(self, node): # pylint: disable=invalid-name
        """Replace sizeof(var) with sizeof(type)"""
        return self.ReplaceIDWithType(self.envr).visit(node)
