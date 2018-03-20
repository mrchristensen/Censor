"""
LiftToCompoundBlock Transform
"""

from copy import deepcopy
from pycparser.c_ast import Compound, UnaryOp, PtrDecl, Decl, ID
from .lift_node import LiftNode
from .type_helpers import get_type, add_identifier

class LiftToCompoundBlock(LiftNode):
    """
    Transform to lift nodes from problematic places in the AST to
    the nearest Compound block. Examples of nodes that need to be lifted

    - FuncCall
    - StructRef
    - ArrayRef
    - Assignment
    - BinaryOp

    These nodes will be assigned an identifier in the Compound block which
    will be used to replace the node in its original position.

    This has the extra affect of flattening nodes that can be nested in themselves
    like the StructRef, ArrayRef, and Assignment nodes
    TODO: Decide whether to use this transformation only for struct and array references
    or to use it for assignments, binary ops and other things like we are currently
    """

    def __init__(self, id_generator, environments):
        super().__init__(id_generator, environments)
        self.ptr_class_names = [
            'StructRef',
            'ArrayRef'
        ]
        self.value_class_names = [
            'BinaryOp',
            # 'FuncCall'
        ]

    def generic_visit(self, node):
        for field in node.__class__.__slots__:
            old_value = getattr(node, field, None)
            if self.skip(old_value):
                continue
            elif isinstance(old_value, list):
                old_value[:] = self.visit_list(old_value)
            elif self.is_node(old_value):
                node = self.visit_node(node, field, old_value)
            if not isinstance(node, Compound):
                node = self.lift_field(node, field)
        return node

    def lift_field(self, node, field):
        """Lift field value to compound block if necessary"""
        value = getattr(node, field, None)
        if value is None:
            return node
        if value.__class__.__name__ in self.ptr_class_names:
            return self.lift_to_ptr(node, field, value)
        elif value.__class__.__name__ in self.value_class_names:
            return self.lift_to_value(node, field, value)
        elif value.__class__.__name__ == 'Assignment':
            return self.lift_assignment(node, field, value)

        return node

    def lift_to_ptr(self, node, field, value):
        """Lift node to compound block"""
        name = self.id_generator.get_unique_id()
        addr = UnaryOp('&', value)
        typ = get_type(value, self.envr)
        ptr = PtrDecl([], add_identifier(typ, name))
        decl = Decl(name, [], [], [], ptr, addr, None)
        self.insert_into_scope(decl)
        self.envr.add(name, ptr)
        ref = UnaryOp('*', ID(name))
        setattr(node, field, ref)
        return node

    def lift_to_value(self, node, field, value):
        """Lift node to compound block"""
        name = self.id_generator.get_unique_id()
        typ = get_type(value, self.envr)
        decl = Decl(name, [], [], [], add_identifier(typ, name), value, None)
        self.insert_into_scope(decl)
        self.envr.add(name, typ)
        ref = ID(name)
        setattr(node, field, ref)
        return node

    def lift_assignment(self, node, field, value):
        """Lift node to compound block"""
        self.insert_into_scope(value)
        ref = deepcopy(value.lvalue)
        setattr(node, field, ref)
        return node
