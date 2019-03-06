"""Functions to interpret c code directly"""
import logging
import pycparser.c_ast as AST
from transforms.sizeof import get_size_ast
from cesk.values import generate_constant_value, cast
from cesk.values.base_values import BaseInteger
from cesk.structures import (State, Ctrl, Envr, Kont, FrameAddress)
import cesk.linksearch as ls
import cesk.library_functions as lib_func
from cesk.exceptions import CESKException
logging.basicConfig(filename='logfile.txt', level=logging.DEBUG,
                    format='%(levelname)s: %(message)s', filemode='w')

def execute(state):
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states"""
    stmt = state.ctrl.stmt()
    obj_name = stmt.__class__.__name__
    if obj_name in implemented_nodes():
        states = handle(stmt, state)
        if not isinstance(states, set):
            states = {states}
        return states
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
    next_states = set()
    truth = value.get_truth_value()
    if True in truth:
        new_ctrl = Ctrl(stmt.iftrue)
        next_states.add(State(new_ctrl, state.envr,
                              state.stor, state.kont_addr))
    if False in truth:
        next_states.add(state.get_next())
    if next_states:
        return next_states
    raise CESKException("Value " + str(value) +
                        " has invalid truth values: " + str(truth))

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

def handle_FuncCall(stmt, state, address=None): # pylint: disable=invalid-name
    '''Handles FuncCalls'''
    if isinstance(stmt.name, AST.UnaryOp):
        logging.debug("FuncCall to %s", stmt.name)
        func_def_frame_addr = get_address(stmt.name, state)
        return func(stmt, state, func_def_frame_addr, address)

    logging.debug("FuncCall to %s", stmt.name.name)
    if stmt.name.name in dir(lib_func):
        args = []
        if stmt.args is not None:
            args = [get_value(val, state) for val in stmt.args.exprs]
        return getattr(lib_func, stmt.name.name)(state, args, address)
    elif stmt.name.name == "malloc":
        return state.get_next()
    else:
        func_def_frame_addr = state.envr.get_address(stmt.name.name)
        return func(stmt, state, func_def_frame_addr, address)

def func(stmt, state, func_def_frame_addr, address=None):
    '''handles most function calls delegated by handle_FuncCall'''
    if stmt.args is None:
        expr_list = []
    else:
        expr_list = stmt.args.exprs

    func_defs = state.stor.read(func_def_frame_addr)
    if isinstance(func_defs, set):
        func_defs = set([func_def.node for func_def in func_defs])
    else:
        func_defs = set([func_defs.node])
    return_states = set()
    for func_def in func_defs:
        if func_def.decl.type.args is None:
            param_list = []
        else:
            param_list = func_def.decl.type.args.params
        if len(expr_list) != len(param_list):
            raise Exception("Function " + func_def.decl.name +
                            " expected " +
                            str(len(param_list)) +
                            " parameters but received " +
                            str(len(expr_list)))
        return_states.add(func_helper(param_list, expr_list, func_def,
                                      state, address))
    return return_states

def func_helper(param_list, expr_list, func_def, state, address):
    '''Prepares the next_state from param_list and expr_list'''
    next_ctrl = Ctrl(0, func_def.body) # f_0
    next_envr = Envr(state) #calls allocf
    kont = Kont(state, address)
    kont_addr = Kont.allocK(state, next_ctrl, next_envr)
    state.stor.write_kont(kont_addr, kont) # stor = stor[a_k'->K]
    new_state = State(next_ctrl, next_envr, state.stor, kont_addr)

    for decl, expr in zip(param_list, expr_list): #add parameters to environment
        new_state = decl_helper(decl, new_state)
        new_address = new_state.envr.get_address(decl.name)
        value = get_value(expr, state)
        new_state.stor.write(new_address, value)

    return new_state


def handle_EmptyStatement(stmt, state): #pylint: disable=invalid-name
     #pylint: disable=unused-argument
    '''Handles EmptyStatement'''
    return state.get_next()

def handle_Decl(stmt, state):#pylint: disable=invalid-name
    '''Handles Decls'''
    logging.debug("Decl %s    %s", str(stmt.name), str(stmt.type))
    decl_helper(stmt, state)
    if stmt.init:
        address = state.envr.get_address(stmt.name)
        logging.debug("init %s", stmt.name)
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

def handle_Cast(stmt, state): #pylint: disable=invalid-name,unused-argument
    '''Handles Cast'''
    logging.debug('Cast')
    #is not evaluated becase the operator is not stored
    # anywhere so should not affect the program
    return state.get_next()

def handle_BinaryOp(stmt, state): #pylint: disable=invalid-name,unused-argument
    '''Handles BinaryOps'''
    logging.debug("BinaryOp")
    #is not evaluated becase the operator is not stored
    # anywhere so should not affect the program
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
        value = None
        if is_malloc(exp):
            value = malloc(exp, state)
        elif isinstance(exp, AST.FuncCall):
            return handle_FuncCall(exp, state, address)
        else:
            value = get_value(exp, state)
        logging.debug("Frame Address %s assigned to %s",
                      str(address), str(value))
        state.stor.write(address, value)
        return state.get_next()
    else:
        raise Exception(operator + " is not yet implemented")

def decl_helper(decl, state):
    """Maps the identifier to a new address and passes assignment part"""
    name = decl.name
    f_addr = state.envr.map_new_identifier(name)

    if (isinstance(decl.type, (AST.TypeDecl,
                               AST.PtrDecl))):
        if (isinstance(decl.type.type, AST.Struct)
                and isinstance(decl.type, AST.TypeDecl)):
            handle_decl_struct(decl.type.type, state, f_addr)
        else:
            size = []
            ls.get_sizes(decl.type, size)
            state.stor.allocM(f_addr, size)

            #the address is mapped then if additional space is need for
            # a struct handle decl struct manages it

    elif isinstance(decl.type, AST.ArrayDecl):
        data_address = handle_decl_array(decl.type, [], state, f_addr)
        logging.debug(" Mapped %s to %s", str(name), str(data_address))
        if decl.init:
            raise Exception("array init should be transformed")

    else:
        raise Exception("Declarations of " + str(decl.type) +
                        " are not yet implemented")

    return state

def handle_decl_array(array, list_of_sizes, state, f_addr):
    """Calculates size and allocates Array. Returns address of first item"""
    logging.debug('  Array Decl')
    if isinstance(array.type, AST.ArrayDecl):
        raise Exception("Multidim. arrays should be transformed to single")
    elif isinstance(array.type, (AST.TypeDecl, AST.PtrDecl)):
        if isinstance(array.dim, (AST.Constant, AST.ID)):
            value = get_value(array.dim, state)
            logging.debug("Array Size is %s", str(value))
            length = get_int_data(value)
        else:
            raise Exception("Unsupported ArrayDecl dimension "+str(array.dim))

        if length < 1:
            raise Exception("Non-positive Array Sizes are not supported")

        if length == 0:
            # TODO
            raise NotImplementedError("Arrays of size 0 not implemented")
        if isinstance(array.type.type, (AST.Struct, AST.Union)):
            # TODO handle Union
            list_of_sizes = []
            ls.get_sizes(array.type, list_of_sizes)
            data_address = state.stor.allocM(f_addr, list_of_sizes, length)
        else:
            constant = get_size_ast(array.type)
            size = generate_constant_value(constant.value, constant.type).data
            data_address = state.stor.allocM(f_addr, [size], length)
        #Allocated block: passing back the Array object that points to block
        return data_address
    else:
        raise Exception("Declarations of " + str(array.type) +
                        " are not yet implemented")

def handle_decl_struct(struct, state, f_addr):
    """Handles struct declaration"""
    list_of_sizes = []
    ls.get_sizes(struct, list_of_sizes)
    data_address = state.stor.allocM(f_addr, list_of_sizes)
    return data_address

def handle_UnaryOp(stmt, state): # pylint: disable=invalid-name,unused-argument
    """decodes and evaluates unary_ops"""
    return state.get_next()

def get_int_data(integer):
    """ When a store is weak determines what integer value to use for size,
        It chooses the smalles value """
    if isinstance(integer, set):
        smallest = None
        for item in integer:
            if isinstance(item.data, int):
                if smallest is None or smallest > item.data:
                    smallest = item.data
        if smallest is None:
            smallest = 1
        return smallest
    if isinstance(integer, BaseInteger):
        return integer.data
    raise CESKException("Integer was expected")

def handle_Return(stmt, state):# pylint: disable=invalid-name
    """satisfies kont"""
    exp = stmt.expr
    value = None
    if exp: #exp is always an ID because of transforms
        address = state.envr.get_address(exp.name)
        value = state.stor.read(address) #safe
    #TODO invoke a list rather then a single call
    ret_set = set()
    for kont in state.get_kont():
        k = kont.invoke(state, value)
        if k is not None:
            ret_set.add(k)
    return ret_set

def get_value(stmt, state): #pylint: disable=too-many-return-statements
    """ get value for simple id's constants or references and casts of them """
    if isinstance(stmt, AST.Constant):
        value = generate_constant_value(stmt.value, stmt.type)
        return value
    elif isinstance(stmt, AST.ID):
        return state.stor.read(get_address(stmt, state))
    elif isinstance(stmt, AST.Cast):
        val = get_value(stmt.expr, state)
        val = cast(val, stmt.to_type, state)
        return val
    elif isinstance(stmt, AST.BinaryOp):
        left = get_value(stmt.left, state)
        right = get_value(stmt.right, state)
        logging.debug("\tBinop: %s %s %s", str(left), stmt.op, str(right))
        return left.perform_operation(stmt.op, right)
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '&':
        address = get_address(stmt.expr, state)
        if isinstance(address, FrameAddress):
            return state.stor.fa2ptr(address)
        return address
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '*':
        return state.stor.read(get_address(stmt, state))
    elif isinstance(stmt, AST.FuncCall):
        raise Exception("Cannot get value from " + stmt.name.name + "()")
    else:
        raise Exception("Cannot get value from " + stmt.__class__.__name__)

