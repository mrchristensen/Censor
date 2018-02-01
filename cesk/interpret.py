"""Functions to interpret c code directly"""

import copy
import pycparser
import cesk.structures

def execute(state):
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    """Takes a state evaluates the stmt from ctrl and returns a set of
    states"""
    successors = []
    stmt = state.ctrl.stmt()

    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        # TODO
        print("ArrayDecl")
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        print("ArrayRef")
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # TODO
        print("Assignment")
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        # TODO
        print("BinaryOp")
    elif isinstance(stmt, pycparser.c_ast.Break):
        # TODO
        print("Break")
    elif isinstance(stmt, pycparser.c_ast.Case):
        # TODO
        print("Case")
    elif isinstance(stmt, pycparser.c_ast.Cast):
        # TODO
        print("Cast")
    elif isinstance(stmt, pycparser.c_ast.Compound):
        # TODO
        print("Compound")
    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        # TODO
        print("CompoundLiteral")
    elif isinstance(stmt, pycparser.c_ast.Constant):
        # TODO
        print("Constant")
    elif isinstance(stmt, pycparser.c_ast.Continue):
        # TODO
        print("Continue")
    elif isinstance(stmt, pycparser.c_ast.Decl):
        # TODO
        print("Decl")
        new_ctrl = get_next(state.ctrl)

        new_envr = copy.deepcopy(state.envr)
        new_address = state.stor.get_next_address()
        new_envr.map_new_identifier(stmt.name, new_address)

        new_stor = copy.deepcopy(state.stor)
        new_stor.write(new_address, stmt.init)

        successors.append(cesk.structures.State(new_ctrl, new_envr, new_stor))

        return successors
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # TODO
        print("DeclList")
    elif isinstance(stmt, pycparser.c_ast.Default):
        # TODO
        print("Default")
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        # TODO
        print("DoWhile")
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        # TODO
        print("EllipsisParam")
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        # TODO
        print("EmptyStatement")
    elif isinstance(stmt, pycparser.c_ast.Enum):
        # TODO
        print("Enum")
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        # TODO
        print("Enumerator")
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        # TODO
        print("EnumeratorList")
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        # TODO
        print("ExprList")
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        # TODO
        print("FileAST")
    elif isinstance(stmt, pycparser.c_ast.For):
        # TODO
        print("For")
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        # TODO
        print("FuncCall")
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        # TODO
        print("FuncDecl")
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        # TODO
        print("FuncDef")
    elif isinstance(stmt, pycparser.c_ast.Goto):
        # TODO
        print("Goto")
    elif isinstance(stmt, pycparser.c_ast.ID):
        # TODO
        print("ID")
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        # TODO
        print("IdentifierType")
    elif isinstance(stmt, pycparser.c_ast.If):
        # TODO
        print("If")
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO
        print("InitList")
    elif isinstance(stmt, pycparser.c_ast.Label):
        # TODO
        print("Label")
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        # TODO
        print("NamedInitializer")
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        # TODO
        print("ParamList")
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        # TODO
        print("PtrDecl")
    elif isinstance(stmt, pycparser.c_ast.Return):
        # TODO
        print("Return")
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO
        print("Struct")
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO
        print("StructRef")
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO
        print("Switch")
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        # TODO
        print("TernaryOp")
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # TODO
        print("TypeDecl")
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        print("Typedef")
    elif isinstance(stmt, pycparser.c_ast.Typename):
        # TODO
        print("Typename")
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        # TODO
        print("UnaryOp")
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        print("Union")
    elif isinstance(stmt, pycparser.c_ast.While):
        # TODO
        print("While")
    elif isinstance(stmt, pycparser.c_ast.Pragma):
        # TODO
        print("Pragma")
    # DEBUG CODE TO REMOVE SOON
    elif stmt is None:
        return successors
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))

    new_ctrl = get_next(state.ctrl)
    successors.append(cesk.structures.State(new_ctrl, state.envr, state.stor))

    return successors

def get_next(ctrl):
    """takes ctrl and returns a Ctrl for the next statment to execute"""
    if len(ctrl.function.body.block_items) <= ctrl.index + 1:
        return None
    return ctrl + 1
