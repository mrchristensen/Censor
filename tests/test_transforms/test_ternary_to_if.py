"""Test TernaryToIf"""

from transforms.ternary_to_if import TernaryToIf
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from helpers import GoldenTestCase

class TestTernaryToIf(GoldenTestCase):
    """Test TernaryToIf transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/ternary_to_if'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        calculator = TypeEnvironmentCalculator()
        self.transformer = TernaryToIf(
            IDGenerator(ast),
            calculator.get_environments(ast)
            )
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test TernaryToIf"""
        self.assert_all_golden(self.transform, self.fixtures)
