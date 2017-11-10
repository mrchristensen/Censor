"""A static analyzer; see the README for details."""

import argparse
from os.path import dirname
from collections import namedtuple
import pycparser

Function = namedtuple('Function', ['body'])

Thread = namedtuple('Thread', ['function', 'init_state'])

def inject_thread(function):
    """Takes a function and makes a thread that can be placed on the thread
    queue.
    """
    return Thread(function, {})

def is_main(ext):
    """Determines if an AST object is a FuncDef named main."""
    return isinstance(ext, pycparser.c_ast.FuncDef) and ext.decl.name == 'main'

def main():
    """Main function."""
    thread_queue = []

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
        thread_queue.append(main_thread)
        print(main_function)
    else:
        print("Expected a unique main function")

if __name__ == "__main__":
    main()
