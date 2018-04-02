"""Test PragmaToOmpCancel -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_cancel import PragmaToOmpCancel

#pylint: disable=missing-docstring,invalid-name
class TestOmpCancel(unittest.TestCase):
    """Test OmpCancel Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpCancelVisitor(omp.omp_ast.NodeVisitor):
        """OmpCancel node visitor; recursibely collect all OmpCancel nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpCancel(self, node):
            """Recursively collect OmpCancel nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpCancel()

    def test_clauses_one(self):
        """Test omp cancel pragma with one clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp cancel parallel
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpCancelVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp.clause.Parallel))

    def test_clauses_many(self):
        """Test omp cancel pragma with two clauses"""
        c = """
        int main() {
            #pragma omp cancel if(10) parallel
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpCancelVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)
        self.assertTrue(isinstance(ov.nodes[0].clauses[1], omp.clause.Parallel))
