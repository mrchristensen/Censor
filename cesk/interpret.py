"""Functions to interpret c code directly"""

import copy
import pycparser
from cesk.values import generate_constant_value

def execute(state):
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # pylint: disable=fixme
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states"""
    successors = []
    stmt = state.ctrl.stmt()

    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        # TODO
        #print("ArrayDecl")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        #print("ArrayRef")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # TODO
        #print("Assignment")
        state = generate_default_kont_state(state)
        ident = stmt.lvalue
        exp = stmt.rvalue
        successors.append(handle_assignment(stmt.op, ident, exp, state))
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        # TODO
        #print("BinaryOp")
        state = generate_default_kont_state(state)
        new_kont = LeftBinopKont(stmt.op, stmt.right, state.kont)
        successors.append(State(Ctrl(stmt.left), state.envr, state.stor,
                                new_kont))
    elif isinstance(stmt, pycparser.c_ast.Break):
        # TODO
        #print("Break")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Case):
        # TODO
        #print("Case")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Cast):
        # TODO
        #print("Cast")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Compound):
        # TODO
        #print("Compound")
        state = generate_default_kont_state(state)
        new_ctrl = Ctrl(0, stmt)
        new_envr = Envr(state.envr) #make blank env at head of linked list
        new_kont = DefaultKont(state)
        if stmt.block_items is None:
            successors.append(new_kont.satisfy(state))
        else:
            successors.append(State(new_ctrl, new_envr, state.stor, new_kont))

    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        # TODO
        #print("CompoundLiteral")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Constant):
        # TODO
        #print("Constant")
        state = generate_default_kont_state(state)
        value = generate_constant_value(stmt.value)
        successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.Continue):
        # TODO
        #print("Continue")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Decl):
        # TODO
        #print("Decl")
        state = generate_default_kont_state(state)
        type_of = stmt.type
        ident = stmt
        exp = stmt.init
        successors.append(handle_decl(type_of, ident, exp, state))
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # TODO
        #print("DeclList")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Default):
        # TODO
        #print("Default")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        # TODO
        #print("DoWhile")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        # TODO
        #print("EllipsisParam")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        # TODO
        #print("EmptyStatement")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Enum):
        # TODO
        #print("Enum")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        # TODO
        #print("Enumerator")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        # TODO
        #print("EnumeratorList")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        # TODO
        #print("ExprList")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        # TODO
        #print("FileAST")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.For):
        # TODO
        #print("For")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        # TODO
        #print("FuncCall")
        state = generate_default_kont_state(state)
        if stmt.name.name == "printf":
            id_to_print = stmt.args.exprs[1].name #FIXME should evalueate exp
            address = state.envr.get_address(id_to_print)
            value = state.stor.read(address)
            print(value.data)
        else:
            print(stmt.name.name)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        # TODO
        #print("FuncDecl")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        # TODO
        #print("FuncDef")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Goto):
        # TODO
        #print("Goto")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.ID):
        # TODO
        #print("ID")
        state = generate_default_kont_state(state)
        name = stmt.name
        address = state.envr.get_address(name)
        value = state.stor.read(address)
        successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        # TODO
        #print("IdentifierType")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.If):
        # TODO
        #print("If")
        state = generate_default_kont_state(state)
        new_kont = IfKont(state, stmt.iftrue, stmt.iffalse)
        new_ctrl = Ctrl(stmt.cond)
        successors.append(State(new_ctrl, state.envr, state.stor, new_kont))
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO
        #print("InitList")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Label):
        # TODO
        #print("Label")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        # TODO
        #print("NamedInitializer")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        # TODO
        #print("ParamList")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        # TODO
        #print("PtrDecl")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Return):
        # TODO
        #print("Return")
        exp = stmt.expr
        successors.append(handle_return(exp, state))
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO
        #print("Struct")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO
        #print("StructRef")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO
        #print("Switch")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        # TODO
        #print("TernaryOp")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # TODO
        #print("TypeDecl")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        #print("Typedef")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Typename):
        # TODO
        #print("Typename")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        # TODO
        #print("UnaryOp")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        #print("Union")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.While):
        # TODO
        #print("While")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    elif isinstance(stmt, pycparser.c_ast.Pragma):
        # TODO
        #print("Pragma")
        state = generate_default_kont_state(state)
        successors.append(state.kont.satisfy(state))
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))

    return successors

def handle_assignment(operator, ident, exp, state):
    """Creates continuation to evalueate exp and assigns resulting value to the
    address associated with ident"""
    #pylint: disable=too-many-function-args
    if operator == '=':
        new_ctrl = Ctrl(exp) #build special ctrl for exp
        new_kont = AssignKont(ident.name, state)
    elif operator == "+=":
        assign_kont = AssignKont(ident.name, state)
        new_kont = LeftBinopKont("+", exp, assign_kont)
        new_ctrl = Ctrl(ident)
    elif operator == "*=":
        assign_kont = AssignKont(ident.name, state)
        new_kont = LeftBinopKont("*", exp, assign_kont)
        new_ctrl = Ctrl(ident)
    else:
        raise Exception(operator + " is not yet implemented")
    return State(new_ctrl, state.envr, state.stor, new_kont)

def handle_decl(type_of, ident, exp, state): # pylint: disable=unused-argument
    """Maps the identifier to a new address and passes assignment part"""

    # type_of ident = exp;
    #map new ident
    if state.envr.is_localy_defined(ident.name):
        raise Exception("Error: redefinition of " + ident.name)
    new_envr = copy.deepcopy(state.envr)
    new_address = state.stor.get_next_address()
    new_envr.map_new_identifier(ident.name, new_address)

    if exp is not None:
        new_state = State(state.ctrl, new_envr, state.stor, state.kont)
        return handle_assignment("=", ident, exp, new_state)
    #case: type_of ident;
    return state.kont.satisfy(new_state)

def handle_return(exp, state):
    """makes a ReturnKont to pass a value to the parrent kont"""
    if isinstance(state.kont, DefaultKont):
        returnable_kont = ReturnKont(state.kont.get_returnable())
    else:
        returnable_kont = ReturnKont(state.kont)
    if exp is None:
        return returnable_kont.satisfy(state)
    return State(Ctrl(exp), state.envr, state.stor, returnable_kont)

def generate_default_kont_state(state):
    """If the states continuation requires a return statement we generate this
    default kont to prevent incorect returns"""
    if isinstance(state.kont, (Halt, VoidKont)):
        default_kont = DefaultKont(state)
        return State(state.ctrl, state.envr, state.stor, default_kont)
    return state

# imports are down here to allow for circular dependencies between structures.py and interpret.py
from cesk.structures import State, Ctrl, Envr, AssignKont, DefaultKont, Halt, ReturnKont, VoidKont # pylint: disable=wrong-import-position
from cesk.structures import LeftBinopKont, IfKont # pylint: disable=wrong-import-position
