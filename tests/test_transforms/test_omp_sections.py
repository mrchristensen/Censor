"""Test PragmaToOmpSections -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp.omp_ast
from transforms.omp_sections import PragmaToOmpSections

#pylint: disable=missing-docstring,invalid-name
class TestOmpSections(unittest.TestCase):
    """Test OmpSections Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpSectionsVisitor(omp.omp_ast.NodeVisitor):
        """OmpSections node visitor; recursibely collect all OmpSections
        nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpSections(self, node):
            """Recursively collect OmpSections nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpSections()

    def test_simple(self):
        """Test simple omp sections pragma"""
        c = """
        int main() {
            #pragma omp sections
            {
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpSectionsVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].sections)


    def test_clauses_one(self):
        """Test omp sections pragma with private clause"""
        c = """
        int main() {
            int i = 0;
            #pragma omp sections firstprivate(i)
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
        child = ast.ext[0].body.block_items[2]
        pv = self.PragmaVisitor()
        ov = self.OmpSectionsVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(3, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].sections)
        self.assertEqual(ov.nodes[0].clauses[0].ids, ['i'])

    def test_clauses_many(self):
        """Test omp sections pragma with two clauses"""
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
        child = ast.ext[0].body.block_items[2]
        pv = self.PragmaVisitor()
        ov = self.OmpSectionsVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(3, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].sections)
        self.assertEqual(ov.nodes[0].clauses[0].ids, ['i'])
        self.assertEqual(ov.nodes[0].clauses[1].ids, ['i'])
        self.assertEqual(ov.nodes[0].clauses[1].op, '+')
