#!/usr/bin/python3
"""Tests basic functionality of arithmatic, functions, and linked lists,
using only ints and pointers, not worrying about corner cases."""

from ceskvsgcc import CESKvsGCC

class DifficultPointer(CESKvsGCC):
    """Tests basic functionality"""
    def test_pointers(self):
        """Tests basic functionality"""
        self.assert_all_equal("./fixtures/difficult_pointer")

if __name__ == "__main__":
    TEST = DifficultPointer()
    TEST.test_pointers()
