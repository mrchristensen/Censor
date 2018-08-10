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
    obj_name = stmt.__class__.__name__
    method_name = "handle_" + obj_name
    handle_node = globals()[method_name]
    return handle_node(stmt, state)

def handle_Label(stmt, state): # pylint: disable=invalid-name
    '''Handles Labels'''
    new_ctrl = Ctrl(stmt.stmt)
    return State(new_ctrl, state.envr, state.stor, state.kont)

def handle_If(stmt, state): # pylint: disable=invalid-name
    '''Handles Ifs'''
    logging.debug("If")
    value = get_value(stmt.cond, state)
    if value.get_truth_value():
        new_ctrl = Ctrl(stmt.iftrue)
        return State(new_ctrl, state.envr, state.stor, state.kont)
    elif stmt.iffalse is not None:
        raise Exception("False Branch should be transformed")
    else:
        return get_next(state)

def handle_ID(stmt, state): # pylint: disable=invalid-name
    '''Handles IDs'''
    logging.debug("ID %s", stmt.name)
    name = stmt.name
    address = state.envr.get_address(name)
    value = address.dereference() #safe
    if value is None:
        raise Exception(name + ": " + str(state.stor.memory))
    if isinstance(state.kont, FunctionKont): #Don't return to function
        return get_next(state)
    else:
        return state.kont.satisfy(state, value)

def handle_Goto(stmt, state): # pylint: disable=invalid-name
    '''Handles Gotos'''
    logging.debug('Goto %s', stmt.name)
    label_to = ls.LinkSearch.label_lut[stmt.name]
    body = label_to
    while not isinstance(body, AST.Compound):
        index = ls.LinkSearch.index_lut[body]
        body = ls.LinkSearch.parent_lut[body]
    new_ctrl = Ctrl(index, body)
    logging.debug('\t Body: %s', str(body))
    if body in ls.LinkSearch.envr_lut:
        new_envr = ls.LinkSearch.envr_lut[body]
    else:
        #forward jump into previously undefined scope
        new_envr = state.envr
    return State(new_ctrl, new_envr, state.stor, state.kont)

def handle_FuncCall(stmt, state): # pylint: disable=invalid-name
    '''Handles FuncCalls'''
    logging.debug("FuncCall")
    if stmt.name.name == "printf":
        return printf(stmt, state)
    elif stmt.name.name == "malloc":
        return malloc(stmt, state)
    elif stmt.name.name == "free":
        return get_next(state)
    else:
        return func(stmt, state)

def handle_EmptyStatement(stmt, state): #pylint: disable=invalid-name
    '''Handles EmptyStatement'''
    return get_next(state)

def handle_Decl(stmt, state):#pylint: disable=invalid-name
    '''Handles Decls'''
    logging.debug("Decl "+str(stmt.name)+'    '+str(stmt.type))
    decl_helper(stmt, state)
    if stmt.init is not None:
        new_address = state.envr.get_address(stmt.name)
        new_state = assignment_helper("=", new_address, stmt.init, state)
        return new_state
    elif isinstance(state.kont, FunctionKont):
        return get_next(state)
    else:
        return state.kont.satisfy(state)

def handle_Constant(stmt, state): #pylint: disable=invalid-name
    '''Handles Constants'''
    logging.debug("Constant %s", stmt.type)
    value = generate_constant_value(stmt.value, stmt.type)
    if isinstance(state.kont, FunctionKont):
        return get_next(state)
    else:
        return state.kont.satisfy(state, value)

def handle_Compound(stmt, state): #pylint: disable=invalid-name
    '''Handles Compounds'''
    logging.debug("Compound")
    new_ctrl = Ctrl(0, stmt)
    new_envr = state.envr
    ls.LinkSearch.envr_lut[stmt] = new_envr #save to table for goto lookup
    if stmt.block_items is None:
        return get_next(state)
    else:
        return State(new_ctrl, new_envr, state.stor, state.kont)

def handle_Cast(stmt, state): #pylint: disable=invalid-name
    '''Handles Cast'''
    # TODO try and remove Cast Kontinuations
    logging.debug('Cast')
    new_ctrl = Ctrl(stmt.expr)
    if isinstance(state.kont, FunctionKont):
        new_kont = state.kont #ignore cast b/c it is not used
    else:
        new_kont = CastKont(state.kont, stmt.to_type)
    new_state = State(new_ctrl, state.envr, state.stor, new_kont)
    return new_state
    #old_value = get_address(stmt.expr, state).dereference()
    #cast_value = cast(old_value, stmt.to_type, state)
    #if isinstance(state.kont, FunctionKont): #Don't return to function
    #    successors.append(get_next(state))
    #else:
    #    successors.append(state.kont.satisfy(state, cast_value))

