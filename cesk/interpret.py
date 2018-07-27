"""Functions to interpret c code directly"""
import logging
import pycparser.c_ast as AST
from transforms.sizeof import get_size_ast
from cesk.values import generate_constant_value, cast
import cesk.linksearch as ls
logging.basicConfig(filename='logfile.txt', level=logging.DEBUG,
                    format='%(levelname)s: %(message)s', filemode='w')

def execute(state):
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-locals
    # pylint: disable=fixme
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states"""
    successors = []
    stmt = state.ctrl.stmt()
    if isinstance(stmt, AST.ArrayDecl):
        raise Exception("ArrayDecl should have been found as a child of Decl")
    elif isinstance(stmt, AST.ArrayRef):
        raise Exception("Array should be transformed")
    elif isinstance(stmt, AST.Assignment):
        logging.debug("Assignment")
        rexp = stmt.rvalue
        #if isinstance(stmt.lvalue, AST.UnaryOp) and stmt.lvalue.op == '*':
        #    laddress = get_address(stmt.lvalue.expr, state)
        #else:
        laddress = get_address(stmt.lvalue, state)
        logging.debug('   %s', str(stmt.lvalue))
        logging.debug('   %s', str(laddress))
        # take an operater, address (ReferenceValue),
        #  the expression on the right side, and the state
        successors.append(handle_assignment(stmt.op, laddress, rexp, state))
    elif isinstance(stmt, AST.BinaryOp):
        left = get_value(stmt.left, state)
        right = get_value(stmt.right, state)
        value = left.perform_operation(stmt.op, right)
        logging.debug("BinaryOp %s%s%s = %s", str(left), stmt.op,
                      str(right), str(value))
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, AST.Break):
        # logging.debug("Break")
        raise Exception("Break has not yet been implemented")
    elif isinstance(stmt, AST.Case):
        raise Exception("Case staments should be transformed out")
        #logging.debug("Case")
        #successors.append(get_next(state))
    elif isinstance(stmt, AST.Cast):
        # TODO try and remove Cast Kontinuations
        logging.debug('Cast')
        new_ctrl = Ctrl(stmt.expr)
        if isinstance(state.kont, FunctionKont):
            new_kont = state.kont #don't return: castvalue not used
        else:
            new_kont = CastKont(state.kont, stmt.to_type)
        new_state = State(new_ctrl, state.envr, state.stor, new_kont)
        successors.append(new_state)
        #old_value = get_address(stmt.expr, state).dereference()
        #cast_value = cast(old_value, stmt.to_type, state)
        #if isinstance(state.kont, FunctionKont): #Don't return to function
        #    successors.append(get_next(state))
        #else:
        #    successors.append(state.kont.satisfy(state, cast_value))

    elif isinstance(stmt, AST.Compound):
        logging.debug("Compound")
        new_ctrl = Ctrl(0, stmt)
        new_envr = Envr(state.envr)
        ls.LinkSearch.envr_lut[stmt] = new_envr #save to table for goto lookup
        if stmt.block_items is None:
            successors.append(get_next(state))
        else:
            successors.append(State(new_ctrl, new_envr, state.stor, state.kont))

    elif isinstance(stmt, AST.CompoundLiteral):
        # TODO
        # logging.debug("CompoundLiteral")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Constant):
        logging.debug("Constant "+stmt.type)
        value = generate_constant_value(stmt.value, stmt.type)
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, AST.Continue):
        logging.error("Continue should be transformed out")
        # logging.debug("Continue")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Decl):
        logging.debug("Decl "+str(stmt.name)+'    '+str(stmt.type))
        handle_decl(stmt, state)
        if stmt.init is not None:
            new_address = state.envr.get_address(stmt.name)
            new_state = handle_assignment("=", new_address, stmt.init, state)
            successors.append(new_state)
        elif isinstance(state.kont, FunctionKont):
            #Don't return to function/do not execute function until called
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, AST.DeclList):
        # Should be transformed to multiple Decl nodes
        raise Exception("DeclList should be transformed out")
        #successors.append(get_next(state))
    elif isinstance(stmt, AST.Default):
        raise Exception("Default should be transformed")
        # logging.debug("Default")
        #successors.append(get_next(state))
    elif isinstance(stmt, AST.DoWhile):
        raise Exception("DoWhile should be transformed")
        # logging.debug("DoWhile")
        #successors.append(get_next(state))
    elif isinstance(stmt, AST.EllipsisParam):
        # TODO
        # logging.debug("EllipsisParam")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.EmptyStatement):
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Enum):
        # TODO
        # logging.debug("Enum")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Enumerator):
        # TODO
        # logging.debug("Enumerator")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.EnumeratorList):
        # TODO
        # logging.debug("EnumeratorList")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.ExprList):
        raise Exception("ExprList should only appear inside FuncCall/Decl")
    elif isinstance(stmt, AST.FileAST):
        raise Exception("FileAST is not a valid control point")
    elif isinstance(stmt, AST.For):
        # TODO manage pragma omp for loops others are transformed
        logging.error("For should be transformed to goto")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.FuncCall):
        logging.debug("FuncCall")
        if stmt.name.name == "printf":
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
                successors.append(get_next(state))
            else:
                successors.append(
                    state.kont.satisfy(state, generate_constant_value("0")))
        elif stmt.name.name == "malloc":
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
                successors.append(get_next(state))
            else:
                successors.append(state.kont.satisfy(state, pointer))
        elif stmt.name.name == "free":
            successors.append(get_next(state))
        else:
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
                new_envr = Envr(Envr.get_global_scope())
                new_state = State(new_ctrl, new_envr, state.stor, state.kont)

                for decl, expr in zip(param_list, expr_list):
                    new_state = handle_decl(decl, new_state)
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

                func_type = func_def.decl.type.type
                if (isinstance(func_type, AST.TypeDecl) and
                        isinstance(func_type.type, AST.IdentifierType) and
                        'void' in func_type.type.names):
                    new_kont = VoidKont(state)
                else:
                    new_kont = FunctionKont(state)
                successors.append(State(new_ctrl,
                                        new_state.envr,
                                        new_state.stor,
                                        new_kont))
    elif isinstance(stmt, AST.FuncDecl):
        logging.debug("FuncDecl")
        raise Exception("FuncDecl out of Global scope")
    elif isinstance(stmt, AST.FuncDef):
        logging.debug("FuncDef")
        raise Exception("FuncDef out of Global scope")
    elif isinstance(stmt, AST.Goto):
        logging.debug('Goto '+stmt.name)
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
            new_envr = create_forward_jump_envr(body, state)

        logging.debug("Now leaving scope %s to %s", str(state.envr.id),
                      str(new_envr.id))
        successors.append(State(new_ctrl, new_envr, state.stor, state.kont))
    elif isinstance(stmt, AST.ID):
        logging.debug("ID %s", stmt.name)
        name = stmt.name
        address = state.envr.get_address(name)
        value = address.dereference() #safe
        if value is None:
            raise Exception(name + ": " + str(state.stor.memory))
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, AST.IdentifierType):
        logging.error("IdentifierType should not appear on there own")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.If):
        logging.debug("If")
        value = get_value(stmt.cond, state)
        if value.get_truth_value():
            new_ctrl = Ctrl(stmt.iftrue)
            successors.append(State(new_ctrl, state.envr,
                                    state.stor, state.kont))
        elif stmt.iffalse is not None:
            raise Exception("False Branch should be transformed")
        else:
            successors.append(get_next(state))
    elif isinstance(stmt, AST.InitList):
        # TODO transform nested
        # Init list is tranformed
        logging.error("InitList")
        raise Exception("Initilizer List is not implemented")
        #successors.append(get_next(state))
    elif isinstance(stmt, AST.Label):
        # logging.debug("Label")
        new_ctrl = Ctrl(stmt.stmt)
        successors.append(State(new_ctrl, state.envr, state.stor, state.kont))
    elif isinstance(stmt, AST.NamedInitializer):
        # TODO
        # logging.debug("NamedInitializer")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.ParamList):
        # TODO
        # logging.debug("ParamList")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.PtrDecl):
        logging.error("PtrDecl should not appear outside of a decl")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Return):
        # logging.debug("Return")
        exp = stmt.expr
        successors.append(handle_return(exp, state))
    elif isinstance(stmt, AST.Struct):
        # TODO decide what to do with structs as a whole
        # logging.debug("Struct")
        #struct = stmt
        successors.append(get_next(state))
    elif isinstance(stmt, AST.StructRef):
        # transformed to pointer arithmetic to avoid intermediate value
        raise Exception("StructRef should be transform to pointer arith")
    elif isinstance(stmt, AST.Switch):
        # tranformed
        raise Exception("Switch should be tranformed")
    elif isinstance(stmt, AST.TernaryOp):
        logging.error("TernaryOp should be removed by transform")
        raise Exception("TernaryOp should have been removed in the transforms")
    elif isinstance(stmt, AST.TypeDecl):
        raise Exception("TypeDecl should have been found as child of Decl")
    elif isinstance(stmt, AST.Typedef):
        # logging.debug("Typedef")
        # typedef'ed names ares replaced by there values in
        #    transform so just skip over
        successors.append(get_next(state))
    elif isinstance(stmt, AST.Typename):
        logging.error("Typename should appear only nested inside another type")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.UnaryOp):
        logging.debug("UnaryOp %s", stmt.op)
        opr = stmt.op
        expr = stmt.expr
        successors.append(handle_unary_op(opr, expr, state))
    elif isinstance(stmt, AST.Union):
        # TODO
        # logging.debug("Union")
        successors.append(get_next(state))
    elif isinstance(stmt, AST.While):
        logging.error("While should be removed in the transform")
        raise Exception("While should be removed in the transform")
    elif isinstance(stmt, AST.Pragma):
        # TODO
        # logging.debug("Pragma")
        successors.append(get_next(state))
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))

    return successors

def handle_assignment(operator, address, exp, state):
    """Creates continuation to evaluate exp and assigns resulting value to the
    given address"""
    #pylint: disable=too-many-function-args
    if operator == '=':
        new_ctrl = Ctrl(exp) #build special ctrl for exp
        new_kont = AssignKont(address, state)
    else:
        raise Exception(operator + " is not yet implemented")
    return State(new_ctrl, state.envr, state.stor, new_kont)

def handle_decl(decl, state):
    """Maps the identifier to a new address and passes assignment part"""
    name = decl.name
    if state.envr.is_localy_defined(name):
        logging.debug(str(Exception("Error: redefinition of " + name)))

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
            raise Exception("array init needs to be transformed")

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
        if length == 0: #TODO
            raise NotImplementedError("Arrays of size 0 not implemented")
        if isinstance(array.type.type, (AST.Struct, AST.Union)):
            #TODO handle Union
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

def handle_unary_op(opr, expr, state):
    """decodes and evaluates unary_ops"""
    if isinstance(state.kont, FunctionKont): #don't return to function
        return get_next(state)

    if opr == "&":
        value = get_address(expr, state)
        return state.kont.satisfy(state, value)
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
        return state.kont.satisfy(state, value)
    else:
        raise Exception(opr + " is not yet implemented")


def handle_return(exp, state):
    """makes a ReturnKont. The exp return value is passed to parent kont"""
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
                handle_decl(checked_decl, state)
        address = state.envr.get_address(ident.name)
        return address

    elif isinstance(reference, AST.ArrayRef):
        raise Exception("ArrayRef needs to be transformed out")

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
        raise Exception("Needs to be transformed to pointer arithmetic")
    elif isinstance(reference, AST.Struct):
        #TODO
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
    #raise Exception("Could not determine Implicit Decl")

def create_forward_jump_envr(body, state): # pylint: disable=inconsistent-return-statements
    """Recursively searches for a defined parent scope to inherit from"""
    if body in ls.LinkSearch.parent_lut:
        compound = None
        parent = ls.LinkSearch.parent_lut[body]
        while True:
            logging.debug("Loop at %s", parent)
            if isinstance(parent, AST.Compound):
                compound = parent
                break
            if parent not in ls.LinkSearch.parent_lut:
                break
            parent = ls.LinkSearch.parent_lut[parent]
        if compound in ls.LinkSearch.envr_lut:
            return Envr(ls.LinkSearch.envr_lut[compound])
        return Envr(create_forward_jump_envr(compound, state))
    else:
        #TODO does this work why?
        #raise Exception("Expected parent of %s for forward jump", body)
        return state.envr

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
                new_envr = state.envr.parent #fall off: return to parent scope
                logging.debug("Fall off compound. Leaving scope %s to %s",
                              state.envr.id, new_envr.id)

            else:
                #if the parent is not a compound (probably an if statement)
                new_ctrl = Ctrl(parent) #make a special ctrl and try again
                new_envr = state.envr.parent

            return get_next(State(new_ctrl, new_envr, state.stor, state.kont))

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
