""" Run regression tests on dataracebench tests. """

from helpers import RegressionTestCase #pylint: disable=no-name-in-module

class TestBasic(RegressionTestCase): #pylint: disable=no-name-in-module
    """ Test dataracebench micro-benchmakrs """

    def setUp(self): #pylint: disable=invalid-name
        """Setup"""
        self.fixtures = 'basic'
        self.includes = []
        self.add_flags = []

    def test_all(self):
        """ Assert same output for non-omp and omp transformations.
        """
        self.assert_individual_non_omp()
        self.assert_all_omp()
        self.assert_same_output_series()
