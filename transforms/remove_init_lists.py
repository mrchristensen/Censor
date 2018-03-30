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
from pycparser.c_ast import Decl, FuncDef, FuncDecl, FuncCall, IdentifierType
from pycparser.c_ast import Compound, ExprList, TypeDecl, ID, ArrayDecl
from pycparser.c_ast import ArrayRef, Assignment, Constant
from .node_transformer import NodeTransformer
from .helpers import prepend_statement


# On implementation:
# The hard parts are going to be things like
#   int e[10][10] = {1, 2, 3, 4, 5};
#   int d[10][10] = {[2] = {1, 2, 3}, {4, 5, 6}};
#   int a[4][4] = { {{1},{2}}};
#   int a[4][4] = {1,2};
# or struct and array initializer lists arbitrarily nested inside one another.
# Really, to implement this, you need a full understanding of the grammar of
# initializers, which is in the spec
# http://www.open-std.org/jtc1/sc22/WG14/www/docs/n1256.pdf
# on pages 125 - 130 (yes, its long. There are like 40 examples)


# TODO: figure out what to do with cases like
# char wow[100] = "wow"; where an array is initialized
# from a string

# TODO: once this transform is implemented, uncomment the
# "raise IncorrectTransformOrder" in insert_explicit_type_casts

class RemoveInitLists(NodeTransformer):
    """Transform for removing all initializer lists and compound
    initializers."""
    def __init__(self, id_generator, environments):
        self.environments = environments
        self.env = environments["GLOBAL"]
        self.id_generator = id_generator

    def visit_FileAST(self, node): # pylint: disable=invalid-name,too-many-locals
        """Insert function declaration, definition, and call for initializing
        globals."""
        # node.show()
        func_name = self.id_generator.get_unique_id() + "_INIT_GLOBALS"
        func_type = TypeDecl(func_name, [], IdentifierType(["void"]))
        init_globals_decl = Decl(func_name, [], [], [],
                                 FuncDecl(None, func_type), None, None)
        init_globals_def = FuncDef(init_globals_decl, [], Compound([]))
        init_globals_call = FuncCall(ID(func_name), ExprList([]))

        main_index = None
        inits = []
        for i, decl in enumerate(node.ext):
            if is_main(decl):
                main_index = i
                prepend_statement(decl.body, init_globals_call)
            elif isinstance(decl, Decl):
                if isinstance(decl.type, ArrayDecl):
                    for j, init in enumerate(decl.init.exprs):
                        index = Constant(IdentifierType(["int"]), str(j))
                        lvalue = ArrayRef(ID(decl.name), index)
                        assign = Assignment("=", lvalue, init)
                        inits.append(assign)

        init_globals_def.body.block_items = inits

        node.ext.insert(main_index, init_globals_decl)
        node.ext.append(init_globals_def)

        return node


def is_main(node):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(node, FuncDef) and node.decl.name == 'main'