def handle_BinaryOp(stmt, state): #pylint: disable=invalid-name
    '''Handles BinaryOps'''
    left = get_value(stmt.left, state)
    right = get_value(stmt.right, state)
    value = left.perform_operation(stmt.op, right)
    logging.debug("BinaryOp %s%s%s = %s", str(left), stmt.op,
                  str(right), str(value))
    if isinstance(state.kont, FunctionKont): #Don't return to function
        return get_next(state)
    else:
        return state.kont.satisfy(state, value)

def handle_Assignment(stmt, state): #pylint: disable=invalid-name
    '''Handles Assignments'''
    logging.debug("Assignment")
    rexp = stmt.rvalue

    laddress = get_address(stmt.lvalue, state)

    # take an operater, address (ReferenceValue),
    #  the expression on the right side, and the state
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
        new_ctrl = Ctrl(exp) #build special ctrl for exp
        new_kont = AssignKont(address, state)
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

        state.envr.map_new_identifier(name, ref_address)
            #the address is mapped then if additional space is need for
            # a struct handle decl struct manages it

    elif isinstance(decl.type, AST.ArrayDecl):
        data_address = handle_decl_array(decl.type, [], state)
        state.envr.map_new_identifier(decl.name, data_address)
        logging.debug(" Mapped "+str(name)+" to "+str(data_address))
        if decl.init is not None:
            raise Exception("array init should be transformed")

    else:
        raise Exception("Declarations of " + str(decl.type) +
                        " are not yet implemented")

    return state

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

    if opr == "&":
        value = get_address(expr, state)
    elif opr == "*":
        if isinstance(expr, AST.ID):
            address = state.envr.get_address(expr)
            pointer = address.dereference() #safe

            value = pointer.dereference() #todo add size
        elif isinstance(expr, AST.UnaryOp) and expr.op == "&":
            address = get_address(expr.expr, state)
            value = address.dereference() #todo maybe add size
        elif (isinstance(expr, AST.Cast) and
              isinstance(expr.to_type, AST.PtrDecl)):
            temp = get_address(expr.expr, state).dereference()
            address = cast(temp, expr.to_type, state)
            value = address.dereference() #todo add size
        else:
            raise Exception("Unknown Case in UnaryOp: " + str(expr))
    else:
        raise Exception(opr + " is not yet implemented")

    if isinstance(state.kont, FunctionKont):
        return get_next(state)
    return state.kont.satisfy(state, value)

def printf(stmt, state):
    '''performs printf'''
    if isinstance(stmt.args.exprs[1], AST.Constant):
        value = generate_constant_value(stmt.args.exprs[1].value,
                                        stmt.args.exprs[1].type)
    else:
        value = get_address(stmt.args.exprs[1], state).dereference()
    if isinstance(stmt.args.exprs[0], AST.Constant):
        print_string = stmt.args.exprs[0].value % (value.data)
    elif isinstance(stmt.args.exprs[0], AST.Cast):
        print_string = stmt.args.exprs[0].expr.value % (value.data)
    else:
        raise Exception("printf does not know how to handle "
                        +str(stmt.args.exprs[0]))
    print_string = print_string[1:][:-1] #drop quotes
    print(print_string.replace("\\n", "\n"), end="") #convert newlines
    if isinstance(state.kont, FunctionKont): #Don't return to function
        return get_next(state)
    else:
        return state.kont.satisfy(state, generate_constant_value("0"))
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
    #pointer = state.stor.allocate_block(length)
    #TODO find cause of error on basic func 12
    if isinstance(state.kont, FunctionKont): #Don't return to function
        return get_next(state)
    else:
        return state.kont.satisfy(state, pointer)
def func(stmt, state):
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
        new_ctrl = Ctrl(0, func_def.body)
        new_state = State(new_ctrl, Envr(), state.stor, state.kont)
        new_state = func_helper(param_list, expr_list, new_ctrl, state)
        func_type = func_def.decl.type.type
        if (isinstance(func_type, AST.TypeDecl) and
                isinstance(func_type.type, AST.IdentifierType) and
                'void' in func_type.type.names):
            new_kont = VoidKont(state)
        else:
            new_kont = FunctionKont(state)
    return State(new_ctrl, new_state.envr, new_state.stor, new_kont)
def func_helper(param_list, expr_list, new_ctrl, state):
    '''Prepares the next_state from param_list and expr_list'''
    new_state = State(new_ctrl, Envr(), state.stor, state.kont)
    for decl, expr in zip(param_list, expr_list):
        new_state = decl_helper(decl, new_state)
        new_address = new_state.envr.get_address(decl.name)
        while isinstance(expr, AST.Cast):
            expr = expr.expr #todo not ignore cast
        if isinstance(expr, AST.Constant):
            value = generate_constant_value(expr.value, expr.type)
        elif isinstance(expr, AST.ID):
            address = state.envr.get_address(expr.name)
            value = address.dereference() #safe
        else:
            raise Exception("Values passed to functions must be " +
                            "Constant or ID not " + str(expr))
        new_state.stor.write(new_address, value)
    return new_state

