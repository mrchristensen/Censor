"""Functions to interpret c code directly"""
from functools import reduce
import pycparser
from cesk.values import ReferenceValue, generate_constant_value
from cesk.values import generate_array, Array
import logging
logging.basicConfig(filename='logfile.txt',level=logging.DEBUG, format='%(levelname)s: %(message)s', filemode='w')

class LinkSearch(pycparser.c_ast.NodeVisitor):
    """Holds various look-up-tables for functions, labels, etc."""
    parent_lut = {}
    index_lut = {}
    label_lut = {}
    envr_lut = {}
    function_lut = {}

    def generic_visit(self, node):

        if isinstance(node, pycparser.c_ast.Label):
            if node.name in LinkSearch.label_lut:
                raise Exception("Duplicate label name")
            LinkSearch.label_lut[node.name] = node

        if isinstance(node, pycparser.c_ast.FuncDef):
            name = node.decl.name
            LinkSearch.function_lut[name] = node

        for i, child in enumerate(node):
            if isinstance(child, pycparser.c_ast.Node):
                if child in LinkSearch.parent_lut:
                    print(Exception("Node duplicated in tree"))
                LinkSearch.parent_lut[child] = node
                LinkSearch.index_lut[child] = i
                self.visit(child)
        if not node in LinkSearch.parent_lut:
            LinkSearch.parent_lut[node] = None
            LinkSearch.index_lut[node] = 0
        return node

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
    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        # logging.debug("ArrayDecl")
        raise Exception("ArrayDecl should have been found as a child of Decl")
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # logging.debug("ArrayRef")
        list_of_index = []
        while not isinstance(stmt, pycparser.c_ast.ID):
            if isinstance(stmt.subscript, pycparser.c_ast.ID):
                address = state.envr.get_address(stmt.subscript.name)
                index = address.dereference().data
            elif isinstance(stmt.subscript, pycparser.c_ast.Constant):
                index = generate_constant_value(stmt.subscript.value).data
            else:
                raise Exception("Array subscripts of type " +
                                str(stmt.subscript) + "are not yet implemented")
            list_of_index.insert(0, index)
            stmt = stmt.name
        name = stmt.name
        pointer_address = state.envr.get_address(name)
        pointer = pointer_address.dereference()
        if isinstance(pointer, ReferenceValue):
            value = pointer.index(state.stor, list_of_index)
        else:
            raise Exception(name + " is not an array nor pointer nor vector" +
                            str(pointer))
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # logging.debug("Assignment")
        exp = stmt.rvalue
        if isinstance(stmt.lvalue, pycparser.c_ast.ID):
            ident = stmt.lvalue
            address = state.envr.get_address(ident.name)
        elif isinstance(stmt.lvalue, pycparser.c_ast.ArrayRef):
            # logging.debug('ArrayRef lvalue')
            array = stmt.lvalue
            list_of_index = []
            while not isinstance(array, pycparser.c_ast.ID):
                if isinstance(array, pycparser.c_ast.UnaryOp):
                    #TODO figure out how this is to be handled since tranforms inserts it here
                    logging.error("UnaryOp in ArrayRef lvalue")
                    #new_state = handle_unary_op(array.op,array.expr,state)
                    # logging.debug('State Ctr: '+str(new_state.ctrl.stmt()))
                    #successors.append(new_state)
                    #return successors
                    #break           
                if isinstance(array.subscript, pycparser.c_ast.ID):
                    address = state.envr.get_address(array.subscript.name)
                    index = address.dereference().data
                elif isinstance(array.subscript, pycparser.c_ast.Constant):
                    index = generate_constant_value(array.subscript.value).data
                else:
                    raise Exception("Array subscripts of type " +
                                    str(array.subscript) +
                                    "are not yet implemented")
                list_of_index.insert(0, index)
                array = array.name
            name = array.name
            pointer = state.envr.get_address(name).dereference()
            address = pointer.index_for_address(list_of_index)

        elif isinstance(stmt.lvalue, pycparser.c_ast.UnaryOp):
            unary_op = stmt.lvalue
            if unary_op.op == "*":
                name = unary_op.expr
                pointer = state.envr.get_address(name)
                address = pointer.dereference()
            else:
                raise Exception("Unsupported UnaryOp lvalue in assignment: " + unary_op.op)

        elif isinstance(stmt.lvalue, pycparser.c_ast.StructRef):
            #TODO finish StructRef assignment
            # logging.debug('Assign value to item in struct')
            ref = stmt.lvalue
            # logging.debug('Name: ' + str(ref.name.name) + '\nType: ' + str(ref.type) + '\nField: '+ str(ref.field.name))
            struct_ptr = state.envr.get_address(ref.name.name)
            struct = struct_ptr.dereference()
            # logging.debug('Pointer: '+str(struct_ptr))
            # logging.debug('Struct: '+str(struct.data))
            address = struct_ptr
        #elif isinstance(stmt.lvalue, pycparser.c_ast.Struct):
        #    # logging.debug('Assign struct')
        else:
            raise Exception("unsupported assign lvalue: " + str(stmt.lvalue))
        # logging.debug('\tEnd->Address: '+str(address.data)+'   rvalue: '+str(exp))
        successors.append(handle_assignment(stmt.op, address, exp, state))
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        # logging.debug("BinaryOp")
        new_kont = LeftBinopKont(state, stmt.op, stmt.right, state.kont)
        successors.append(State(Ctrl(stmt.left), state.envr, state.stor,
                                new_kont))
    elif isinstance(stmt, pycparser.c_ast.Break):
        # TODO
        # logging.debug("Break")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Case):
        # TODO
        # logging.debug("Case")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Cast):
        # TODO
        # logging.debug('Cast')
        # logging.debug(stmt.expr)
        new_ctrl = Ctrl(stmt.expr)
        if isinstance(state.kont, FunctionKont): #don't return: don't cast
            new_kont = state.kont
        else:
            new_kont = CastKont(state.kont, stmt.to_type)
        new_state = State(new_ctrl, state.envr, state.stor, new_kont)
        successors.append(new_state)
    elif isinstance(stmt, pycparser.c_ast.Compound):
        # logging.debug("Compound")
        new_ctrl = Ctrl(0, stmt)
        new_envr = Envr(state.envr)
        LinkSearch.envr_lut[stmt] = new_envr #save to table for goto lookup
        if stmt.block_items is None:
            successors.append(get_next(state))
        else:
            successors.append(State(new_ctrl, new_envr, state.stor, state.kont))

    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        # TODO
        # logging.debug("CompoundLiteral")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Constant):
        # logging.debug("Constant")
        value = generate_constant_value(stmt.value, stmt.type)
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.Continue):
        # TODO
        # logging.debug("Continue")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Decl):
        # logging.debug("Decl")
        handle_decl(stmt, state)
        if stmt.init is not None:
            new_address = state.envr.get_address(stmt.name)
            new_state = handle_assignment("=", new_address, stmt.init, state)
            successors.append(new_state)
        elif isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # TODO
        # logging.debug("DeclList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Default):
        # TODO
        # logging.debug("Default")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        # TODO
        # logging.debug("DoWhile")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        # TODO
        # logging.debug("EllipsisParam")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        # TODO
        # logging.debug("EmptyStatement")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Enum):
        # TODO
        # logging.debug("Enum")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        # TODO
        # logging.debug("Enumerator")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        # TODO
        # logging.debug("EnumeratorList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        # TODO
        # logging.debug("ExprList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        # TODO
        # logging.debug("FileAST")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.For):
        # TODO
        # logging.debug("For")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        # logging.debug("FuncCall")
        if stmt.name.name == "printf":
            if not isinstance(stmt.args.exprs[1], pycparser.c_ast.ID):
                raise Exception("printf test stub only supports ID not " +
                                str(stmt.args.exprs[1]))
            id_to_print = stmt.args.exprs[1].name
            address = state.envr.get_address(id_to_print)
            value = address.dereference()
            

            #testing # logging.debug statements
            #causing error when transform is active because a cast is placed on formal parameters that need it
            if isinstance(stmt.args.exprs[0], pycparser.c_ast.Constant):
                print_string = stmt.args.exprs[0].value % (value.data)
            elif isinstance(stmt.args.exprs[0], pycparser.c_ast.Cast):     
                # TODO cast the value not just grap from cast object
                print_string = stmt.args.exprs[0].expr.value % (value.data) #still a work around 
            else:
                raise Exception("# logging.debug does not know how to handle "+str(stmt.args.exprs[0]))

            print_string = print_string[1:][:-1] #drop quotes
            print(print_string.replace("\\n", "\n"), end="") #convert newlines
            successors.append(get_next(state))

        else:
            if not stmt.name.name in LinkSearch.function_lut:
                raise Exception("Undefined reference to " + stmt.name.name)
            else:
                func_def = LinkSearch.function_lut[stmt.name.name]
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
                    if isinstance(expr, pycparser.c_ast.Constant):
                        value = generate_constant_value(expr.value)
                    elif isinstance(expr, pycparser.c_ast.ID):
                        address = state.envr.get_address(expr.name)
                        value = address.dereference()
                    else:
                        raise Exception("Values passed to functions must be " +
                                        "Constant or ID not " + str(expr))
                    new_state.stor.write(new_address, value)

                new_kont = FunctionKont(state)
                successors.append(State(new_ctrl,
                                        new_state.envr,
                                        new_state.stor,
                                        new_kont))
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        # logging.debug("FuncDecl")
        raise Exception("FuncDecl out of Global scope")
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        # logging.debug("FuncDef")
        raise Exception("FuncDef out of Global scope")
    elif isinstance(stmt, pycparser.c_ast.Goto):
        # logging.debug('Goto')
        label_to = LinkSearch.label_lut[stmt.name]
        body = label_to
        while not isinstance(body, pycparser.c_ast.Compound):
            index = LinkSearch.index_lut[body]
            body = LinkSearch.parent_lut[body]
        new_ctrl = Ctrl(index, body)
        # logging.debug('\t Body: '+str(body))
        if body in LinkSearch.envr_lut:
            new_envr = LinkSearch.envr_lut[body]
        else:
            new_envr = state.envr
            # logging.error('Need to make decisions on scope of forward jump')
            #raise Exception("Need to make decisions on scope of forward jump")

        successors.append(State(new_ctrl, new_envr, state.stor, state.kont))
    elif isinstance(stmt, pycparser.c_ast.ID):
        # logging.debug("ID")
        name = stmt.name
        address = state.envr.get_address(name)
        value = address.dereference()
        if value is None:
            raise Exception(name + ": " + str(state.stor.memory))
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        # TODO
        # logging.debug("IdentifierType")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.If):
        # logging.debug("If")
        new_kont = IfKont(state, stmt.iftrue, stmt.iffalse)
        new_ctrl = Ctrl(stmt.cond)
        successors.append(State(new_ctrl, state.envr, state.stor, new_kont))
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO
        # should get transformed out
        # logging.debug("InitList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Label):
        # logging.debug("Label")
        new_ctrl = Ctrl(stmt.stmt)
        successors.append(State(new_ctrl, state.envr, state.stor, state.kont))
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        # TODO
        # logging.debug("NamedInitializer")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        # TODO
        # logging.debug("ParamList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        # TODO
        # logging.debug("PtrDecl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Return):
        # logging.debug("Return")
        exp = stmt.expr
        successors.append(handle_return(exp, state))
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO
        # logging.debug("Struct")
        struct = stmt
        # logging.debug(str(struct.name))
        # logging.debug(str(struct.decls))
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO
        # logging.debug("StructRef")

        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO
        # logging.debug("Switch")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        # logging.debug("TernaryOp")
        raise Exception("TernaryOp should have been removed in the transforms")
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # logging.debug("TypeDecl")
        raise Exception("TypeDecl should have been found as child of Decl")
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        # logging.debug("Typedef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Typename):
        # TODO
        # logging.debug("Typename")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        # logging.debug("UnaryOp "+stmt.op)
        opr = stmt.op
        expr = stmt.expr
        successors.append(handle_unary_op(opr, expr, state))
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        # logging.debug("Union")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.While):
        # TODO
        # logging.debug("While")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Pragma):
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
        pass
        #raise Exception("Error: redefinition of " + name)

    elif (isinstance(decl.type, (pycparser.c_ast.TypeDecl,
                                 pycparser.c_ast.PtrDecl))):#pointers are ints
        new_address = state.stor.get_next_address()
        state.envr.map_new_identifier(name, new_address)
        return state

    elif isinstance(decl.type, pycparser.c_ast.ArrayDecl):
        ref_address = handle_decl_array(decl.type, [], state)
        state.envr.map_new_identifier(decl.name, ref_address)
        if decl.init is not None:
            ## TODO if init evaluates to an address don't allocate just
            # assign
            raise Exception("array init not yet implemented")
        return state
    else:
        raise Exception("Declarations of " + str(decl.type) +
                        " are not yet implemented")

    return state

