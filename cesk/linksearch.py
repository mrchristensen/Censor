"""Functions to interpret c code directly"""
import logging
from copy import deepcopy
import pycparser.c_ast as AST
from cesk.limits import StructPackingScheme as SPS
import cesk.limits as limits

class LinkSearch(AST.NodeVisitor): #
    """Holds various look-up-tables for functions, labels, etc."""
    parent_lut = {}
    index_lut = {}
    label_lut = {}
    envr_lut = {}
    function_lut = {}
    func_name_lut = {}
    struct_lut = {}
    union_lut = {}
    scope_decl_lut = {}
    global_decl_list = []

    def generic_visit(self, node):
        # pylint: disable=too-many-branches
        #create look-up-table (lut) for labels
        if isinstance(node, AST.Label):
            if node.name in LinkSearch.label_lut:
                raise Exception("Duplicate label name")
            LinkSearch.label_lut[node.name] = node

        #create lut for functions
        if isinstance(node, AST.FuncDef):
            name = node.decl.name
            LinkSearch.function_lut[name] = node
            LinkSearch.func_name_lut[node] = name

        if isinstance(node, AST.Struct) and node.decls:
            name = node.name
            LinkSearch.struct_lut[name] = node
            logging.debug('Store struct '+str(name)
                          +' with decls '+str(node.decls))

        if isinstance(node, AST.Union) and node.decls:
            name = node.name
            LinkSearch.union_lut[name] = node
            logging.debug('Store union '+str(name)
                          +' with decls '+str(node.decls))

        #link children to parents via lut
        for i, child in enumerate(node):
            if isinstance(child, AST.Node):
                if child in LinkSearch.parent_lut:
                    logging.error("Transform Adds Duplication")
                    logging.debug("Child: %s", str(child))
                    logging.debug("Old Parent: %s",
                                  str(LinkSearch.parent_lut[child]))
                    logging.debug("New Parent: %s",
                                  str(node))
                    child = deepcopy(child)
                    #temp_guy = node
                    #while temp_guy in LinkSearch.parent_lut:
                    #    temp_guy = LinkSearch.parent_lut[temp_guy]
                    #    logging.debug("Grandparent: %s", str(temp_guy))
                    #raise Exception("Node duplicated in tree: ")
                LinkSearch.parent_lut[child] = node
                LinkSearch.index_lut[child] = i
                self.visit(child)
        #if a node does not have a parent set it to none
        if node not in LinkSearch.parent_lut:
            LinkSearch.parent_lut[node] = None
            LinkSearch.index_lut[node] = 0

        #Make a list of Decls in compounds for continuation edge case 12
        if isinstance(node, AST.Decl) and node in LinkSearch.parent_lut:
            compound = None
            parent = LinkSearch.parent_lut[node]
            while True:
                if isinstance(parent, AST.Compound):
                    compound = parent
                    break
                if parent not in LinkSearch.parent_lut:
                    break
                parent = LinkSearch.parent_lut[parent]

            if compound != None:
                if compound in LinkSearch.scope_decl_lut:
                    LinkSearch.scope_decl_lut[compound].append(node)
                else:
                    LinkSearch.scope_decl_lut[compound] = [node]
            else: #is global, or part of struct
                parent = LinkSearch.parent_lut[node]
                if (not isinstance(node.type, (AST.FuncDecl, AST.Struct,
                                               AST.Union))
                        and isinstance(parent, AST.FileAST)):
                    LinkSearch.global_decl_list.append(node)
        return node


def get_sizes(ast_type, list_so_far):
    """ Populates list_so_far with a list of sizes for each variable in
        the struct """
    if isinstance(ast_type, AST.ArrayDecl):
        alignment = get_array_sizes(ast_type, list_so_far)
    elif isinstance(ast_type, (AST.Decl, AST.TypeDecl, AST.Typename)):
        alignment = get_sizes(ast_type.type, list_so_far)
    elif isinstance(ast_type, AST.FuncDecl):
        raise Exception("Function Decl in struct not allowed")
    elif isinstance(ast_type, AST.IdentifierType):
        num_bytes = limits.CONFIG.get_size(ast_type.names)
        if num_bytes < limits.CONFIG.get_word_size():
            alignment = num_bytes
        else:
            alignment = limits.CONFIG.get_word_size()
        list_so_far.append(num_bytes)
    elif isinstance(ast_type, AST.PtrDecl):
        size = limits.CONFIG.get_word_size()
        list_so_far.append(size)
        alignment = limits.CONFIG.get_word_size()
    elif isinstance(ast_type, AST.Struct):
        alignment = get_struct_sizes(ast_type, list_so_far)
    elif isinstance(ast_type, AST.Union):
        alignment = get_union_sizes(ast_type, list_so_far)
    else:
        raise Exception('Unknown Type '+str(ast_type))

    if limits.CONFIG.packing_scheme == limits.StructPackingScheme.PACT_COMPACT:
        alignment = 1
    return alignment

