"""Test IfToIfGoto -- Replace if-else-if-else with if-goto statements"""

from transforms.if_goto import IfToIfGoto
from transforms.id_generator import IDGenerator
from helpers import GoldenTestCase

class TestIfToIfGoto(GoldenTestCase):
    """Test IfToIfGoto transform"""

    def setUp(self):
        """Setup"""
        self.fixtures = './test_transforms/fixtures/if_goto'
        self.transformer = None

    def transform(self, ast):
        """Transform Step"""
        self.transformer = IfToIfGoto(IDGenerator(ast))
        ast = self.transformer.visit(ast)
        return ast

    def test_simple_stmt(self):
        """ Test if-else statement
        """
        input_file = self.fixtures + '/if_else_input.c'
        golden_file = self.fixtures + '/if_else_golden.c'
        self.assert_golden(self.transform, golden_file, input_file)

    def test_complex_stmt(self):
        """ Test if-else-if-else statement
        """
        input_file = self.fixtures + '/if_else_if_else_input.c'
        golden_file = self.fixtures + '/if_else_if_else_golden.c'
        self.assert_golden(self.transform, golden_file, input_file)

    def test_simple_nested_stmt(self):
        """ Test if-else-if-else statement
        """
        input_file = self.fixtures + '/nested_if_input.c'
        golden_file = self.fixtures + '/nested_if_golden.c'
        self.assert_golden(self.transform, golden_file, input_file)

    def test_nested_if_else_stmt(self):
        """ Test if-else-if-else statement
        """
        input_file = self.fixtures + '/nested_if_else_input.c'
        golden_file = self.fixtures + '/nested_if_else_golden.c'
        self.assert_golden(self.transform, golden_file, input_file)
