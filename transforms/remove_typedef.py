"""Typedef transform"""

from copy import deepcopy
import pycparser.c_ast as AST
from transforms.lift_node import LiftNode
from transforms.helpers import propagate_constant

class RemoveTypedef(LiftNode):
    """
    Replace typedefined types with their actual types
    """

    in_def = 0
    def visit_ArrayDecl(self, node): #pylint: disable=invalid-name
        """ Checks Arraydecls within a typedef to remove non const sizing """
        self.generic_visit(node)
        if self.in_def != 0:
            if isinstance(node.dim, AST.BinaryOp):
                node.dim = propagate_constant(node.dim)
            if isinstance(node.dim, AST.Constant):
                return node
            #raise Exception("typedef'd arrays must be of constant size")
            new_id = self.id_generator.get_unique_id()
            id_type = AST.TypeDecl(new_id, ['const'],
                                   AST.IdentifierType(['unsigned']))

            const_decl = AST.Decl(new_id, ['const'], [], [],
                                  id_type, node.dim, None, coord=node.coord)
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

    def visit_Enum(self, node): #pylint: disable=invalid-name
        """ If a enum is namless when defined add an unique name to it """
        if node.values is None:
            return node #not defining a struct
        else:
            node.values = self.visit(node.values)
        if node.name is None:
            node.name = self.id_generator.get_unique_id()
            struct_name = type(node).__name__ + " " + node.name
            self.envr.add(struct_name,
                          AST.TypeDecl(struct_name, [], node))
        return node

    def visit_Union(self, node): #pylint: disable=invalid-name
        """ If a enum is namless when defined add an unique name to it """
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
            type_def = deepcopy(self.envr.get_type(ident_type.names[0]))
            if isinstance(type_def, AST.TypeDecl):
                if isinstance(type_def.type, (AST.Struct, AST.Enum, AST.Union)):
                    struct_name = \
                        type(type_def.type)(deepcopy(type_def.type.name), None)
                    node.type = struct_name
                    return node
                node.type = deepcopy(type_def.type)
            elif isinstance(type_def,
                            (AST.PtrDecl, AST.ArrayDecl, AST.FuncDecl)):
                new_node = deepcopy(type_def)
                type_decl = new_node.type
                while not isinstance(type_decl, AST.TypeDecl):
                    type_decl = type_decl.type
                type_decl.declname = deepcopy(node.declname)
                if isinstance(type_decl.type,
                              (AST.Struct, AST.Enum, AST.Union)):
                    struct_name = \
                        type(type_decl.type)(type_decl.type.name, None)
                    type_decl.type = struct_name

                node = new_node
        return node
