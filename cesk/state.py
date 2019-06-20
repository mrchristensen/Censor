"""CESK states and an error state variant."""

import logging
import pycparser.c_ast as AST
import cesk.linksearch as ls
from cesk.values import generate_constant_value
from cesk.values import cast
import cesk.config as cnf
from cesk.exceptions import UnknownConfiguration, CESKException
from cesk.structures import FrameAddress
from cesk.interpret import get_int_data

class State:
    """Holds a program state"""
    #ctrl = None #control
    #envr = None  #environment
    #stor = None #store
    #kont_addr = None #k(c)ontinuation Address
    #time_stamp = None

    _time = 0

    none = lambda state: frozenset()
    if_branches = lambda state: state.get_addresses(state.ctrl.stmt.cond)
    id_addresses = lambda state: \
        frozenset([state.get_address(state.ctrl.stmt)[0]])
    expr_addresses = lambda state: state.get_address(state.ctrl.stmt.expr)
    binop_addresses = lambda state: (state.get_address(state.ctrl.stmt.left) |
                                     state.get_address(state.ctrl.stmt.right))
    assign_addresses = lambda state: state.get_address(state.ctrl.stmt.rvalue)

    branch_funs = {
        'Label' : none,
        'If' : if_branches,
        'ID' : none,
        'Goto' : none,
        'FuncCall' : none,
        'EmptyStatement' : none,
        'Decl' : none,
        'Constant' : none,
        'Compound' : none,
        'Cast' : none,
        'BinaryOp' : none,
        'Assignment' : none,
        'UnaryOp' : none,
        'Return' : none,
    }

    address_funs = {
        'Label' : none,
        'If' : if_branches,
        'ID' : id_addresses,
        'Goto' : none,
        'FuncCall' : none,
        'EmptyStatement' : none,
        'Decl' : none,
        'Constant' : none,
        'Compound' : none,
        'Cast' : expr_addresses,
        'BinaryOp' : binop_addresses,
        'Assignment' : assign_addresses,
        'UnaryOp' : expr_addresses,
        'Return' : expr_addresses,
    }

    def __init__(self, ctrl, envr, stor, kont_addr):
        self.set_ctrl(ctrl)
        self.set_envr(envr)
        self.set_stor(stor)
        self.set_kont_addr(kont_addr)
        self.tick()
        self.e_p = None

    def set_ctrl(self, ctrl):
        """attaches a control object to the state"""
        self.ctrl = ctrl

    def set_envr(self, envr):
        """attaches an environment object to the state"""
        self.envr = envr

    def set_stor(self, stor):
        """attaches a stor object to the state"""
        self.stor = stor

    def set_kont_addr(self, kont_addr):
        """attaches a kont_addr object to the state"""
        self.kont_addr = kont_addr

    def get_kont(self):
        '''returns kont'''
        if self.kont_addr == 0:
            return None #halt kont
        else:
            return self.stor.read_kont(self.kont_addr)

    def get_next(self):
        """ Moves the ctrl and returns the new state """
        next_ctrl = self.ctrl.get_next()
        return State(next_ctrl, self.envr, self.stor, self.kont_addr)

    def get_error(self, err_str):
        """ generates an error state based on current state """
        return ErrorState(self, err_str)

    def tick(self):
        """ Sets the time stamp for the state """
        if cnf.CONFIG['tick'] == 'concrete':
            State._time += 1
            self.time_stamp = State._time
        elif cnf.CONFIG['tick'] == 'abstract':
            if self.stor is None:
                self.time_stamp = State._time
            else:
                self.time_stamp = self.stor.get_time()
        elif cnf.CONFIG['tick'] == 'trivial':
            self.time_stamp = State._time
        else:
            raise UnknownConfiguration('tick')

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.ctrl == other.ctrl and
                self.envr == other.envr and
                self.kont_addr == other.kont_addr)

    def __hash__(self):
        result = hash(self.ctrl)
        result = result * hash(self.envr) + 37
        result = result * hash(self.kont_addr) + 17
        return result

    def __str__(self):
        return (str(self.ctrl)+"\n"+
                str(self.envr)+"\n"+
                "ka "+str(self.kont_addr)).replace(':', ' ')

    def get_array_length(self, array):
        """Calculates size and allocates Array. Returns address of first item"""
        logging.debug('  Array Decl')
        if isinstance(array.type, AST.ArrayDecl):
            raise CESKException("All arrays should have a single dimension")
        elif isinstance(array.type, (AST.TypeDecl, AST.PtrDecl)):
            if isinstance(array.dim, (AST.Constant, AST.ID)):
                value, _ = self.get_value(array.dim)
                #never should get an err when reading an id
                length = get_int_data(value) #support for abstract type
            else:
                raise CESKException("Index %i is out of bounds" % array.dim)

            if length < 1:
                raise CESKException("Array size must be positive")
                # could implement arrays of size 0

            return length
        else:
            raise CESKException("Declarations of " + str(array.type) +
                                " are not yet implemented")

    def get_value(self, stmt): #pylint: disable=too-many-return-statements
        """Compute the value of an expression."""
        if isinstance(stmt, AST.Constant):
            value = generate_constant_value(stmt.value, stmt.type)
            return value, set()
        elif isinstance(stmt, AST.ID):
            return self.stor.read(self.get_address(stmt)[0])
        elif isinstance(stmt, AST.Cast):
            logging.debug(stmt.expr)
            value, errors = self.get_value(stmt.expr)
            value = cast(value, stmt.to_type, self)
            return value, errors
        elif isinstance(stmt, AST.BinaryOp):
            left, errors = self.get_value(stmt.left)
            right, errs = self.get_value(stmt.right)
            errors.update(errs)
            result = left.perform_operation(stmt.op, right)
            logging.debug("\tBinop: %s %s %s", str(left), stmt.op, str(right))
            logging.debug("\t\t= %s size %d", str(result), result.size)
            return result, errors
        elif isinstance(stmt, AST.UnaryOp) and stmt.op == '&':
            value, errors = self.get_address(stmt.expr)
            if isinstance(value, FrameAddress):
                value = self.stor.fa2ptr(value)
            return value, errors
        elif isinstance(stmt, AST.UnaryOp) and stmt.op == '*':
            address, errors = self.get_address(stmt)
            value, errs = self.stor.read(address)
            errors.update(errs)
            return value, errors
        else:
            if isinstance(stmt, AST.FuncCall):
                name = stmt.name.name + "()"
            else:
                name = stmt.__class__.__name__
            raise CESKException("Cannot get value from %s" % name)

    def get_address(self, reference):
        # pylint: disable=too-many-branches
        """get_address"""
        if isinstance(reference, AST.ID):
            ident = reference
            while not isinstance(ident, str):
                ident = ident.name
            if ident not in self.envr:
                checked_decl = ls.check_for_implicit_decl(ident)
                if checked_decl is not None:
                    logging.debug("Found implicit decl: %s", checked_decl.name)
                    self.decl_helper(checked_decl)
                else:
                    raise CESKException("Decl for %s not found"%(ident))
            return self.envr.get_address(ident), set()

        elif isinstance(reference, AST.ArrayRef):
            raise CESKException("ArrayRef should be transformed")

        elif isinstance(reference, AST.UnaryOp):
            unary_op = reference
            if unary_op.op == "*":
                name = unary_op.expr
                if isinstance(name, AST.ID):
                    pointer = self.envr.get_address(name)
                    return self.stor.read(pointer)
                elif isinstance(name, AST.UnaryOp) and name.op == "&":
                    return self.get_address(name.expr) #They cancel out
                elif isinstance(name, AST.Cast):
                    if isinstance(name.to_type, AST.PtrDecl):
                        to_type = name.to_type
                    elif isinstance(name.to_type, AST.Typename):
                        to_type = name.to_type.type
                    address, errors = self.get_address(name.expr)
                    address, errs = self.stor.read(address)
                    errors.update(errs)
                    address = cast(address, to_type, self)
                    return address, errors
                elif isinstance(name, AST.UnaryOp) and name.op == "*":
                    pointer, errors = self.get_value(name.expr)
                    address, errs = self.stor.read(pointer)
                    errors.update(errs)
                    return address, errors
                else:
                    raise CESKException("Unknown UnaryOp: %s" % str(name))
            else:
                raise CESKException("Unsupported UnaryOp lvalue in assignment: "
                                    + unary_op.op)

        elif isinstance(reference, AST.StructRef):
            raise CESKException("StructRef should be transformed")
        elif isinstance(reference, AST.Struct):
            # TODO
            raise NotImplementedError("Structs as values, not containers")
        else:
            raise CESKException("Unsupported lvalue " + str(reference))

    def decl_helper(self, decl):
        """Maps the identifier to a new address and passes assignment part"""
        name = decl.name
        f_addr = self.envr.map_new_identifier(name)

        length = 1
        size = []
        if isinstance(decl.type, AST.ArrayDecl):
            length = self.get_array_length(decl.type)
            ls.get_sizes(decl.type.type, size)
            if decl.init:
                raise CESKException("array init should be transformed")
        else:
            ls.get_sizes(decl.type, size)

        self.stor.allocM(f_addr, size, length)
        return f_addr

    def stack_height(self, kont_addr, seen=frozenset()):
        """Get the state's stack height."""
        if kont_addr in seen:
            return None
        # TODO is this how to check for halt?
        if kont_addr == 0:
            return 0
        height = None
        konts = self.stor.read_kont(kont_addr)
        for kont in konts:
            s_h = self.stack_height(kont.kont_addr, seen + kont_addr)
            if s_h is None:
                return None
            if height:
                if s_h is height:
                    # the stack height matches what we've seen before
                    pass
                else:
                    return None
            else:
                height = s_h
        return height + 1

    # do not call this function before abstract interpretation is over!
    def get_e_p(self):
        """Compute the state's execution point, if necessary, and return it."""
        if not self.e_p:
            self.e_p = (self.ctrl, self.stack_height(self.kont_addr))
        return self.e_p

    def get_branches(self):
        """Retrieve the set of addresses that influence control flow at this
           state."""
        State.branch_funs[self.ctrl.stmt.__class__.__name__](self)

    def get_addresses(self, stmt):
        """Retrieve the set of addresses read at this state."""
        State.address_funs[stmt.__class__.__name__](self)

class ErrorState: #pylint: disable=too-few-public-methods
    """ Holds program state that errored upon execution """
    def __init__(self, state, msg): #ctrl, envr, stor, kont_addr, time_stamp):
        self.ctrl = state.ctrl
        self.envr = state.envr
        self.stor = state.stor
        self.kont_addr = state.kont_addr
        self.time_stamp = state.time_stamp
        self.message = msg

    def __eq__(self, other):
        if not isinstance(other, ErrorState):
            return False
        return (self.ctrl == other.ctrl and
                self.envr == other.envr and
                self.message == other.message and
                self.kont_addr == other.kont_addr)

    def __hash__(self):
        result = hash(self.ctrl) + 53
        result = result * hash(self.envr) + 37
        result = result * hash(self.kont_addr) + 17
        result = result * hash(self.message)
        return result

    def __str__(self):
        return ("Error in "+str(self.envr)+"\nat "+str(self.ctrl)+"\n"+
                "to "+str(self.kont_addr)).replace(':', ' ')+"\n"+self.message

    def get_e_p(self):
        """Get an execution point for the error state."""
        return (None, 0)

    def get_branches(self):
        """Retrieve the set of addresses that influence control flow at the
           error state."""
        return frozenset()
