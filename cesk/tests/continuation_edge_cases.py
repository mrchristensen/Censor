"""Tests basic functionality of arithmatic, functions, and linked lists,
using only ints and pointers, not worrying about corner cases."""

from ceskvsgcc import CESKvsGCC

class ContinuationEdgeCases(CESKvsGCC):
    """Tests basic functionality"""
    def test_continuaiton_edge_cases(self):
        """Tests basic functionality"""
        self.assert_all_equal("./fixtures/continuation_edge_cases")

if __name__ == "__main__":
    TEST = ContinuationEdgeCases()
    #pylint: disable=no-member
    TEST.test_continuation_edge_cases()
