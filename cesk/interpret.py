"""Functions to interpret c code directly"""
from functools import reduce
import logging
import pycparser
from cesk.values import ReferenceValue, generate_constant_value
from cesk.values import generate_struct, Struct
import logging
logging.basicConfig(filename='logfile.txt',level=logging.DEBUG, format='%(levelname)s: %(message)s', filemode='w')

class LinkSearch(pycparser.c_ast.NodeVisitor):
    """Holds various look-up-tables for functions, labels, etc."""
    parent_lut = {}
    index_lut = {}
    label_lut = {}
    envr_lut = {}
    function_lut = {}
    struct_lut = {}

    def generic_visit(self, node):
        if isinstance(node, pycparser.c_ast.Label):
            if node.name in LinkSearch.label_lut:
                raise Exception("Duplicate label name")
            LinkSearch.label_lut[node.name] = node

        if isinstance(node, pycparser.c_ast.FuncDef):
            name = node.decl.name
            LinkSearch.function_lut[name] = node

        if isinstance(node, pycparser.c_ast.Struct) and node.decls is not None:
            name = node.name
            LinkSearch.struct_lut[name] = node
            logging.debug('Store struct '+str(name)
                          +' with decls '+str(node.decls))

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
        logging.debug("ArrayRef")

        address = get_address(stmt,state)
        value = address.dereference()  

        logging.debug('   Address '+str(address)+'   Value: '+str(value))

        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        logging.debug("Assignment")
        rexp = stmt.rvalue
        laddress = get_address(stmt.lvalue,state)
        logging.debug(str(stmt.lvalue))
        logging.debug('   '+str(laddress))
         #take an operater, address (ReferenceValue), the expression on the right side, and the state       
        successors.append(handle_assignment(stmt.op, laddress, rexp, state)) 
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        logging.debug("BinaryOp "+str(stmt.op))
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
        logging.debug('Cast')
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
        logging.debug("Constant")
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
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # Should be transformed to multiple Decl nodes 
        logging.error("DeclList should be transformed out")
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
        # This should be transformed out
        logging.error("For should be transformed to goto")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        # logging.debug("FuncCall")
        if stmt.name.name == "printf":
            if isinstance(stmt.args.exprs[1],pycparser.c_ast.Constant):
                value = generate_constant_value(stmt.args.exprs[1].value)
            else:
                value = get_address(stmt.args.exprs[1], state).dereference()

            if isinstance(stmt.args.exprs[0], pycparser.c_ast.Constant):
                print_string = stmt.args.exprs[0].value % (value.data)
            elif isinstance(stmt.args.exprs[0], pycparser.c_ast.Cast):
                # TODO cast the value not just grab from cast object
                print_string = stmt.args.exprs[0].expr.value % (value.data) #still a work around
            else:
                raise Exception("logging.debug does not know how to handle "+str(stmt.args.exprs[0]))

            print_string = print_string[1:][:-1] #drop quotes
            print(print_string.replace("\\n", "\n"), end="") #convert newlines
            successors.append(get_next(state))
        elif stmt.name.name == "malloc":

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
        logging.debug("FuncDecl")
        raise Exception("FuncDecl out of Global scope")
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        logging.debug("FuncDef")
        raise Exception("FuncDef out of Global scope")
    elif isinstance(stmt, pycparser.c_ast.Goto):
        logging.debug('Goto')
        label_to = LinkSearch.label_lut[stmt.name]
        body = label_to
        while not isinstance(body, pycparser.c_ast.Compound):
            index = LinkSearch.index_lut[body]
            body = LinkSearch.parent_lut[body]
        new_ctrl = Ctrl(index, body)
        logging.debug('\t Body: '+str(body))
        if body in LinkSearch.envr_lut:
            new_envr = LinkSearch.envr_lut[body]
        else:
            new_envr = state.envr
            logging.error('Need to make decisions on scope of forward jump')
            #raise Exception("Need to make decisions on scope of forward jump")

        successors.append(State(new_ctrl, new_envr, state.stor, state.kont))
    elif isinstance(stmt, pycparser.c_ast.ID):
        logging.debug("ID "+stmt.name)
        name = stmt.name
        address = state.envr.get_address(name)
        #value = address.dereference()
        value = state.stor.read(address.data)
        if value is None:
            raise Exception(name + ": " + str(state.stor.memory))
        if isinstance(state.kont, FunctionKont): #Don't return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        logging.error("IdentifierType should not appear on there own")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.If):
        # logging.debug("If")
        new_kont = IfKont(state, stmt.iftrue, stmt.iffalse)
        new_ctrl = Ctrl(stmt.cond)
        successors.append(State(new_ctrl, state.envr, state.stor, new_kont))
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO transform nested
        # Init list is tranformed
        logging.error("InitList")
        raise Exception("Initilizer List is not implemented")
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
        logging.error("PtrDecl should not appear outside of a decl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Return):
        # logging.debug("Return")
        exp = stmt.expr
        successors.append(handle_return(exp, state))
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO decide what to do with structs as a whole
        # logging.debug("Struct")
        struct = stmt
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO transform to pointer arithmetic to avoid intermediate value
        logging.debug("StructRef")
        ref_address = get_address(stmt,state)
        value = ref_address.dereference()
        
        if isinstance(state.kont, FunctionKont):
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state,value))
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO tranform out
        # logging.debug("Switch")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        logging.error("TernaryOp should be removed by transform")
        raise Exception("TernaryOp should have been removed in the transforms")
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # logging.debug("TypeDecl")
        raise Exception("TypeDecl should have been found as child of Decl")
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        # logging.debug("Typedef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Typename):
        logging.error("Typename should appear only nested inside another type")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        logging.debug("UnaryOp "+stmt.op)
        opr = stmt.op
        expr = stmt.expr
        successors.append(handle_unary_op(opr, expr, state))
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        # logging.debug("Union")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.While):
        logging.error("While should be removed in the transform")
        raise Exception("While should be removed in the transform")
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
                                 pycparser.c_ast.PtrDecl))):       
        ref_address = state.stor.get_next_address() #Pointer type is returned
        state.envr.map_new_identifier(name, ref_address)       #the address is mapped then if additional space is need for a struct handle decl struct manages it 

        if (isinstance(decl.type.type, pycparser.c_ast.Struct) 
                    and isinstance(decl.type, pycparser.c_ast.TypeDecl)):
            handle_decl_struct(decl.type.type, ref_address, state)
                
    elif isinstance(decl.type, pycparser.c_ast.ArrayDecl):
        ref_address = state.stor.get_next_address()
        data_address = handle_decl_array(decl.type, [], state)
        state.envr.map_new_identifier(decl.name, ref_address)
        state.stor.write(ref_address,data_address)
        logging.debug(" Mapped "+str(name)+" to "+str(ref_address))
        if decl.init is not None:
            # TODO if init evaluates to an address don't allocate just
            # assign
            raise Exception("array init not yet implemented")
        
    else:
        raise Exception("Declarations of " + str(decl.type) +
                        " are not yet implemented")

    return state

