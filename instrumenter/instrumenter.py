"""Instrumenter class for traversing anc instrumenting an AST"""

from transforms.lift_node import LiftNode
from instrumenter.logger import Logger, is_yeti
from instrumenter.naive_instrumenter import NaiveInstrumenter
from utils import is_main

class Instrumenter(LiftNode):
    """Instrumenter class"""
    def __init__(self, id_generator, environments):
        super().__init__(id_generator, environments)
        self.registry = Logger()

    def make_instrumenter(self):
        """Return instrumenter for current environment"""
        # TODO replace NaiveInstrumenter with BigfootInstrumenter
        return NaiveInstrumenter(
            self.id_generator,
            self.environments,
            self.envr,
            self.registry
            )

    def visit_FileAST(self, node): # pylint:disable=invalid-name,no-self-use
        """Instrument file with function definitions"""
        node = self.generic_visit(node)
        return self.registry.embed_definitions(node)

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        """Log reads and writes in parallel regions"""
        return self.make_instrumenter().visit(node)

    def visit_FuncDef(self, node): #pylint: disable=invalid-name
        """Log reads and writes in function definitions"""
        # TODO maybe do a first pass to see which functions
        # are actually called in parallel regions and only
        # instrument those
        if is_main(node) or is_yeti(node):
            return self.generic_visit(node)
        return self.make_instrumenter().visit(node)
