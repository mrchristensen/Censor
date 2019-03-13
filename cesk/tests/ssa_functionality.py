#!/usr/bin/python3
"""Tests basic functionality of unions - arrays, alignment, casting,
pointers, nesting, etc."""

from ceskvsgcc import CESKvsGCC

class SsaFunctionality(CESKvsGCC):
    """Tests ssa functionality"""
    def test_ssa_functionality(self):
        """Tests ssa functionality"""
        self.assert_all_equal("./fixtures/ssa_functionality")

if __name__ == "__main__":
    TEST = SsaFunctionality()
    TEST.test_ssa_functionality()
