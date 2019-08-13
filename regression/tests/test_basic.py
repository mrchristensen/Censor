""" Run regression tests on basic test files. """

from regression.tests.helpers import RegressionTestCase #pylint: disable=no-name-in-module

class TestBasic(RegressionTestCase): #pylint: disable=no-name-in-module
    """ Test dataracebench micro-benchmarks """

    def setUp(self): #pylint: disable=invalid-name
        """Setup"""
        self.fixtures = 'basic'
        self.includes = []
        self.add_flags = []

    def test_all(self):
        """ Test all fixtures """
        self.assert_end_result_same()
