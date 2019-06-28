#!/usr/bin/python3
"""Main function for generic c analyzer"""

import argparse
import sys
#import tempfile #removed for windows compatability, should find way to use
from os import path

from ssl.correct_call_order import verify_openssl_correctness
import instrumenter
import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from cesk.limits import set_config
from transforms import transform

def read_args():
    """ build argument parser and returns parsed args """

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs='+')
    parser.add_argument('--tool', '-t',
                        choices=['censor', 'cesk',
                                 'observer', 'ssl', 'print',
                                 'transform', 'instrumenter'],
                        required=False, type=str.lower,
                        help='the (case-insensitive) name of the analysis')
    parser.add_argument('--pycparser', '-p',
                        required=False, type=str, help='the path to pycparser')
    parser.add_argument('--sanitize', '-s',
                        required=False, action="store_true",
                        help='remove typedefs added by fake includes')
    parser.add_argument('--includes', '-I',
                        required=False, type=str,
                        help='Comma separated includes for preprocessing')
    parser.add_argument('--configuration', '-c',
                        required=False, type=str, help='limits for types')
    return parser.parse_args()

def main():
    """Parses arguments and calls correct tool"""
    args = read_args()

    ast = parse(args.filenames[0], args.includes, args.pycparser, args.sanitize)

    if args.configuration is not None:
        set_config(args.configuration)

    return run_tool(args.tool, ast, args)

#pylint: disable=too-many-locals
def parse(filename, includes, pycparser_path, sanitize, preproccess=True):
    """ Calls pycparser and returns the ast """
    dir_name = path.dirname(filename)

    temp = None
    if sanitize:
        temp = open('tempfile~', 'wb')
        temp.write(open(filename, 'rb').read())
        temp.flush()
        utils.preserve_include_preprocess(temp.name)
        filename = temp.name

    if pycparser_path is not None:
        sys.path.append(pycparser_path)
        fake_libc_path = path.join(pycparser_path, r'utils/fake_libc_include/')
    else:
        pycparser_path = path.dirname(path.abspath(__file__))
        fake_libc_path = path.join(pycparser_path, r'fake_libc_include/')

    import pycparser
    cpp_args = [
        '-nostdinc',
        '-E', '-x', 'c',
        ''.join(['-I', fake_libc_path]),
        ''.join(['-I', dir_name]),
        ''.join(['-I', dir_name, '/utilities']),
    ]
    if includes is not None:
        cpp_args.extend([''.join(['-I', include]) \
                for include in includes.split(',')])

    import platform
    if platform.system() == "Windows":
        cpp_compiler = 'g++'
    else:
        cpp_compiler = 'gcc'

    cparser = pycparser.c_parser.CParser()
    if preproccess:
        text = pycparser.preprocess_file(filename, cpp_path=cpp_compiler,
                                         cpp_args=cpp_args)
    else:
        text = open(filename, 'r').read()

    text = utils.remove_gcc_extentions(text) #only for large code base
    with open("preprocessed.c", "w") as preprocessed_text:
        preprocessed_text.write(text)
    ast = cparser.parse(text, filename)
    return ast


def run_tool(tool, ast, args):
    """ figure out what analysis is supposed to happen and call the
        appropriate one """
    if tool == "censor":
        import censor
        censor.main(ast)
    elif tool == "instrumenter":
        transform(ast)
        instrumenter.main(ast)
    elif tool == "cesk":
        import cesk
        print("Deprecated please use cesk_main.py")
        #transform(ast)
        #cesk.main(ast) #config not customizable
    elif tool == "observer":
        import observer
        observe_ast(ast, observer, cesk)
    elif tool == "ssl":
        verify_openssl_correctness(ast)
    elif tool == "print":
        print_ast(ast)
    elif tool == "transform":
        transform(ast)
        if args.sanitize:
            utils.sanitize(ast)
            print(CWithOMPGenerator().visit(ast).replace("#pragma BEGIN ", ""))
        else:
            print(CWithOMPGenerator().visit(ast))
    else:
        print("No valid tool name given; defaulting to censor.")
        censor.main(ast) #default to censor

def print_ast(ast):
    """ Steps to print the ast """
    print("-------------------------BEFORE TRANSFORMS------------------------")
    from copy import deepcopy
    copy_ast = deepcopy(ast)
    utils.sanitize(copy_ast)
    copy_ast.show()
    transform(ast)
    print("-------------------------AFTER TRANSFORMS-------------------------")
    utils.sanitize(ast)
    ast.show()

def observe_ast(ast, observer, cesk):
    """ Steps to Observe """
    watchman = observer.Observer()
    transform(ast)
    watchman.visit(ast)
    watchman.report()
    watchman.coverage(cesk.implemented_nodes())

if __name__ == "__main__":
    main()
