import pycparser.c_ast as AST
from cesk.limits import get_word_size, get_size, Struct_Packing_Scheme as SPS, config

#returns size as an AST node and alignment as an in
def get_size_and_alignment(ast_type):
    if isinstance(ast_type, AST.ArrayDecl):
        size, alignment = get_size_and_alignment(ast_type.type)
        size = AST.BinaryOp('*',size,ast_type.dim)
    elif isinstance(ast_type, AST.FuncDecl):

    elif isinstance(ast_type, AST.IdentifierType):
        num_bytes = get_size(ast_type.names)
        size = AST.Constant('unsigned long',str(num_bytes))
        if num_bytes < get_word_size():
            alignment = num_bytes
        else:
            alignment = get_word_size()
    elif isinstance(ast_type, AST.PtrDecl):
        size = AST.Constant('unsigned long',str(get_word_size()))
        alignment = get_word_size()
    elif isinstance(ast_type, AST.Struct):
        if config.packing_scheme == SPS.PACT_COMPACT:
            size = 0
            alignment = 1
            for decl in ast_type.decls:
                decl_size, decl_alignment = get_size_and_alignment(decl)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
        elif config.packing_scheme == SPS.GCC_STD:
            size = 0
            alignment = 1
            for decl in ast_type.decls:
                decl_size, decl_alignment = get_size_and_alignment(decl)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
        else:
            raise Exception("Unknown Packing Scheme")

        num_bytes = 0
        last_aligned = 0
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
