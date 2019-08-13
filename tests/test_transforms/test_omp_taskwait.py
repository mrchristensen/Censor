'''Test PragmaToOmpTaskwait -- Replacing Pragma omp with Omp Nodes'''

import unittest
import pycparser
import omp
from transforms.omp_taskwait import PragmaToOmpTaskwait

#pylint: disable=invalid-name
class TestOmpTaskwait(unittest.TestCase):
    '''Test OmpTaskwait Node'''

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        '''Pragma node visitor; collect all pragma nodes'''

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            '''Collect nodes, does not recurse as Pragma nodes have no
            children'''
            self.nodes.append(node)

    class OmpTaskwaitVisitor(omp.omp_ast.NodeVisitor):
        '''OmpTaskwait node visitor'''

        def __init__(self):
            self.nodes = []

        def visit_OmpTaskwait(self, node):
            '''Collect OmpTaskwait nodes'''
            self.nodes.append(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpTaskwait()

    def test_simple(self):
        '''Test simple omp taskwait pragma'''
        c = '''
        int main() {
            #pragma omp parallel
            {
                #pragma omp task
                {
                }
                #pragma omp taskwait
            }
        }
        '''
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpTaskwaitVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(2, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
