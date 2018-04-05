"""Main function for generic c analyzer"""

import argparse
import sys
from os import path

import yeti


def main():
    """Parses arguments and calls correct tool"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument('--tool', '-t', choices=['censor', 'yeti', 'cesk'],
                        required=False, type=str.lower,
                        help='the (case-insensitive) name of the analysis')
    parser.add_argument('--pycparser', '-p',
                        required=False, type=str, help='the path to pycparser')
    args = parser.parse_args()
    dir_name = path.dirname(args.filename)

    if args.pycparser is not None:
        sys.path.append(args.pycparser)
        fake_libc_path = path.join(args.pycparser, r'utils/fake_libc_include/')
    else:
        args.pycparser = path.dirname(path.abspath(__file__))
        fake_libc_path = path.join(args.pycparser, r'fake_libc_include/')

    import pycparser
    import censor
    import cesk
    # figure out what analysis is supposed to happen and call the
    # appropriate one
    ast = pycparser.parse_file(
        args.filename, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E',
                  ''.join(['-I', fake_libc_path]),
                  ''.join(['-I', dir_name]),
                  ''.join(['-I', dir_name, '/utilities'])
                 ])
    if args.tool == "censor":
        censor.main(ast)
    elif args.tool == "yeti":
        yeti.main(ast)
    elif args.tool == "cesk":
        cesk.main(ast)
    else:
        print("No valid tool name given; defaulting to censor.")
        censor.main(ast) #default to censor

if __name__ == "__main__":
    main()
