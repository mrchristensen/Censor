"""Test PragmaToOmpParallelFor -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_parallel_for import PragmaToOmpParallelFor

#pylint: disable=missing-docstring,invalid-name
class TestOmpParallelFor(unittest.TestCase):
    """Test OmpParallelFor Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpParallelForVisitor(omp.omp_ast.NodeVisitor):
        """OmpParallelFor node visitor; recursibely collect all OmpParallelFor nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpParallel(self, node):
            """Recursively collect OmpParallel nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

        def visit_OmpFor(self, node):
            """Recursively collect OmpFor nodes"""
            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpParallelFor()

    def test_simple(self):
        """Test simple omp parallel for pragma"""
        c = """
        int main() {
            #pragma omp parallel for
            for (int i = 0; i < 10; i++)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpParallelForVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(ov.nodes[1], ov.nodes[0].block.block_items[0])
        self.assertEqual(child, ov.nodes[1].loops)


    def test_clauses_one(self):
        """Test omp parallel for pragma with if clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp parallel for if(10) schedule(static, 2)
            for (int i = 0; i < 10; i++)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[2]
        pv = self.PragmaVisitor()
        ov = self.OmpParallelForVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(ov.nodes[1], ov.nodes[0].block.block_items[0])
        self.assertEqual(child, ov.nodes[1].loops)
        self.assertEqual(10, ov.nodes[0].clauses[0].scalar)
        self.assertEqual('static', ov.nodes[1].clauses[0].kind)

    def test_clauses_many(self):
        """Test omp parallel for pragma with two clauses"""
        c = """
        int main() {
            int i = 0;
            #pragma omp parallel for if(10) num_threads(4) default(shared) private(a) reduction(+: a, b, c) lastprivate(i)
            for(int i = 0; i < 10; i++);
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[2]
        pv = self.PragmaVisitor()
        ov = self.OmpParallelForVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(ov.nodes[1], ov.nodes[0].block.block_items[0])
        self.assertEqual(child, ov.nodes[1].loops)
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)
        self.assertEqual(ov.nodes[0].clauses[1].num, 4)
        self.assertEqual(ov.nodes[0].clauses[2].state, 'shared')
        self.assertEqual(ov.nodes[0].clauses[3].ids, ['a'])
        self.assertEqual(ov.nodes[0].clauses[4].ids, ['a', 'b', 'c'])
        self.assertEqual(ov.nodes[0].clauses[4].op, '+')
        self.assertEqual(ov.nodes[1].clauses[0].ids, ['a'])
        self.assertEqual(ov.nodes[1].clauses[1].op, '+')
        self.assertEqual(ov.nodes[1].clauses[1].ids, ['a', 'b', 'c'])
        self.assertEqual(ov.nodes[1].clauses[2].ids, ['i'])
