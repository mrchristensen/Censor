"""
Creates a manifest of all external identifiers
(functions, structs, variables, etc.)
for a given file
"""
import pycparser.c_ast as AST
from pycparser.c_ast import Decl, FuncDecl, Struct, FuncDef

class ManifestVisitor(AST.NodeVisitor):
    """ visitor class to create manifest """
    def __init__(self, name):
        self.filename = name
        print(name)
        self.externals = []

    def visit_FileAST(self, node): # pylint: disable=invalid-name
        """ visit the root of the AST and look at surface level children """
        children = node.children()
        for child in children:
            child = child[1]
            if isinstance(child, Decl):
                if isinstance(child.type, FuncDecl):
                    pass
                    #self.externals.append("not a cool boi")
                elif 'extern' in child.storage:
                    pass
                    #self.externals.append("not a local boi")
                elif isinstance(child.type, Struct):
                    if child.type.decls is None:
                        pass
                    else:
                        self.externals.append(str(child.type.name))
                else:
                    self.externals.append(str(child.name))
            elif isinstance(child, FuncDef):
                self.externals.append(str(child.decl.name))
            else:
                pass
