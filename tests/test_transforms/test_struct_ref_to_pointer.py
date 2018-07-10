"""Test Struct Ref removal"""

from transforms.struct_ref_to_pointer import StructRefToPointerArith
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase

class StructRefToPointerTest(GoldenTestCase):
    """Test TernaryToIf transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/struct_ref_to_pointer'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        calculator = TypeEnvironmentCalculator()
        self.transformer = StructRefToPointerArith(
            IDGenerator(ast),
            calculator.get_environments(ast)
            )
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test TernaryToIf"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
