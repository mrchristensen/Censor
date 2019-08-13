'''AST transform: switch statements, as in:

        switch (x) {
            case 1:
                break;
            default:
            case 2:
                break;
        }

    into else-if-goto chains, like:

        if (x == 1) {
            goto Case1;
        } else if (x == 2) {
            goto Case2;
        } else {
            goto Default;
        }

        Case1:
            goto End;
        Default:
        Case2:
            goto End;
        End:
'''

from copy import deepcopy
from pycparser.c_ast import If, Compound, Goto, Label, BinaryOp
from pycparser.c_ast import Default, For, DoWhile, While, EmptyStatement
from .node_transformer import NodeTransformer

class SwitchToIf(NodeTransformer):
    '''NodeTransformer to change switch statements to if-else-if-goto changes'''

    def __init__(self, id_gen):
        self.id_gen = id_gen

    def visit_Switch(self, node): #pylint: disable=invalid-name
        '''Recursively modify Switch'''
        node = self.generic_visit(node)

        complist = []
        labellist = []
        cond = node.cond
        default_label = None

        # Make if statements for the case nodes
        for stmt in node.stmt:
            label = self.id_gen.get_unique_id()
            if isinstance(stmt, Default):
                default_label = label
                labellist.append((default_label,
                                  Compound(stmt.stmts, coord=stmt.coord)))
                continue
            binop = BinaryOp('==', deepcopy(cond), deepcopy(stmt.expr),
                             coord=stmt.coord)
            iftrue = Compound([Goto(label, coord=stmt.coord)], coord=stmt.coord)
            iffalse = None
            labellist.append((label, Compound(stmt.stmts, coord=stmt.coord)))
            complist.append(If(binop, iftrue, iffalse, coord=node.coord))

        endlabel = self.id_gen.get_unique_id()

        # Make if statement for default
        if default_label is not None:
            complist.append(Compound([Goto(default_label, coord=node.coord)],
                                     coord=node.coord))
        else:
            complist.append(Compound([Goto(endlabel, coord=node.coord)],
                                     coord=node.coord))

        # Create labels for if statements to jump to
        for label in labellist:
            compound = self.BreakToGoto(endlabel).generic_visit(label[1])
            current_label = Label(label[0], compound, coord=compound.coord)
            complist.append(current_label)

        complist.append(Label(endlabel, EmptyStatement(coord=node.coord),
                              coord=node.coord))

        return Compound(complist, coord=node.coord)

    class BreakToGoto(NodeTransformer):
        '''NodeTransformer to change breaks into Goto statements'''

        def __init__(self, endlabel):
            self.endlabel = endlabel

        def generic_visit(self, node):
            if isinstance(node, (For, DoWhile, While)):
                return node
            else:
                return super().generic_visit(node)

        def visit_Break(self, node): #pylint: disable=invalid-name
            '''Changes breaks to Goto nodes'''
            return Goto(self.endlabel, coord=node.coord)