def handle_decl_array(array, list_of_sizes, state):
    """Calculates size and allocates Array. Returns address of first item"""
    logging.debug('  Array Decl')
    if isinstance(array.type, pycparser.c_ast.ArrayDecl):
        #Recursively add sizes array to list
        size = generate_constant_value(array.dim.value).data
        if size < 1:
            raise Exception("Non-positive Array Sizes are not supported")
        list_of_sizes.append(size)
        return handle_decl_array(array.type, ref_address, list_of_sizes, state)

    elif isinstance(array.type, pycparser.c_ast.TypeDecl):
        if isinstance(array.dim,pycparser.c_ast.Constant):
            size = generate_constant_value(array.dim.value).data
        elif isinstance(array.dim,pycparser.c_ast.ID):
            size = get_address(array.dim,state).dereference().data
        else:
            raise Exception("Unsupported ArrayDecl dimension "+str(array.dim))

        if size < 1:
            raise Exception("Non-positive Array Sizes are not supported")
        list_of_sizes.append(size)
        #List of sizes populated: allocate the array

        length = reduce(lambda x, y: x*y, list_of_sizes) #multiply all together
        data_address = state.stor.allocate_block(length)
        logging.debug('   Generated array of size '+str(list_of_sizes))
        #Allocated block: passing back the Array object that points to block

        # TODO handle array of structs
        if isinstance(array.type.type, pycparser.c_ast.Struct):
            for offset in range(length):
                handle_decl_struct(array.type.type, data_address+offset, state)

        return data_address
    else:
        raise Exception("Declarations of " + str(array.type) +
                        " are not yet implemented")

