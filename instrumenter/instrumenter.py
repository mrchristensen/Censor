"""Instrumenter class for traversing anc instrumenting an AST"""
from transforms.node_transformer import NodeTransformer
from utils import is_main
from .helpers import ensure_compound
from .logger import Logger

class Instrumenter(NodeTransformer): #pylint: disable=too-many-public-methods
    """Instrumenter class"""
    def __init__(self):
        self.logger = Logger()

    def instrument_omp_log(self, compound, construct):
        """Add sandwiching log statements at the beginning and end of an omp structured block"""
        compound.block_items.insert(0, self.logger.log_omp_enter(construct))
        compound.block_items.append(self.logger.log_omp_exit(construct))
        return compound

    def visit_FileAST(self, node): #pylint: disable=invalid-name
        """visit_FileAST"""
        node = self.generic_visit(node)
        for i, block in enumerate(node.ext):
            if is_main(block):
                node.ext.insert(i, self.logger.log_omp_def)
                node.ext.insert(i, self.logger.log_heap_def)
                break
        return node

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        """visit_OmpParallel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(ensure_compound(node.block), 'parallel')
        return node

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        """visit_OmpFor"""
        node = self.generic_visit(node)
        return node

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        """visit_OmpSections"""
        node = self.generic_visit(node)
        return node

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        """visit_OmpSection"""
        node = self.generic_visit(node)
        return node

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        """visit_OmpSingle"""
        node = self.generic_visit(node)
        return node

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        """visit_OmpTask"""
        node = self.generic_visit(node)
        return node

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloop"""
        node = self.generic_visit(node)
        return node

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        """visit_OmpMaster"""
        node = self.generic_visit(node)
        return node

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        """visit_OmpCritical"""
        node = self.generic_visit(node)
        return node

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        """visit_OmpBarrier"""
        node = self.generic_visit(node)
        return node

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskwait"""
        node = self.generic_visit(node)
        return node

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskgroup"""
        node = self.generic_visit(node)
        return node

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        """visit_OmpAtomic"""
        node = self.generic_visit(node)
        return node

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        """visit_OmpFlush"""
        node = self.generic_visit(node)
        return node

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        """visit_OmpCancel"""
        node = self.generic_visit(node)
        return node

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        """visit_OmpCancellationPoint"""
        node = self.generic_visit(node)
        return node

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        """visit_OmpThreadprivate"""
        node = self.generic_visit(node)
        return node
