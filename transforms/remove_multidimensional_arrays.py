"""
Changes all array accesses to pointer arithmetic

Examples:
int array[3][4][5];
array[1][2][3] = 100;

->
int array_size = 3*4*5;
int array[array_size];

int array_index = (((1*4)+2)*5)+3;
array[array_index] = 100;

--------------------------
Also makes sure to lift all subscripts to a constant or id value
int n = 4, m = 6;
char buf[100];
buf[n*m] = 'm';
->
int n = 4, m = 6;
char buf[100];
int temp = n*m;
buf[temp]='m';
"""
from copy import deepcopy
import pycparser.c_ast as AST
from .lift_node import LiftNode
from .type_helpers import make_temp_value, get_type, _is_array
#possibly change names to Simplify Arrays and ArrayReferences
class RemoveMultidimensionalArray(LiftNode):
    """Remove Multidimensional Arrays Transform"""

    def visit_UnaryOp(self, node): #pylint: disable=invalid-name
        """ Checks for array_ref nested inside a UnaryOp """
        if (node.op == '&') and isinstance(node.expr, AST.ArrayRef):
            node = self.visit_array_ref(node.expr, True)
            return node

        self.generic_visit(node)
        #TODO check proper behavior
        if node.op == '*' and _is_array(get_type(node.expr, self.envr)):
            node.expr = AST.UnaryOp('&', node.expr)

        return node

    def visit_ArrayRef(self, node): #pylint: disable=invalid-name
        """ Simplifies ArrayRef to a single dimension """
        node = self.visit_array_ref(node)
        return node

    def visit_ArrayDecl(self, node): #pylint: disable=invalid-name
        """ Simplifies Arrays to a single dimension """
        self.visit_array_decl(node)
        node = self.generic_visit(node)
        #lift non_constant array decl dim to a value so that the size is
        # always stored in a known variable
        if not isinstance(node.dim, AST.Constant):
            #add further checks if its a const id then no need to lift
            name = node
            while not isinstance(name, AST.TypeDecl):
                name = name.type
            if not self.envr.is_global(name.declname) and node.dim is not None:
                node.dim = self.lift_to_value(node.dim)
        return node

    def visit_array_ref(self, array_ref, is_referenced=False):
        """Visits and simplifies array ref to single dimension with
            only constants and id's for subscripts"""
        name = array_ref
        while isinstance(name, AST.ArrayRef):
            name = name.name

        if isinstance(name, AST.ID): # all array refs
            ref_type = self.envr.get_type(name)
        else: #another stucture needs to be evaluated first to obtain the array
            ref_type = get_type(name, self.envr)

        #visits the array ref and returns the resulting type of the reference
        #   combines any nested references into a single on eif possible
        result_type = self.visit_array_ref_helper(array_ref, deepcopy(ref_type))

        array_ref = AST.BinaryOp('+', array_ref.name, array_ref.subscript)
        if (not is_referenced) and (not isinstance(result_type, AST.ArrayDecl)):
            array_ref = AST.UnaryOp('*', array_ref)
            parent = array_ref.expr
        else:
            parent = array_ref

        #parent will be a binop

        while isinstance(parent.left, AST.ArrayRef):
            if isinstance(parent.left.name, AST.ID):
                name_type = self.envr.get_type(parent.left.name)
                if _is_array(name_type):
                    parent.left.name = AST.UnaryOp('&', parent.left.name)
            parent.left = AST.BinaryOp('+', parent.left.name,
                                       parent.left.subscript)
            parent.left = AST.UnaryOp('*', parent.left)
            parent = parent.left.expr

        return array_ref

    def _get_size(self, ref_type, index): #pylint: disable=no-self-use
        """computes the product of all nested dimensions"""
        result = index
        while isinstance(ref_type, AST.ArrayDecl):
            result = AST.BinaryOp('*', result, ref_type.dim)
            ref_type = ref_type.type

        return result

    def visit_array_ref_helper(self, ref, typ):
        """get the refrences paired with the right dimension to calculate
         stride, leftover type is at bottom of tree"""
        rtyp = self._reverse_type(typ, ref.name)
        array_ref = ref
        while isinstance(ref, AST.ArrayRef):

            if isinstance(rtyp, AST.ArrayDecl):
                indices = [ref.subscript]
                offsets = [rtyp.dim]
                ref_temp = ref.name
                typ_temp = rtyp.type

                while (isinstance(ref_temp, AST.ArrayRef)
                       and isinstance(typ_temp, AST.ArrayDecl)):
                    indices.append(ref_temp.subscript)
                    offsets.append(typ_temp.dim)
                    ref_temp = ref_temp.name
                    typ_temp = typ_temp.type

                new_subscript = None
                num_dim = len(offsets)
                #for each extra dimension that is part of a multi demintional
                # array extract extra references to a binop calculation
                i = num_dim-2
                while i >= 0:
                    if new_subscript is None:
                        new_subscript = (
                            AST.BinaryOp('*', offsets[i], indices[i+1]))
                    else:
                        new_subscript = (
                            AST.BinaryOp('+', new_subscript, indices[i+1]))
                        new_subscript = (
                            AST.BinaryOp('*', new_subscript, offsets[i]))
                    i -= 1

                if new_subscript is not None:
                    new_subscript = (
                        AST.BinaryOp('+', new_subscript, indices[i+1]))
                    ref.subscript = new_subscript

                    ref.name = ref_temp
                    rtyp.type = typ_temp

            ref = ref.name
            rtyp = rtyp.type

        if isinstance(rtyp, AST.ArrayDecl):
            #partial index into an array
            array_ref.subscript = self._get_size(rtyp, array_ref.subscript)

        return rtyp

    def _reverse_type(self, typ, ref_counter):
        """ Reverses a type for a certian number of array references
            the rest is tacked on the end and is equivalent to the type
            of the result of the array reference """
        bottom = self._make_next(typ, None)
        if bottom is None:
            return typ
        top = None

        #ref_counter tracks how far we need to recurse
        #in the case of a partial reference
        temp = typ.type
        while ((not isinstance(temp, AST.TypeDecl))
               and isinstance(ref_counter, AST.ArrayRef)):
            if top is None:
                top = self._make_next(temp, bottom)
            else:
                top = self._make_next(temp, top)
            temp = temp.type
            ref_counter = ref_counter.name

        bottom.type = temp

        if top is not None:
            return top
        return bottom

    def _make_next(self, typ, subpart): #pylint: disable=no-self-use
        """ Helper for _reverse_type to build the proper nodes """
        if isinstance(typ, AST.ArrayDecl):
            return AST.ArrayDecl(subpart, typ.dim, typ.dim_quals)
        elif isinstance(typ, AST.PtrDecl):
            return AST.PtrDecl(typ.quals, subpart)
        else:
            return None

    def visit_array_decl(self, array_decl): #pylint: disable=no-self-use
        """ Visit a combines nested array_decl nodes """
        temp = array_decl.type
        #copy = deepcopy(array_decl) #might need this for type aliasing
        while isinstance(temp, AST.ArrayDecl):
            array_decl.dim = AST.BinaryOp('*', array_decl.dim, temp.dim)
            array_decl.type = temp.type
            temp = temp.type

        return array_decl

    def lift_to_value(self, value):
        """Lift node to compound block"""
        decl = make_temp_value(value, self.id_generator, self.envr)
        decl.quals = ['const']
        decl.type.quals += ['const']
        self.insert_into_scope(decl)
        self.envr.add(decl.name, decl.type)
        return AST.ID(decl.name)
