"""Test WhileToDoWhile -- Replacing while with do while loops"""
from transforms.loops_to_goto import WhileToGoto
from transforms.id_generator import IDGenerator
from tests.helpers import GoldenTestCase


class TestWhileToDoWhile(GoldenTestCase):
    """Test WhileToDoWhile transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/while_to_do_while'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        self.transformer = WhileToGoto(IDGenerator(ast))
        return self.transformer.visit(ast)

    def test_while_to_do_while(self):
        """Run golden test cases"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
