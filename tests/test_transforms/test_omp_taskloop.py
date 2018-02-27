"""Test PragmaToOmpTaskloop -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_taskloop import PragmaToOmpTaskloop

#pylint: disable=missing-docstring,invalid-name
class TestOmpTaskloop(unittest.TestCase):
    """Test OmpTaskloop Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpTaskloopVisitor(omp.omp_ast.NodeVisitor):
        """OmpTaskloop node visitor; recursibely collect all OmpTaskloop nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpTaskloop(self, node):
            """Recursively collect OmpTaskloop nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpTaskloop()

    def test_simple(self):
        """Test simple omp taskloop pragma"""
        c = """
        int main() {
            #pragma omp taskloop
            for (int i = 0; i < 10; i++)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpTaskloopVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].loops)


    def test_clauses_one(self):
        """Test omp taskloop pragma with if clause"""
        c = """
        int main() {
            #pragma omp taskloop if(10)
            for (int i = 0; i < 10; i++)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpTaskloopVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].loops)
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)

    def test_clauses_many(self):
        """Test omp taskloop pragma with two clauses"""
        c = """
        int main() {
            #pragma omp taskloop if(10) default(shared) private(a) priority(10)
            for (int i = 0; i < 10; i++) {}
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpTaskloopVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].loops)
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)
        self.assertEqual(ov.nodes[0].clauses[1].state, 'shared')
        self.assertEqual(ov.nodes[0].clauses[2].ids, ['a'])
        self.assertEqual(ov.nodes[0].clauses[3].value, 10)
