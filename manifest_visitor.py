"""
Creates a manifest of all external identifiers
(functions, structs, variables, etc.)
for a given file
"""
import pycparser.c_ast as AST
from pycparser.c_ast import Decl, FuncDecl, Struct, FuncDef, Union

class ManifestVisitor(AST.NodeVisitor):
    """visitor class to create manifest"""
    def __init__(self, name):
        self.filenames = name
        print(name)
        self.externals = {}
        self.current_manifest = {}
        self.local_manifests = {}

    def create_manifest(self, trees):
        """initial method for creating all manifests"""
        if len(self.filenames) != len(trees):
            return None
        for i in range(0, len(self.filenames)):
            self.visit(trees[i])
            self.local_manifests[self.filenames[i]] = self.current_manifest
            self.current_manifest = {}

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        """visit the root of the AST and look at surface level children"""
        children = node.children()
        for child in children:
            child = child[1]
            if isinstance(child, Decl):
                if isinstance(child.type, FuncDecl):
                    pass
                elif 'extern' in child.storage:
                    pass
                elif 'static' in child.storage:
                    self.current_manifest[str(child.name)] = child
                elif isinstance(child.type, (Struct, Union)):
                    if child.type.decls is None:
                        pass
                    else:
                        if str(child.type.name) not in self.externals.keys():
                            self.externals[str(child.type.name)] = child
                            self.current_manifest[str(child.type.name)] = child
                else:
                    if str(child.name) not in self.externals.keys():
                        self.externals[str(child.name)] = child
                        self.current_manifest[str(child.name)] = child
            elif isinstance(child, FuncDef):
                #static functions?
                if str(child.decl.name) not in self.externals.keys():
                    self.externals[str(child.decl.name)] = child
                    self.current_manifest[str(child.decl.name)] = child
