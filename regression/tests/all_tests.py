#!/usr/bin/env python
"""Regression Test Driver"""
import sys
import unittest

sys.path[0:0] = ['.', '..', '../..']

SUITE = unittest.TestLoader().loadTestsFromNames(
    [
        'test_dataracebench'
    ]
)
TESTRESULT = unittest.TextTestRunner(verbosity=1).run(SUITE)
sys.exit(0 if TESTRESULT.wasSuccessful() else 1)
