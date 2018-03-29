"""Test SharedVars"""

import unittest
from pycparser.c_parser import CParser
from instrumenter.shared_vars import SharedVarsVisitor
from transforms.for_to_while import ForToWhile
from transforms.omp_parallel_for import PragmaToOmpParallelFor

TRANSFORMS = [
    PragmaToOmpParallelFor(),
    ForToWhile(),
]

def transform_omp(ast):
    """Transform Pragmas to Omp Nodes"""
    for transform in TRANSFORMS:
        ast = transform.visit(ast)
    return ast

class TestSharedVars(unittest.TestCase):
    """Test SharedVars"""
    # TODO Create exhaustive list of test cases
    # If we don't get to all of them then we will at least know which
    # situations we need to throw a NotImplementedError in

    def setUp(self):
        """Set up test case"""
        self.parser = CParser()
        self.visitor = SharedVarsVisitor()

    def test_simple_parallel(self):
        """Simple test case, 'a' and 't' are shared"""
        c_source = '''
        int main() {
          int a[100];
          int t = 0;
          #pragma omp parallel for
          for (int i = 0; i < 100; i++)
              t += a[i];
        }
        '''
        ast = transform_omp(self.parser.parse(c_source))
        self.visitor.visit(ast)
        omp_parallel_scope = ast.ext[0].body.block_items[2].block
        omp_for_scope = omp_parallel_scope.block_items[0].loops
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('a'))
        self.assertTrue(self.visitor.scopes[omp_for_scope].contains('a'))
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('t'))
        self.assertTrue(self.visitor.scopes[omp_for_scope].contains('t'))

    def test_parallel_with_private(self):
        """Simple test case with some private clauses.
        Note: technically these firstprivate and lastprivate aren't used correctly here
        because the variables are used unitialized but it doesn't matter for the test.
        """
        c_source = '''
        int main() {
          int a[100];
          int b[100];
          int c[100];
          int d[100];
          int e[100];
          int t = 0;
          #pragma omp parallel for private(b) firstprivate(c, d) lastprivate(d, e)
          for (int i = 0; i < 100; i++)
              t += a[i] + b[i] + c[i] + d[i] + e[i];
        }
        '''
        ast = transform_omp(self.parser.parse(c_source))
        self.visitor.visit(ast)
        omp_parallel_scope = ast.ext[0].body.block_items[6].block
        omp_for_scope = omp_parallel_scope.block_items[0].loops
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('a'))
        self.assertFalse(self.visitor.scopes[omp_parallel_scope].contains('b'))
        self.assertFalse(self.visitor.scopes[omp_parallel_scope].contains('c'))
        self.assertFalse(self.visitor.scopes[omp_parallel_scope].contains('d'))
        # no last private clause on parallel construct
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('e'))
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('t'))
        self.assertTrue(self.visitor.scopes[omp_for_scope].contains('a'))
        self.assertFalse(self.visitor.scopes[omp_for_scope].contains('b'))
        self.assertFalse(self.visitor.scopes[omp_for_scope].contains('c'))
        self.assertFalse(self.visitor.scopes[omp_for_scope].contains('d'))
        self.assertFalse(self.visitor.scopes[omp_for_scope].contains('e'))
        self.assertTrue(self.visitor.scopes[omp_for_scope].contains('t'))

    def test_inc_variable(self):
        """Test that inc variables are not detected as shared inside for loop"""
        c_source = '''
        int main() {
          int a[100];
          int i = 0;
          int t = 0;
          #pragma omp parallel for
          for (i = 0; i < 100; i++)
              t += a[i];
        }
        '''
        ast = transform_omp(self.parser.parse(c_source))
        self.visitor.visit(ast)
        omp_parallel_scope = ast.ext[0].body.block_items[3].block
        omp_for_scope = omp_parallel_scope.block_items[0].loops
        self.assertTrue(self.visitor.scopes[omp_parallel_scope].contains('i'))
        self.assertFalse(self.visitor.scopes[omp_for_scope].contains('i'))
