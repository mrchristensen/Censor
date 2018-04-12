"""Test SimplifyOmpFor """

from transforms.simplify_omp_for import SimplifyOmpFor
from transforms.omp_for import PragmaToOmpFor
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from helpers import GoldenTestCase

class TestRemoveCompoundAssignment(GoldenTestCase):
    """Test RemoveCompoundAssignment transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/simplify_omp_for'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        id_generator = IDGenerator(ast)
        environments = TypeEnvironmentCalculator().get_environments(ast)
        pre_transformer = PragmaToOmpFor()
        ast = pre_transformer.visit(ast)
        self.transformer = SimplifyOmpFor(id_generator, environments)
        return self.transformer.visit(ast)

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_golden(self.transform, self.fixtures)
