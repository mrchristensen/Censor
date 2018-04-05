"""Instrumenter class for traversing anc instrumenting an AST"""
from transforms.lift_node import LiftNode
from transforms.helpers import ensure_compound
from utils import is_main
from .logger import Logger

class Instrumenter(LiftNode): #pylint: disable=too-many-public-methods
    """Instrumenter class"""
    def __init__(self, id_generator, environments):
        super().__init__(id_generator, environments)
        self.logger = Logger()

    def instrument_omp_log(self, block, construct):
        """Add sandwiching log statements at the beginning and end of an omp
        structured block"""
        block = ensure_compound(block)
        block.block_items.insert(0, self.logger.log_omp_enter(construct))
        block.block_items.append(self.logger.log_omp_exit(construct))
        return block

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
        node.block = self.instrument_omp_log(node.block, 'parallel')
        return node

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        """visit_OmpFor"""
        node = self.generic_visit(node)
        self.insert_into_scope(self.logger.log_omp_enter('for'))
        self.append_to_scope(self.logger.log_omp_exit('for'))
        return node

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        """visit_OmpSections"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.sections, 'sections')
        return node

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        """visit_OmpSection"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'section')
        return node

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        """visit_OmpSingle"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'single')
        return node

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        """visit_OmpTask"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'task')
        return node

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloop"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.loops, 'taskloop')
        return node

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        """visit_OmpMaster"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'master')
        return node

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        """visit_OmpCritical"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'critical')
        return node

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        """visit_OmpBarrier"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'barrier')
        return node

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskwait"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'taskwait')
        return node

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskgroup"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'taskgroup')
        return node

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        """visit_OmpAtomic"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'atomic')
        return node

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        """visit_OmpFlush"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'flush')
        return node

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        """visit_OmpCancel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'cancel')
        return node

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        """visit_OmpCancellationPoint"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'cancellationpoint')
        return node

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        """visit_OmpThreadprivate"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp_log(node.block, 'threadprivate')
        return node
