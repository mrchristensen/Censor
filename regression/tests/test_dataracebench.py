""" Run regression tests on dataracebench tests. """

from transforms.for_to_while import ForToWhile
from helpers import RegressionTestCase, get_fixtures #pylint: disable=no-name-in-module

class TestDataRaceBench(RegressionTestCase): #pylint: disable=no-name-in-module
    """ Test dataracebench micro-benchmakrs """

    def setUp(self): #pylint: disable=invalid-name
        """Setup"""
        self.fixtures = '../dataracebench/micro-benchmarks'
        self.includes = ['../dataracebench/micro-benchmarks',
                         '../dataracebench/micro-benchmarks/utilities']
        self.add_flags = [
            '../dataracebench/micro-benchmarks/utilities/polybench.c',
            '-DPOLYBENCH_NO_FLUSH_CACHE',
            '-DPOLYBENCH_TIME',
            '-D_POSIX_C_SOURCE=200112L'
        ]

    def test_for_to_while(self):
        """ Test ForToWhile transform.
            (This should run each transform in sequence eventually though)
        """
        for fixture in get_fixtures(self.fixtures):
            with self.subTest(msg=fixture):
                print("Testing fixture: " + fixture)
                self.assert_same_output_individual(ForToWhile().visit, fixture)
