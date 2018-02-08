"""Test WhileToDoWhile -- Replacing while with do while loops"""
from transforms.while_to_do_while import WhileToDoWhile
from helpers import GoldenTestCase


class TestWhileToDoWhile(GoldenTestCase):
    """Test WhileToDoWhile transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.module = 'while_to_do_while'
        self.transform = WhileToDoWhile()

    def test_while_to_do_while(self):
        """Run golden test cases"""
        self.assert_all_golden()
