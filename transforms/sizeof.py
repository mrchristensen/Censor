import pycparser.c_ast as AST
from cesk.limits import get_word_size, get_size, Struct_Packing_Scheme as SPS, config

#returns the size in bytes of the ast type, nested in an unsigned long constant
def get_size_ast(ast_type_node, env=None):
    size, _  = get_size_and_alignment(ast_type_node,env)
    return size

#returns size as an AST node and alignment as an in
def get_size_and_alignment(ast_type, env=None):
    if isinstance(ast_type, AST.ArrayDecl):
        size, alignment = get_size_and_alignment(ast_type.type,env)
        size = AST.BinaryOp('*',size,ast_type.dim)
    elif isinstance(ast_type, AST.Decl):
        size, alignment = get_size_and_alignment(ast_type.type,env)
    elif isinstance(ast_type, AST.FuncDecl):
        size = AST.Constant('long',1)
        alignment = 1 #do not know what to do exactly
    elif isinstance(ast_type, AST.IdentifierType):
        #TODO handle typedef'd Types
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
        decls = ast_type.decls
        if decls is None:
            if env is None:
                raise Exception("Environment needed to determine size of struct")
            struct_type_string = type(ast_type).__name__ + " " + ast_type.name
            decls = env.get_type(struct_type_string).decls
        if config.packing_scheme == SPS.PACT_COMPACT:
            num_bytes = 0
            alignment = 1
            for decl in decls:
                decl_size, decl_alignment = get_size_and_alignment(decl,env)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
        elif config.packing_scheme == SPS.GCC_STD:
            num_bytes = 0
            alignment = 1
            for decl in decls:
                decl_size, decl_alignment = get_size_and_alignment(decl,env)
                if num_bytes % decl_alignment != 0:
                    num_bytes += decl_alignment - (num_bytes % decl_alignment)
                num_bytes += int(decl_size.value)
                if alignment < decl_alignment:
                    alignment = decl_alignment
            if num_bytes % alignment != 0:
                num_bytes += alignment - (num_bytes % alignment) 
        else:
            raise Exception("Unknown Packing Scheme")

        size = AST.Constant('long',str(num_bytes))
    elif isinstance(ast_type, AST.TypeDecl):
        size, alignment = get_size_and_alignment(ast_type.type,env)
    elif isinstance(ast_type, AST.Typename):
        size, alignment = get_size_and_alignment(ast_type.type,env)
    elif isinstance(ast_type, AST.Union):
        if env is None:
            raise Exception("Environment needed to determine size of union")
        decls = ast_type.decls
        if decls is None:
            union_type_string = type(ast_type).__name__ + " " + ast_type.name
            decls = env.get_type(union_type_string).decls
        size = None
        alignment = None
        for decl in ast_type.decls:
            decl_size, decl_alignment = get_size_and_alignment(decl,env)
            if (size is None) or (int(size.value) < int(decl_size.value)):
                size = decl_size
            if (alignment is None) or (alignment < decl_alignment):
                alignment = decl_alignment
    else:
        raise Exception('Unknown Type '+str(ast_type))
    
    if config.packing_scheme == SPS.PACT_COMPACT:
        alignment = 1
    return size, alignment
