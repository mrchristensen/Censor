#!/usr/bin/python3
"""Tests basic functionality of arithmatic, functions, and linked lists,
using only ints and pointers, not worrying about corner cases."""

from ceskvsgcc import CESKvsGCC

class BasicFunctionality(CESKvsGCC):
    """Tests basic functionality"""
    def test_basic_functionality(self):
        """Tests basic functionality"""
        self.assert_all_equal("./fixtures/basic_functionality")

if __name__ == "__main__":
    TEST = BasicFunctionality()
    TEST.test_basic_functionality()
