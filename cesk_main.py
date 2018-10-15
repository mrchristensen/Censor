#!/usr/bin/python3
"""Main function for cesk analyzer"""

import argparse
from main import parse
from transforms import transform
from cesk.limits import set_config
import cesk.config as cnf
from main import parse
import cesk
# store updates concrete/abstact
# allocation finite/infinite

def main():
    """Parses arguments and calls correct tool"""

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument('--pycparser', '-p',
                        required=False, type=str, help='the path to pycparser')
    parser.add_argument('--includes', '-I',
                        required=False, type=str,
                        help='Comma separated includes for preprocessing')
    parser.add_argument('--configuration', '-c',
                        required=False, type=str, help='comma seperate config '\
                            'values. ex: -c limits=cesk,store_update=strong')
    args = parser.parse_args()

    if args.configuration is not None:
        configs = args.configuartion.split(',')
        for config in configs:
            conf = configs.split('=')
            #todo add error check for invalid input
            cnf.CONFIG[conf[0]] = conf[1] #set or add new config

    set_config(cnf.CONFIG['limits'])

    ast = parse(args.filename, args.includes, args.pycparser, True)
    transform(ast)
    cesk.main(ast)

if __name__ == "__main__":
    main()
