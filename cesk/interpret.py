"""Functions to interpret c code directly"""
import logging
import pycparser.c_ast as AST
<<<<<<< HEAD
from cesk.values import generate_constant_value, cast
from cesk.values.base_values import BaseInteger
from cesk.structures import (State, Ctrl, Envr, Kont, FrameAddress)
=======
from transforms.sizeof import get_size_ast
from cesk.values import generate_constant_value, cast, Integer
from cesk.structures import State, Ctrl, Envr, Kont, SegFault
>>>>>>> Setjmp+Longjmp
import cesk.linksearch as ls
import cesk.library_functions as lib_func
from cesk.exceptions import CESKException
logging.basicConfig(filename='logfile.txt', level=logging.DEBUG,
                    format='%(levelname)s: %(message)s', filemode='w')

def execute(state):
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states, and a set of error strings if an error occured"""
    stmt = state.ctrl.stmt()
    obj_name = stmt.__class__.__name__
    if obj_name in implemented_nodes():
        states, errors = handle(stmt, state)
        if not isinstance(states, set):
            raise Exception("state should be in set")
        return states, errors
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
    return {State(new_ctrl, state.envr, state.stor, state.kont_addr)}, {}

def handle_If(stmt, state): # pylint: disable=invalid-name
    '''Handles Ifs'''
    logging.debug("If")
    value, errors = get_value(stmt.cond, state)
    next_states = set()
    truth = value.get_truth_value()
    if True in truth:
        new_ctrl = Ctrl(stmt.iftrue)
        next_states.add(State(new_ctrl, state.envr,
                              state.stor, state.kont_addr))
    if False in truth:
        next_states.add(state.get_next())

    if next_states:
        return next_states, errors
    raise CESKException("Value " + str(value) +
                        " has invalid truth values: " + str(truth))

def handle_ID(stmt, state): # pylint: disable=invalid-name
    '''Handles IDs'''
    logging.debug("ID %s", stmt.name)
    return {state.get_next()}, set()

def handle_Goto(stmt, state): # pylint: disable=invalid-name
    '''Handles Gotos'''
    logging.debug('Goto %s', stmt.name)
    body = ls.LinkSearch.label_lut[stmt.name]
    logging.debug(body)
    while not isinstance(body, AST.Compound):
        index = ls.LinkSearch.index_lut[body]
        body = ls.LinkSearch.parent_lut[body]
    new_ctrl = Ctrl(index, body)
    return {State(new_ctrl, state.envr, state.stor, state.kont_addr)}, {}

def handle_FuncCall(stmt, state, address=None): # pylint: disable=invalid-name
    '''Handles FuncCalls'''
    if isinstance(stmt.name, AST.UnaryOp):
        logging.debug("FuncCall to %s", stmt.name)
        func_def_frame_addr, _ = get_address(stmt.name, state)
        return func(stmt, state, func_def_frame_addr, address)

    logging.debug("FuncCall to %s", stmt.name.name)
    if stmt.name.name in dir(lib_func):
        args = []
        error_states = set()
        if stmt.args is not None:
            arguments = [get_value(val, state) for val in stmt.args.exprs]
            for arg, errs in arguments:
                args.append(arg)
                error_states.update(errs)
        results, errs = getattr(lib_func, stmt.name.name)(state, args, address)
        error_states.update(errs)
        return results, error_states
    elif stmt.name.name == "malloc":
        return {state.get_next()}, set()
    else:
        func_def_frame_addr = state.envr.get_address(stmt.name.name)
        if func_def_frame_addr is None:
            return {state.get_next()}, set()
        else: 
            return func(stmt, state, func_def_frame_addr, address)

def func(stmt, state, func_def_frame_addr, address=None):
    '''handles most function calls delegated by handle_FuncCall'''
    if stmt.args is None:
        expr_list = []
        return state.get_next()
    elif stmt.name.name == "free":
        return state.get_next()
    elif stmt.name.name == "setjmp":
        return setjmp(stmt, state, address)
    elif stmt.name.name == "longjmp":
        return longjmp(stmt, state)
    else:
        expr_list = stmt.args.exprs

    func_defs, errors = state.stor.read(func_def_frame_addr)
    if isinstance(func_defs, set):
        func_defs = set([func_def.node for func_def in func_defs])
    else:
        func_defs = set([func_defs.node])
    return_states = set()
    errors = set()
    for func_def in func_defs:
        if func_def.decl.type.args is None:
            param_list = []
        else:
            param_list = func_def.decl.type.args.params
        if len(expr_list) != len(param_list):
            raise CESKException("Function " + func_def.decl.name +
                                " expected " +
                                str(len(param_list)) +
                                " parameters but received " +
                                str(len(expr_list)))
        state, errs = func_helper(zip(param_list, expr_list), func_def,
                                  state, address)
        return_states.add(state)
        errors.update(errs)
    return return_states, errors

def func_helper(params, func_def, state, ret_address):#pylint: disable=too-many-locals
    '''Prepares the next_state from param_list and expr_list'''
    next_ctrl = Ctrl(0, func_def.body) # f_0
    func_name = ls.LinkSearch.func_name_lut[func_def] #necessary for func ptrs
    next_envr = Envr(func_name, state.ctrl) #calls allocf
    kont = Kont(state, ret_address)
    kont_addr = Kont.allocK(state, next_ctrl, next_envr)
    state.stor.write_kont(kont_addr, kont) # stor = stor[a_k'->K]
    new_state = State(next_ctrl, next_envr, state.stor, kont_addr)

    errors = set()
    for decl, expr in params: #add parameters to environment
        new_address = decl_helper(decl, new_state)
        value, errs = get_value(expr, state)
        errors.update(errs)
        errs = new_state.stor.write(new_address, value)
        errors.update(errs)

    return new_state, errors


def setjmp(stmt, state, address):
    '''Resolves setjmp by storing a Kont in the setjmp'''
    new_buf_name = AST.UnaryOp('*',stmt.args.exprs[0])
    buf_name = stmt.args.exprs[0]
    buf_name = new_buf_name
    buf_addr = get_address(buf_name, state)
    jmp_buf = Kont.allocK()
    state.stor.write_kont(jmp_buf, Kont(state, address))

    # return 0
    if address:
        state.stor.write(address, Integer(0, 'int'))

    return assignment_helper('=', buf_addr, AST.Constant('int', str(jmp_buf)), state)

def longjmp(stmt, state):
    '''Resolves longjmp by restoring the kont in jmp_buf'''
    buf_val = get_value(stmt.args.exprs[0], state)
    kont = state.stor.read_kont(buf_val.data)

    val = get_value(stmt.args.exprs[1], state)
    if val.data == 0:
        val = Integer(1, 'int')
    return kont.invoke(state, val)

def handle_EmptyStatement(stmt, state): #pylint: disable=invalid-name
     #pylint: disable=unused-argument
    '''Handles EmptyStatement'''
    return {state.get_next()}, set()

def handle_Decl(stmt, state):#pylint: disable=invalid-name
    '''Handles Decls'''
    logging.debug("Decl %s", str(stmt.name))
    address = decl_helper(stmt, state)
    if stmt.init:
        logging.debug("\tinit %s", stmt.name)
        return assignment_helper("=", address, stmt.init, state)
    else:
        return {state.get_next()}, set()

def handle_Constant(stmt, state): #pylint: disable=invalid-name
    '''Handles Constants'''
    logging.debug("Constant %s", stmt.type)
    return {state.get_next()}, set()

def handle_Compound(stmt, state): #pylint: disable=invalid-name
    '''Handles Compounds'''
    logging.debug("Compound")
    if stmt.block_items is None:
        return {state.get_next()}, set()
    else:
        new_ctrl = Ctrl(0, stmt)
        new_envr = state.envr
        ls.LinkSearch.envr_lut[stmt] = new_envr #save to table for goto lookup
        return {State(new_ctrl, new_envr, state.stor, state.kont_addr)}, set()

def handle_Cast(stmt, state): #pylint: disable=invalid-name,unused-argument
    '''Handles Cast'''
    logging.debug('Cast')
    #is not evaluated becase the operator is not stored
    # anywhere so should not affect the program
    return {state.get_next()}, set()

def handle_BinaryOp(stmt, state): #pylint: disable=invalid-name,unused-argument
    '''Handles BinaryOps'''
    logging.debug("BinaryOp")
    #is not evaluated becase the operator is not stored
    # anywhere so should not affect the program
    return {state.get_next()}, set()

def handle_Assignment(stmt, state): #pylint: disable=invalid-name
    '''Handles Assignments'''
    logging.debug("Assignment")
    rexp = stmt.rvalue
    laddress, errors = get_address(stmt.lvalue, state)
    states, errs = assignment_helper(stmt.op, laddress, rexp, state)
    errors.update(errs)
    return states, errors

def handle_UnaryOp(stmt, state): # pylint: disable=invalid-name,unused-argument
    """decodes and evaluates unary_ops"""
    return {state.get_next()}, set()

def handle_Return(stmt, state):# pylint: disable=invalid-name
    """satisfies kont"""
    logging.debug("Return")
    exp = stmt.expr
    value = None
    errors = set()
    if exp: #exp is always an ID because of transforms
        address = state.envr.get_address(exp.name)
        value, errors = state.stor.read(address) #safe
    ret_set = set()
    errors = set()
    for kont in state.get_kont():
        next_states, errs = kont.invoke(state, value)
        ret_set.update(next_states)
        errors.update(errs)
    return ret_set, errors

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
        errors = set()
        if is_malloc(exp):
            value = malloc(exp, state)
        elif isinstance(exp, AST.FuncCall):
            return handle_FuncCall(exp, state, address)
        else:
            value, errs = get_value(exp, state)
            errors.update(errs)

        errs = state.stor.write(address, value)
        errors.update(errs)
        return {state.get_next()}, errors
    else:
        raise CESKException(operator + " is not yet implemented")

def decl_helper(decl, state):
    """Maps the identifier to a new address and passes assignment part"""
    name = decl.name
    f_addr = state.envr.map_new_identifier(name)

    length = 1
    size = []
    if isinstance(decl.type, AST.ArrayDecl):
        length = get_array_length(decl.type, state)
        ls.get_sizes(decl.type.type, size)
        if decl.init:
            raise CESKException("array init should be transformed")
    else:
        ls.get_sizes(decl.type, size)

    state.stor.allocM(f_addr, size, length)
    return f_addr

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
        if isinstance(integer.data, int):
            return integer.data
        return 1 #could make more versitile
    raise CESKException("Integer was expected")

def get_array_length(array, state):
    """Calculates size and allocates Array. Returns address of first item"""
    logging.debug('  Array Decl')
    if isinstance(array.type, AST.ArrayDecl):
        raise CESKException("Multidim. arrays should be transformed to single")
    elif isinstance(array.type, (AST.TypeDecl, AST.PtrDecl)):
        if isinstance(array.dim, (AST.Constant, AST.ID)):
            value, _ = get_value(array.dim, state)
            #never should get an err when reading an id
            length = get_int_data(value) #support for abstract type
        else:
            raise CESKException("Unsupported Array dimension "+str(array.dim))

        if length < 1:
            raise CESKException("Non-positive Array Sizes are not supported")
            #TODO could implement arrays of size 0

        return length
    else:
        raise CESKException("Declarations of " + str(array.type) +
                            " are not yet implemented")

def get_value(stmt, state): #pylint: disable=too-many-return-statements
    """ get value for simple id's constants or references and casts of them """
    if isinstance(stmt, AST.Constant):
        value = generate_constant_value(stmt.value, stmt.type)
        return value, set()
    elif isinstance(stmt, AST.ID):
        return state.stor.read(get_address(stmt, state)[0])
    elif isinstance(stmt, AST.Cast):
        value, errors = get_value(stmt.expr, state)
        value = cast(value, stmt.to_type, state)
        return value, errors
    elif isinstance(stmt, AST.BinaryOp):
        left, errors = get_value(stmt.left, state)
        right, errs = get_value(stmt.right, state)
        errors.update(errs)
        result = left.perform_operation(stmt.op, right)
        logging.debug("\tBinop: %s %s %s", str(left), stmt.op, str(right))
        logging.debug("\t\t= %s size %d", str(result), result.size)
        return result, errors
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '&':
        value, errors = get_address(stmt.expr, state)
        if isinstance(value, FrameAddress):
            value = state.stor.fa2ptr(value)
        return value, errors
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '*':
        address, errors = get_address(stmt, state)
        value, errs = state.stor.read(address)
        errors.update(errs)
        return value, errors
    elif isinstance(stmt, AST.FuncCall):
        raise CESKException("Cannot get value from " + stmt.name.name + "()")
    else:
        raise CESKException("Cannot get value from " + stmt.__class__.__name__)

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
            else:
                raise CESKException("Decl for %s not found"%(ident))
        return state.envr.get_address(ident), set()

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
                address, errors = get_address(name.expr, state)
                address, errs = state.stor.read(address)
                errors.update(errs)
                address = cast(address, name.to_type, state)
                return address, errors
            else:
                raise CESKException("Unknown Case for UnaryOp, nested part is "
                                    + str(name))
        else:
            raise CESKException("Unsupported UnaryOp lvalue in assignment: "
                                + unary_op.op)

    elif isinstance(reference, AST.StructRef):
        raise CESKException("StructRef should be transformed")
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
        #could fetch this concretely no matter what
        value = generate_constant_value(param.value, param.type)
    #elif isinstance(param, AST.ID):
    #    value, _ = get_value(param, state) #id's should not produce an error
    #else:
    #    raise CESKException("Constant or ID expected %s "%repr(param))
    else:
        value, _ = get_value(param, state) #possibilty of ignored errors

    num_bytes = get_int_data(value)
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
