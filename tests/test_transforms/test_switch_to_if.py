"""Test SwitchToIf -- Replace switch statement with if and goto statements"""

from transforms.switch_if import SwitchToIf
from transforms.id_generator import IDGenerator
from helpers import GoldenTestCase

class TestSwitchToIf(GoldenTestCase):
    """Test SwitchToGoto transform"""

    def setUp(self):
        """Setup"""
        self.fixtures = '/test_transforms/fixtures/switch_to_if'
        self.transformer = None

    def transform(self, ast):
        """Transform Step"""
        self.transformer = SwitchToIf(IDGenerator(ast))
        ast = self.transformer.visit(ast)
        return ast

    def test_basic_switch(self):
        """ Test basic switch statement
        """
        input_file = self.fixtures + '/basic_switch_input.c'
        golden_file = self.fixtures + '/basic_switch_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_switch_no_default(self):
        """ Test switch statement with no default branch
        """
        input_file = self.fixtures + '/switch_no_default_input.c'
        golden_file = self.fixtures + '/switch_no_default_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_switch_reordered_default(self):
        """ Test switch statement with a default branch at some place other than the end
        """
        input_file = self.fixtures + '/switch_reordered_input.c'
        golden_file = self.fixtures + '/switch_reordered_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_nested_statements(self):
        """ Test switch statements with other switch or loop statements nested inside
        """
        input_file = self.fixtures + '/nested_statements_input.c'
        golden_file = self.fixtures + '/nested_statements_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_fall_through(self):
        """ Test cases with no breaks, forcing fall through
        """
        input_file = self.fixtures + '/fall_through_input.c'
        golden_file = self.fixtures + '/fall_through_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)
