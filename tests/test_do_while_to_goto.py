"""Test DoWhileToGoto -- Replacing while loops with goto code"""

from transforms.do_while_to_goto import DoWhileToGoto
from helpers import GoldenTestCase

class TestForToWhile(GoldenTestCase):
    """Test ForToWhile transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.module = 'do_while_to_goto'
        self.transform = DoWhileToGoto()

    def test_for_to_while(self):
        """Run golden test cases"""
        self.assert_all_golden()
