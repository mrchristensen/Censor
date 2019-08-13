'''Test RemoveInitLists'''

from transforms.remove_init_lists import RemoveInitLists
from transforms.id_generator import IDGenerator
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase

class TestRemoveInitLists(GoldenTestCase):
    '''Test RemoveInitLists transform'''

    def setUp(self):
        '''Set up test variables needed for GoldenTestCase'''
        self.fixtures = '/test_transforms/fixtures/remove_init_lists'
        self.transformer = None

    def transform(self, ast):
        '''Transform input AST'''
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = RemoveInitLists(IDGenerator(ast), environments)
        return self.transformer.visit(ast)

    def test_remove_init_lists(self):
        '''Run golden test cases'''
        self.assert_all_transform_golden(self.transform, self.fixtures)