def handle_Return(stmt, state):# pylint: disable=invalid-name
    """makes a ReturnKont. The exp return value is passed to parent kont"""
    exp = stmt.expr
    #All expressions refuse to return to FunctionKont to prevent expression
    # in statement position errors. Only ReturnKont will satisfy FunctionKont
    if isinstance(state.kont, FunctionKont):
        returnable_kont = ReturnKont(state.kont)
    else:
        raise Exception("Unexpected return statement: "+str(state.kont))
    if exp is None:
        if isinstance(state.kont, VoidKont):
            return state.kont.satisfy(state)
        else:
            throw("Exception: No return value was given in non-void function")
    return State(Ctrl(exp), state.envr, state.stor, returnable_kont)

def get_value(stmt, state):
    """ get value for simple id's constants or references and casts of them """
    if isinstance(stmt, AST.Constant):
        value = generate_constant_value(stmt.value, stmt.type)
        return value
    elif isinstance(stmt, AST.UnaryOp) and stmt.op == '&':
        return get_address(stmt.expr, state)
    elif isinstance(stmt, AST.Cast):
        val = get_value(stmt.expr, state)
        return cast(val, stmt.to_type, state)
    else:
        return get_address(stmt, state).dereference()

def get_address(reference, state):
    # pylint: disable=too-many-branches
    """get_address"""
    if isinstance(reference, AST.ID):
        ident = reference
        if not state.envr.is_localy_defined(ident):
            checked_decl = check_for_implicit_decl(ident)
            if checked_decl != None:
                logging.debug("Found implicit decl: %s", checked_decl.name)
                decl_helper(checked_decl, state)
        address = state.envr.get_address(ident.name)
        return address

    elif isinstance(reference, AST.ArrayRef):
        raise Exception("ArrayRef should be transformed")

    elif isinstance(reference, AST.UnaryOp):
        unary_op = reference
        if unary_op.op == "*":
            name = unary_op.expr
            if isinstance(name, AST.ID):
                pointer = state.envr.get_address(name)
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

    if compound != None:
        if compound in ls.LinkSearch.envr_lut:
            comp_envr = ls.LinkSearch.envr_lut[compound]
            if comp_envr.is_localy_defined(ident.name):
                return None
        if compound in ls.LinkSearch.scope_decl_lut:
            for decl in ls.LinkSearch.scope_decl_lut[compound]:
                if decl.name == ident.name:
                    return decl
    return None

def get_next(state):
    """takes state and returns a state with ctrl for the next statement
    to execute"""
    ctrl = state.ctrl
    if not isinstance(state.kont, FunctionKont):
        print(Exception("CESK error: called get_next in bad context"))
        print(ctrl.stmt().coord)
        print("You are probably trying to get a value from something that " +
              "is not implemented. Defaulting to 0")
        state.kont.satisfy(state, generate_constant_value("0"))

    if ctrl.body is not None: #if a standard compound-block:index ctrl
        if ctrl.index + 1 < len(ctrl.body.block_items):
            #if there are more items in the compound block go to next
            new_ctrl = ctrl + 1
            return State(new_ctrl, state.envr, state.stor, state.kont)
        else:
            #if we are falling off the end of a compound block
            parent = ls.LinkSearch.parent_lut[ctrl.body]
            if parent is None:
                #we are falling off and there is no parent block
                #this is an end of a function call. Satisfy kont.
                if isinstance(state.kont, VoidKont):
                    return state.kont.satisfy()
                else:
                    raise Exception("Expected Return Statement")

            elif isinstance(parent, AST.Compound):
                #find current compound block position in the parent block
                parent_index = ls.LinkSearch.index_lut[ctrl.body]
                new_ctrl = Ctrl(parent_index, parent)

            else:
                #if the parent is not a compound (probably an if statement)
                new_ctrl = Ctrl(parent) #make a special ctrl and try again

            return get_next(State(new_ctrl, state.envr, state.stor, state.kont))

    if ctrl.node is not None:
        #if it is a special ctrl as created by binop or assign
        #try to convert to normal ctrl and try again
        parent = ls.LinkSearch.parent_lut[ctrl.node]
        if isinstance(parent, AST.Compound):
            #we found the compound we can create normal ctrl
            parent_index = ls.LinkSearch.index_lut[ctrl.node]
            new_ctrl = Ctrl(parent_index, parent)
        else:
            #we couldn't make a normal try again on parent
            new_ctrl = Ctrl(parent)
        return get_next(State(new_ctrl, state.envr, state.stor, state.kont))

    raise Exception("Malformed ctrl: this should have been unreachable")


# imports are down here to allow for circular dependencies between
# structures.py and interpret.py
from cesk.structures import (State, Ctrl, Envr, AssignKont, ReturnKont, # pylint: disable=wrong-import-position
                             FunctionKont, VoidKont,
                             CastKont, throw)
