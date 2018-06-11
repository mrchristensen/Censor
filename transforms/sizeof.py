import pycparser.c_ast as AST
from cesk.limits import get_word_size, get_size, Struct_Packing_Scheme as SPS, config

#returns the size in bytes of the ast type, nested in an unsigned long constant
def get_size_ast(ast_type_node):
    size, _  = get_size_and_alignment(ast_type_node)
    return size

#returns size as an AST node and alignment as an in
def get_size_and_alignment(ast_type):
    if isinstance(ast_type, AST.ArrayDecl):
        size, alignment = get_size_and_alignment(ast_type.type)
        size = AST.BinaryOp('*',size,ast_type.dim)
    elif isinstance(ast_type, AST.FuncDecl):
        size = AST.Constant('long',1)
        alignment = 1 #do not know what to do exactly
    elif isinstance(ast_type, AST.IdentifierType):
        num_bytes = get_size(ast_type.names)
        size = AST.Constant('long',str(num_bytes))
        if num_bytes < get_word_size():
            alignment = num_bytes
        else:
            alignment = get_word_size()
    elif isinstance(ast_type, AST.PtrDecl):
        size = AST.Constant('long',str(get_word_size()))
        alignment = get_word_size()
    elif isinstance(ast_type, AST.Struct):
        ast_type.show()
        if config.packing_scheme == SPS.PACT_COMPACT:
            num_bytes = 0
            alignment = 1
            for decl in ast_type.decls:
                decl_size, decl_alignment = get_size_and_alignment(decl)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
        elif config.packing_scheme == SPS.GCC_STD:
            num_bytes = 0
            alignment = 1
            for decl in ast_type.decls:
                decl_size, decl_alignment = get_size_and_alignment(decl)
                if num_bytes % decl_alignment != 0:
                    num_bytes += decl_alignment - (num_bytes % decl_alignment)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
            if num_bytes % alignment != 0:
                num_bytes += alignment - (num_bytes % alignment) 
        else:
            raise Exception("Unknown Packing Scheme")

        return AST.Constant('long',str(num_bytes)), alignment
    elif isinstance(ast_type, AST.TypeDecl):
        size, alignment = get_size_and_alignment(ast_type.type)
    elif isinstance(ast_type, AST.Typename):
        size, alignment = get_size_and_alignment(ast_type.type)
    elif isinstance(ast_type, AST.Union):
        size = None
        alignment = None
        for decl in ast_type.decls:
            decl_size, decl_alignment = get_size_and_alignment(decl)
            if (size is None) or (int(size.value) < int(decl_size.value)):
                size = decl_size
            if (alignment is None) or (alignment < decl_alignment):
                alignment = decl_alignment
    else:
        raise Exception('Unknown Type '+str(ast_type))

    return size, alignment
