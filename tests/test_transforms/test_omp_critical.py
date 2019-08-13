'''Test PragmaToOmpCritical -- Replacing Pragma omp with Omp Nodes'''

import unittest
import pycparser
import omp
from transforms.omp_critical import PragmaToOmpCritical

#pylint: disable=invalid-name
class TestOmpCritical(unittest.TestCase):
    '''Test OmpCritical Node'''

    class PragmaVisitor(omp.omp_ast.NodeVisitor):
        '''Pragma node visitor; collect all pragma nodes'''

        def __init__(self):
            self.nodes = []

        def visit_Pragma(self, node):
            '''Collect nodes, does not recurse as Pragma nodes have no
            children'''
            self.nodes.append(node)

    class OmpCriticalVisitor(omp.omp_ast.NodeVisitor):
        '''OmpCritical node visitor; recursibely collect all OmpCritical
        nodes'''

        def __init__(self):
            self.nodes = []

        def visit_OmpCritical(self, node):
            '''Recursively collect OmpCritical nodes'''

            self.nodes.append(node)
            self.generic_visit(node)

    @classmethod
    def setUpClass(cls):
        cls.parser = pycparser.CParser()
        cls.transform = PragmaToOmpCritical()

    def test_simple(self):
        '''Test simple omp critical pragma'''
        c = '''
        int main() {
            #pragma omp critical
            for (int i = 0; i < 100; i++) {

            }
        }
        '''
        ast = self.parser.parse(c)
        child = ast.ext[0].body.block_items[1]
        pv = self.PragmaVisitor()
        ov = self.OmpCriticalVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertEqual(child, ov.nodes[0].block.block_items[0])
        self.assertEqual(ov.nodes[0].clauses[0].name, None)


    def test_clauses_one(self):
        '''Test omp critical pragma with name clause'''
        c = '''
        int main() {
            int i = 0;
            #pragma omp critical(name)
            {
            }
        }
        '''
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpCriticalVisitor()

        ast = self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block, pycparser.c_ast.Compound))
        self.assertEqual(ov.nodes[0].clauses[0].name, "name")

    def test_clauses_many(self):
        '''Test omp critical pragma with two clauses'''
        c = '''
        int main() {
            int i = 0;
            #pragma omp critical(name) hint(0)
            i++;
        }
        '''
        ast = self.parser.parse(c)
        pv = self.PragmaVisitor()
        ov = self.OmpCriticalVisitor()

        self.transform.visit(ast)

        ov.visit(ast)
        pv.visit(ast)

        self.assertEqual(0, len(pv.nodes))
        self.assertEqual(1, len(ov.nodes))
        self.assertTrue(isinstance(ov.nodes[0].block, pycparser.c_ast.Compound))
        self.assertTrue(isinstance(ov.nodes[0].block.block_items[0],
                                   pycparser.c_ast.UnaryOp))
        self.assertEqual(ov.nodes[0].clauses[0].name, "name")
        self.assertEqual(ov.nodes[0].clauses[1].hint, 0)