def handle_decl_array(array, list_of_sizes, state):
    """Calculates size and allocates Array. Returns address of first item"""
    if isinstance(array.type, pycparser.c_ast.ArrayDecl):
        #Recursively add sizes array to list
        size = generate_constant_value(array.dim.value).data
        if size < 1:
            raise Exception("Non-positive Array Sizes are not supported")
        list_of_sizes.append(size)
        return handle_decl_array(array.type, list_of_sizes, state)

    elif isinstance(array.type, pycparser.c_ast.TypeDecl):
        size = generate_constant_value(array.dim.value).data
        if size < 1:
            raise Exception("Non-positive Array Sizes are not supported")
        list_of_sizes.append(size)
        #List of sizes populated: allocate the array
        ref_address = state.stor.get_next_address()
        length = reduce(lambda x, y: x*y, list_of_sizes) #multiply all together
        data_address = state.stor.allocate_block(length)
        new_array = generate_array(data_address, list_of_sizes, state.stor)
        state.stor.write(ref_address, new_array)
        #Allocated block: passing back the Array object that points to block
        return ref_address
    else:
        raise Exception("Declarations of " + str(array.type) +
                        " are not yet implemented")

def handle_unary_op(opr, expr, state): #pylint: disable=inconsistent-return-statements
    """decodes and evaluates unary_ops"""
    if isinstance(state.kont, FunctionKont): #don't return to function
        return get_next(state)

    if opr == "&":
        if isinstance(expr, pycparser.c_ast.ID):
            ident = expr.name
            address = state.envr.get_address(ident)
            value = address
            return state.kont.satisfy(state, value)
        elif isinstance(expr, pycparser.c_ast.ArrayRef):
            array = expr
            list_of_index = []
            #Compile a list of index
            while not isinstance(array, pycparser.c_ast.ID):
                # logging.debug('\tSub: '+str(array.subscript))
                if isinstance(array.subscript, pycparser.c_ast.ID):
                    address = state.envr.get_address(array.subscript.name)
                    index = address.dereference().data
                elif isinstance(array.subscript, pycparser.c_ast.Constant):
                    index = generate_constant_value(array.subscript.value).data
                else:
                    raise Exception("Array subscripts of type " +
                                    str(array.subscript) +
                                    "are not yet implemented")
                list_of_index.insert(0, index) #Push to front of list
                array = array.name
            name = array.name
            # logging.debug('\tName: '+name)
            pointer = state.envr.get_address(name).dereference()
            # logging.debug('\tPTR_Deref: '+str(pointer))
            if isinstance(pointer, Array):
                value = pointer.index_for_address(list_of_index)
            else:  #is another type of object, treat it like an array by returning the pointer
                value = state.envr.get_address(name)

            # logging.debug('\tValue: ' + str(value))
            return state.kont.satisfy(state, value)
        else:
            raise Exception("& operator not implemented for " + str(expr))

    elif opr == "*":
        pointer = state.envr.get_address(expr.name).dereference()
        # logging.debug('\tPointer: '+str(pointer))
        value = pointer.dereference()
        # logging.debug('\tValue: '+str(value.data))    
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

