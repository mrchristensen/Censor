"""Test Instrumenter"""

from helpers import GoldenTestCase
from instrumenter.instrumenter import Instrumenter
from transforms.omp_parallel import PragmaToOmpParallel
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator

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
    #TODO test these cases where OpenMP pragmas cause
    # implicit references to variables
    # if
    # num_threads
    # schedule
    # final
    # firstprivate
    # lastprivate
    # linear
    # reduction
    # copyprivate
    # map (may cause a reference)

    def setUp(self): #pylint: disable=invalid-name
        """Set up test case"""
        self.fixtures = '/test_instrumenter/fixtures/instrumenter'
        self.instrumenter = None

    def transform(self, ast):
        """Transform input AST"""
        id_generator = IDGenerator(ast)
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.instrumenter = Instrumenter(id_generator, environments)
        return self.instrumenter.visit(transform_omp(ast))

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_golden(self.transform, self.fixtures)
