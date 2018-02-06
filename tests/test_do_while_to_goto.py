"""Test DoWhileToGoto -- Replacing do-while loops with goto code"""

from transforms.do_while_to_goto import DoWhileToGoto
from helpers import GoldenTestCase

class TestDoWhileToGoto(GoldenTestCase):
    """Test DoWhileToGoto transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.module = 'do_while_to_goto'
        self.transform = DoWhileToGoto()

    def test_do_while_to_goto(self):
        """Run golden test cases"""
        self.assert_all_golden()