def get_address(reference, state):
    # pylint: disable=too-many-branches
    """get_address"""
    if isinstance(reference, AST.ID):
        ident = reference
        while not isinstance(ident, str):
            ident = ident.name
        if ident not in state.envr:
            checked_decl = ls.check_for_implicit_decl(ident)
            if checked_decl is not None:
                logging.debug("Found implicit decl: %s", checked_decl.name)
                decl_helper(checked_decl, state)
        return state.envr.get_address(ident)

    elif isinstance(reference, AST.ArrayRef):
        raise CESKException("ArrayRef should be transformed")

    elif isinstance(reference, AST.UnaryOp):
        unary_op = reference
        if unary_op.op == "*":
            name = unary_op.expr
            if isinstance(name, AST.ID):
                pointer = state.envr.get_address(name)
                return state.stor.read(pointer) #safe
            elif isinstance(name, AST.UnaryOp) and name.op == "&":
                return get_address(name.expr, state) #They cancel out
            elif (isinstance(name, AST.Cast) and
                  isinstance(name.to_type, AST.PtrDecl)):
                temp = get_address(name.expr, state)
                temp = state.stor.read(temp)
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
        raise CESKException("Unsupported lvalue " + str(reference))

def malloc(exp, state):
    """ Calls malloc and evaluates the cast """
    if isinstance(exp, AST.Cast):
        malloc_call = exp
        while isinstance(malloc_call, AST.Cast): #handle nested cast
            malloc_type = malloc_call.to_type
            malloc_call = malloc_call.expr

        if isinstance(malloc_type, AST.Typename):
            malloc_type = malloc_type.type.type
        else:
            malloc_type = malloc_type.type
        size_list = []
        ls.get_sizes(malloc_type, size_list)
        malloc_result = malloc_helper(malloc_call, state, size_list)
        malloc_result = cast(malloc_result, exp.to_type, state)
    else:
        raise CESKException("Malloc appeared without a cast")
        #malloc_result = malloc(exp, state, [1])
    return malloc_result

def malloc_helper(stmt, state, break_up_list):
    '''performs malloc returns CESKPointer to allocated memory'''
    param = stmt.args.exprs[0]
    if isinstance(param, AST.Constant):
        val = generate_constant_value(param.value, param.type)
        num_bytes = val.data
    else:
        num_bytes = get_int_data(get_value(param, state))
    logging.info("Malloc(%d) with structure: %s", num_bytes, str(break_up_list))
    heap_pointer = state.stor.allocH(state)

    block_size = sum(break_up_list)
    num_blocks = num_bytes // block_size
    leftover = num_bytes % block_size
    if num_blocks == 0:
        pointer = state.stor.allocM(heap_pointer, [num_bytes])
    else:
        pointer = state.stor.allocM(heap_pointer, break_up_list,
                                    num_blocks, leftover)
    return pointer

def is_malloc(stmt):
    """ check to see if a function is a call to malloc """
    while isinstance(stmt, AST.Cast):
        stmt = stmt.expr
    return (isinstance(stmt, AST.FuncCall) and
            stmt.name.name == 'malloc')
