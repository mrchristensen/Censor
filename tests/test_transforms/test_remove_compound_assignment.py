"""Test RemoveCompoundAssignment -- Removing all
all compound assignments such as "a += 4.5;"""

from transforms.remove_compound_assignment import RemoveCompoundAssignment
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase

class TestRemoveCompoundAssignment(GoldenTestCase):
    """Test RemoveCompoundAssignment transform"""

    def setUp(self):
        """Set up test variables needed for GoldenTestCase"""
        self.fixtures = '/test_transforms/fixtures/remove_compound_assignment'
        self.transformer = None

    def transform(self, ast):
        """Transform input AST"""
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = RemoveCompoundAssignment(IDGenerator(ast),
                                                    environments)
        return self.transformer.visit(ast)

    def test_remove_compound_assignment(self):
        """Run golden test cases"""
        self.assert_all_transform_golden(self.transform, self.fixtures)
