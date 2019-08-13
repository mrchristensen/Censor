'''Renames all variables so that they are unique in
    the function and global scope'''
import pycparser.c_ast as AST  # pylint: disable=wildcard-import, unused-wildcard-import
from .node_transformer import NodeTransformer

GLOBAL_IDS = set() #IDs specific to global scope
FUNCTION_IDS = set() #All IDs declared in that function so far
TO_RENAME_STACK_MAP = {} # map from an old_id to a stack of new_ids.
RE_DECLS_IN_SCOPE = [set()] # Stack of sets of all ids of new decls in scopes.

class AlphaName(NodeTransformer):
    '''Renames all variables so that functions can contain removable scopes'''

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        '''Find all global variables and add their ids to GLOBAL_IDS
            Assume those are unique'''
        function_nodes = []
        for global_node in node.ext:
            if isinstance(global_node, AST.Decl):
                GLOBAL_IDS.add(global_node.name)
            else:
                function_nodes.append(global_node)

        for f_node in function_nodes:
            self.visit(f_node)

        GLOBAL_IDS.clear()
        TO_RENAME_STACK_MAP.clear()
        RE_DECLS_IN_SCOPE[-1].clear()
        return node

    def visit_Struct(self, node): # pylint: disable=invalid-name,no-self-use
        '''Don't transform Structs, their decls are unique already'''
        return node

    def visit_For(self, node): # pylint: disable=invalid-name
        '''Handles declarations in a for loop'''
        return self.visit_Compound(node)

    def visit_Compound(self, node): # pylint: disable=invalid-name
        '''Create new set for decls in this scope, put on stack
           do a generic visit
           pop each stack for each element in set
           delete the set'''
        RE_DECLS_IN_SCOPE.append(set())

        node = self.generic_visit(node)

        ids_to_remove = RE_DECLS_IN_SCOPE.pop()
        for name in ids_to_remove:
            TO_RENAME_STACK_MAP[name].pop()
            if not TO_RENAME_STACK_MAP[name]:
                del TO_RENAME_STACK_MAP[name]
        return node

    def visit_Decl(self, node): # pylint: disable=invalid-name
        '''Check if id has been declared before,
            make new name if exists in different scope'''
        if isinstance(node, AST.Decl):
            if isinstance(node.type, AST.FuncDecl):
                return self.generic_visit(node) # ignore

        self.generic_visit(node)

        if node.name in FUNCTION_IDS:
            self.rename_decl(node)
        else:
            FUNCTION_IDS.add(node.name)

        return node

    def visit_ID(self, node): # pylint: disable=invalid-name
        '''Check ID to see if it should be changed, and change it.'''
        if node.name in TO_RENAME_STACK_MAP:
            node.name = TO_RENAME_STACK_MAP[node.name][-1]
        return self.generic_visit(node)

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        '''Handle FUNCTION_IDS'''
        FUNCTION_IDS.update(GLOBAL_IDS)
        self.generic_visit(node)
        TO_RENAME_STACK_MAP.clear()
        RE_DECLS_IN_SCOPE[-1].clear()
        FUNCTION_IDS.clear()
        return node

    def rename_decl(self, decl): #pylint: disable=no-self-use
        '''Finds a name not declared yet, places in map
            add to function IDs'''
        old_name = decl.name
        if not old_name in TO_RENAME_STACK_MAP:
            TO_RENAME_STACK_MAP[old_name] = []

        try_count = 0
        new_name = old_name + '_' + str(try_count)
        while new_name in FUNCTION_IDS:
            try_count += 1
            new_name = old_name + '_' + str(try_count)

        FUNCTION_IDS.add(new_name)
        RE_DECLS_IN_SCOPE[-1].add(old_name)
        TO_RENAME_STACK_MAP[old_name].append(new_name)
        decl.name = new_name
        decl_type = decl.type
        while not isinstance(decl_type, AST.TypeDecl):
            decl_type = decl_type.type
        decl_type.declname = new_name
