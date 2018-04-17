"""
Both for implementing certain transforms (e.g. inserting explicit type casts)
and for doing the interpreting, dealing with initializer lists like

int a[3] = {1, 3, 7};

will be difficult, especially in cases of array and struct initializer lists
arbitrarily nested inside of one another. This transfrom will take the above to

int a[3];
a[0] = 1;
a[1] = 3;
a[2] = 7;

This is great, but we can't do it for globally declared arrays/structs because
a[0] = 1; can't exist at the global scope. So a program with globally
initialized objects, like this:

int a[2] = {1,3};
int main() {
    .
    .
}
int b[2] = {2,4};
.

will be transformed into this:

int a[2] = {1,3};
void censorXX_INIT_GLOBALS();
int main() {
    censorXX_INIT_GLOBALS();
    .
    .
}

int b[2] = {2,4};
.
.
void censorXX_INIT_GLOBALS() {
    a[0] = 1;
    a[1] = 3;
    b[0] = 2;
    b[1] = 4;
}
"""
# after having four lines of pycparser import, I decided to do them all at once
from pycparser.c_ast import * # pylint: disable=wildcard-import, unused-wildcard-import
from .node_transformer import NodeTransformer
from .helpers import prepend_statement
from .type_helpers import get_type

# NOTE: currently, the only parts of this implemented are the really basic
# cases, see the tests to see what exaclty

# NOTES on implementation:
# The hard parts are going to be things like
#   int e[10][10] = {1, 2, 3, 4, 5};
#   int d[10][10] = {[2] = {1, 2, 3}, {4, 5, 6}};
#   int a[4][4] = {{{1},{2}}};
#   int a[4][4] = {1, 2, 3, 4, 5, 6, 7};
#   int g[][3] = {1,2,3,4,5,6};
# (and many analagous thing that can be done for structs)
# or struct and array initializer lists arbitrarily nested inside one another.
# Really, to implement this, you need a full understanding of the grammar AND
# the semantics of initializers, which is in the spec
# http://www.open-std.org/jtc1/sc22/WG14/www/docs/n1256.pdf
# on pages 125 - 130 (yes, its long)

# TODO: figure out what to do with cases like
# char wow[100] = "wow"; where an array is initialized
# from a string

# TODO: once this transform is implemented, uncomment the
# "raise IncorrectTransformOrder" in insert_explicit_type_casts

_NOT_IMPLEMENTED_MESSAGE = """The RemoveInitLists transform has only been
implemented for initializer lists that are a list of constant expressions."""

class RemoveInitLists(NodeTransformer):
    """Transform for removing all initializer lists and compound
    initializers."""
    def __init__(self, id_generator, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_Compound(self, node): # pylint: disable=invalid-name
        """Reassign the environment to be the environment of the current
        compound block."""
        parent = self.env
        self.env = self.environments[node]
        retval = self.generic_visit(node)
        self.env = parent
        return retval

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        """Insert function declaration, definition, and call for initializing
        globals."""
        # node.show()
        func_name = self.id_generator.get_unique_id() + "_INIT_GLOBALS"
        func_type = TypeDecl(func_name, [], IdentifierType(["void"]))
        init_globals_decl = Decl(func_name, [], [], [],
                                 FuncDecl(ParamList([]), func_type), None, None)
        init_globals_def = FuncDef(init_globals_decl, [], Compound([]))
        init_globals_call = FuncCall(ID(func_name), ExprList([]))

        main_index = None
        inits = []
        for i, decl in enumerate(node.ext):
            node.ext[i] = self.generic_visit(decl)
            if is_main(decl):
                main_index = i
            elif isinstance(decl, Decl):
                if isinstance(decl.type, ArrayDecl):
                    inits += flatten_array_init(decl)
                    decl.init = None
                elif isinstance(decl.type, TypeDecl) and \
                            isinstance(decl.type.type, Struct):
                    inits += flatten_struct_init(decl, self.env)
                    decl.init = None

        if inits:
            prepend_statement(node.ext[main_index].body, init_globals_call)
            init_globals_def.body.block_items = inits
            node.ext.insert(main_index, init_globals_decl)
            node.ext.append(init_globals_def)

        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name,no-self-use
        """Flatten initializer lists that happen in non-global scope."""
        if isinstance(node.type, ArrayDecl) and node.init:
            retval = [node]
            retval += flatten_array_init(node)
            node.init = None
            return retval
        elif isinstance(node.type, TypeDecl) and \
            isinstance(node.type.type, Struct) and node.init:
            retval = [node]
            retval += flatten_struct_init(node, self.env)
            node.init = None
            return retval
        else:
            return node

def is_main(node):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(node, FuncDef) and node.decl.name == 'main'

def is_constant_expression(node):
    """Returns a boolean telling if a node represents a constant
    expression in C or not."""
    if isinstance(node, UnaryOp):
        return is_constant_expression(node.expr)
    elif isinstance(node, BinaryOp):
        return is_constant_expression(node.left) \
            and is_constant_expression(node.right)
    else:
        return isinstance(node, Constant)

def flatten_array_init(decl):
    """Takes a Decl with an initializer list, returns a list of assignment
    nodes that take care of the initialization."""
    inits = []
    for i, init in enumerate(decl.init.exprs):
        if not is_constant_expression(init):
            decl.show()
            raise NotImplementedError(_NOT_IMPLEMENTED_MESSAGE)
        index = Constant(IdentifierType(["int"]), str(i))
        lvalue = ArrayRef(ID(decl.name), index)
        assignment = Assignment("=", lvalue, init)
        inits.append(assignment)
    return inits

def flatten_struct_init(decl, env):
    """Takes a Decl with an initializer list, returns a list of assignment
    nodes that take care of the initialization."""
    typ = get_type(decl.name, env)
    fields = typ.type.decls
    inits = []
    for i, init in enumerate(decl.init.exprs):
        if not is_constant_expression(init):
            decl.show()
            raise NotImplementedError(_NOT_IMPLEMENTED_MESSAGE)
        field = ID(fields[i].name)
        lvalue = StructRef(ID(decl.name), ".", field)
        assignment = Assignment("=", lvalue, init)
        inits.append(assignment)
    return inits
