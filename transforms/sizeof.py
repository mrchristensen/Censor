""" Computes the size and alignment based on values in limits.py """
import re
import pycparser.c_ast as AST
import cesk.limits as limits
from cesk.limits import StructPackingScheme as SPS
from transforms.helpers import propagate_constant

def get_size_ast(ast_type_node, env=None):
    """returns the size in bytes of the ast type,
        nested in an unsigned long constant"""
    size, _ = get_size_and_alignment(ast_type_node, env)
    return size

def c_to_int(constant):
    """ takes in a Constant ast node and returns a python int """
    int_str = re.sub(r"l|u|L|U", "", constant.value)
    return int(int_str, 0)

def get_size_and_alignment(ast_type, env=None):
    """returns size as an AST node and alignmentas an integer"""
    if isinstance(ast_type, AST.ArrayDecl):
        size, alignment = get_size_and_alignment(ast_type.type, env)
        if (isinstance(size, AST.Constant) and
                isinstance(ast_type.dim, AST.Constant)):
            size = AST.Constant('int', str(c_to_int(size) *
                                           c_to_int(ast_type.dim))+'l')
        else:
            size = AST.BinaryOp('*', size, ast_type.dim, ast_type.coord)
    elif isinstance(ast_type, (AST.Decl, AST.TypeDecl, AST.Typename)):
        size, alignment = get_size_and_alignment(ast_type.type, env)
    elif isinstance(ast_type, AST.FuncDecl):
        size = AST.Constant('int', '1l')
        alignment = 1 #do not know what to do exactly
    elif isinstance(ast_type, AST.IdentifierType):
        size, alignment = get_identifier_size(ast_type)
    elif isinstance(ast_type, AST.PtrDecl):
        size = AST.Constant('int', str(limits.CONFIG.get_word_size())+'l')
        alignment = limits.CONFIG.get_word_size()
    elif isinstance(ast_type, AST.Struct):
        size, alignment = get_struct_size_and_align(ast_type, env)
    elif isinstance(ast_type, AST.Union):
        size, alignment = get_union_size_and_align(ast_type, env)
    else:
        raise Exception('Unknown Type '+str(ast_type))

    if limits.CONFIG.packing_scheme == SPS.PACT_COMPACT:
        alignment = 1
    return size, alignment

def get_identifier_size(ast_type):
    """ gets the size of simple types int, long, etc """
    num_bytes = limits.CONFIG.get_size(ast_type.names)
    size = AST.Constant('int', str(num_bytes)+'l')
    if num_bytes < limits.CONFIG.get_word_size():
        alignment = num_bytes
    else:
        alignment = limits.CONFIG.get_word_size()
    return size, alignment

def _size_compact(decls, env):
    num_bytes = 0
    alignment = 1
    for decl in decls:
        decl_size, decl_alignment = get_size_and_alignment(decl, env)
        if isinstance(decl_size, AST.Constant):
            num_bytes += c_to_int(decl_size)
        elif isinstance(decl_size, AST.BinaryOp):
            num_bytes += _reduce_binop(decl_size)
        else:
            raise Exception("Not Implemented, Arrays not constant size")
        if alignment < decl_alignment:
            alignment = decl_alignment
    return num_bytes, alignment

def _reduce_binop(binop):
    """ evaluates binops of constant integer values """
    binop = propagate_constant(binop)
    if not isinstance(binop, AST.Constant):
        raise Exception("Arrays must be of constant size to get size")
    return binop

def _size_std(decls, env):
    num_bytes = 0
    alignment = 1
    for decl in decls:
        decl_size, decl_alignment = get_size_and_alignment(decl, env)
        if num_bytes % decl_alignment != 0:
            num_bytes += decl_alignment - (num_bytes % decl_alignment)
        if isinstance(decl_size, AST.Constant):
            num_bytes += c_to_int(decl_size)
        elif isinstance(decl_size, AST.BinaryOp):
            num_bytes += _reduce_binop(decl_size)
        else:
            raise Exception("Not Implemented, Arrays are not constant size")
            #num_bytes = AST.BinaryOp('+',offset,decl_size, ast_type.coord)
        if alignment < decl_alignment:
            alignment = decl_alignment
    if num_bytes % alignment != 0:
        num_bytes += alignment - (num_bytes % alignment)
    return num_bytes, alignment

