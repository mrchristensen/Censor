"""Extended CGenerator to support OMP Nodes"""

from pycparser.c_generator import CGenerator

# This class is following a pattern that is required by the pycparser.CGenerator
# that pylint doesn't like. So:
#pylint: disable=invalid-name,missing-docstring,too-many-public-methods
class CWithOMPGenerator(CGenerator):
    """ Uses CGenerator to emit C code from an AST.
        Customized to support OMP Nodes.

        From CGenerator: Uses the same visitor pattern as c_ast.NodeVisitor,
        but modified to return a value from each visit method, using string
        accumulation in generic_visit.
    """

    def visit_OmpFor(self, n):
        pass

    def visit_OmpParallel(self, n):
        pass

    def visit_OmpSections(self, n):
        pass

    def visit_OmpSection(self, n):
        pass

    def visit_OmpSingle(self, n):
        pass

    def visit_OmpSimd(self, n):
        pass

    def visit_OmpDeclareSimd(self, n):
        pass

    def visit_OmpForSimd(self, n):
        pass

    def visit_OmpTask(self, n):
        pass

    def visit_OmpTaskloop(self, n):
        pass

    def visit_OmpTaskloopSimd(self, n):
        pass

    def visit_OmpTaskyield(self, n):
        pass

    def visit_OmpMaster(self, n):
        pass

    def visit_OmpCritical(self, n):
        pass

    def visit_OmpBarrier(self, n):
        pass

    def visit_OmpTaskwait(self, n):
        pass

    def visit_OmpTaskgroup(self, n):
        pass

    def visit_OmpAtomic(self, n):
        pass

    def visit_OmpFlush(self, n):
        pass

    def visit_OmpOrdered(self, n):
        pass

    def visit_OmpCancel(self, n):
        pass

    def visit_OmpCancellationPoint(self, n):
        pass

    def visit_OmpThreadprivate(self, n):
        pass

    def visit_OmpDeclareReduction(self, n):
        pass
