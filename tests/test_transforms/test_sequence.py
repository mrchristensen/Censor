"""Test Sequence"""

from transforms.sequence import Sequence
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase

class TestSequence(GoldenTestCase):
    """Test Sequence transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/sequence'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        calculator = TypeEnvironmentCalculator()
        self.transformer = Sequence(
            IDGenerator(ast),
            calculator.get_environments(ast)
            )
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test Sequence"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
