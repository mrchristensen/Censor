"""Test PragmaToOmpFlush -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_flush import PragmaToOmpFlush

#pylint: disable=invalid-name
class TestOmpFlush(unittest.TestCase):
    """Test OmpFlush Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpFlushVisitor(omp.omp_ast.NodeVisitor):
        """OmpFlush node visitor; recursibely collect all OmpFlush nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpFlush(self, node):
            """Recursively collect OmpFlush nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpFlush()

    def test_simple(self):
        """Test simple omp flush pragma"""
        c = """
        int main() {
            #pragma omp flush
            for (int i = 0; i < 100; i++) {

            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpFlushVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(ov.nodes[0].clauses[0].ids, [])


    def test_clauses_one(self):
        """Test omp flush pragma with name clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp flush(id1, id2)
            {
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpFlushVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(ov.nodes[0].clauses[0].ids, ['id1', 'id2'])
