""" Run regression tests on dataracebench tests. """

from helpers import RegressionTestCase #pylint: disable=no-name-in-module

class TestDataRaceBench(RegressionTestCase): #pylint: disable=no-name-in-module
    """ Test dataracebench micro-benchmakrs """

    def setUp(self): #pylint: disable=invalid-name
        """Setup"""
        self.fixtures = '../dataracebench/micro-benchmarks/no'
        self.includes = ['../dataracebench/micro-benchmarks',
                         '../dataracebench/micro-benchmarks/utilities']
        self.add_flags = [
            '-fopenmp',
            '../dataracebench/micro-benchmarks/utilities/polybench.c',
            '-DPOLYBENCH_NO_FLUSH_CACHE',
            '-DPOLYBENCH_TIME',
            '-D_POSIX_C_SOURCE=200112L'
        ]

    def test_all(self):
        """ Assert same output for non-omp and omp transformations.
        """
        self.assert_end_result_same()
