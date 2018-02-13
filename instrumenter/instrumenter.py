"""Instrumenter class for traversing anc instrumenting an AST"""
from transforms.node_transformer import NodeTransformer


class Instrumenter(NodeTransformer): #pylint: disable=too-many-public-methods
    """Instrumenter class"""
    def __init__(self):
        pass

    def visit_OmpParallel(self, node): #pylint: disable=invalid-name
        """visit_OmpParallel"""
        self.generic_visit(node)
        print('Visiting OmpParallel')
        node.show()

    def visit_OmpFor(self, node): #pylint: disable=invalid-name
        """visit_OmpFor"""
        self.generic_visit(node)
        print('Visiting OmpFor')
        node.show()

    def visit_OmpSections(self, node): #pylint: disable=invalid-name
        """visit_OmpSections"""
        self.generic_visit(node)
        print('Visiting OmpSections')
        node.show()

    def visit_OmpSection(self, node): #pylint: disable=invalid-name
        """visit_OmpSection"""
        self.generic_visit(node)
        print('Visiting OmpParallel')
        node.show()

    def visit_OmpSingle(self, node): #pylint: disable=invalid-name
        """visit_OmpSingle"""
        self.generic_visit(node)
        print('Visiting OmpSingle')
        node.show()

    def visit_OmpSimd(self, node): #pylint: disable=invalid-name
        """visit_OmpSimd"""
        self.generic_visit(node)
        print('Visiting OmpSimd')
        node.show()

    def visit_OmpDeclareSimd(self, node): #pylint: disable=invalid-name
        """visit_OmpDeclareSimd"""
        self.generic_visit(node)
        print('Visiting OmpDeclareSimd')
        node.show()

    def visit_OmpForSimd(self, node): #pylint: disable=invalid-name
        """visit_OmpForSimd"""
        self.generic_visit(node)
        print('Visiting OmpForSimd')
        node.show()

    def visit_OmpTask(self, node): #pylint: disable=invalid-name
        """visit_OmpTask"""
        self.generic_visit(node)
        print('Visiting OmpTask')
        node.show()

    def visit_OmpTaskloop(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloop"""
        self.generic_visit(node)
        print('Visiting OmpTaskloop')
        node.show()

    def visit_OmpTaskloopSimd(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskloopSimd"""
        self.generic_visit(node)
        print('Visiting OmpTaskloopSimd')
        node.show()

    def visit_OmpTaskyield(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskyield"""
        self.generic_visit(node)
        print('Visiting OmpTaskyield')
        node.show()

    def visit_OmpMaster(self, node): #pylint: disable=invalid-name
        """visit_OmpMaster"""
        self.generic_visit(node)
        print('Visiting OmpMaster')
        node.show()

    def visit_OmpCritical(self, node): #pylint: disable=invalid-name
        """visit_OmpCritical"""
        self.generic_visit(node)
        print('Visiting OmpCritical')
        node.show()

    def visit_OmpBarrier(self, node): #pylint: disable=invalid-name
        """visit_OmpBarrier"""
        self.generic_visit(node)
        print('Visiting OmpBarrier')
        node.show()

    def visit_OmpTaskwait(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskwait"""
        self.generic_visit(node)
        print('Visiting OmpTaskwait')
        node.show()

    def visit_OmpTaskgroup(self, node): #pylint: disable=invalid-name
        """visit_OmpTaskgroup"""
        self.generic_visit(node)
        print('Visiting OmpTaskgroup')
        node.show()

    def visit_OmpAtomic(self, node): #pylint: disable=invalid-name
        """visit_OmpAtomic"""
        self.generic_visit(node)
        print('Visiting OmpAtomic')
        node.show()

    def visit_OmpFlush(self, node): #pylint: disable=invalid-name
        """visit_OmpFlush"""
        self.generic_visit(node)
        print('Visiting OmpFlush')
        node.show()

    def visit_OmpOrdered(self, node): #pylint: disable=invalid-name
        """visit_OmpOrdered"""
        self.generic_visit(node)
        print('Visiting OmpOrdered')
        node.show()

    def visit_OmpCancel(self, node): #pylint: disable=invalid-name
        """visit_OmpCancel"""
        self.generic_visit(node)
        print('Visiting OmpCancel')
        node.show()

    def visit_OmpCancellationPoint(self, node): #pylint: disable=invalid-name
        """visit_OmpCancellationPoint"""
        self.generic_visit(node)
        print('Visiting OmpCancellationPoint')
        node.show()

    def visit_OmpThreadprivate(self, node): #pylint: disable=invalid-name
        """visit_OmpThreadprivate"""
        self.generic_visit(node)
        print('Visiting OmpThreadprivate')
        node.show()

    def visit_OmpDeclareReduction(self, node): #pylint: disable=invalid-name
        """visit_OmpDeclareReduction"""
        self.generic_visit(node)
        print('Visiting OmpDeclareReduction')
        node.show()
