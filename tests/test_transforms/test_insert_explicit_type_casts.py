"""Test ImplicitToExplicitTypeCasts -- Making all type casts explicit."""

from transforms.insert_explicit_type_casts import InsertExplicitTypeCasts
from helpers import GoldenTestCase

class TestInsertExplicitTypeCasts(GoldenTestCase):
    """Test InsertExplicitTypeCasts transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = './test_transforms/fixtures/insert_explicit_type_casts'
        self.transform = InsertExplicitTypeCasts()

    def test_insert_explicit_type_casts(self):
        """Run golden test cases"""
        self.assert_all_golden(self.fixtures)
