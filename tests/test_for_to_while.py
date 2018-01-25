"""Test ForToWhile -- Replacing for with while loops"""

import unittest
import pycparser
from transforms.for_to_while import ForToWhile
from helpers import ForVisitor, WhileVisitor, CompoundVisitor

SIMPLE_FOR_LOOP_EMPTY = """
int main() {
    for (int i = 0; i < 100; i++) {
    }
}
"""
SIMPLE_FOR_LOOP_STMT = """
int main() {
    int j = 0;
    for (int i = 0; i < 100; i++)
        j++;
}
"""
SIMPLE_FOR_LOOP_STMTS = """
int main() {
    int j = 0;
    for (int i = 0; i < 100; i++) {
        j++;
    }
}
"""
NESTED_FOR_LOOP = """
int main() {
    int k = 0;
    for (int i = 0; i < 100; i++) {
        k++;
        for (int j = 0; j < 100; j++) {
            k++;
        }
    }
}
"""
FOR_LOOP_NO_INIT = """
int main() {
    int j = 0;
    for (;j < 10; j++)
        j++;
}
"""
FOR_LOOP_NO_COND = """
int main() {
    int j = 0;
    for (int i = 0;; i++)
        j++;
}
"""
FOR_LOOP_NO_NEXT = """
int main() {
    int j = 0;
    for (int i = 0; i<10;)
        continue;
}
"""
FOR_LOOP_CONTINUE = """
int main() {
    int j = 0;
    int z = 0;
    for (int i = 0; i < 10; z++) {
        if (i % 2 == 0)
            continue;
        j++;
        continue;
        j--;
    }
}
"""
NESTED_FOR_LOOP_CONTINUE = """
int main() {
    for (int i = 0; i<10; i++) {
        for (int j = 0; j < 10; j++) {
            if (j % 2 == 0) {
                continue;
            }
            continue;
        }
    }
}
"""

