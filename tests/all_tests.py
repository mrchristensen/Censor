#!/usr/bin/env python
"""Unittest Driver"""
import sys
import unittest

sys.path[0:0] = ['.', '..']

SUITE = unittest.TestLoader().loadTestsFromNames(
    [
        'test_for_to_while',
        'test_omp_for',
        'test_omp_critical',
        'test_do_while_to_goto',
        'test_while_to_do_while',
        'test_omp_parallel',
        'test_omp_barrier',
        'test_omp_master'
    ]
)
TESTRESULT = unittest.TextTestRunner(verbosity=1).run(SUITE)
sys.exit(0 if TESTRESULT.wasSuccessful() else 1)
