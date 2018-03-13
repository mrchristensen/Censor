"""Test ThreePlaceOperations -- Removing all"""

from transforms.three_place_operations import ThreePlaceOperations
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from helpers import GoldenTestCase

class TestThreePlaceOperations(GoldenTestCase):
    """Test ThreePlaceOperations transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/three_place_operations'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = ThreePlaceOperations(IDGenerator(ast), environments)
        return self.transformer.visit(ast)

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_golden(self.transform, self.fixtures)
