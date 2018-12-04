"""Test AlphaName"""

from transforms.alpha_name import AlphaName
from tests.helpers import GoldenTestCase

# pylint: disable=no-self-use
class TestAlphaName(GoldenTestCase):
    """Test AlphaName transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/alpha_name'

    def transform(self, ast):
        """Transform input AST"""
        return AlphaName().visit(ast)

    def test_fixtures(self):
        """Test AlphaName"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
