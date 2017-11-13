"""A static analyzer; see the README for details."""

import argparse
from collections import deque, namedtuple
from os.path import dirname
import pycparser

Function = namedtuple('Function', ['funcDef'])

Thread = namedtuple('Thread', ['function', 'init_store'])

State = namedtuple('State', ['index', 'function', 'store'])

def inject_thread(function):
    """Takes a function and makes a thread that can be placed on the thread
    queue.
    """
    return Thread(function, {})

def is_main(ext):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(ext, pycparser.c_ast.FuncDef) and ext.decl.name == 'main'

THREAD_QUEUE = []

def analyze_threads():
    """Driver function. Iterates through the list of threads (which may expand),
    analyzing each in turn.
    """
    for thread in THREAD_QUEUE:
        analyze_thread(thread)

def eval_exp(exp, store):
    """Evaluate an expression. Return its result as an abstract value."""
    # TODO
    return (exp, store)

def analyze_statement(stmt: pycparser.c_ast.Node, store):
    """Execute one statement. Return the resulting state."""
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    successors = []
    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        # TODO
        print("ArrayDecl")
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        # TODO
        print("ArrayRef")
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        # rhs = eval_exp(stmt.rvalue, store)
        eval_exp(stmt.rvalue, store)
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
    queue = deque([State(index, func, store)])
    while queue:
        state = queue.popleft()
        if state.index >= len(state.function.funcDef.body.block_items):
            raise ValueError("Past the end of a function")
        stmt = state.function.funcDef.body.block_items[state.index]
        successors = analyze_statement(stmt, state.store)
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
