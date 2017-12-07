"""A static analyzer; see the README for details."""

import argparse
from collections import deque, namedtuple
from os.path import dirname
import pycparser

Function = namedtuple('Function', ['funcDef'])

Thread = namedtuple('Thread', ['function', 'init_store'])

State = namedtuple('State', ['index', 'function', 'store'])

# make sure this works in a multidimensional setting
ArrayAddress = namedtuple('ArrayAddress', ['array', 'index'])

StructAddress = namedtuple('StructAddress', ['struct', 'field'])

class Location:
    """Represents a program location."""
    def __init__(self, index, function):
        self.index = index
        self.function = function

    def __add__(self, offset):
        """Returns the location in the same function with the line number offset
        by the value offset. This is used most commonly as loc+1 to get the
        syntactic successor to a Location.
        """
        return Location(self.index+offset, self.function)

    def stmt(self):
        """Retrieves the statement at the location."""
        return self.function.funcDef.body.block_items[self.index]

    def funcdef(self):
        """Retrieves the FuncDef object wrapped in the function."""
        return self.function.funcDef

class Store:
    """Represents the contents of memory at a moment in time."""
    def __init__(self, memory=None):
        if memory is None:
            self.memory = {}
        else:
            self.memory = memory

    def read(self, address):
        """Read the contents of the store at address. Returns None if undefined.
        """
        if address in self.memory:
            return self.memory[address]
        else:
            return None

    def write(self, address, value):
        """Write value to the store at address. If there is an existing value,
        merge value into the existing value.
        """
        memory = self.memory.copy()
        if address in self.memory:
            memory[address] = self.memory[address].merge(value)
        else:
            memory[address] = value
        return Store(memory)

def inject_thread(function):
    """Takes a function and makes a thread that can be placed on the thread
    queue.
    """
    return Thread(function, Store())

def is_main(ext):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(ext, pycparser.c_ast.FuncDef) and ext.decl.name == 'main'

THREAD_QUEUE = []

# TODO
BOTTOM = None

def analyze_threads():
    """Driver function. Iterates through the list of threads (which may expand),
    analyzing each in turn.
    """
    for thread in THREAD_QUEUE:
        analyze_thread(thread)

def may_be_zero(aint):
    """Evaluate if the given abstract int may be zero."""
    # TODO
    return aint == aint

def may_be_nonzero(aint):
    """Evaluate if the given abstract int may be nonzero. This is not simply the
    inverse of may_be_zero!
    """
    # TODO
    return aint == aint

def do_unary_op(unop, store):
    """Evaluate a unary op. Return the result and the store, which may change.
    """
    return (unop, store)

def do_binary_op(binop, store):
    """Evaluate a binary op. Return the result and the store, which may change.
    """
    return (binop, store)

def eval_exp(exp, store):
    """Evaluate an expression. Return its result as an abstract value."""
    rvalue = exp
    if isinstance(exp, pycparser.c_ast.UnaryOp):
        (rvalue, store) = do_unary_op(exp, store)
    elif isinstance(exp, pycparser.c_ast.BinaryOp):
        (rvalue, store) = do_binary_op(exp, store)
    elif isinstance(exp, pycparser.c_ast.TernaryOp):
        condition = eval_exp(exp.cond, store)
        if may_be_zero(condition):
            (rvalue, store) = eval_exp(exp.iffalse, store)
        else:
            rvalue = BOTTOM
        if may_be_nonzero(condition):
            (result, store) = eval_exp(exp.iftrue, store)
            rvalue = rvalue.merge(result)
    else:
        # consider an error that indicates what couldn't be matched
        return NotImplemented
    return (rvalue, store)

def resolve(lvalue, store):
    """Determine the abstract address to use for a given lvalue."""
    # pylint: disable=redefined-variable-type
    address = lvalue
    if isinstance(lvalue, pycparser.c_ast.ID):
        address = lvalue.name
    elif isinstance(lvalue, pycparser.c_ast.ArrayRef):
        (subscript, store) = eval_exp(lvalue.subscript, store)
        address = ArrayAddress(lvalue.name, subscript)
    elif isinstance(lvalue, pycparser.c_ast.StructRef):
        # this is probably not correct
        address = StructAddress(lvalue.name, lvalue.field)
    else:
        # OH NOES
        return NotImplemented
    return (address, store)

def handle_assignment(state: State):
    """Evaluate an assignment statement."""
    stmt = state.loc.stmt
    store = state.store
    address = resolve(stmt.lvalue, store)
    (value, store) = eval_exp(stmt.rvalue, store)
    store = store.write(address, value)
    return State(state.loc+1, store)

def analyze_statement(state: State):
    """Execute one statement. Return the resulting state."""
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    stmt = state.loc.stmt()
    successors = []
    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        # TODO
        print("ArrayDecl")
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        print("ArrayRef")
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        successors.append(handle_assignment(state))
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
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))
    return successors

def analyze_thread(thread: Thread):
    """Performs analysis on a single function."""
    func = thread.function
    store = thread.init_store
    index = 0
    queue = deque([State(Location(index, func), store)])
    while queue:
        successors = analyze_statement(queue.popleft())
        if successors is not NotImplemented:
            queue.extend(successors)

def main():
    """Main function."""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    dir_name = dirname(args.filename)

    ast = pycparser.parse_file(
        args.filename, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E',
                  r'-Ifake_libc_include/',
                  ''.join(['-I', dir_name]),
                  ''.join(['-I', dir_name, '/utilities'])
                 ])
    mains = [child for child in ast.ext if is_main(child)]
    if len(mains) == 1:
        main_function = Function(mains[0])
        main_thread = inject_thread(main_function)
        THREAD_QUEUE.append(main_thread)
        analyze_threads()
    else:
        print("Expected a unique main function")

if __name__ == "__main__":
    main()
