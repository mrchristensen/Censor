'''Test PragmaToOmpThreadprivate -- Replacing Pragma omp with Omp Nodes'''

import unittest
import pycparser
import omp
from transforms.omp_threadprivate import PragmaToOmpThreadprivate

#pylint: disable=invalid-name
class TestOmpThreadprivate(unittest.TestCase):
    '''Test OmpThreadprivate Node'''

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        '''Pragma node visitor; collect all pragma nodes'''

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            '''Collect nodes, does not recurse as Pragma nodes have no
            children'''
            self.nodes.append(node)

    class OmpThreadprivateVisitor(omp.omp_ast.NodeVisitor):
        '''OmpThreadprivate node visitor; recursibely collect all
        OmpThreadprivate nodes'''

        def __init__(self):
            self.nodes = []

        def visit_OmpThreadprivate(self, node):
            '''Recursively collect OmpThreadprivate nodes'''

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpThreadprivate()

    def test_clauses_one(self):
        '''Test omp threadprivate pragma with name clause'''
        c = '''
        int main() {
            int i = 0;
            #pragma omp threadprivate(id1, id2)
            {
            }
        }
        '''
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpThreadprivateVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(ov.nodes[0].clauses[0].ids, ['id1', 'id2'])
