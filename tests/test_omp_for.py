"""Test PragmaToOmpFor -- Replacing Pragma omp with Omp Nodes"""

import unittest
import pycparser
from transforms.omp_for import PragmaToOmpFor

#pylint: disable=missing-docstring,invalid-name
class TestOmpFor(unittest.TestCase):
    """Test OmpFor Node"""

    class PragmaVisitor(pycparser.c_ast.NodeVisitor):
        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            self.nodes.append(node)

    class CompoundVisitor(pycparser.c_ast.NodeVisitor):
        def __init__(self):
            self.nodes = []

        def visit_Compound(self, node):
            self.nodes.append(node)

    class OmpForVisitor(pycparser.c_ast.NodeVisitor):
        def __init__(self):
            self.nodes = []

        def visit_OmpFor(self, node):
            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.omp_gen = PragmaToOmpFor()

    def test_simple(self):
        c = """
int main() {
    #pragma omp for
    for (int i = 0; i < 100; i++) {

    }
}
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        ast = self.omp_gen.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))


    def test_clauses_one(self):
        c = """
int main() {
    #pragma omp for collapse(2)
    for (int i = 0; i < 100; i++) {

    }
}
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        ast = self.omp_gen.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(["collapse(2)"], ov.nodes[0].clauses)

    def test_clauses_many(self):
        c = """
int main() {
    #pragma omp for collapse(2) ordered(2)
    for (int i = 0; i < 100; i++) {

    }
}
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        self.omp_gen.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(["collapse(2)", "ordered(2)"], ov.nodes[0].clauses)

    def test_nested_for(self):
        c = """
int main() {
    #pragma omp for collapse(2) ordered(2)
    for (int i = 0; i < 100; i++) {
        #pragma omp for
        for (int i = 0; i < 10; i++) {

        }
    }
}
        """
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpForVisitor()

        self.omp_gen.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(2, len(ov.nodes))
        self.assertEqual(["collapse(2)", "ordered(2)"], ov.nodes[0].clauses)
        self.assertEqual([], ov.nodes[1].clauses)
