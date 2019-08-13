'''Test DoWhileToGoto -- Replacing do-while loops with goto code'''

from transforms.loops_to_goto import WhileToGoto
from transforms.id_generator import IDGenerator
from tests.helpers import GoldenTestCase

class TestDoWhileToGoto(GoldenTestCase):
    '''Test DoWhileToGoto transform'''

    def setUp(self):
        '''Set up test variables needed for GoldenTestCase'''
        self.fixtures = '/test_transforms/fixtures/do_while_to_goto'
        self.transformer = None

    def transform(self, ast):
        '''Transform input AST'''
        self.transformer = WhileToGoto(IDGenerator(ast))
        return self.transformer.visit(ast)

    def test_simple_stmt(self):
        '''Test DoWhile loop with one statement'''
        input_file = self.fixtures + '/simple_stmt_input.c'
        golden_file = self.fixtures + '/simple_stmt_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_simple_compound(self):
        '''Test DoWhile loop with a compound statement'''
        input_file = self.fixtures + '/simple_compound_input.c'
        golden_file = self.fixtures + '/simple_compound_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)

    def test_nested(self):
        '''Test DoWhile loop with a nested loop'''
        input_file = self.fixtures + '/nested_input.c'
        golden_file = self.fixtures + '/nested_golden.c'
        self.assert_transform_golden(self.transform, golden_file, input_file)