def get_array_sizes(ast_type, list_so_far):
    """ handles finding sizes and alignment for array type """
    arr_list = []
    alignment = get_sizes(ast_type.type, arr_list)
    if isinstance(ast_type.dim, AST.Constant):
        size = int(ast_type.dim.value)
    elif isinstance(ast_type.dim, AST.ID):
        size = 1 #length needs to be handle in interpret.py
        #raise Exception("Size of dynamically sized array unknown")
    else:
        raise Exception('Array dim must be constant or id')
    for _ in range(size):
        list_so_far.extend(arr_list)
    return alignment

def get_struct_sizes(ast_type, list_so_far):
    """ handles finding sizes and alignment for struct type """
    decls = ast_type.decls
    if decls is None:
        if ast_type.name in LinkSearch.struct_lut:
            decls = LinkSearch.struct_lut[ast_type.name].decls
        else:
            raise Exception('Struct ' + ast_type.name + ' not found')
    if limits.CONFIG.packing_scheme == SPS.PACT_COMPACT:
        alignment = 1
        for decl in decls:
            decl_alignment = get_sizes(decl, list_so_far)
            if alignment < decl_alignment:
                alignment = decl_alignment
    elif limits.CONFIG.packing_scheme == SPS.GCC_STD:
        num_bytes = 0
        alignment = 1
        for decl in decls:
            decl_alignment = get_sizes(decl, list_so_far)
            if num_bytes % decl_alignment != 0:
                buffer_size = decl_alignment - (num_bytes % decl_alignment)
                list_so_far[-1] += buffer_size
            num_bytes += list_so_far[-1]
            if alignment < decl_alignment:
                alignment = decl_alignment
        if num_bytes % alignment != 0:
            buffer_size = alignment - (num_bytes % alignment)
            list_so_far[-1] += buffer_size
    else:
        raise Exception("Unknown Packing Scheme")
    return alignment

def get_union_sizes(ast_type, list_so_far):
    """ handles finding sizes and alignment for union type """
    decls = ast_type.decls
    if decls is None:
        if ast_type.name in LinkSearch.union_lut:
            decls = LinkSearch.union_lut[ast_type.name].decls
        else:
            raise Exception("Union" + ast_type.name + ' not found')
    size = None
    alignment = None
    #largest_decl_size = None
    for decl in decls:
        decl_size = []
        decl_alignment = get_sizes(decl, decl_size)
        size_of_decl = 0
        for element_size in decl_size:
            size_of_decl += element_size
        if (size is None) or (size < size_of_decl):
            #largest_decl_size = decl_size
            size = size_of_decl
        if (alignment is None) or (alignment < decl_alignment):
            alignment = decl_alignment
    #list_so_far.extend(largest_decl_size)
    list_so_far.append(size)
    if limits.CONFIG.packing_scheme == SPS.GCC_STD:
        if size % alignment != 0:
            buffer_size = alignment - (size % alignment)
            list_so_far[-1] += buffer_size
    logging.debug("union size:")
    logging.debug(size)
    logging.debug("union alignment:")
    logging.debug(alignment)
    logging.debug("union list_so_far:")
    logging.debug(list_so_far)
    return alignment

def check_for_implicit_decl(ident):
    """See continuation edge case 12. Determine if a implicit decl is needed"""
    compound = None
    parent = LinkSearch.parent_lut[ident]
    while True:
        if isinstance(parent, AST.Compound):
            compound = parent
            break
        if parent not in LinkSearch.parent_lut:
            break
        parent = LinkSearch.parent_lut[parent]

    if compound is not None:
        if compound in LinkSearch.envr_lut:
            comp_envr = LinkSearch.envr_lut[compound]
            if comp_envr.is_localy_defined(ident.name):
                return None
        if compound in LinkSearch.scope_decl_lut:
            for decl in LinkSearch.scope_decl_lut[compound]:
                if decl.name == ident.name:
                    return decl
    return None
