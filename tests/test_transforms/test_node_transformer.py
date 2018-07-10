"""Test NodeTransformer"""

from tests.helpers import GoldenTestCase
from transforms.node_transformer import NodeTransformer

class TestNodeTransformer(GoldenTestCase):
    """Test NodeTransformer"""

    class TestTransform(NodeTransformer):
        """
        Test transform to make sure base class handles lists
        See fixtures for test case (it is contrived but verifies the
        functionality)
        """
        def visit_FuncDef(self, node): #pylint: disable=invalid-name
            """Visit FileAST"""
            node = self.generic_visit(node)
            return [node, node]
        def visit_Assignment(self, node): #pylint: disable=invalid-name
            """Visit Assignment"""
            node = self.generic_visit(node)
            return [node, node]
        def visit_UnaryOp(self, node): #pylint: disable=invalid-name
            """Visit UnaryOp"""
            node = self.generic_visit(node)
            return [node, node]

    def setUp(self): #pylint: disable=invalid-name
        """Set up test case"""
        self.fixtures = '/test_transforms/fixtures/node_transformer'
        self.transformer = self.TestTransform()

    def transform(self, ast):
        """Transform input AST"""
        return self.transformer.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
