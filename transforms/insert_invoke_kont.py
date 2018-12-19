"""BarrierKont Transform"""

# pylint: disable=invalid-name

from transforms.node_transformer import NodeTransformer
from omp.omp_ast import InvokeKont

class InsertInvokeKont(NodeTransformer):
    """Insert special InvokeKont"""

    def visit_OmpCritical(self, n):
        """Insert special InvokeKont node"""
        n = self.generic_visit(n)
        n.block.block_items.append(InvokeKont(None))
        return n

    def visit_OmpParallel(self, n):
        """Insert special InvokeKont node"""
        n = self.generic_visit(n)
        n.block.block_items.append(InvokeKont(None))
        return n

    def visit_OmpFor(self, n):
        """Insert special InvokeKont node"""
        n = self.generic_visit(n)
        n.loops.stmt.block_items.append(InvokeKont(None))
        return n
