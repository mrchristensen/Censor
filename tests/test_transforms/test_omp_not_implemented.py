"""Test OmpNotImplemented"""


import unittest
from pycparser.c_parser import CParser
from transforms.omp_not_implemented import OmpNotImplemented
from transforms.omp_parallel import PragmaToOmpParallel

class TestOmpNotImplemented(unittest.TestCase):
    """Test OmpNotImplemented"""

    def setUp(self):
        """Set up test case"""
        self.parser = CParser()
        self.transform = OmpNotImplemented()

    def test_throws_error(self):
        """Test that error is raised on pragma omp"""
        c_source = '''
        int main() {
          #pragma omp parallel
          {
          }
        }
        '''
        ast = self.parser.parse(c_source)
        self.assertRaises(NotImplementedError, self.transform.visit, ast)

    def test_no_error(self):
        """Test error is not thrown on Omp node"""
        c_source = '''
        int main () {
            #pragma omp parallel
            {}
        }
        '''
        ast = self.parser.parse(c_source)
        ast = PragmaToOmpParallel().visit(ast)
        ast = self.transform.visit(ast)
