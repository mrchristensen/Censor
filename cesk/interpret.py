"""Functions to interpret c code directly"""
import logging
import pycparser.c_ast as AST
from transforms.sizeof import get_size_ast
from cesk.values import generate_constant_value, cast
import cesk.linksearch as ls
logging.basicConfig(filename='logfile.txt', level=logging.DEBUG,
                    format='%(levelname)s: %(message)s', filemode='w')

def execute(state):
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states"""
    stmt = state.ctrl.stmt()
    obj_name = stmt.__class__.__name__
    if obj_name in implemented_nodes():
        return handle(stmt, state)
    elif obj_name in should_be_transformed_nodes():
        raise Exception(obj_name + " should be transformed but wasn't")
    elif obj_name in todo_implement_nodes():
        raise Exception(obj_name + " not yet implemented")
    elif obj_name in should_not_find():
        raise Exception(should_not_find()[obj_name])

    raise ValueError("Unknown C AST object type: {0}".format(stmt))

def handle(stmt, state):
    '''Handles all implemented nodes'''
    method_name = "handle_" + stmt.__class__.__name__
    handle_node = globals()[method_name]
    return handle_node(stmt, state)

def handle_Label(stmt, state): # pylint: disable=invalid-name
    '''Handles Labels'''
    new_ctrl = Ctrl(stmt.stmt)
    return State(new_ctrl, state.envr, state.stor, state.kont_addr)

def handle_If(stmt, state): # pylint: disable=invalid-name
    '''Handles Ifs'''
    logging.debug("If")
    value = get_value(stmt.cond, state)
    if value.get_truth_value():
        new_ctrl = Ctrl(stmt.iftrue)
        return State(new_ctrl, state.envr, state.stor, state.kont_addr)
    elif stmt.iffalse:
        raise Exception("False Branch should be transformed")
    else:
        return state.get_next()

def handle_ID(stmt, state): # pylint: disable=invalid-name
    '''Handles IDs'''
    logging.debug("ID %s", stmt.name)
    return state.get_next()

def handle_Goto(stmt, state): # pylint: disable=invalid-name
    '''Handles Gotos'''
    logging.debug('Goto %s', stmt.name)
    body = ls.LinkSearch.label_lut[stmt.name]
    while not isinstance(body, AST.Compound):
        index = ls.LinkSearch.index_lut[body]
        body = ls.LinkSearch.parent_lut[body]
    new_ctrl = Ctrl(index, body)
    return State(new_ctrl, state.envr, state.stor, state.kont_addr)

def handle_FuncCall(stmt, state, address = None): # pylint: disable=invalid-name
    '''Handles FuncCalls'''
    logging.debug("FuncCall")
    if stmt.name.name == "printf":
        return printf(stmt, state)
    elif stmt.name.name == "malloc":
        return state.get_next()
    elif stmt.name.name == "free":
        return state.get_next()
    else:
        return func(stmt, state, address)

def handle_EmptyStatement(stmt, state): #pylint: disable=invalid-name
     #pylint: disable=unused-argument
    '''Handles EmptyStatement'''
    return state.get_next()

def handle_Decl(stmt, state):#pylint: disable=invalid-name
    '''Handles Decls'''
    logging.debug("Decl %s    %s", str(stmt.name), str(stmt.type))
    decl_helper(stmt, state)
    if stmt.init:
        frame_address = state.envr.get_frame_address(stmt.name)
        address = state.envr.get_address(frame_address)
        return assignment_helper("=", address, stmt.init, state)
    else:
        return state.get_next()

def handle_Constant(stmt, state): #pylint: disable=invalid-name
    '''Handles Constants'''
    logging.debug("Constant %s", stmt.type)
    return state.get_next()

def handle_Compound(stmt, state): #pylint: disable=invalid-name
    '''Handles Compounds'''
    logging.debug("Compound")
    if stmt.block_items is None:
        return state.get_next()
    else:
        new_ctrl = Ctrl(0, stmt)
        new_envr = state.envr
        ls.LinkSearch.envr_lut[stmt] = new_envr #save to table for goto lookup
        return State(new_ctrl, new_envr, state.stor, state.kont_addr)

def handle_Cast(stmt, state): #pylint: disable=invalid-name
    '''Handles Cast'''
    logging.debug('Cast')
    return state.get_next()

def handle_BinaryOp(stmt, state): #pylint: disable=invalid-name
    '''Handles BinaryOps'''
    logging.debug("BinaryOp")
    return state.get_next()

def handle_Assignment(stmt, state): #pylint: disable=invalid-name
    '''Handles Assignments'''
    logging.debug("Assignment")
    rexp = stmt.rvalue
    laddress = get_address(stmt.lvalue, state)
    return assignment_helper(stmt.op, laddress, rexp, state)

def implemented_nodes():
    """ Return set of nodes that the interpreter currently implements.
    """
    return {
        'Assignment',
        'BinaryOp',
        'Cast',
        'Compound',
        'Constant',
        'Decl',
        'EmptyStatement',
        'FuncCall',
        'Goto',
        'ID',
        'If',
        'Label',
        'Return',
        'UnaryOp'
    }

def should_not_find():
    """ Return map of nodes that the interpreter shouldn't find.
    Includes reason why it should not be found
    """
    return {
        'ArrayDecl':'ArrayDecl should have been found as a child of Decl',
        'ExprList':'ExprList should only appear inside FuncCall/Decl',
        'FileAST':'FileAST is not a valid control point',
        'FuncDecl':'FuncDecl out of Global scope',
        'FuncDef':'FuncDef out of Global scope',
        'IdentifierType':'IdentifierType should not appear',
        'PtrDecl':'PtrDecl should not appear outside of a decl',
        'TypeDecl':'TypeDecl should have been found as child of Decl',
        'Typename':'Typename should appear only nested inside another type'
    }

def todo_implement_nodes():
    """ Return set of nodes that were marked as '#todo implement' at some point
    """
    # TODO these of course :)
    return {
        'CompoundLiteral',
        'EllipsisParam',
        'Enum',
        'Enumerator',
        'EnumeratorList',
        'For',
        'NamedInitializer',
        'ParamList',
        'Struct',
        'Union',
        'Pragma'
    }

def should_be_transformed_nodes():
    """ Return set of nodes that should have been removed by transforms.
    """
    return {
        'ArrayRef',
        'Break',
        'Case',
        'Continue',
        'DeclList',
        'Default',
        'DoWhile',
        'InitList',
        'StructRef',
        'Switch',
        'TernaryOp',
        'Typedef',
        'While'
    }

def assignment_helper(operator, address, exp, state):
    """Creates continuation to evaluate exp and assigns resulting value to the
    given address"""
    #pylint: disable=too-many-function-args
    if operator == '=':
        if isinstance(exp, AST.FuncCall) and not is_malloc(exp):
            return handle_FuncCall(exp, state, address)
        elif (is_malloc(exp) or (isinstance(exp, AST.Cast) and
              is_malloc(exp.expr))):
            return malloc_helper(exp, state, address)
        else:
            value = get_value(exp, state)
            state.stor.write(address, value)
            return state.get_next()
    else:
        raise Exception(operator + " is not yet implemented")
    return State(new_ctrl, state.envr, state.stor, new_kont)

def decl_helper(decl, state):
    """Maps the identifier to a new address and passes assignment part"""
    name = decl.name
    if state.envr.is_localy_defined(name):
        logging.error("redefinition of %s", name)

    elif (isinstance(decl.type, (AST.TypeDecl,
                                 AST.PtrDecl))):
        if (isinstance(decl.type.type, AST.Struct)
                and isinstance(decl.type, AST.TypeDecl)):
            ref_address = handle_decl_struct(decl.type.type, state)
        else:
            size_ast = get_size_ast(decl.type)
            size = generate_constant_value(size_ast.value, size_ast.type).data
            ref_address = state.stor.get_next_address(size)

        frame_address = state.envr.get_frame_address(name)
        state.envr.map_new_identifier(frame_address, ref_address)
            #the address is mapped then if additional space is need for
            # a struct handle decl struct manages it

    elif isinstance(decl.type, AST.ArrayDecl):
        data_address = handle_decl_array(decl.type, [], state)
        frame_address = state.envr.get_frame_address(decl.name)
        state.envr.map_new_identifier(frame_address, data_address)
        logging.debug(" Mapped %s to %s", str(name), str(data_address))
        if decl.init:
            raise Exception("array init should be transformed")

    else:
        raise Exception("Declarations of " + str(decl.type) +
                        " are not yet implemented")

    return state
def malloc_helper(exp, state, address):
    if isinstance(exp, AST.Cast):
        malloc_result = malloc(exp.expr, state)
        malloc_result = cast(malloc_result, exp.to_type, state)
    else:
        malloc_result = malloc(exp, state) # if malloc is assigned to a void*
    state.stor.write(address, malloc_result)
    return state.get_next()
def handle_decl_array(array, list_of_sizes, state):
    """Calculates size and allocates Array. Returns address of first item"""
    logging.debug('  Array Decl')
    if isinstance(array.type, AST.ArrayDecl):
        raise Exception("Multidim. arrays should be transformed to single")
    elif isinstance(array.type, AST.TypeDecl):
        if isinstance(array.dim, AST.Constant):
            size = generate_constant_value(array.dim.value, array.dim.type).data
        elif isinstance(array.dim, AST.ID):
            size = get_address(array.dim, state).dereference().data #safe
        else:
            raise Exception("Unsupported ArrayDecl dimension "+str(array.dim))

        if size < 1:
            raise Exception("Non-positive Array Sizes are not supported")

        length = size #reduce(lambda x, y: x*y, list_of_sizes)
        if length == 0:
            # TODO
            raise NotImplementedError("Arrays of size 0 not implemented")
        if isinstance(array.type.type, (AST.Struct, AST.Union)):
            # TODO handle Union
            list_of_sizes = []
            alignment = ls.get_sizes(array, list_of_sizes, state) #pylint: disable=unused-variable
            data_address = state.stor.allocate_nonuniform_block(list_of_sizes)
        else:
            constant = get_size_ast(array.type)
            size = generate_constant_value(constant.value, constant.type).data
            data_address = state.stor.allocate_block(length, size)
        #Allocated block: passing back the Array object that points to block
        return data_address
    else:
        raise Exception("Declarations of " + str(array.type) +
                        " are not yet implemented")
def handle_decl_struct(struct, state):
    """Handles struct declaration"""
    list_of_sizes = []
    alignment = ls.get_sizes(struct, list_of_sizes, state) #pylint: disable=unused-variable
    data_address = state.stor.allocate_nonuniform_block(list_of_sizes)
    return data_address

def handle_UnaryOp(stmt, state): # pylint: disable=invalid-name
    """decodes and evaluates unary_ops"""
    opr = stmt.op
    expr = stmt.expr
    logging.debug("UnaryOp %s", opr)
    # note: may reference for reads/writes
    # if opr == "&":
    #     value = get_address(expr, state)
    # elif opr == "*":
    #     value = get_value(expr, state)
    return state.get_next()

def printf(stmt, state):
    '''performs printf'''
    value_array = []
    for i in range(1, len(stmt.args.exprs)):
        expr = stmt.args.exprs[i]
        if isinstance(expr, AST.Constant):
            value = generate_constant_value(expr.value, expr.type)
        else:
            value = get_address(expr, state).dereference()
        value_array.append(value.data)
    if isinstance(stmt.args.exprs[0], AST.Constant):
        print_string = stmt.args.exprs[0].value % tuple(value_array)
    elif isinstance(stmt.args.exprs[0], AST.Cast):
        print_string = stmt.args.exprs[0].expr.value % tuple(value_array)
    else:
        raise Exception("printf does not know how to handle "
                        +str(stmt.args.exprs[0]))
    print_string = print_string[1:][:-1] #drop quotes
    print_string = print_string.replace("\\n", "\n")
    print(print_string, end ="") #convert newlines
    return state.get_next()
def malloc(stmt, state):
    '''performs malloc'''
    param = stmt.args.exprs[0]
    if isinstance(stmt.args.exprs[0], AST.Cast):
        param = stmt.args.exprs[0].expr
    if isinstance(param, AST.Constant):
        length = int(param.value, 0)
    else:
        length = get_address(param, state).dereference().data
    logging.info("Malloc %d", length)
    pointer = state.stor.get_next_address(length)
    # assume malloc is always in an assignment and/or cast
    return pointer

def func(stmt, state, address = None):
    '''handles most function calls delegated by handle_FuncCall'''
    if stmt.name.name not in ls.LinkSearch.function_lut:
        raise Exception("Undefined reference to " + stmt.name.name)
    else:
        logging.debug(" Calling Function: %s", stmt.name.name)
        func_def = ls.LinkSearch.function_lut[stmt.name.name]
        if func_def.decl.type.args is None:
            param_list = []
        else:
            param_list = func_def.decl.type.args.params
        if stmt.args is None:
            expr_list = []
        else:
            expr_list = stmt.args.exprs
        if len(expr_list) != len(param_list):
            raise Exception("Function " + stmt.name.name +
                            " expected " +
                            str(len(param_list)) +
                            " parameters but received " +
                            str(len(expr_list)))
    return func_helper(param_list, expr_list, func_def, state, address)

def func_helper(param_list, expr_list, func_def, state, address):
    '''Prepares the next_state from param_list and expr_list'''
    next_ctrl = Ctrl(0, func_def.body) # f_0
    next_envr = Envr() # allocf
    kont = Kont(state, address)
    kont_addr = Kont.allocK()
    state.stor.write_kont(kont_addr, kont) # stor = stor[a_k'->K]
    new_state = State(next_ctrl, next_envr, state.stor, kont_addr)
    for decl, expr in zip(param_list, expr_list):
        new_state = decl_helper(decl, new_state)
        frame_address = new_state.envr.get_frame_address(decl.name)
        new_address = new_state.envr.get_address(frame_address)

        value = get_value(expr, state)
        new_state.stor.write(new_address, value)
    return new_state

def handle_Return(stmt, state):# pylint: disable=invalid-name
    """satisfies kont"""
    exp = stmt.expr
    value = None
    if exp:
        frame_address = state.envr.get_frame_address(exp.name)
        address = state.envr.get_address(frame_address)
        value = address.dereference() #safe
    return state.get_kont().invoke(state, value)
    # return State(Ctrl(exp), state.envr, state.stor, returnable_kont)

def get_value(stmt, state):
    """ get value for simple id's constants or references and casts of them """
    if isinstance(stmt, AST.Constant):
        value = generate_constant_value(stmt.value, stmt.type)
        return value
    elif isinstance(stmt, AST.ID):
        return get_address(stmt, state).dereference()
    elif isinstance(stmt, AST.Cast):
        val = get_value(stmt.expr, state)
        return cast(val, stmt.to_type, state)
    elif isinstance(stmt, AST.BinaryOp):
        left = get_value(stmt.left, state)
        right = get_value(stmt.right, state)
        return left.perform_operation(stmt.op, right)
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '&':
        return get_address(stmt.expr, state)
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '*':
        return get_address(stmt, state).dereference()
    elif isinstance(stmt, AST.FuncCall):
        raise Exception("Cannot get value from " + stmt.name.name + "()")
    else:
        raise Exception("Cannot get value from " + stmt.__class__.__name__)

