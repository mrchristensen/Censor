#!/usr/bin/python3
'''Main function for generic c analyzer'''

import argparse

import utils

def main():
    '''takes a path to a diretory with a make file
        outputs the list of c files used by that make file'''
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument('--outfile', '-o',
                        required=False, type=str, help='the path to pycparser')
    parser.add_argument('--makefile', '-f',
                        required=False, type=str, help='the path to pycparser')
    args = parser.parse_args()
    if args.makefile:
        array_of_files = utils.find_dependencies(args.directory, args.makefile)
    else:
        array_of_files = utils.find_dependencies(args.directory)

    string_of_includes = ""
    for filename in array_of_files:
        string_of_includes += '#include <'+filename+'>\n'

    if args.outfile:
        outfile = open(args.outfile, "w+")
    else:
        outfile = open("includes.c", "w+")

    outfile.write(string_of_includes)
    outfile.close()

if __name__ == "__main__":
    main()
