"""Test Instrumenter"""

from tests.helpers import GoldenTestCase
from instrumenter.instrumenter import Instrumenter
from transforms.omp_parallel_for import PragmaToOmpParallelFor
from transforms.omp_parallel import PragmaToOmpParallel
from transforms.omp_for import PragmaToOmpFor
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator

TRANSFORMS = [
    PragmaToOmpParallelFor(),
    PragmaToOmpParallel(),
    PragmaToOmpFor()
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
        self.fixtures = '/test_instrumenter/fixtures/instrumenter'
        self.instrumenter = None

    def transform(self, ast):
        """Transform input AST"""
        ast = transform_omp(ast)
        id_generator = IDGenerator(ast)
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.instrumenter = Instrumenter(id_generator, environments)
        return self.instrumenter.visit(ast)

    def test_fixtures(self):
        """Test all golden files"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
