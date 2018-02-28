"""Test WhileToDoWhile -- Replacing while with do while loops"""
from transforms.while_to_do_while import WhileToDoWhile
from helpers import GoldenTestCase


class TestWhileToDoWhile(GoldenTestCase):
    """Test WhileToDoWhile transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/while_to_do_while'
        self.transformer = WhileToDoWhile()

    def transform(self, ast):
        """Transform input AST"""
        return self.transformer.visit(ast)

    def test_while_to_do_while(self):
        """Run golden test cases"""
        self.assert_all_golden(self.transform, self.fixtures)
