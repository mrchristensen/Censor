"""Test Instrumenter"""

from helpers import GoldenTestCase
from instrumenter.instrumenter import Instrumenter
from transforms.omp_parallel import PragmaToOmpParallel

TRANSFORMS = [
    PragmaToOmpParallel()
]

def transform_omp(ast):
    """Transform Pragmas to Omp Nodes"""
    for transform in TRANSFORMS:
        ast = transform.visit(ast)
    return ast

class TestInstrumenter(GoldenTestCase):
    """Test Instrumenter"""

    def setUp(self): #pylint: disable=invalid-name
        """Set up test case"""
        self.fixtures = './test_instrumenter/fixtures/instrumenter'
        self.instrumenter = Instrumenter()

    def transform(self, ast):
        """Transform input AST"""
        return self.instrumenter.visit(transform_omp(ast))

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_golden(self.transform, self.fixtures)
