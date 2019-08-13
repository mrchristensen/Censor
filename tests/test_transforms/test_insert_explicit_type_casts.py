'''Test ImplicitToExplicitTypeCasts -- Making all type casts explicit.'''

from transforms.insert_explicit_type_casts import InsertExplicitTypeCasts
from transforms.type_environment_calculator import TypeEnvironmentCalculator
from tests.helpers import GoldenTestCase
from cesk.limits import set_config

class TestInsertExplicitTypeCasts(GoldenTestCase):
    '''Test InsertExplicitTypeCasts transform'''

    def setUp(self):
        '''Set up test variables needed for GoldenTestCase'''
        self.fixtures = '/test_transforms/fixtures/insert_explicit_type_casts'
        self.transformer = None

    def transform(self, ast):
        '''Transform input AST'''
        set_config('std')
        environments = TypeEnvironmentCalculator().get_environments(ast)
        self.transformer = InsertExplicitTypeCasts(environments)
        return self.transformer.visit(ast)

    def test_insert_explicit_type_casts(self):
        '''Run golden test cases'''
        self.assert_all_transform_golden(self.transform, self.fixtures)
