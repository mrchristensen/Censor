"""Test """

from helpers import GoldenTestCase
from transforms.sequence import Sequence
from transforms.id_generator import IDGenerator
from transforms.break_to_goto import BreakToGoto
from transforms.type_environment_calculator import TypeEnvironmentCalculator


class TestBreakToGoto(GoldenTestCase):
    """Test BreakToGoto transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/break_to_goto'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        calculator = TypeEnvironmentCalculator()
        self.transformer = BreakToGoto(
            IDGenerator(ast),
            calculator.get_environments(ast)
            )
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test BreakToGoto"""
        self.assert_all_transform_golden(self.transform, self.fixtures)