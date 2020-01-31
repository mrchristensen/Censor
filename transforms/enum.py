'''Replaces all enums with integer constants'''
import pycparser.c_ast as AST
from transforms.node_transformer import NodeTransformer
from transforms.helpers import propagate_constant

class Enum(NodeTransformer):
    """Replaces all enums with integer constants"""

    def __init__(self, _=None, __=None):
        super().__init__()
        self.name_to_number = {}

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        '''collects all enum definitions and visits then removes them'''
        all_enum_definitions = []
        for element in node.ext:
            if ((isinstance(element, AST.Decl) and
                 isinstance(element.type, AST.Enum)) or
                    (isinstance(element, AST.Typedef) and
                     isinstance(element.type.type, AST.Enum))):
                all_enum_definitions.append(element)
        for element in all_enum_definitions:
            self.visit(element)
            node.ext.remove(element)
        return self.generic_visit(node)

    def visit_Compound(self, node): # pylint: disable=invalid-name
        '''collects all enum definitions and visits then removes them'''
        all_enum_definitions = []
        if not node.block_items:
            return self.generic_visit(node)
        for element in node.block_items:
            if ((isinstance(element, AST.Decl) and
                 isinstance(element.type, AST.Enum)) or
                    (isinstance(element, AST.Typedef) and
                     isinstance(element.type.type, AST.Enum))):
                all_enum_definitions.append(element)
        for element in all_enum_definitions:
            self.visit(element)
            node.block_items.remove(element)
        return self.generic_visit(node)

    def visit_EnumeratorList(self, node): # pylint: disable=invalid-name
        '''Numbers Enumerators and maps to their names'''
        current_constant = AST.Constant('int', '0')
        for enumerator in node.enumerators:
            enumerator = self.generic_visit(enumerator)
            if enumerator.value:
                self.name_to_number[enumerator.name] = \
                    propagate_constant(enumerator.value)
            else:
                self.name_to_number[enumerator.name] = current_constant
            current_constant = propagate_constant( \
                AST.BinaryOp('+', AST.Constant('int', '1'),
                             self.name_to_number[enumerator.name],
                             node.coord))
        return node

    def visit_ID(self, node): # pylint: disable=invalid-name
        '''Replaces all IDs that are enums with their literal value'''
        if node.name in self.name_to_number:
            return self.name_to_number[node.name]
        return self.generic_visit(node)

    def visit_TypeDecl(self, node):  # pylint: disable=invalid-name
        '''Replaces all enum types to int types'''
        node = self.generic_visit(node)
        if isinstance(node.type, AST.Enum):
            node.type = AST.IdentifierType(['int'])
        return node
