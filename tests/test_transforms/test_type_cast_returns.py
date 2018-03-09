"""Test """

from transforms.type_cast_returns import TypeCastReturns
from helpers import GoldenTestCase

class TestRemoveCompoundAssignment(GoldenTestCase):
    """Test RemoveCompoundAssignment transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/type_cast_returns'
        self.transformer = TypeCastReturns()

    def transform(self, ast):
        """Transform input AST"""
        return self.transformer.visit(ast)

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_golden(self.transform, self.fixtures)
