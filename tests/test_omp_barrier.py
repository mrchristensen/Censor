"""Test PragmaToOmpBarrier -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_barrier import PragmaToOmpBarrier

#pylint: disable=invalid-name
class TestOmpBarrier(unittest.TestCase):
    """Test OmpBarrier Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpBarrierVisitor(omp.omp_ast.NodeVisitor):
        """OmpBarrier node visitor"""

        def __init__(self):
            self.nodes = []

        def visit_OmpBarrier(self, node):
            """Collect OmpBarrier nodes"""
            self.nodes.append(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpBarrier()

    def test_simple(self):
        """Test simple omp barrier pragma"""
        c = """
        int main() {
            #pragma omp parallel
            {
                #pragma omp master
                for (int i = 0; i < 10; i++) {
                }
                #pragma omp barrier
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpBarrierVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(2, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
