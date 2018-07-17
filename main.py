#!/usr/bin/python3
"""Main function for generic c analyzer"""

import argparse
import sys
import tempfile
from os import path
import shelve

from ssl.correct_call_order import verify_openssl_correctness
import yeti
import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from cesk.limits import set_config
from transforms import transform

def main():
    """Parses arguments and calls correct tool"""

    parser = build_parser()

    args = parser.parse_args()
    dir_name = path.dirname(args.filename[0])

    if args.pycparser is not None:
        sys.path.append(args.pycparser)
        fake_libc_path = path.join(args.pycparser, r'utils/fake_libc_include/')
    else:
        args.pycparser = path.dirname(path.abspath(__file__))
        fake_libc_path = path.join(args.pycparser, r'fake_libc_include/')

    import pycparser
    from pycparser.c_parser import CParser

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

    if args.opensslDirectory is not None:
        opensslfile = args.opensslDirectory + 'crypto/ec/curve448/arch_32/,'
        opensslfile += args.opensslDirectory + 'crypto/ec/curve448/,'
        opensslfile += args.opensslDirectory + ','
        opensslfile += args.opensslDirectory + 'crypto/include/,'
        opensslfile += args.opensslDirectory + 'include/,'
        opensslfile += args.opensslDirectory + 'crypto/modes/,'
        opensslfile += args.opensslDirectory + 'apps/'
        if args.includes:
            args.includes += ','+opensslfile
        else:
            args.includes = opensslfile
        cpp_args.extend(['-DMAP_USE_HASHTABLE', '-DSET_USE_RBTREE',
                        '-DOPENSSLDIR="' + args.opensslDirectory + '"'])

    if args.includes is not None:
        cpp_args.extend([''.join(['-I', include]) \
                for include in args.includes.split(',')])

    ast = pycparser.c_ast.FileAST([])
    cparser = CParser()
    database = None
    if args.database:
        print('opened database')
        database = shelve.open(args.database, writeback=True)
        if 'map_of_includes' in database:
            include_map = database['map_of_includes']
        else:
            include_map = {}
    else:
        database = None
        include_map = None

    for filename in args.filename:
        if database is not None and \
           orig_name_map[filename] in database:
            print('Old: '+orig_name_map[filename])
            continue
            file_ast = database[orig_name_map[filename]]
        else:
            print('New: '+orig_name_map[filename])
            local_path = ["-I"+path.dirname(orig_name_map[filename])]
            text = pycparser.preprocess_file(filename, cpp_path='gcc',
                                             cpp_args=cpp_args+local_path)
            #preprocessed_file = open(filename, "w")
            #preprocessed_file.write(text)
            #preprocessed_file.close()
            text = utils.remove_gcc_extentions(text,filename)

            pre_proccess_record = open('preprocessed.txt', 'w')
            pre_proccess_record.write(orig_name_map[filename])
            pre_proccess_record.write(text)#orig_name_map[filename])
            pre_proccess_record.close()

            #file_ast = pycparser.parse_file(filename)
            file_ast = cparser.parse(text, orig_name_map[filename])
            if database is not None:
                utils.sanitize(file_ast, include_map)
                database['map_of_includes'] = include_map
                database[orig_name_map[filename]] = file_ast
                database.sync()
                print('Saved: '+orig_name_map[filename])
                continue

        ast.ext.append(file_ast)

    if database is not None:
        database.close()

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
        print(CWithOMPGenerator().visit(ast).replace("#pragma BEGIN ", ""))
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
    pyc_file = open("just_pyc.c", "w")
    pyc_file.write(CWithOMPGenerator().visit(ast_copy).replace("#pragma BEGIN ", "")) #pylint: disable:line-too-long
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

def build_parser():
    """ Builds all of the option parameters """
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
    parser.add_argument('--opensslDirectory', '-o',
                        required=False, type=str, help='directory to openssl')
    parser.add_argument('--database', '-d',
                        required=False, type=str, help='database to fetch and store ast rather than use pycparser to produce') #pylint: disable:line-too-long
    return parser

if __name__ == "__main__":
    main()
