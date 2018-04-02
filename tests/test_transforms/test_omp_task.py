"""Test PragmaToOmpTask -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_task import PragmaToOmpTask

#pylint: disable=missing-docstring,invalid-name
class TestOmpTask(unittest.TestCase):
    """Test OmpTask Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpTaskVisitor(omp.omp_ast.NodeVisitor):
        """OmpTask node visitor; recursibely collect all OmpTask nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpTask(self, node):
            """Recursively collect OmpTask nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpTask()

    def test_simple(self):
        """Test simple omp task pragma"""
        c = """
        int main() {
            #pragma omp task
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpTaskVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block)


    def test_clauses_one(self):
        """Test omp task pragma with if clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp task if(10)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpTaskVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block, pycparser.c_ast.Compound))
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)

    def test_clauses_many(self):
        """Test omp task pragma with two clauses"""
        c = """
        int main() {
            int i = 0;
            #pragma omp task if(10) default(shared) private(a) priority(10)
            functionCall();
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpTaskVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block.block_items[0],
                                   pycparser.c_ast.FuncCall))
        self.assertEqual(ov.nodes[0].clauses[0].scalar, 10)
        self.assertEqual(ov.nodes[0].clauses[1].state, 'shared')
        self.assertEqual(ov.nodes[0].clauses[2].ids, ['a'])
        self.assertEqual(ov.nodes[0].clauses[3].value, 10)
