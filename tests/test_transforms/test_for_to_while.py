"""Test ForToWhile -- Replacing for with while loops"""

from transforms.for_to_while import ForToWhile
from transforms.omp_for import PragmaToOmpFor
from tests.helpers import GoldenTestCase

class TestForToWhile(GoldenTestCase):
    """Test ForToWhile transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/for_to_while'
        self.transformer = ForToWhile()

    def transform(self, ast):
        """Transform input AST"""
        pre_transformer = PragmaToOmpFor()
        ast = pre_transformer.visit(ast)
        return self.transformer.visit(ast)

    def test_for_to_while(self):
        """Run golden test cases"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
