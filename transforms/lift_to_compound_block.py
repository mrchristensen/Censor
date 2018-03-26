"""
This transform uses the LiftNode base class to enforce a simply structured AST.
It defines an array of class names to search for. It performs a depth first search
so it transforms the most deeply nested node first. This should ensure that things are
done in the right order.

When it sees a node that matches a class name it is looking for it checks to see if it's
direct parent is a Compound node. If it isn't then the node needs to be replaced by an ID.
It creates a new Decl node for the new ID and inserts it into the current scope.

At the end of the transform all nodes with class names in the array searched for will be
direct children of Assignment nodes which are direct children of a Compound block.

Examples:

if (a < b)... becomes

int censor01 = a < b;
if (censor1)...

obj->x[3].prop = a + b + c; becomes

struct object (*censor01)[5] = &obj->x;
struct object *censor2 = &(*censor01)[3];
int *censor03 = &(*censor02).prop;
int censor04 = a + b;
int censor05 = censor04 + c;
*censor03 = censor05;

Special considerations:
Pointers are always created for StructRef and ArrayRef nodes. This is because ArrayRef nodes
always need to be replaced by a pointer and I couldn't find an easy way to determine if the
property referenced in a StructRef was an array or not.

Assignment nodes are a special case because they don't require the same process of finding
the type of the node and creating a new Decl. They are just lifted into the current scope
and replaced by their lvalue.

UnaryOp Nodes are also a special case because they only need to be lifted if they mutate.

Dependencies:
This transform will only work properly if all 'else if' nodes have already been transformed to
have their own scope so that statements in their conditions are only evaluated if the are
reached.

This transform will also break if a Label node only has one statement and it has parts that need
to be lifted. The problem is fixed if the label's child is a Compound block.
"""

from copy import deepcopy
from pycparser.c_ast import Compound, UnaryOp, ID, Assignment
from .lift_node import LiftNode
from .type_helpers import make_temp_ptr, make_temp_value

class LiftToCompoundBlock(LiftNode):
    """LiftToCompoundBlock Transform"""


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
        klass = value.__class__.__name__
        if klass in self.ptr_class_names:
            return self.lift_to_ptr(node, field, value)
        elif isinstance(value, UnaryOp):
            return self.lift_unaryop(node, field, value)
        elif isinstance(value, Assignment):
            return self.lift_assignment(node, field, value)
        elif isinstance(node, Assignment):
            return node
        elif klass in self.value_class_names:
            return self.lift_to_value(node, field, value)

        return node

    def lift_to_ptr(self, node, field, value):
        """Lift node to compound block"""
        decl = make_temp_ptr(value, self.id_generator, self.envr)
        self.insert_into_scope(decl)
        self.envr.add(decl.name, decl.type)
        ref = UnaryOp('*', ID(decl.name))
        setattr(node, field, ref)
        return node

    def lift_to_value(self, node, field, value):
        """Lift node to compound block"""
        decl = make_temp_value(value, self.id_generator, self.envr)
        self.insert_into_scope(decl)
        self.envr.add(decl.name, decl.type)
        ref = ID(decl.name)
        setattr(node, field, ref)
        return node

    def lift_assignment(self, node, field, value):
        """Lift node to compound block"""
        self.insert_into_scope(value)
        ref = deepcopy(value.lvalue)
        setattr(node, field, ref)
        return node

    def lift_unaryop(self, node, field, value):
        """Lift node to compound block"""
        if value.op not in ['++', '--', 'p++', 'p--']:
            return node
        if 'p' in value.op:
            self.append_to_scope(value)
        else:
            self.insert_into_scope(value)
        ref = deepcopy(value.expr)
        setattr(node, field, ref)
        return node
