"""Test PragmaToOmpAtomic -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_atomic import PragmaToOmpAtomic

#pylint: disable=invalid-name
class TestOmpAtomic(unittest.TestCase):
    """Test OmpAtomic Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpAtomicVisitor(omp.omp_ast.NodeVisitor):
        """OmpAtomic node visitor; recursibely collect all OmpAtomic nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpAtomic(self, node):
            """Recursively collect OmpAtomic nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpAtomic()

    def test_simple(self):
        """Test simple omp atomic pragma"""
        c = """
        int main() {
            #pragma omp atomic
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpAtomicVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block)
        self.assertEqual(0, len(ov.nodes[0].clauses))


    def test_clauses_one(self):
        """Test omp atomic pragma with name clause"""
        c = """
        int main() {
            #pragma omp atomic read
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpAtomicVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block)
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp.clause.Read))

    def test_clauses_many(self):
        """Test omp atomic pragma with two clauses"""
        c = """
        int main() {
            #pragma omp atomic seq_cst write
            i++;
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpAtomicVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block.block_items[0])
        self.assertTrue(isinstance(ov.nodes[0].clauses[1], omp.clause.Write))
        self.assertTrue(isinstance(ov.nodes[0].clauses[0], omp.clause.SeqCst))
