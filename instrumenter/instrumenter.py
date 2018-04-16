"""Instrumenter class for traversing anc instrumenting an AST"""
from omp.clause import Reduction, FirstPrivate, LastPrivate
from transforms.lift_node import LiftNode
from transforms.helpers import ensure_compound
from .logger import Logger

class Instrumenter(LiftNode): #pylint: disable=too-many-public-methods
    """Instrumenter class"""
    def __init__(self, id_generator, environments):
        super().__init__(id_generator, environments)
        self.registry = Logger()

    def register_implicit_reads(self, omp_node):
        """Instrument AST with a list of AST objects to register implicit
        reads made by OpenMP clauses on the omp node"""
        if hasattr(omp_node, 'clauses'):
            for clause in omp_node.clauses:
                if isinstance(clause, (Reduction, FirstPrivate)):
                    refs = [self.registry.register_read(r) for r in clause.ids]
                    self.insert_into_scope(*refs)

    def register_implicit_writes(self, omp_node):
        """Instrument AST with a list of AST objects to register implicit
        writes made by OpenMP clauses on the omp node"""
        if hasattr(omp_node, 'clauses'):
            for clause in omp_node.clauses:
                if isinstance(clause, (LastPrivate, Reduction)):
                    refs = [self.registry.register_write(w) for w in clause.ids]
                    self.append_to_scope(*refs)

    def instrument_omp(self, block, construct):
        """Add sandwiching log statements at the beginning and end of an omp
        structured block"""
        block = ensure_compound(block)
        block.block_items.insert(0, self.registry.register_omp_enter(construct))
        block.block_items.append(self.registry.register_omp_exit(construct))
        return block

    def visit_FileAST(self, node): #pylint: disable=invalid-name
        """visit_FileAST"""
        node = self.generic_visit(node)
        return self.registry.embed_definitions(node)

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        """visit_OmpParallel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'parallel')
        return node

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        """visit_OmpFor"""
        node = self.generic_visit(node)
        self.register_implicit_reads(node)
        self.insert_into_scope(self.registry.register_omp_enter('for'))
        self.append_to_scope(self.registry.register_omp_exit('for'))
        self.register_implicit_writes(node)
        return node

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        """visit_OmpSections"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.sections, 'sections')
        return node

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        """visit_OmpSection"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'section')
        return node

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        """visit_OmpSingle"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'single')
        return node

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        """visit_OmpTask"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'task')
        return node

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloop"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.loops, 'taskloop')
        return node

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        """visit_OmpMaster"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'master')
        return node

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        """visit_OmpCritical"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'critical')
        return node

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        """visit_OmpBarrier"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'barrier')
        return node

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskwait"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'taskwait')
        return node

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskgroup"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'taskgroup')
        return node

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        """visit_OmpAtomic"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'atomic')
        return node

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        """visit_OmpFlush"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'flush')
        return node

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        """visit_OmpCancel"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'cancel')
        return node

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        """visit_OmpCancellationPoint"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'cancellationpoint')
        return node

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        """visit_OmpThreadprivate"""
        node = self.generic_visit(node)
        node.block = self.instrument_omp(node.block, 'threadprivate')
        return node
