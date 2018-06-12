"""Test ChangeToVoidPointer transform"""

from tests.helpers import GoldenTestCase
from transforms.change_void_pointer import ChangeToVoidPointer
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from transforms.sizeof_type import SizeofType

class TestRemoveMultiDimensionalArrays(GoldenTestCase):
    """Test LiftToCompoundBlock transform"""

    def setUp(self):
        """Set up test cases"""
        self.fixtures = '/test_transforms/fixtures/change_void_pointer'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        ast = SizeofType(environments).visit(ast)
        self.transformer = ChangeToVoidPointer(IDGenerator(ast), environments)
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
