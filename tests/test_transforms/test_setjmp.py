'''Test AlphaName'''

from transforms.setjmp import Setjmp
from tests.helpers import GoldenTestCase

class TestSetjmp(GoldenTestCase):
    '''Test AlphaName transform'''

    def setUp(self):
        '''Set up test variables needed for GoldenTestCase'''
        self.fixtures = '/test_transforms/fixtures/setjmp'

    def transform(self, ast):
        '''Transform input AST'''
        return Setjmp().visit(ast)

    def test_fixtures(self):
        '''Test AlphaName'''
        self.assert_all_transform_golden(self.transform, self.fixtures)
