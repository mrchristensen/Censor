"""A static analyzer; see the README for details."""

# import argparse

from collections import namedtuple
import pycparser

Function = namedtuple('Function', ['body'])

Thread = namedtuple('Thread', ['function', 'init_state'])

def inject_thread(function, init_state):
    """Takes a function and makes a thread that can be placed on the thread
    queue.
    """
    return Thread(function, init_state)

def __main__():
    thread_queue = []
    ast = pycparser.parse_file(
        "filename", use_cpp=True, cpp_path='gcc',
        cpp_args=['-E', r'-I/usr/share/python3-pycparser/fake_libc_include/'])
    main_function = Function(ast)
    main_thread = inject_thread(main_function, {})
    thread_queue.append(main_thread)
