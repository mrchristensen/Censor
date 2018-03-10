"""Functions to interpret c code directly"""

import pycparser
from cesk.values import generate_constant_value

class LinkSearch(pycparser.c_ast.NodeVisitor):
    """NodeTransformer to link children nodes to parents"""
    parent_lut = {}
    index_lut = {}
    label_lut = {}
    envr_lut = {}

    def generic_visit(self, node):

        if isinstance(node, pycparser.c_ast.Label):
            if node.name in LinkSearch.label_lut:
                raise Exception("Duplicate label name")
            LinkSearch.label_lut[node.name] = node

        for i, child in enumerate(node):
            if isinstance(child, pycparser.c_ast.Node):
                if child in LinkSearch.parent_lut:
                    raise Exception("Node duplicated in tree")
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
        # TODO
        #print("ArrayDecl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        #print("ArrayRef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # TODO
        #print("Assignment")
        ident = stmt.lvalue
        exp = stmt.rvalue
        successors.append(handle_assignment(stmt.op, ident, exp, state))
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        # TODO
        #print("BinaryOp")
        new_kont = LeftBinopKont(state, stmt.op, stmt.right, state.kont)
        successors.append(State(Ctrl(stmt.left), state.envr, state.stor,
                                new_kont))
    elif isinstance(stmt, pycparser.c_ast.Break):
        # TODO
        #print("Break")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Case):
        # TODO
        #print("Case")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Cast):
        # TODO
        #print("Cast")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Compound):
        # TODO
        #print("Compound")
        new_ctrl = Ctrl(0, stmt)
        if stmt in LinkSearch.envr_lut:
            new_envr = LinkSearch.envr_lut[stmt]
        else:
            new_envr = Envr(state.envr) #make blank env at head of linked list
            LinkSearch.envr_lut[stmt] = new_envr
        if stmt.block_items is None:
            successors.append(get_next(state))
        else:
            successors.append(State(new_ctrl, new_envr, state.stor, state.kont))

    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        # TODO
        #print("CompoundLiteral")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Constant):
        # TODO
        #print("Constant")
        value = generate_constant_value(stmt.value)
        if isinstance(state.kont, FunctionKont): #dont return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.Continue):
        # TODO
        #print("Continue")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Decl):
        # TODO
        #print("Decl")
        type_of = stmt.type
        ident = stmt
        exp = stmt.init
        successors.append(handle_decl(type_of, ident, exp, state))
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        # TODO
        #print("DeclList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Default):
        # TODO
        #print("Default")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        # TODO
        #print("DoWhile")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        # TODO
        #print("EllipsisParam")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        # TODO
        #print("EmptyStatement")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Enum):
        # TODO
        #print("Enum")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Enum):
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        # TODO
        #print("Enumerator")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        # TODO
        #print("EnumeratorList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        # TODO
        #print("ExprList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        # TODO
        #print("FileAST")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.For):
        # TODO
        #print("For")
        successors.append(get_next(state))
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
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        # TODO
        #print("FuncDecl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        # TODO
        #print("FuncDef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Goto):
        # TODO
        #print("Goto")
        label_to = LinkSearch.label_lut[stmt.name]
        body = label_to
        while not isinstance(body, pycparser.c_ast.Compound):
            index = LinkSearch.index_lut[body]
            body = LinkSearch.parent_lut[body]
        new_ctrl = Ctrl(index, body)
        new_envr = state.envr
        if body in LinkSearch.envr_lut:
            new_envr = LinkSearch.envr_lut[body]
        successors.append(State(new_ctrl, new_envr, state.stor, state.kont))
    elif isinstance(stmt, pycparser.c_ast.ID):
        # TODO
        #print("ID")
        name = stmt.name
        address = state.envr.get_address(name)
        value = state.stor.read(address)
        if isinstance(state.kont, FunctionKont): #dont return to function
            successors.append(get_next(state))
        else:
            successors.append(state.kont.satisfy(state, value))
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        # TODO
        #print("IdentifierType")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.If):
        # TODO
        #print("If")
        new_kont = IfKont(state, stmt.iftrue, stmt.iffalse)
        new_ctrl = Ctrl(stmt.cond)
        successors.append(State(new_ctrl, state.envr, state.stor, new_kont))
    elif isinstance(stmt, pycparser.c_ast.InitList):
        # TODO
        #print("InitList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Label):
        # TODO
        #print("Label")
        body = stmt
        while not isinstance(body, pycparser.c_ast.Compound):
            body = LinkSearch.parent_lut[body]
        LinkSearch.envr_lut[body] = state.envr
        new_ctrl = Ctrl(stmt.stmt)
        successors.append(State(new_ctrl, state.envr, state.stor, state.kont))
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        # TODO
        #print("NamedInitializer")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        # TODO
        #print("ParamList")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        # TODO
        #print("PtrDecl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Return):
        # TODO
        #print("Return")
        exp = stmt.expr
        successors.append(handle_return(exp, state))
    elif isinstance(stmt, pycparser.c_ast.Struct):
        # TODO
        #print("Struct")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        # TODO
        #print("StructRef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Switch):
        # TODO
        #print("Switch")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        # TODO
        #print("TernaryOp")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        # TODO
        #print("TypeDecl")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        # TODO
        #print("Typedef")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Typename):
        # TODO
        #print("Typename")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        # TODO
        #print("UnaryOp")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Union):
        # TODO
        #print("Union")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.While):
        # TODO
        #print("While")
        successors.append(get_next(state))
    elif isinstance(stmt, pycparser.c_ast.Pragma):
        # TODO
        #print("Pragma")
        successors.append(get_next(state))
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
    else:
        raise Exception(operator + " is not yet implemented")
    return State(new_ctrl, state.envr, state.stor, new_kont)

