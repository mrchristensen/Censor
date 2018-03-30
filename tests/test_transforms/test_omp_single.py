"""Test PragmaToOmpSingle -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_single import PragmaToOmpSingle

#pylint: disable=invalid-name
class TestOmpSingle(unittest.TestCase):
    """Test OmpSingle Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
             children"""
            self.nodes.append(node)

    class OmpSingleVisitor(omp.omp_ast.NodeVisitor):
        """OmpSingle node visitor; recursibely collect all OmpSingle nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpSingle(self, node):
            """Recursively collect OmpSingle nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpSingle()

    def test_simple(self):
        """Test simple omp single pragma"""
        c = """
        int main() {
            #pragma omp parallel
            {
                #pragma omp single
                for (int i = 0; i < 100; i++) {

                }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSingleVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(1, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))

    def test_clauses(self):
        """Test simple omp single pragma with clauses"""
        c = """
        int main() {
            #pragma omp parallel
            {
                #pragma omp single firstprivate(i) nowait
                for (int i = 0; i < 100; i++) {

                }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSingleVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(1, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(ov.nodes[0].clauses[0].ids, ['i'])
        self.assertTrue(isinstance(ov.nodes[0].clauses[0],
                                   omp.clause.FirstPrivate))
        self.assertTrue(isinstance(ov.nodes[0].clauses[1], omp.clause.NoWait))
