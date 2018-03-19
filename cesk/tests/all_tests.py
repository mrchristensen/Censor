#!/usr/bin/env python
"""Unittest Driver"""
import sys
import unittest

sys.path[0:0] = ['.', '..']

SUITE = unittest.TestLoader().loadTestsFromNames(
    [
        'basic_functionality',
        'continuation_edge_cases'
    ]
)
TESTRESULT = unittest.TextTestRunner(verbosity=1).run(SUITE)
sys.exit(0 if TESTRESULT.wasSuccessful() else 1)
