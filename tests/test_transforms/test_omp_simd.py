"""Test PragmaToOmpSimd -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
import omp.clause as OmpClause
from transforms.omp_simd import PragmaToOmpSimd

#pylint: disable=missing-docstring,invalid-name
class TestOmpSimd(unittest.TestCase):
    """Test OmpSimd Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpSimdVisitor(omp.omp_ast.NodeVisitor):
        """OmpSimd node visitor; recursibely collect all OmpSimd nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpSimd(self, node):
            """Recursively collect OmpSimd nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpSimd()

    def test_simple(self):
        c = """
        int main() {
            #pragma omp simd
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSimdVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))


    def test_clauses_one(self):
        c = """
        int main() {
            #pragma omp simd collapse(2)
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSimdVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], OmpClause.Collapse))
        self.assertEqual(2, ov.nodes[0].clauses[0].n)

    def test_clauses_many(self):
        c = """
        int main() {
            #pragma omp simd collapse(2)
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSimdVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], OmpClause.Collapse))
        self.assertEqual(2, ov.nodes[0].clauses[0].n)

    def test_nested_for(self):
        c = """
        int main() {
            #pragma omp simd collapse(2)
            for (int i = 0; i < 100; i++) {
                #pragma omp simd
                for (int i = 0; i < 10; i++) {

                }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSimdVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(1, len(ov.nodes[0].clauses))
        self.assertEqual(0, len(ov.nodes[1].clauses))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], OmpClause.Collapse))
        self.assertEqual([], ov.nodes[1].clauses)
