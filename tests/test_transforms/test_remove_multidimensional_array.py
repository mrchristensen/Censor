"""Test RemoveMultidimensionalArray transform"""

from tests.helpers import GoldenTestCase
from transforms.remove_multidimensional_arrays import RemoveMultidimensionalArray #pylint: disable=line-too-long
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from transforms.sizeof_type import SizeofType

class TestRemoveMultiDimensionalArrays(GoldenTestCase):
    """Test LiftToCompoundBlock transform"""

    def setUp(self): #pylint: disable=invalid-name
        """Set up test cases"""
        self.fixtures = ('/test_transforms/fixtures' +
                         '/remove_multidimensional_arrays')
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        ast = SizeofType(environments).visit(ast)
        self.transformer = (
            RemoveMultidimensionalArray(IDGenerator(ast), environments))
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
