"""Test ForToWhile -- Replacing for with while loops"""

import unittest
import pycparser
from transforms.for_to_while import ForToWhile
from helpers import ForVisitor, WhileVisitor

SIMPLE_FOR_LOOP = """
int main() {
    for (int i = 0; i < 100; i++) {

    }
}
"""
NESTED_FOR_LOOP = """
int main() {
    for (int i = 0; i < 100; i++) {
        for (int i = 0; i < 100; i++) {

        }
    }
}
"""

class TestForToWhile(unittest.TestCase):
    """Test ForToWhile transform"""

    @classmethod
    def setUpClass(cls):
        cls.transform = ForToWhile()
        cls.parser = pycparser.CParser()

    def test_replace_one(self):
        """Test that one for loop translates to one while loop"""

        ast = self.parser.parse(SIMPLE_FOR_LOOP)
        fors = ForVisitor()
        whiles = WhileVisitor()

        ast = self.transform.visit(ast)

        fors.visit(ast)
        whiles.visit(ast)

        self.assertEqual(0, len(fors.nodes))
        self.assertEqual(1, len(whiles.nodes))

    def test_nested_for(self):
        """Test that nested for loops are transformed"""

        ast = self.parser.parse(NESTED_FOR_LOOP)
        fors = ForVisitor()
        whiles = WhileVisitor()

        ast = self.transform.visit(ast)
        ast.show()

        fors.visit(ast)
        whiles.visit(ast)

        self.assertEqual(0, len(fors.nodes))
        self.assertEqual(1, len(whiles.nodes))

        whiles.visit(whiles.nodes[0])
        self.assertEqual(2, len(whiles.nodes))
