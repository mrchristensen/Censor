"""Test PragmaToOmpCancellationPoint -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_cancellation_point import PragmaToOmpCancellationPoint

#pylint: disable=missing-docstring,invalid-name
class TestOmpCancellationPoint(unittest.TestCase):
    """Test OmpCancellationPoint Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpCancellationPointVisitor(omp.omp_ast.NodeVisitor):
        """OmpCancellationPoint node visitor; recursibely collect all OmpCancel
        nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpCancellationPoint(self, node):
            """Recursively collect OmpCancellationPoint nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpCancellationPoint()

    def test_clauses_one(self):
        """Test omp cancellation point pragma with one clause"""
        c = """
        int main() {
            #pragma omp cancellation point parallel
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpCancellationPointVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp.clause.Parallel))
