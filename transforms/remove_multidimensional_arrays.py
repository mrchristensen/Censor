"""

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
import sys
from copy import deepcopy
import pycparser.c_ast as AST
from .lift_node import LiftNode
from .type_helpers import make_temp_ptr, make_temp_value, get_type
#possibly change names to Simplify Arrays and ArrayReferences
class RemoveMultidimensionalArray(LiftNode):
    """LiftToCompoundBlock Transform"""
    
    def visit_UnaryOp(self, node):
        if (node.op == '&') and isinstance(node.expr,AST.ArrayRef):
            node = self.visit_array_ref(node.expr,True)
        return node

    def visit_ArrayRef(self, node):
        node = self.visit_array_ref(node)
        return node

    def visit_ArrayDecl(self, node):
        self.visit_array_decl(node)
        node = self.generic_visit(node)
        #lift non_constant array decl dim to a value so that the size is always stored in a known variable 
        if not isinstance(node.dim,AST.Constant):
            node.dim = self.lift_to_value(node.dim) #maybe add lift to constant value
        return node

    def visit_array_ref(self, array_ref, is_referenced=False):  
        """Visits and simplifies array ref to single dimension with only constants and id's for subscripts"""
        name = array_ref
        while isinstance(name, AST.ArrayRef):
            name = name.name 

        if isinstance(name,AST.ID): # all array refs
            ref_type = self.envr.get_type(name)
        else: #another stucture needs to be evaluated first to obtain the array
            ref_type = get_type(name,self.envr) 

        #visits the array ref and returns the resulting type of the reference
        #   combines any nested references into a single on eif possible
        result_type = self.visit_array_ref_helper(array_ref,deepcopy(ref_type))

        array_ref = AST.BinaryOp('+',array_ref.name,array_ref.subscript)
        if (not is_referenced) and (not isinstance(result_type,AST.ArrayDecl)):
            array_ref = AST.UnaryOp('*',array_ref)  
            parent = array_ref.expr
        else:
            parent = array_ref

        #parent will be a binop

        while isinstance(parent.left,AST.ArrayRef):
            parent.left = AST.BinaryOp('+',parent.left.name,parent.left.subscript)
            parent.left = AST.UnaryOp('*',parent.left)
            parent = parent.left.expr

        return array_ref

    #computes the product of all nested dimensions
    def _get_size(self, ref_type, index):
        result = index
        while isinstance(ref_type,AST.ArrayDecl):
            result = AST.BinaryOp('*',result,ref_type.dim)
            ref_type = ref_type.type

        return result
    
    def visit_array_ref_helper(self,ref,typ):
        #get the refrences paired with the right dimension to calculate stride, leftover type is at bottom of tree
        rtyp = self._reverse_type(typ,ref.name)
        array_ref = ref
        while isinstance(ref,AST.ArrayRef):

            if isinstance(rtyp, AST.ArrayDecl):
                indices = [ref.subscript]
                offsets = [rtyp.dim]
                ref_temp = ref.name
                typ_temp = rtyp.type 
                
                while isinstance(ref_temp, AST.ArrayRef) and isinstance(typ_temp, AST.ArrayDecl):
                    indices.append(ref_temp.subscript)
                    offsets.append(typ_temp.dim)
                    ref_temp = ref_temp.name
                    typ_temp = typ_temp.type

                new_subscript = None
                num_dim = len(offsets)
                #for each extra dimension that is part of a multi demintional array extract extra references to a binop calculation
                i = num_dim-2;
                while i >= 0 :
                    if new_subscript is None:
                        new_subscript = AST.BinaryOp('*',offsets[i],indices[i+1])
                    else:
                        new_subscript = AST.BinaryOp('+',new_subscript,indices[i+1])
                        new_subscript = AST.BinaryOp('*',new_subscript,offsets[i])
                    i-=1

                if new_subscript is not None:
                    new_subscript = AST.BinaryOp('+',new_subscript,indices[i+1])    
                    ref.subscript = new_subscript

                    ref.name = ref_temp
                    rtyp.type = typ_temp
                
            ref = ref.name
            rtyp = rtyp.type

        if isinstance(rtyp,AST.ArrayDecl):
            #partial index into an array
            array_ref.subscript = self._get_size(rtyp,array_ref.subscript)

        return rtyp
        
    def _reverse_type(self,typ,ref_counter):
        bottom = self._make_next(typ,None)
        if bottom is None:
            return typ
        top = None

        #ref_counter tracks how far we need to recurse in the case of a partial reference

        temp = typ.type
        while (not isinstance(temp,AST.TypeDecl)) and isinstance(ref_counter,AST.ArrayRef):
            if top is None:
                top = self._make_next(temp,bottom)
            else:
                top = self._make_next(temp,top)
            temp = temp.type
            ref_counter = ref_counter.name
        
        bottom.type = temp

        if top is not None:
            return top
        return bottom


    def _make_next(self,typ,subpart):
        if isinstance(typ, AST.ArrayDecl):
            return AST.ArrayDecl(subpart,typ.dim,typ.dim_quals)
        elif isinstance(typ, AST.PtrDecl):
            return AST.PtrDecl(typ.quals,subpart)
        else:
            return None

    def visit_array_decl(self, arrayDecl):
        temp = arrayDecl.type
        #copy = deepcopy(arrayDecl) #might need this for type aliasing
        while isinstance(temp,AST.ArrayDecl):
            arrayDecl.dim = AST.BinaryOp('*',arrayDecl.dim,temp.dim)
            arrayDecl.type = temp.type
            temp = temp.type

        return arrayDecl

    def lift_subscript(self, array_ref):
        if not isinstance(array_ref.subscript,(AST.ID,AST.Constant)):
            array_ref.subscript = self.lift_to_value(subscript)
        return 
        
    def lift_to_ptr(self, value):
        """Lift node to compound block"""
        decl = make_temp_ptr(value, self.id_generator, self.envr)
        decl.type = self.visit(decl.type) # simplify array decls
        self.insert_into_scope(decl)
        self.envr.add(decl.name, decl.type)
        return AST.UnaryOp('*', AST.ID(decl.name))

    def lift_to_value(self, value):
        """Lift node to compound block"""
        decl = make_temp_value(value, self.id_generator, self.envr)
        self.insert_into_scope(decl)
        self.envr.add(decl.name, decl.type)
        return AST.ID(decl.name)


