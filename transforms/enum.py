'''Replaces all enums with integer constants'''
import pycparser.c_ast as AST  # pylint: disable=wildcard-import, unused-wildcard-import
from .node_transformer import NodeTransformer


NAME_TO_NUMBER = {}

class Enum(NodeTransformer):
    """Replaces all enums with integer constants"""

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        '''collects all enum definitions and visits then removes them'''
        all_enum_definitions = []
        for element in node.ext:
            if isinstance(element, AST.Decl):
                if isinstance(element.type, AST.Enum):
                    all_enum_definitions.append(element)
        for element in all_enum_definitions:
            self.visit(element)
            node.ext.remove(element)
        return self.generic_visit(node)

    def visit_EnumeratorList(self, node): # pylint: disable=invalid-name
        '''Numbers Enumerators and maps to their names'''
        current_constant = AST.Constant('int', '0')
        for enumerator in node.enumerators:
            enumerator = self.generic_visit(enumerator)
            if enumerator.value:
                NAME_TO_NUMBER[enumerator.name] = enumerator.value
            else:
                NAME_TO_NUMBER[enumerator.name] = current_constant
            current_constant = AST.BinaryOp('+', AST.Constant('int', '1'),
                                            NAME_TO_NUMBER[enumerator.name])
        return node

    def visit_ID(self, node): # pylint: disable=invalid-name
        '''Replaces all IDs that are enums with their literal value'''
        if node.name in NAME_TO_NUMBER:
            return NAME_TO_NUMBER[node.name]
        return self.generic_visit(node)

    def visit_TypeDecl(self, node):  # pylint: disable=invalid-name
        '''Replaces all enum types to int types'''
        if isinstance(node.type, AST.Enum):
            node.type = AST.IdentifierType(['int'])
        return self.generic_visit(node)
