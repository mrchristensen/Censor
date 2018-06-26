"""Test RemoveTypedef Transform"""

from tests.helpers import GoldenTestCase
from transforms.remove_typedef import RemoveTypedef
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from transforms.sizeof_type import SizeofType

class TestRemoveTypedef(GoldenTestCase):
    """Test RemoveTypedef transform"""

    def setUp(self): #pylint: disable=invalid-name
        """Set up test cases"""
        self.fixtures = ('/test_transforms/fixtures' +
                         '/remove_typedef')
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        ast = SizeofType(environments).visit(ast)
        self.transformer = (
            RemoveTypedef(IDGenerator(ast), environments))
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