def handle_decl(type_of, ident, exp, state): # pylint: disable=unused-argument
    """Maps the identifier to a new address and passes assignment part"""
    # type_of ident = exp;
    #map new ident
    if state.envr.is_localy_defined(ident.name):
        raise Exception("Error: redefinition of " + ident.name)
    new_envr = state.envr
    new_address = state.stor.get_next_address()
    new_envr.map_new_identifier(ident.name, new_address)

    if exp is not None:
        new_state = State(state.ctrl, new_envr, state.stor, state.kont)
        return handle_assignment("=", ident, exp, new_state)
    #case: type_of ident;
    if isinstance(state.kont, FunctionKont): #dont return to function
        return get_next(state)
    return state.kont.satisfy(state)

def handle_return(exp, state):
    """makes a ReturnKont to pass a value to the parrent kont"""
    if isinstance(state.kont, FunctionKont):
        returnable_kont = ReturnKont(state.kont)
    else:
        raise Exception("Unexpected return statement")
    if exp is None:
        if isinstance(state.kont, VoidKont):
            return state.kont.satisfy(state)
        else:
            throw("Exception: No return value was given in non-void function")
    return State(Ctrl(exp), state.envr, state.stor, returnable_kont)

def get_next(state): #pylint: disable=inconsistent-return-statements
    """takes state and returns a state with ctrl for the next statment
    to execute"""
    ctrl = state.ctrl
    if not isinstance(state.kont, FunctionKont):
        print(Exception("CESK error: called get_next in bad context"))
        print("You are probably trying to get a value from somthing that " +
              "is not implemented. Defaulting to 0")
        state.kont.satisfy(state, generate_constant_value("0"))

    if ctrl.body is not None and ctrl.index + 1 < len(ctrl.body.block_items):
        new_ctrl = ctrl + 1
        return State(new_ctrl, state.envr, state.stor, state.kont)

    if ctrl.node is not None:
        parent = LinkSearch.parent_lut[ctrl.node]
        parent_index = LinkSearch.index_lut[ctrl.node]
    else:
        parent = LinkSearch.parent_lut[ctrl.body]
        parent_index = LinkSearch.index_lut[ctrl.body]

    while not isinstance(parent, pycparser.c_ast.Compound):
        parent_index = LinkSearch.index_lut[parent]
        parent = LinkSearch.parent_lut[parent]
        if parent is None:
            if isinstance(state.kont, VoidKont):
                return state.kont.satisfy()
            else:
                raise Exception("Excpected Return Statememnt")
    parent_ctrl = Ctrl(parent_index, parent)
    new_envr = LinkSearch.envr_lut[parent] #set environment to parent scope
    return get_next(State(parent_ctrl, new_envr, state.stor, state.kont))

# imports are down here to allow for circular dependencies between structures.py and interpret.py

from cesk.structures import State, Ctrl, Envr, AssignKont, ReturnKont # pylint: disable=wrong-import-position
from cesk.structures import FunctionKont, LeftBinopKont, IfKont, VoidKont # pylint: disable=wrong-import-position
from cesk.structures import throw # pylint: disable=wrong-import-position
