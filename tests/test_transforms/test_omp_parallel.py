"""Test PragmaToOmpParallel -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_parallel import PragmaToOmpParallel

#pylint: disable=missing-docstring,invalid-name
class TestOmpParallel(unittest.TestCase):
    """Test OmpParallel Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpParallelVisitor(omp.omp_ast.NodeVisitor):
        """OmpParallel node visitor; recursibely collect all OmpParallel nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpParallel(self, node):
            """Recursively collect OmpParallel nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpParallel()

    def test_simple(self):
        """Test simple omp parallel pragma"""
        c = """
        int main() {
            #pragma omp parallel
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpParallelVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block)


    def test_clauses_one(self):
        """Test omp parallel pragma with if clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp parallel if(10)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpParallelVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block, pycparser.c_ast.Compound))
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)

    def test_clauses_many(self):
        """Test omp parallel pragma with two clauses"""
        c = """
        int main() {
            int i = 0;
            #pragma omp parallel if(10) num_threads(4) default(shared) private(a) reduction(+: a, b, c)
            functionCall();
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpParallelVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block, pycparser.c_ast.FuncCall))
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)
        self.assertEqual(ov.nodes[0].clauses[1].num, 4)
        self.assertEqual(ov.nodes[0].clauses[2].state, 'shared')
        self.assertEqual(ov.nodes[0].clauses[3].ids, ['a'])
        self.assertEqual(ov.nodes[0].clauses[4].ids, ['a', 'b', 'c'])
        self.assertEqual(ov.nodes[0].clauses[4].op, '+')
