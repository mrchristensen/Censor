"""Test FlattenStructRefs transform"""

from helpers import GoldenTestCase
from transforms.flatten_refs import FlattenRefs
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator

class TestFlattenStructRefs(GoldenTestCase):
    """Test FlattenStructRefs transform"""

    def setUp(self):
        """Set up test cases"""
        self.fixtures = './test_transforms/fixtures/flatten_refs'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = FlattenRefs(IDGenerator(ast), environments)
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_golden(self.transform, self.fixtures)