class TestForToWhile(unittest.TestCase):
    """Test ForToWhile transform"""

    @classmethod
    def setUpClass(cls):
        cls.transform = ForToWhile()
        cls.parser = pycparser.CParser()
        cls.fors = ForVisitor()
        cls.whiles = WhileVisitor()
        cls.compounds = CompoundVisitor()

    def setUp(self):
        self.fors.nodes = []
        self.whiles.nodes = []
        self.compounds.nodes = []

    def visit(self, ast):
        """Reset visitors for given AST"""
        self.fors.nodes = []
        self.whiles.nodes = []
        self.compounds.nodes = []
        self.fors.visit(ast)
        self.whiles.visit(ast)
        self.compounds.visit(ast)

    def test_one_empty(self):
        """Test transformation of one empty for loop"""
        ast = self.parser.parse(SIMPLE_FOR_LOOP_EMPTY)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        inner = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(3, len(self.compounds.nodes))
        self.assertEqual(inner.block_items[0], for_node.next)
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(scope.block_items[1], while_node)

    def test_one_stmt(self):
        """Test transformation of one for loop with one statment"""
        ast = self.parser.parse(SIMPLE_FOR_LOOP_STMT)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        inner = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(3, len(self.compounds.nodes))
        self.assertEqual(inner.block_items[0], for_node.stmt)
        self.assertEqual(inner.block_items[1], for_node.next)
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(scope.block_items[1], while_node)

    def test_one_stmts(self):
        """Test transformation of one for loop with compound statment"""
        ast = self.parser.parse(SIMPLE_FOR_LOOP_STMTS)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        inner = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(3, len(self.compounds.nodes))
        self.assertEqual(inner.block_items[0], for_node.stmt.block_items[0])
        self.assertEqual(inner.block_items[1], for_node.next)
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(scope.block_items[1], while_node)

    def test_nested(self):
        """Test transformation of nested for loops"""
        ast = self.parser.parse(NESTED_FOR_LOOP)
        self.fors.visit(ast)
        outer_for = self.fors.nodes[0]
        inner_for = self.fors.nodes[1]
        ast = self.transform.visit(ast)
        self.visit(ast)
        outer_while = self.whiles.nodes[0]
        inner_while = self.whiles.nodes[1]
        scope_one = self.compounds.nodes[1]
        stmt_one = self.compounds.nodes[2]
        scope_two = self.compounds.nodes[3]
        stmt_two = self.compounds.nodes[4]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(2, len(self.whiles.nodes))
        self.assertEqual(5, len(self.compounds.nodes))
        self.assertEqual(scope_one.block_items[0], outer_for.init)
        self.assertEqual(scope_one.block_items[1], outer_while)
        self.assertEqual(scope_two.block_items[0], inner_for.init)
        self.assertEqual(scope_two.block_items[1], inner_while)
        self.assertEqual(stmt_one.block_items[0], outer_for.stmt.block_items[0])
        self.assertEqual(stmt_one.block_items[1], scope_two)
        self.assertEqual(stmt_one.block_items[2], outer_for.next)
        self.assertEqual(stmt_two.block_items[0], inner_for.stmt.block_items[0])
        self.assertEqual(stmt_two.block_items[1], inner_for.next)

    def test_no_init(self):
        """Test transformation of for loop with no init"""
        ast = self.parser.parse(FOR_LOOP_NO_INIT)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        func = self.compounds.nodes[0]
        stmt = self.compounds.nodes[1]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(2, len(self.compounds.nodes))
        self.assertEqual(stmt.block_items[0], for_node.stmt)
        self.assertEqual(stmt.block_items[1], for_node.next)
        self.assertEqual(func.block_items[1], while_node)

    def test_no_cond(self):
        """Test transformation of for loop with no cond"""
        ast = self.parser.parse(FOR_LOOP_NO_COND)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        stmt = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(3, len(self.compounds.nodes))
        self.assertEqual(True, isinstance(while_node.cond, pycparser.c_ast.ID))
        self.assertEqual("true", while_node.cond.name)
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(stmt.block_items[0], for_node.stmt)
        self.assertEqual(stmt.block_items[1], for_node.next)

    def test_no_next(self):
        """Test transformation of for loop with no next (and a continue stmt)"""
        ast = self.parser.parse(FOR_LOOP_NO_NEXT)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        stmt = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(3, len(self.compounds.nodes))
        self.assertEqual(1, len(stmt.block_items))
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(scope.block_items[1], while_node)
        self.assertEqual(stmt.block_items[0], for_node.stmt)

    def test_continue(self):
        """Test transformation with continue statement"""
        ast = self.parser.parse(FOR_LOOP_CONTINUE)
        self.fors.visit(ast)
        for_node = self.fors.nodes[0]
        ast = self.transform.visit(ast)
        self.visit(ast)
        while_node = self.whiles.nodes[0]
        scope = self.compounds.nodes[1]
        stmt = self.compounds.nodes[2]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(1, len(self.whiles.nodes))
        self.assertEqual(5, len(self.compounds.nodes))
        self.assertEqual(5, len(stmt.block_items))
        self.assertEqual(scope.block_items[0], for_node.init)
        self.assertEqual(scope.block_items[1], while_node)
        self.assertEqual(stmt.block_items[0].iftrue.block_items[0], for_node.next)
        self.assertEqual(stmt.block_items[1], for_node.stmt.block_items[1])
        self.assertEqual(stmt.block_items[2].block_items[0], for_node.next)
        self.assertEqual(stmt.block_items[4], for_node.next)

    def test_nested_continue(self):
        """Test transformation with nested for loops and continue statement"""
        ast = self.parser.parse(NESTED_FOR_LOOP_CONTINUE)
        self.fors.visit(ast)
        outer_for = self.fors.nodes[0]
        inner_for = self.fors.nodes[1]
        ast = self.transform.visit(ast)
        self.visit(ast)
        outer_while = self.whiles.nodes[0]
        inner_while = self.whiles.nodes[1]
        scope_one = self.compounds.nodes[1]
        scope_two = self.compounds.nodes[3]
        stmt_one = self.compounds.nodes[2]
        stmt_two = self.compounds.nodes[4]
        self.assertEqual(0, len(self.fors.nodes))
        self.assertEqual(2, len(self.whiles.nodes))
        self.assertEqual(8, len(self.compounds.nodes))
        self.assertEqual(2, len(scope_one.block_items))
        self.assertEqual(2, len(scope_two.block_items))
        self.assertEqual(2, len(stmt_one.block_items))
        self.assertEqual(3, len(stmt_two.block_items))
        self.assertEqual(scope_one.block_items[0], outer_for.init)
        self.assertEqual(scope_one.block_items[1], outer_while)
        self.assertEqual(scope_two.block_items[0], inner_for.init)
        self.assertEqual(scope_two.block_items[1], inner_while)
        self.assertEqual(stmt_one.block_items[0], scope_two)
        self.assertEqual(stmt_one.block_items[1], outer_for.next)
        self.assertEqual(
            stmt_two.block_items[0].iftrue.block_items[0].block_items[0],
            inner_for.next
            )
        self.assertEqual(stmt_two.block_items[1].block_items[0], inner_for.next)
        self.assertEqual(stmt_two.block_items[2], inner_for.next)
