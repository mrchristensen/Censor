"""Test PragmaToOmpSection -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_section import PragmaToOmpSection

#pylint: disable=missing-docstring,invalid-name
class TestOmpSection(unittest.TestCase):
    """Test OmpSection Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpSectionVisitor(omp.omp_ast.NodeVisitor):
        """OmpSection node visitor; recursibely collect all OmpSection nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpSection(self, node):
            """Recursively collect OmpSection nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpSection()

    def test_simple(self):
        """Test omp section pragma with two clauses"""
        c = """
        int main() {
            int i = 0;
            #pragma omp sections private(i) reduction(+: i)
            {
                #pragma omp section
                { i++; }
                #pragma omp section
                { i++; }
                #pragma omp section
                { i++; }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpSectionVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(1, len(pv.nodes))
        self.assertEqual(3, len(ov.nodes))
        for section in ov.nodes:
            self.assertTrue(isinstance(section.block, pycparser.c_ast.Compound))
