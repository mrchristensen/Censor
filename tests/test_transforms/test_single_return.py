"""Test """

from transforms.single_return import SingleReturn
from transforms.id_generator import IDGenerator
from helpers import GoldenTestCase

class TestSingleReturn(GoldenTestCase):
    """Test RemoveCompoundAssignment transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/single_return'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        self.transformer = SingleReturn(IDGenerator(ast))
        return self.transformer.visit(ast)

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_golden(self.transform, self.fixtures)
