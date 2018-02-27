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
        golden_file = './fixtures/do_while_to_goto/simple_stmt_golden.c'
        self.assert_golden(golden_file, input_file)

    def test_simple_compound(self):
        """Test DoWhile loop with a compound statement"""
        input_file = './fixtures/do_while_to_goto/simple_compound_input.c'
        golden_file = './fixtures/do_while_to_goto/simple_compound_golden.c'
        self.assert_golden(golden_file, input_file)

    def test_nested(self):
        """Test DoWhile loop with a nested loop"""
        input_file = './fixtures/do_while_to_goto/nested_input.c'
        golden_file = './fixtures/do_while_to_goto/nested_golden.c'
        self.assert_golden(golden_file, input_file)
