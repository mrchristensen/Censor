#!/usr/bin/python3
"""Tests basic functionality of unions - arrays, alignment, casting,
pointers, nesting, etc."""

from ceskvsgcc import CESKvsGCC

class UnionFunctionality(CESKvsGCC):
    """Tests basic functionality"""
    def test_union_functionality(self):
        """Tests basic functionality"""
        self.assert_all_equal("./fixtures/union_functionality")

if __name__ == "__main__":
    TEST = UnionFunctionality()
    TEST.test_union_functionality()
