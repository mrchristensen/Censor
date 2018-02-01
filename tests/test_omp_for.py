"""Test PragmaToOmpFor -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp_ast
from transforms.omp_for import PragmaToOmpFor

#pylint: disable=missing-docstring,invalid-name
class TestOmpFor(unittest.TestCase):
    """Test OmpFor Node"""

    class PragmaVisitor(pycparser.c_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpForVisitor(pycparser.c_ast.NodeVisitor):
        """OmpFor node visitor; recursibely collect all OmpFor nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpFor(self, node):
            """Recursively collect OmpFor nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpFor()

    def test_simple(self):
        c = """
        int main() {
            #pragma omp for
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))


    def test_clauses_one(self):
        c = """
        int main() {
            #pragma omp for collapse(2)
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp_ast.OmpClauseCollapse))
        self.assertEqual(2, ov.nodes[0].clauses[0].n)

    def test_clauses_many(self):
        c = """
        int main() {
            #pragma omp for collapse(2) ordered
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp_ast.OmpClauseCollapse))
        self.assertEqual(2, ov.nodes[0].clauses[0].n)
        self.assertTrue(isinstance(ov.nodes[0].clauses[1], omp_ast.OmpClauseOrdered))

    def test_nested_for(self):
        c = """
        int main() {
            #pragma omp for collapse(2) ordered
            for (int i = 0; i < 100; i++) {
                #pragma omp for
                for (int i = 0; i < 10; i++) {

                }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(2, len(ov.nodes[0].clauses))
        self.assertEqual(0, len(ov.nodes[1].clauses))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp_ast.OmpClauseCollapse))
        self.assertEqual(2, ov.nodes[0].clauses[0].n)
        self.assertTrue(isinstance(ov.nodes[0].clauses[1], omp_ast.OmpClauseOrdered))
        self.assertEqual([], ov.nodes[1].clauses)
