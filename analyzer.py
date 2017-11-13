"""A static analyzer; see the README for details."""

import argparse
from os.path import dirname
from collections import namedtuple
import pycparser

Function = namedtuple('Function', ['funcDef'])

Thread = namedtuple('Thread', ['function', 'init_state'])

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

def analyze_statement(stmt: pycparser.c_ast.Node, state):
    """Execute one statement. Return the resulting state."""
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    if isinstance(stmt, pycparser.c_ast.ArrayDecl):
        pass
    elif isinstance(stmt, pycparser.c_ast.ArrayRef):
        pass
    elif isinstance(stmt, pycparser.c_ast.Assignment):
        pass
    elif isinstance(stmt, pycparser.c_ast.BinaryOp):
        pass
    elif isinstance(stmt, pycparser.c_ast.Break):
        pass
    elif isinstance(stmt, pycparser.c_ast.Case):
        pass
    elif isinstance(stmt, pycparser.c_ast.Cast):
        pass
    elif isinstance(stmt, pycparser.c_ast.Compound):
        pass
    elif isinstance(stmt, pycparser.c_ast.CompoundLiteral):
        pass
    elif isinstance(stmt, pycparser.c_ast.Constant):
        pass
    elif isinstance(stmt, pycparser.c_ast.Continue):
        pass
    elif isinstance(stmt, pycparser.c_ast.Decl):
        pass
    elif isinstance(stmt, pycparser.c_ast.DeclList):
        pass
    elif isinstance(stmt, pycparser.c_ast.Default):
        pass
    elif isinstance(stmt, pycparser.c_ast.DoWhile):
        pass
    elif isinstance(stmt, pycparser.c_ast.EllipsisParam):
        pass
    elif isinstance(stmt, pycparser.c_ast.EmptyStatement):
        pass
    elif isinstance(stmt, pycparser.c_ast.Enum):
        pass
    elif isinstance(stmt, pycparser.c_ast.Enumerator):
        pass
    elif isinstance(stmt, pycparser.c_ast.EnumeratorList):
        pass
    elif isinstance(stmt, pycparser.c_ast.ExprList):
        pass
    elif isinstance(stmt, pycparser.c_ast.FileAST):
        pass
    elif isinstance(stmt, pycparser.c_ast.For):
        pass
    elif isinstance(stmt, pycparser.c_ast.FuncCall):
        pass
    elif isinstance(stmt, pycparser.c_ast.FuncDecl):
        pass
    elif isinstance(stmt, pycparser.c_ast.FuncDef):
        pass
    elif isinstance(stmt, pycparser.c_ast.Goto):
        pass
    elif isinstance(stmt, pycparser.c_ast.ID):
        pass
    elif isinstance(stmt, pycparser.c_ast.IdentifierType):
        pass
    elif isinstance(stmt, pycparser.c_ast.If):
        pass
    elif isinstance(stmt, pycparser.c_ast.InitList):
        pass
    elif isinstance(stmt, pycparser.c_ast.Label):
        pass
    elif isinstance(stmt, pycparser.c_ast.NamedInitializer):
        pass
    elif isinstance(stmt, pycparser.c_ast.ParamList):
        pass
    elif isinstance(stmt, pycparser.c_ast.PtrDecl):
        pass
    elif isinstance(stmt, pycparser.c_ast.Return):
        pass
    elif isinstance(stmt, pycparser.c_ast.Struct):
        pass
    elif isinstance(stmt, pycparser.c_ast.StructRef):
        pass
    elif isinstance(stmt, pycparser.c_ast.Switch):
        pass
    elif isinstance(stmt, pycparser.c_ast.TernaryOp):
        pass
    elif isinstance(stmt, pycparser.c_ast.TypeDecl):
        pass
    elif isinstance(stmt, pycparser.c_ast.Typedef):
        pass
    elif isinstance(stmt, pycparser.c_ast.Typename):
        pass
    elif isinstance(stmt, pycparser.c_ast.UnaryOp):
        pass
    elif isinstance(stmt, pycparser.c_ast.Union):
        pass
    elif isinstance(stmt, pycparser.c_ast.While):
        pass
    elif isinstance(stmt, pycparser.c_ast.Pragma):
        pass
    else:
        raise ValueError("Unknown C AST object type: {0}".format(stmt))
    # TODO
    print(stmt)
    return state

def analyze_thread(thread: Thread):
    """Performs analysis on a single function."""
    func = thread.function
    state = thread.init_state
    index = 0
    while True:
        if index >= len(func.funcDef.body.block_items):
            raise ValueError("Past the end of a function")
        stmt = func.funcDef.body.block_items[index]
        state = analyze_statement(stmt, state)
        index = index+1

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
