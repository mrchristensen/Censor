'''
    Sequential transform: puts all code between sequence points on a new line.
    After the Sequential transform, all sequence points will be at the end of
    a full expression.

    =====================================================
    y = expr_1, expr_2, ... expr_n;

    is changed to:

    expr_1;
    expr_2;
    ...
    y = expr_n;

    =====================================================
    y = expr_1 && expr_2;

    is changed to:

    int val_1 = 0;
    if(expr_1){
        val_1 = expr_2 != 0;
    }
    y = val_1;

    =====================================================
    y = expr_1 || expr_2;

    is changed to:

    int val_2 = 1;
    if(expr_1 == 0){
        val_2 = expr_2 != 0;
    }
    y = val_2;

    =====================================================
    y = expr_1 ? expr_2 : expr_3;

    is changed to:

    val_1;
    if(expr_1){
        val_1 = expr_2;
    }
    else{
        val_1 = expr_3;
    }
    y = val_1;

    =====================================================
    func(expr_1,expr_2);

    is changed to:

    val_1 = expr_1;
    val_2 = expr_2;
    func(val_1,val_2);

 '''
from pycparser.c_ast import *  # pylint: disable=wildcard-import, unused-wildcard-import
from .lift_node import LiftNode
from .type_helpers import make_temp_value

class Sequence(LiftNode):
    """ Tranforms unary operators into another equivalent AST"""

    def visit_ExprList(self, node): # pylint: disable=invalid-name
        """ Tranforms comma operators into multiple lines"""
        expressions = node.exprs
        expr_num = len(expressions)
        for i in range(expr_num):
            expr = expressions[i]
            if i+1 is not expr_num: # if not last element
                expr = self.visit(expr)
                self.insert_into_scope(expr)
            else:
                node = self.visit(expr)
        return node

    def visit_FuncCall(self, node): # pylint: disable=invalid-name
        """Transforms Functions to evaluate parameters beforehand"""
        expr_list = node.args
        if expr_list is None:
            return node
        elements = expr_list.exprs
        for i, val in enumerate(elements):
            elements[i] = self.visit(val)
            if isinstance(elements[i], (ID, Constant)):
                continue
            if isinstance(elements[i], UnaryOp):
                if elements[i].op == '*':
                    if isinstance(elements[i].expr, (ID, Constant)):
                        continue
            elements[i] = self.lift_from_func(elements[i])
        return node

    def lift_from_func(self, val):
        '''Lifts value'''
        generator = self.id_generator
        decl_1 = make_temp_value(val, generator, self.envr)
        self.envr.add(decl_1.name, decl_1.type)
        self.insert_into_scope(decl_1)
        return ID(decl_1.name)

    def visit_TernaryOp(self, node): # pylint: disable=invalid-name
        """Transform Ternary to If"""
        #initialize variables
        decl_1 = make_temp_value(node, self.id_generator, self.envr)
        decl_1.init = None
        val_1 = decl_1.name
        self.envr.add(val_1, decl_1.type)

        #express if statement
        if_true = Assignment('=', ID(val_1), node.iftrue, node.coord)
        if_true = Compound([if_true], coord=node.coord)
        self.environments[if_true] = self.envr
        if_false = Assignment('=', ID(val_1), node.iffalse, node.coord)
        if_false = Compound([if_false], coord=node.coord)
        self.environments[if_false] = self.envr
        if_statement = If(node.cond, if_true, if_false, coord=node.coord)

        self.generic_visit(if_statement)
        self.insert_into_scope(decl_1, if_statement)
        return ID(val_1)

    def visit_BinaryOp(self, node): # pylint: disable=invalid-name
        """Special case for each binaryOp || and &&"""
        if node.op != '&&' and node.op != '||':
            self.generic_visit(node)
            return node

        #initialize variables
        decl_1 = make_temp_value(node, self.id_generator, self.envr)
        val_1 = decl_1.name
        self.envr.add(val_1, decl_1.type)

        if node.op == '&&':
            decl_1.init = Constant('int', '0')
            condition = node.left

        else: # case ||
            decl_1.init = Constant('int', '1')
            condition = BinaryOp('==', node.left, Constant('int', '0'),
                                 node.coord)

        #add if statement
        if_true = BinaryOp('!=', node.right, Constant('int', '0'), node.coord)
        if_true = Assignment('=', ID(val_1), if_true, node.coord)
        if_compound = Compound([if_true], node.coord)
        if_statement = If(condition, if_compound, None, coord=node.coord)
        self.environments[if_compound] = self.envr
        self.generic_visit(if_statement)
        self.insert_into_scope(decl_1, if_statement)
        return ID(val_1, node.coord)