def handle_decl_struct(struct, ref_address, state):
    """Handles struct declaration"""
    if struct.name in LinkSearch.struct_lut:
        struct = LinkSearch.struct_lut[struct.name]
    else:
        raise Exception('Struct '+struct.name+' not found')

    length = len(struct.decls)
    data_address = state.stor.allocate_block(length)

    logging.debug('\t\tMade new struct: '+str(struct.name)
                  +' at '+str(ref_address.data))
    #todo handle struct or an array within a struct
    new_struct = generate_struct(data_address, struct.decls, state.stor)
    state.stor.write(ref_address, new_struct)

    offset = 0
    for decl in struct.decls:
        #logging.debug('     DeclType: '+str(decl.type.type.names))
        if (isinstance(decl.type, pycparser.c_ast.TypeDecl)
                and isinstance(decl.type.type, pycparser.c_ast.Struct)):
            handle_decl_struct(decl.type.type, data_address+offset, state)
        elif isinstance(decl.type, pycparser.c_ast.ArrayDecl):
            arr_address = handle_decl_array(decl.type, [], state)
            state.stor.write(data_address+offset,arr_address)
        offset += 1   
        #if is instance array handle array

    return ref_address

def handle_unary_op(opr, expr, state): #pylint: disable=inconsistent-return-statements
    """decodes and evaluates unary_ops"""

    if isinstance(state.kont, FunctionKont): #don't return to function
        return get_next(state)

    if opr == "&":
        value = get_address(expr, state)
        return state.kont.satisfy(state, value)
    elif opr == "*":
        if isinstance(expr,pycparser.c_ast.ID):
            address = state.envr.get_address(expr)
            pointer = address.dereference()
            value = pointer.dereference()
        elif isinstance(expr,pycparser.c_ast.UnaryOp) and expr.op == "&":
            address = get_address(expr.expr,state)
            value = address.dereference()
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

def get_address(reference, state):
    """get_address"""
    if isinstance(reference, pycparser.c_ast.ID):
        ident = reference
        return state.envr.get_address(ident.name)

    elif isinstance(reference, pycparser.c_ast.ArrayRef):
        list_of_index = []
        array_ptr = get_address(reference.name, state)
        array = array_ptr.dereference()

        if isinstance(reference.subscript, pycparser.c_ast.ID):
            address = state.envr.get_address(reference.subscript.name)
            index = address.dereference().data
        elif isinstance(reference.subscript, pycparser.c_ast.Constant):
            index = generate_constant_value(reference.subscript.value).data
            #why not just = array.subscript.value
        else:
            raise Exception("Array subscripts of type " +
                            str(reference.subscript) +
                            "are not yet implemented")
        
        list_of_index.insert(0, index) 
                                
        return array.index_for_address(list_of_index)

    elif isinstance(reference, pycparser.c_ast.UnaryOp):
        unary_op = reference
        if unary_op.op == "*":
            name = unary_op.expr
            if isinstance(name, pycparser.c_ast.ID):
                pointer = state.envr.get_address(name)
                return pointer.dereference()
            elif isinstance(name, pycparser.c_ast.UnaryOp) and name.op == "&":
                return get_address(name.expr,state) #They cancel out
            else:
                raise Exception("Unknown Case for get address UnaryOp")   
        else:
            raise Exception("Unsupported UnaryOp lvalue in assignment: "
                            + unary_op.op)

    elif isinstance(reference, pycparser.c_ast.StructRef):
        ref = reference
        struct_ptr = get_address(ref.name, state)
        struct = struct_ptr.dereference()
        address = struct.get_value(ref.field.name)

        return address

    #elif isinstance(reference, pycparser.c_ast.Struct):
    #    logging.debug('Assign struct')
    else:
        raise Exception("unsupported assign lvalue: " + str(reference))


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
