#!/usr/bin/python3
"""Tests basic functionality of unions - arrays, alignment, casting,
pointers, nesting, etc."""

from ceskvsgcc import CESKvsGCC

class SmallTestFileFunctionality(CESKvsGCC):
    """Tests basic functionality"""
    def small_test_file_functionality(self):
        """Tests basic functionality"""
        self.assert_all_equal("./fixtures/small_test_cases")

if __name__ == "__main__":
    TEST = SmallTestFileFunctionality()
    TEST.small_test_file_functionality()
