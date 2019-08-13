'''AST transform that transforms a while loop to a do-while loop

while(x){
    body();
}
    -->
goto check
loop:
    body()
check:
if(x)
    goto loop

----------------------------------
do{
    body();
}while(x)
    -->
loop:
    body()
check:
if(x)
    goto loop

'''

from pycparser.c_ast import If, Label, Goto
from .node_transformer import NodeTransformer
from .helpers import ensure_compound

class WhileToGoto(NodeTransformer):
    '''NodeTransformer to change while and do-while loops to goto'''

    def __init__(self, id_generator):
        self.id_generator = id_generator

    def remove_loop(self, cond, stmt, check_label):
        '''Does the work of transforming the loop'''
        loop_label = self.id_generator.get_unique_id()

        stmt = ensure_compound(stmt)
        if_node = If(cond, Goto(loop_label, coord=cond.coord), None,
                     coord=cond.coord)
        stmt.block_items.append(Label(check_label, ensure_compound(if_node),
                                      coord=cond.coord))
        #stmt.block_items.append(if_node)

        continue_transformer = ContinueToGoto(check_label)
        body = continue_transformer.visit(stmt)

        return Label(loop_label, body, coord=stmt.coord)

    def visit_While(self, node): #pylint: disable=invalid-name
        '''Transform a while loop to goto'''
        node = self.generic_visit(node) #transform inner loops
        check_label = self.id_generator.get_unique_id()
        label = Goto(check_label, coord=node.coord)
        loop = self.remove_loop(node.cond, node.stmt, check_label)
        return [label, loop]

    def visit_DoWhile(self, node): #pylint: disable=invalid-name
        '''Transform a do-while loop to goto code'''
        node = self.generic_visit(node) #remove inner loops
        check_label = self.id_generator.get_unique_id()
        return self.remove_loop(node.cond, node.stmt, check_label)



class ContinueToGoto(NodeTransformer):
    '''NodeTransformer to change continue statements to goto statements'''

    def __init__(self, label):
        self.label = label

    def visit_Continue(self, node): #pylint: disable=invalid-name
        '''Replace continue with goto statement'''
        return Goto(self.label, coord=node.coord)
