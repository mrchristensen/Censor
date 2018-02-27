"""Test RemoveCompoundAssignment -- Removing all
all compound assignments such as "a += 4.5;"""

from transforms.remove_compound_assignment import RemoveCompoundAssignment
from helpers import GoldenTestCase

class TestRemoveCompoundAssignment(GoldenTestCase):
    """Test RemoveCompoundAssignment transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/remove_compound_assignment'
        self.transform = RemoveCompoundAssignment()

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_golden(self.fixtures)
