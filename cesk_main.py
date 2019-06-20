#!/usr/bin/python3
"""Main function for cesk analyzer"""

import tempfile
import json
import time
import os
import sys
import argparse
import pickle
import logging
from main import parse
from transforms import transform
from cesk.limits import set_config
import cesk.config as cnf
import cesk
from cesk.exceptions import CESKException

def run_interpreter(ast, results, graph_name, injection_point):
    """ function for redirecting the output of main to a file and
        returning the result as a string  """
    output = tempfile.NamedTemporaryFile()
    prev = sys.stdout
    prevfd = os.dup(sys.stdout.fileno())
    os.dup2(output.fileno(), sys.stdout.fileno())
    sys.stdout = open(output.name, "w")#I might need to close this

    memory_safe, states_generated, states_matched, states_evaluated \
        = cesk.main(ast, graph_name, injection_point)

    os.dup2(prevfd, prev.fileno())
    sys.stdout = prev

    results['output'] = open(output.name).read()
    results['memory_safe'] = memory_safe
    results['states_generated'] = states_generated
    results['states_matched'] = states_matched
    results['states_evaluated'] = states_evaluated

#pylint: disable=too-many-statements
def main():
    """Parses arguments and calls correct tool"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--no_preprocess", "-n", \
                        required=False, action='store_true', \
                        help='Do not preproccess the file')
    parser.add_argument('--pycparser', '-p',
                        required=False, type=str, help='The path to pycparser')
    parser.add_argument('--graph', '-g',
                        required=False, type=str,
                        help='Name of graph output file')
    parser.add_argument('--includes', '-I',
                        required=False, type=str,
                        help='Comma separated includes for preprocessing')
    parser.add_argument('--configuration', '-c',
                        required=False, type=str,\
                        help='Name of configuration group ex: -c CONCRETE')
    parser.add_argument('--inject', '-j', \
                        required=False, type=str, \
                        help='Name of injection point function')
    parser.add_argument('--serialize_ast_parsing', '-sp',
                        required=False, type=str,
                        help='Skip parsing by passing in a pickle file')
    parser.add_argument('--serialize_ast_transform', '-st',
                        required=False, type=str,
                        help='Skip parsing and trasforming \
                            by passing in a pickle file')
    args = parser.parse_args()

    needs_preprocess = not args.no_preprocess

    #setup passed in configuration
    if args.configuration is not None:
        logging.info("Current configuration: %s", str(args.configuration))
        if args.configuration in dir(cnf):
            cnf.CONFIG = getattr(cnf, args.configuration)
        else:
            print("Invalid configuration group:", args.configuration)
            exit(0)
    else:
        logging.info("Current configuration: DEFAULT")
    set_config(cnf.CONFIG['limits'])

    result = {}
    #TODO add timing option for benchmarks
    try:
        #parse
        if args.serialize_ast_parsing is not None:
            logging.info("Using pickle file for parsing: %s", \
                str(args.serialize_ast_parsing))
            with open(args.serialize_ast_parsing, 'rb') as pickle_file:
                ast = pickle.load(pickle_file)
            result["parse_time"] = 0
        elif args.serialize_ast_transform is None:
            start = time.process_time()
            ast = parse(args.filename, args.includes, args.pycparser, \
                        True, needs_preprocess) #parses with sanitation (True)
            end = time.process_time()
            result["parse_time"] = end - start

        #transform
        if args.serialize_ast_transform is not None:
            logging.info("Using pickle file for parsing and transform: %s", \
                str(args.serialize_ast_transform))
            with open(args.serialize_ast_transform, 'rb') as pickle_file:
                ast = pickle.load(pickle_file)
            result["parse_time"] = 0
            result["transform_time"] = 0
        else:
            start = time.process_time()
            transform(ast)
            end = time.process_time()
            result["transform_time"] = end - start

        #interpret
        start = time.process_time()
        run_interpreter(ast, result, args.graph, args.inject)
        end = time.process_time()
        result["interpretation_time"] = end - start
    except CESKException as exception:
        raise exception #todo add stack trace to result
    print(json.dumps(result))

if __name__ == "__main__":
    main()
