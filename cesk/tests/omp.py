#!/usr/bin/python3
"""Tests OmpRuntime"""

from ceskvsgcc import CESKvsGCC

class Omp(CESKvsGCC):
    """Tests OmpRuntime"""
    def test_omp(self):
        """Tests OmpRuntime"""
        self.assert_all_equal("./fixtures/omp")

if __name__ == "__main__":
    TEST = Omp()
    TEST.test_omp()
