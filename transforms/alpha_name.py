'''Renames all variables so that they are unique in
    the function and global scope'''
import copy
import pycparser.c_ast as AST  # pylint: disable=wildcard-import, unused-wildcard-import
from .node_transformer import NodeTransformer

GLOBAL_IDS = set() #IDs specific to global scope
FUNCTION_IDS = set() #All IDs declared in that function so far
TO_RENAME_IN_SCOPE = [{}] # record of how to rename variables that need renaming

class AlphaName(NodeTransformer):
    """Renames all variables so that functions can contain removable scopes"""

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        '''Find all global variables and add their ids to SET_OF_IDS
            Assume those are unique'''
        function_nodes = []
        for global_node in node.ext:
            if isinstance(global_node, AST.Decl):
                if isinstance(global_node.type, AST.Enum):
                    if global_node.type.values:
                        for enum in global_node.type.values.enumerators:
                            GLOBAL_IDS.add(enum.name)
                else:
                    GLOBAL_IDS.add(global_node.name)
            else:
                function_nodes.append(global_node)

        for f_node in function_nodes:
            self.visit(f_node)

        GLOBAL_IDS.clear()
        TO_RENAME_IN_SCOPE[-1].clear()
        return node

    def visit_Enumerator(self, node): # pylint: disable=invalid-name
        '''All Enumerators are treated as decls'''
        return self.visit_Decl(node)

    def visit_Struct(self, node): # pylint: disable=invalid-name
        '''Don't transform Structs, their decls are unique already'''
        return node

    def visit_Compound(self, node): # pylint: disable=invalid-name
        '''Create new map for things to rename in this scope, put on stack
           do a generic visit
           delete the map you just made'''
        map_of_last_scope = TO_RENAME_IN_SCOPE[-1]
        TO_RENAME_IN_SCOPE.append(copy.deepcopy(map_of_last_scope))
        node = self.generic_visit(node)
        TO_RENAME_IN_SCOPE.pop()
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
        if node.name in TO_RENAME_IN_SCOPE[-1]:
            node.name = TO_RENAME_IN_SCOPE[-1][node.name]
        return self.generic_visit(node)

    def visit_FuncDef(self, node): # pylint: disable=invalid-name
        '''Handle FUNCTION_IDS'''
        FUNCTION_IDS.update(GLOBAL_IDS)
        self.generic_visit(node)
        FUNCTION_IDS.clear()
        return node

    def rename_decl(self, decl):
        '''finds a name not declared yet, places in map
            add to funtion IDs'''
        old_name = decl.name
        try_count = 0
        new_name = old_name + '_' + str(try_count)
        while new_name in FUNCTION_IDS:
            try_count += 1
            new_name = old_name + '_' + str(try_count)
        FUNCTION_IDS.add(new_name)
        TO_RENAME_IN_SCOPE[-1][old_name] = new_name
        decl.name = new_name
        if isinstance(decl, AST.Decl):
            decl.type.declname = new_name
