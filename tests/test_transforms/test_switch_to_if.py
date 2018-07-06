"""Test SwitchToIf -- Replace switch statement with if and goto statements"""

from transforms.switch_if import SwitchToIf
from transforms.id_generator import IDGenerator
from tests.helpers import GoldenTestCase

class TestSwitchToIf(GoldenTestCase):
    """Test SwitchToGoto transform"""

    def setUp(self): #pylint: disable=invalid-name
        """Setup"""
        self.fixtures = '/test_transforms/fixtures/switch_to_if'
        self.transformer = None

    def transform(self, ast):
        """Transform Step"""
        self.transformer = SwitchToIf(IDGenerator(ast))
        ast = self.transformer.visit(ast)
        return ast

    def test_fixtures(self):
        """ Test all switch cases """
        self.assert_all_transform_golden(self.transform, self.fixtures)
