"""Test SizeofType"""

from transforms.sizeof_type import SizeofType
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase

class TestSizeofType(GoldenTestCase):
    """Test SizeofType transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/sizeof_type'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = SizeofType(environments)
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all fixtures"""
        self.assert_all_golden(self.transform, self.fixtures)
