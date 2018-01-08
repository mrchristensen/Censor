"""Main function for generic c analyzer"""

import argparse
from os.path import dirname
import pycparser
import censor


def main():
    """Parses arguments and calls correct tool"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    dir_name = dirname(args.filename)
    # figure out what analysis is supposed to happen and call the
    # appropriate one

    ast = pycparser.parse_file(
        args.filename, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E',
                  r'-Ifake_libc_include/',
                  ''.join(['-I', dir_name]),
                  ''.join(['-I', dir_name, '/utilities'])
                 ])
    args.tool = "censor"

    if args.tool is "censor":
        censor.main(ast)
    elif args.tool is "unkonwn":
        print("No valid tool name given defaulting to censor.")
        censor.main(ast) #default to censor

if __name__ == "__main__":
    main()
