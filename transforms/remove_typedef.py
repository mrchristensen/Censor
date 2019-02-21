"""Typedef transform"""

from copy import deepcopy
import pycparser.c_ast as AST
from .lift_node import LiftNode

class RemoveTypedef(LiftNode):
    """
    Replace typedefined types with their actual names
    """

    in_def = 0
    def visit_ArrayDecl(self, node): #pylint: disable=invalid-name
        """ Checks Arraydecls within a typedef to remove non const sizing """
        self.generic_visit(node)
        if self.in_def != 0:
            if isinstance(node.dim, AST.Constant):
                return node
            new_id = self.id_generator.get_unique_id()
            id_type = AST.TypeDecl(new_id, ['const'],
                                   AST.IdentifierType(['unsigned']))

            const_decl = AST.Decl(new_id, ['const'], [], [],
                                  id_type, node.dim, None)
            # make decl with new ID that is const to store the
            self.insert_into_scope(const_decl)
            node.dim = AST.ID(new_id)
        return node

    def visit_Struct(self, node): #pylint: disable=invalid-name
        """ If a struct is namless when defined add an unique name to it """
        if node.decls is None:
            return node #not defining a struct
        else:
            node.decls = self.visit(node.decls)
        if node.name is None:
            node.name = self.id_generator.get_unique_id()
            struct_name = type(node).__name__ + " " + node.name
            self.envr.add(struct_name,
                          AST.TypeDecl(struct_name, [], node))
        return node

    def visit_Typedef(self, node): #pylint: disable=invalid-name
        """ Set member variable to determine if in typedef or not """
        self.in_def += 1
        node = self.generic_visit(node)
        self.in_def -= 1
        return node

    def visit_TypeDecl(self, node): #pylint: disable=invalid-name
        """ Check Identifier Types for typedef names and replace """
        self.generic_visit(node)
        if not isinstance(node.type, AST.IdentifierType):
            return node
        ident_type = node.type

        if ident_type.names[0] in self.envr:
            type_def = self.envr.get_type(ident_type.names[0])
            if isinstance(type_def, AST.TypeDecl):
                if isinstance(type_def.type, AST.Struct):
                    struct_name = AST.Struct(deepcopy(type_def.type.name), None)
                    node.type = struct_name
                    return node
                #TODO enum, unions
                node.type = deepcopy(type_def.type)
                return node
            if isinstance(type_def, (AST.PtrDecl, AST.ArrayDecl, AST.FuncDecl)):
                new_node = deepcopy(type_def)
                typedecl_name = new_node.type
                while not isinstance(typedecl_name, AST.TypeDecl):
                    typedecl_name = typedecl_name.type
                typedecl_name.declname = deepcopy(node.declname)
                return new_node
        return node
