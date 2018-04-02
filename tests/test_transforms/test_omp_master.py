"""Test PragmaToOmpMaster -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_master import PragmaToOmpMaster

#pylint: disable=invalid-name
class TestOmpMaster(unittest.TestCase):
    """Test OmpMaster Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no
            children"""
            self.nodes.append(node)

    class OmpMasterVisitor(omp.omp_ast.NodeVisitor):
        """OmpMaster node visitor; recursibely collect all OmpMaster nodes"""

        def __init__(self):
            self.nodes = []

        def visit_OmpMaster(self, node):
            """Recursively collect OmpMaster nodes"""

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpMaster()

    def test_simple(self):
        """Test simple omp master pragma"""
        c = """
        int main() {
            #pragma omp parallel
            {
                #pragma omp master
                for (int i = 0; i < 100; i++) {

                }
            }
        }
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpMasterVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(1, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