def get_address(reference, state):
    # pylint: disable=too-many-branches
    """get_address"""
    if isinstance(reference, AST.ID):
        ident = reference
        frame_address = state.envr.get_frame_address(ident)
        if not state.envr.is_localy_defined(frame_address):
            checked_decl = check_for_implicit_decl(ident)
            if checked_decl is not None:
                logging.debug("Found implicit decl: %s", checked_decl.name)
                decl_helper(checked_decl, state)
        address = state.envr.get_address(frame_address)
        return address

    elif isinstance(reference, AST.ArrayRef):
        raise Exception("ArrayRef should be transformed")

    elif isinstance(reference, AST.UnaryOp):
        unary_op = reference
        if unary_op.op == "*":
            name = unary_op.expr
            if isinstance(name, AST.ID):
                frame_address = state.envr.get_frame_address(name)
                pointer = state.envr.get_address(frame_address)
                return pointer.dereference() #safe
            elif isinstance(name, AST.UnaryOp) and name.op == "&":
                return get_address(name.expr, state) #They cancel out
            elif (isinstance(name, AST.Cast) and
                  isinstance(name.to_type, AST.PtrDecl)):
                temp = get_address(name.expr, state)
                temp = temp.dereference()
                address = cast(temp, name.to_type, state)
                return address
            else:
                raise Exception("Unknown Case for UnaryOp, nested part is "
                                + str(name))
        else:
            raise Exception("Unsupported UnaryOp lvalue in assignment: "
                            + unary_op.op)

    elif isinstance(reference, AST.StructRef):
        raise Exception("StructRef should be transformed to pointer arithmetic")
    elif isinstance(reference, AST.Struct):
        # TODO
        raise NotImplementedError("Access to struct as a whole undefined still")
    else:
        raise Exception("Unsupported lvalue " + str(reference))

def check_for_implicit_decl(ident):
    """See continuation edge case 12. Determine if a implicit decl is needed"""
    compound = None
    parent = ls.LinkSearch.parent_lut[ident]
    while True:
        if isinstance(parent, AST.Compound):
            compound = parent
            break
        if parent not in ls.LinkSearch.parent_lut:
            break
        parent = ls.LinkSearch.parent_lut[parent]

    if compound is not None:
        if compound in ls.LinkSearch.envr_lut:
            comp_envr = ls.LinkSearch.envr_lut[compound]
            if comp_envr.is_localy_defined(ident.name):
                return None
        if compound in ls.LinkSearch.scope_decl_lut:
            for decl in ls.LinkSearch.scope_decl_lut[compound]:
                if decl.name == ident.name:
                    return decl
    return None

def is_malloc(stmt):
    return (isinstance(stmt, AST.FuncCall) and
            stmt.name.name == 'malloc')

# imports are down here to allow for circular dependencies between
# structures.py and interpret.py
from cesk.structures import (State, Ctrl, Envr, Kont) # pylint: disable=wrong-import-position
