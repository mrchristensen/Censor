"""Test asserting the correct order of calling functions."""

import unittest
from ssl.correct_call_order import verify_correctness
import pycparser

C = """extern void a();
        extern void b();
        extern void d();
        extern void e();
        extern void f();
        extern void g();

        void c() {
            e();
            f();
            g();
        }

        int main() {
            a();
            b();
            c();

            f();
            g();
        }"""

#pylint: disable=invalid-name
class TestCorrectCallOrder(unittest.TestCase):
    """Test correct call order."""
    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()

    def test_correct(self):
        """true case"""
        defined_orders = {'a': ['a', 'b', 'c'], 'f': ['f', 'g']}
        ast = self.parser.parse(C)
        self.assertTrue(verify_correctness(ast, defined_orders))

    def test_incorrect(self):
        """false case"""
        defined_orders = {'a': ['a', 'b', 'c'], 'f': ['e', 'f', 'g']}
        ast = self.parser.parse(C)
        self.assertFalse(verify_correctness(ast, defined_orders))