def get_next(state): #pylint: disable=inconsistent-return-statements
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
            parent = LinkSearch.parent_lut[ctrl.body]
            if parent is None:
                #we are falling off and there is no parent block
                #this is an end of a function call. Satisfy kont.
                if isinstance(state.kont, VoidKont):
                    return state.kont.satisfy()
                else:
                    raise Exception("Expected Return Statement")

            elif isinstance(parent, pycparser.c_ast.Compound):
                #find current compound block position in the parent block
                parent_index = LinkSearch.index_lut[ctrl.body]
                new_ctrl = Ctrl(parent_index, parent)
                new_envr = state.envr.parent #fall off: return to parent scope

            else:
                #if the parent is not a compound (probably an if statement)
                new_ctrl = Ctrl(parent) #make a special ctrl and try again
                new_envr = state.envr

            return get_next(State(new_ctrl, new_envr, state.stor, state.kont))


    if ctrl.node is not None:
        #if it is a special ctrl as created by binop or assign
        #try to convert to normal ctrl and try again
        parent = LinkSearch.parent_lut[ctrl.node]
        if isinstance(parent, pycparser.c_ast.Compound):
            #we found the compound we can create normal ctrl
            parent_index = LinkSearch.index_lut[ctrl.node]
            new_ctrl = Ctrl(parent_index, parent)
        else:
            #we couldn't make a normal try again on parent
            new_ctrl = Ctrl(parent)
        return get_next(State(new_ctrl, state.envr, state.stor, state.kont))

    raise Exception("Malformed ctrl: this should have been unreachable")


# imports are down here to allow for circular dependencies between
# structures.py and interpret.py
from cesk.structures import State, Ctrl, Envr, AssignKont, ReturnKont # pylint: disable=wrong-import-position
from cesk.structures import FunctionKont, LeftBinopKont, IfKont, VoidKont # pylint: disable=wrong-import-position
from cesk.structures import CastKont, throw # pylint: disable=wrong-import-position
