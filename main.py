#!/usr/bin/python3
"""Main function for generic c analyzer"""

import argparse
import sys
import tempfile
from os import path

from ssl.correct_call_order import verify_openssl_correctness
import instrumenter
import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from cesk.limits import set_config
from transforms import transform


def main():
    """Parses arguments and calls correct tool"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs='+')
    parser.add_argument('--tool', '-t',
                        choices=['censor', 'cesk', 'save',
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
    args = parser.parse_args()
    dir_name = path.dirname(args.filename[0])

    if args.configuration is not None:
        set_config(args.configuration)

    temp_files = [] #file need to remain to not be garbage collected and closed
    if args.sanitize:
        temps = []
        for filename in args.filename:
            temp = tempfile.NamedTemporaryFile()
            temp.write(open(filename, 'rb').read())
            temp.flush()
            utils.preserve_include_preprocess(temp.name)
            temps.append(temp.name)
            temp_files.append(temp)
        args.filename = temps

    if args.tool != "save": # check if pickle file exists
        ast = utils.load_object(args.filename[0][:-2] + ".pkl")
        run_tool(args.tool, ast, args)
        return


    if args.pycparser is not None:
        sys.path.append(args.pycparser)
        fake_libc_path = path.join(args.pycparser, r'utils/fake_libc_include/')
    else:
        args.pycparser = path.dirname(path.abspath(__file__))
        fake_libc_path = path.join(args.pycparser, r'fake_libc_include/')

    import pycparser

    cpp_args = [
        '-nostdinc',
        '-E', '-x', 'c',
        ''.join(['-I', fake_libc_path]),
        ''.join(['-I', dir_name]),
        ''.join(['-I', dir_name, '/utilities']),
    ]
    if args.includes is not None:
        cpp_args.extend([''.join(['-I', include]) \
                for include in args.includes.split(',')])
        cpp_args.extend(['-DMAP_USE_HASHTABLE -DSET_USE_RBTREE'])

    ast = pycparser.c_ast.FileAST([])
    for filename in args.filename:
        ast.ext += pycparser.parse_file(
            filename, use_cpp=True, cpp_path='gcc', cpp_args=cpp_args
            ).ext

    # the instrumenter needs to preserve includes until after
    # instrumentation
    # if args.sanitize:
    #    utils.sanitize(ast)

    run_tool(args.tool, ast, args)

def run_tool(tool, ast, args):
    """ figure out what analysis is supposed to happen and call the
        appropriate one """
    import censor
    import cesk
    import observer
    if tool == "censor":
        censor.main(ast)
    elif tool == "instrumenter":
        transform(ast)
        instrumenter.main(ast)
    elif tool == "cesk":
        transform(ast)
        cesk.main(ast)
    elif tool == "observer":
        observe_ast(ast, observer, cesk)
    elif tool == "ssl":
        verify_openssl_correctness(ast)
    elif tool == "print":
        print_ast(ast)
    elif tool == "save":
        savefile_name = args.filename[0][:-2] + ".pkl"
        utils.save_object(ast, savefile_name)
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
