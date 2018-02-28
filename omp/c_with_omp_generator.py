"""Extended CGenerator to support OMP Nodes"""
from pycparser.c_generator import CGenerator
# This class is following a pattern that is required by the pycparser.CGenerator
# that pylint doesn't like. So:
#pylint: disable=invalid-name,missing-docstring,too-many-public-methods,no-self-use
class CWithOMPGenerator(CGenerator):
    """ Uses CGenerator to emit C code from an AST.
        Customized to support OMP Nodes.
        From CGenerator: Uses the same visitor pattern as c_ast.NodeVisitor,
        but modified to return a value from each visit method, using string
        accumulation in generic_visit.
    """
    def visit_DeclList(self, n):
        """Add semicolon to the end of DeclList"""
        return super().visit_DeclList(n) + ';'

    def visit_OmpFor(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpParallel(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpSections(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpSection(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpSingle(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpTask(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpTaskloop(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpTaskloopSimd(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpMaster(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpCritical(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpBarrier(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpTaskwait(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpTaskgroup(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpAtomic(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpFlush(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpCancel(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpCancellationPoint(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)

    def visit_OmpThreadprivate(self, n):
        """Return pragman string"""
        return '#pragma ' + n.pragma + '\n' + self.generic_visit(n)
