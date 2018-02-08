"""Functions to interpret c code directly"""

import copy
import pycparser
from cesk.values import generate_value

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
        pass #print("ArrayDecl")
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        pass #print("ArrayRef")
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # TODO
        #print("Assignment")
        if stmt.op != '=':
            raise Exception(stmt.op + " is not yet implemented")
        ident = stmt.lvalue
        exp = stmt.rvalue
        successors.append(handle_assignment(ident, exp, state))
        return successors
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        # TODO
        #print("BinaryOp")
        new_kont = LeftBinopKont(stmt.op, stmt.right, state.kont)
        successors.append(State(Ctrl(stmt.left), state.envr, state.stor,
                                new_kont))
        return successors
    elif isinstance(stmt, pycparser.c_ast.Break):
        # TODO
        pass #print("Break")
    elif isinstance(stmt, pycparser.c_ast.Case):
        # TODO
        pass #print("Case")
    elif isinstance(stmt, pycparser.c_ast.Cast):
        # TODO
        pass #print("Cast")
    elif isinstance(stmt, pycparser.c_ast.Compound):
        # TODO
        pass #print("Compound")
    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        # TODO
        pass #print("CompoundLiteral")
    elif isinstance(stmt, pycparser.c_ast.Constant):
        # TODO
        #print("Constant")
        value = generate_value(stmt)
        successors.append(state.kont.satisfy(value, state))
        return successors
    elif isinstance(stmt, pycparser.c_ast.Continue):
        # TODO
        pass #print("Continue")
    elif isinstance(stmt, pycparser.c_ast.Decl):
        # TODO
        #print("Decl")
        type_of = stmt.type
        ident = stmt.name
        exp = stmt.init
        successors.append(handle_decl(type_of, ident, exp, state))
        return successors
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # TODO
        pass #print("DeclList")
    elif isinstance(stmt, pycparser.c_ast.Default):
        # TODO
        pass #print("Default")
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        # TODO
        pass #print("DoWhile")
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        # TODO
        pass #print("EllipsisParam")
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        # TODO
        pass #print("EmptyStatement")
    elif isinstance(stmt, pycparser.c_ast.Enum):
        # TODO
        pass #print("Enum")
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        # TODO
        pass #print("Enumerator")
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        # TODO
        pass #print("EnumeratorList")
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        # TODO
        pass #print("ExprList")
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        # TODO
        pass #print("FileAST")
    elif isinstance(stmt, pycparser.c_ast.For):
        # TODO
        pass #print("For")
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        # TODO
        #print("FuncCall")
        if stmt.name.name == "printf":
            id_to_print = stmt.args.exprs[1].name #FIXME should evalueate exp
            address = state.envr.get_address(id_to_print)
            value = state.stor.read(address)
            print(value.data)
        else:
            print(stmt.name.name)
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        # TODO
        pass #print("FuncDecl")
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        # TODO
        pass #print("FuncDef")
    elif isinstance(stmt, pycparser.c_ast.Goto):
        # TODO
        pass #print("Goto")
    elif isinstance(stmt, pycparser.c_ast.ID):
        # TODO
        #print("ID")
        name = stmt.name
        address = state.envr.get_address(name)
        value = state.stor.read(address)
        successors.append(state.kont.satisfy(value, state))
        return successors
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        # TODO
        pass #print("IdentifierType")
    elif isinstance(stmt, pycparser.c_ast.If):
        # TODO
        pass #print("If")
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO
        pass #print("InitList")
    elif isinstance(stmt, pycparser.c_ast.Label):
        # TODO
        pass #print("Label")
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        # TODO
        pass #print("NamedInitializer")
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        # TODO
        pass #print("ParamList")
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        # TODO
        pass #print("PtrDecl")
    elif isinstance(stmt, pycparser.c_ast.Return):
        # TODO
        #print("Return")
        exp = stmt.expr
        #pass exp parrent continuation
        successors.append(State(Ctrl(exp), state.envr, state.stor, state.kont))
        return successors
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO
        pass #print("Struct")
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO
        pass #print("StructRef")
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO
        pass #print("Switch")
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        # TODO
        pass #print("TernaryOp")
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # TODO
        pass #print("TypeDecl")
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        pass #print("Typedef")
    elif isinstance(stmt, pycparser.c_ast.Typename):
        # TODO
        pass #print("Typename")
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        # TODO
        pass #print("UnaryOp")
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        pass #print("Union")
    elif isinstance(stmt, pycparser.c_ast.While):
        # TODO
        pass #print("While")
    elif isinstance(stmt, pycparser.c_ast.Pragma):
        # TODO
        pass #print("Pragma")
    # DEBUG CODE TO REMOVE SOON
    elif stmt is None:
        return successors
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))

    new_ctrl = get_next(state.ctrl)
    successors.append(State(new_ctrl, state.envr, state.stor,
                            state.kont))

    return successors

def get_next(ctrl):
    """takes ctrl and returns a Ctrl for the next statment to execute"""
    if len(ctrl.function.body.block_items) <= ctrl.index + 1:
        return None
    return ctrl + 1

def handle_assignment(ident, exp, state):
    """Creates continuation to evalueate exp and assigns resulting value to the
    address associated with ident"""
    #pylint: disable=too-many-function-args

    # ident = exp;

    address = state.envr.get_address(ident) #look up address
    new_ctrl = Ctrl(exp) #build special ctrl for exp

    return_ctrl = get_next(state.ctrl) #calculate where to go once complete
    new_kont = AssignKont(address, return_ctrl, state.kont)
    return State(new_ctrl, state.envr, state.stor, new_kont)

def handle_decl(type_of, ident, exp, state): # pylint: disable=unused-argument
    """Maps the identifier to a new address and passes assignment part"""

    # type_of ident = exp;
    #map new ident
    new_envr = copy.deepcopy(state.envr)
    new_address = state.stor.get_next_address()
    new_envr.map_new_identifier(ident, new_address)

    if exp is not None:
        new_state = State(state.ctrl, new_envr, state.stor, state.kont)
        return handle_assignment(ident, exp, new_state)
    #case: type_of ident;
    return State(get_next(state.ctrl), new_envr, state.stor, state.kont)


# imports are down here to allow for circular dependencies between structures.py and interpret.py
from cesk.structures import State, Ctrl, AssignKont # pylint: disable=wrong-import-position
from cesk.structures import LeftBinopKont # pylint: disable=wrong-import-position
