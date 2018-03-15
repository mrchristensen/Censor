"""Transform all functions to contain only a single return statement."""
from copy import deepcopy
from pycparser.c_ast import Return, Label, Goto, Decl, Assignment, ID
from pycparser.c_ast import IdentifierType
from .type_helpers import remove_identifier, add_identifier
from .node_transformer import NodeTransformer
from .helpers import append_statement, prepend_statement

class SingleReturn(NodeTransformer):
    """Transform all functions to contain only a single return statement."""
    def __init__(self, id_generator):
        self.return_type = None
        self.retval_id = None
        self.return_label = None
        self.id_generator = id_generator

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        """Keep track of the return type of the function definition we
        are currently parsing."""
        self.return_type = deepcopy(node.decl.type.type)
        remove_identifier(self.return_type)
        self.return_label = self.id_generator.get_unique_id()

        return_expression = None
        if not is_void(self.return_type):
            self.retval_id = self.id_generator.get_unique_id()
            add_identifier(self.return_type, self.retval_id)

            retval_declaration = Decl(self.retval_id, [], [], [],
                                      self.return_type, None, None)
            node.body = prepend_statement(node.body, retval_declaration)
            return_expression = ID(self.retval_id)

        node = self.generic_visit(node)
        return_statement = Label(self.return_label, Return(return_expression))
        node.body = append_statement(node.body, return_statement)
        return node

    def visit_Return(self, node): # pylint: disable=invalid-name
        """Assign the return variable, then goto the return statement at the end."""
        goto = Goto(self.return_label)
        if is_void(self.return_type):
            return goto

        assignment = Assignment("=", ID(self.retval_id), node.expr)
        return [assignment, goto]


def is_void(return_type):
    """Takes in a TypeDecl that represents the return value of a function,
    returns a boolean of whether it is void or not."""
    if isinstance(return_type.type, IdentifierType):
        if 'void' in return_type.type.names:
            return True
    return False
