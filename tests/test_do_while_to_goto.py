"""Test DoWhileToGoto -- Replacing do-while loops with goto code"""

from transforms.do_while_to_goto import DoWhileToGoto
from helpers import GoldenTestCase

class TestDoWhileToGoto(GoldenTestCase):
    """Test DoWhileToGoto transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.module = 'do_while_to_goto'
        self.transform = DoWhileToGoto()

    def test_simple_stmt(self):
        """Test DoWhile loop with one statement"""
        input_file = './fixtures/do_while_to_goto/simple_stmt_input.c'
        golden = './fixtures/do_while_to_goto/simple_stmt_golden.c'
        input_c = open(input_file, 'r').read()
        ast = self.parser.parse(input_c)
        transformed = self.transform.visit(ast)
        actual = self.generator.visit(transformed)
        self.assert_golden(golden, actual)

    def test_simple_compound(self):
        """Test DoWhile loop with a compound statement"""
        input_file = './fixtures/do_while_to_goto/simple_compound_input.c'
        golden = './fixtures/do_while_to_goto/simple_compound_golden.c'
        input_c = open(input_file, 'r').read()
        ast = self.parser.parse(input_c)
        transformed = self.transform.visit(ast)
        actual = self.generator.visit(transformed)
        self.assert_golden(golden, actual)

    def test_nested(self):
        """Test DoWhile loop with a nested loop"""
        input_file = './fixtures/do_while_to_goto/nested_input.c'
        golden = './fixtures/do_while_to_goto/nested_golden.c'
        input_c = open(input_file, 'r').read()
        ast = self.parser.parse(input_c)
        transformed = self.transform.visit(ast)
        actual = self.generator.visit(transformed)
        self.assert_golden(golden, actual)