def get_struct_size_and_align(ast_type, env):
    """ Same as above, but only for structs """
    decls = ast_type.decls
    if decls is None:
        if env is None:
            raise Exception("Environment needed to get size of struct")
        struct_type_string = type(ast_type).__name__ + " " + ast_type.name
        decls = env.get_type(struct_type_string).decls
    if limits.CONFIG.packing_scheme == SPS.PACT_COMPACT:
        num_bytes, alignment = _size_compact(decls, env)
    elif limits.CONFIG.packing_scheme == SPS.GCC_STD:
        num_bytes, alignment = _size_std(decls, env)
    else:
        raise Exception("Unknown Packing Scheme")

    size = AST.Constant('int', str(num_bytes)+'l')
    return size, alignment

def get_union_size_and_align(ast_type, env=None):
    """ Same as above, but only for unions """
    if env is None:
        raise Exception("Environment needed to determine size of union")
    decls = ast_type.decls
    if decls is None:
        union_type_string = type(ast_type).__name__ + " " + ast_type.name
        decls = env.get_type(union_type_string).decls
    size = None
    alignment = None
    for decl in decls:
        decl_size, decl_alignment = get_size_and_alignment(decl, env)
        if (size is None) or (c_to_int(size) < c_to_int(decl_size)):
            size = decl_size
        if (alignment is None) or (alignment < decl_alignment):
            alignment = decl_alignment

    return size, alignment

def _offset_compact(decls, field, env):
    offset = 0
    alignment = 1
    field_type = None
    for decl in decls:
        if decl.name == field.name:
            field_type = decl.type
            break

        # Functionality for anonymous unions and structs
        added_offset = 0
        if decl.name is None and isinstance(decl.type, AST.Union):
            for nested_decl in decl.type.decls:
                if nested_decl.name == field.name:
                    field_type = nested_decl.type
                    break  
        elif decl.name is None and isinstance(decl.type, AST.Struct):
            for nested_decl in decl.type.decls:
                if nested_decl.name == field.name:
                    field_type = nested_decl.type
                    break
                decl_size, decl_alignment = get_size_and_alignment(nested_decl, env)
                if isinstance(decl_size, AST.Constant):
                    added_offset += c_to_int(decl_size)
                    offset += c_to_int(decl_size)
                else:
                    raise Exception("Not Implemented, Arrays not constant size")
                if alignment < decl_alignment:
                    alignment = decl_alignment
        if field_type is not None:
            break
        offset -= added_offset

        decl_size, decl_alignment = get_size_and_alignment(decl, env)
        if isinstance(decl_size, AST.Constant):
            offset += c_to_int(decl_size)
        else:
            raise Exception("Not Implemented, Arrays not constant size")
            #offset = AST.BinaryOp('+',offset,decl_size, ast_type.coord)
        if alignment < decl_alignment:
            alignment = decl_alignment

    return offset, field_type

def _offset_std(decls, field, env):
    offset = 0
    alignment = 1
    field_type = None
    for decl in decls:
        decl_size, decl_alignment = get_size_and_alignment(decl, env)
        if offset % decl_alignment != 0:
            offset += decl_alignment - (offset % decl_alignment)
        if decl.name == field.name:
            field_type = decl.type
            break
        if isinstance(decl_size, AST.Constant):
            offset += c_to_int(decl_size)
        else:
            raise Exception("Not Implemented, Array is not constant size")
            #offset = AST.BinaryOp('+',offset,decl_size, ast_type.coord)
        if alignment < decl_alignment:
            alignment = decl_alignment
    if offset % alignment != 0:
        offset += alignment - (offset % alignment)

    return offset, field_type

def get_struct_offset(struct_type, field, env):
    """ Calculate and the offset and type of the field requested """
    if isinstance(struct_type, AST.TypeDecl):
        struct_type = struct_type.type
    decls = struct_type.decls
    if decls is None:
        if env is None:
            raise Exception("Environment needed to get size of struct")
        struct_type_string = type(struct_type).__name__ + " " + struct_type.name
        decls = env.get_type(struct_type_string).decls
    field_type = None
    if limits.CONFIG.packing_scheme == SPS.PACT_COMPACT:
        offset, field_type = _offset_compact(decls, field, env)
    elif limits.CONFIG.packing_scheme == SPS.GCC_STD:
        offset, field_type = _offset_std(decls, field, env)
    else:
        raise Exception("Unknown Packing Scheme")

    if field_type is None:
        raise Exception("Field not found")

    if isinstance(struct_type, AST.Union):
        size = AST.Constant('int', '0l')
        return size, field_type

    size = AST.Constant('int', str(offset)+'l')
    return size, field_type
