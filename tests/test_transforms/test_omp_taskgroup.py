"""Test PragmaToOmpTaskgroup -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
import omp
from transforms.omp_taskgroup import PragmaToOmpTaskgroup

#pylint: disable=invalid-name
class TestOmpTaskgroup(unittest.TestCase):
    """Test OmpTaskgroup Node"""

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        """Pragma node visitor; collect all pragma nodes"""

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            """Collect nodes, does not recurse as Pragma nodes have no children"""
            self.nodes.append(node)

    class OmpTaskgroupVisitor(omp.omp_ast.NodeVisitor):
        """OmpTaskgroup node visitor"""

        def __init__(self):
            self.nodes = []

        def visit_OmpTaskgroup(self, node):
            """Collect OmpTaskgroup nodes"""
            self.nodes.append(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpTaskgroup()

    def test_simple(self):
        """Test simple omp taskgroup pragma"""
        c = """
        int main() {
            #pragma omp parallel
            {
                #pragma omp taskgroup
                {
                }
            }
        }
        """
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1].block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpTaskgroupVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(1, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block)
