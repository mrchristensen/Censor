"""Main function for generic c analyzer"""

import argparse
import sys
import tempfile
from os import path

import yeti
import utils


def main():
    """Parses arguments and calls correct tool"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument('--tool', '-t',
                        choices=['censor', 'yeti', 'cesk', 'observer'],
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
    import observer

    temp = None
    if args.sanitize:
        temp = tempfile.NamedTemporaryFile()
        temp.write(open(args.filename, 'rb').read())
        temp.flush()
        utils.preserve_include_preprocess(temp.name)
        args.filename = temp.name

    ast = pycparser.parse_file(
        args.filename, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E', '-x', 'c',
                  ''.join(['-I', fake_libc_path]),
                  ''.join(['-I', dir_name]),
                  ''.join(['-I', dir_name, '/utilities']),
                  *[''.join(['-I', include]) for include \
                          in args.includes.split(',')]
                 ])

    if args.sanitize:
        utils.sanitize(ast)

    # figure out what analysis is supposed to happen and call the
    # appropriate one
    if args.tool == "censor":
        censor.main(ast)
    elif args.tool == "yeti":
        yeti.main(ast)
    elif args.tool == "cesk":
        cesk.main(ast)
    elif args.tool == "observer":
        watchman = observer.Observer()
        watchman.visit(ast)
        watchman.report()
    else:
        print("No valid tool name given; defaulting to censor.")
        censor.main(ast) #default to censor

if __name__ == "__main__":
    main()
