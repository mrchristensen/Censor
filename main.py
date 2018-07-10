#!/usr/bin/python3
"""Main function for generic c analyzer"""

import argparse
import sys
import tempfile
from os import path

from ssl.correct_call_order import verify_openssl_correctness
import yeti
import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from cesk.limits import set_config
from transforms import transform

def main():
    """Parses arguments and calls correct tool"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs='+')
    parser.add_argument('--tool', '-t',
                        choices=['censor', 'yeti', 'cesk',
                                 'observer', 'ssl', 'print',
                                 'transform'],
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

    if args.pycparser is not None:
        sys.path.append(args.pycparser)
        fake_libc_path = path.join(args.pycparser, r'utils/fake_libc_include/')
    else:
        args.pycparser = path.dirname(path.abspath(__file__))
        fake_libc_path = path.join(args.pycparser, r'fake_libc_include/')

    import pycparser

    temp_files = [] #file need to remain to not be garbage collected and closed
    orig_name_map = {} 
    if args.sanitize:
        temps = [] 
        for filename in args.filename:
            temp = tempfile.NamedTemporaryFile()
            temp.write(open(filename, 'rb').read())
            temp.flush()
            utils.preserve_include_preprocess(temp.name)
            temps.append(temp.name)
            temp_files.append(temp)
            orig_name_map[temp.name] = filename
        args.filename = temps

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
        cpp_args.extend(['-DMAP_USE_HASHTABLE,SET_USE_RBTREE'])

    print(cpp_args)

    #delete this when done debugging
    pre_proccess_record = open('preprocessed.txt','w+')
    for filename in args.filename:
        print(orig_name_map[filename])
        if orig_name_map[filename] == "/home/jjones95/openssl/apps/app_rand.c":
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            text = pycparser.preprocess_file('dummy_define.c '+filename, cpp_path='gcc', cpp_args=cpp_args)
            pre_proccess_record.write(text)
    pre_proccess_record.close()
    #end delete this

    ast = pycparser.c_ast.FileAST([])
    for filename in args.filename:
        ast.ext.append(pycparser.parse_file(
            filename, use_cpp=True, cpp_path='gcc', cpp_args=cpp_args
            ))

    if args.configuration is not None:
        set_config(args.configuration)
    # the instrumenter needs to preserve includes until after
    # instrumentation
    # if args.sanitize:
    #    utils.sanitize(ast)

    run_tool(args.tool, ast)

def run_tool(tool, ast):
    """ figure out what analysis is supposed to happen and call the
        appropriate one """
    import censor
    import cesk
    import observer
    if tool == "censor":
        censor.main(ast)
    elif tool == "yeti":
        transform(ast)
        yeti.main(ast)
    elif tool == "cesk":
        transform(ast)
        cesk.main(ast)
    elif tool == "observer":
        observe_ast(ast, observer, cesk)
    elif tool == "ssl":
        verify_openssl_correctness(ast)
    elif tool == "print":
        print_ast(ast)
    elif tool == "transform":
        transform(ast)
        utils.sanitize(ast)
        print(CWithOMPGenerator().visit(ast).replace("#pragma BEGIN ",""))
    else:
        print("No valid tool name given; defaulting to censor.")
        censor.main(ast) #default to censor

def print_ast(ast):
    """ Steps to print the ast """
    print("BEFORE TRANSFORMS---------------------------------------")
    ast.show()
    from copy import deepcopy
    ast_copy = deepcopy(ast) 
    utils.sanitize(ast_copy)
    pyc_file = open("just_pyc.c","w")
    pyc_file.write(CWithOMPGenerator().visit(ast_copy).replace("#pragma BEGIN ",""))
    transform(ast)
    print("--------------------------AFTER TRANSFORMS----------------")
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
