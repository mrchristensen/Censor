#!/usr/bin/python3
"""Main function for cesk analyzer"""

import tempfile
import json
import time
import os
import sys
import argparse
from main import parse
from transforms import transform
from cesk.limits import set_config
import cesk.config as cnf
import cesk
from cesk.exceptions import CESKException

def run_interpreter(ast, results, graph_name, injection_point, man_visit=None):
    """ function for redirecting the output of main to a file and
        returning the result as a string  """
    output = tempfile.NamedTemporaryFile()
    prev = sys.stdout
    prevfd = os.dup(sys.stdout.fileno())
    os.dup2(output.fileno(), sys.stdout.fileno())
    sys.stdout = open(output.name, "w")#I might need to close this

    memory_safe, states_generated, states_matched, states_evaluated \
        = cesk.main(ast, graph_name, injection_point, man_visit)

    os.dup2(prevfd, prev.fileno())
    sys.stdout = prev

    results['output'] = open(output.name).read()
    results['memory_safe'] = memory_safe
    results['states_generated'] = states_generated
    results['states_matched'] = states_matched
    results['states_evaluated'] = states_evaluated

def main():
    """Parses arguments and calls correct tool"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+")
    parser.add_argument("--no_preprocess", "-n", \
                        required=False, action='store_true', \
                        help='Do not preproccess the file')
    parser.add_argument('--pycparser', '-p',
                        required=False, type=str, help='the path to pycparser')
    parser.add_argument('--graph', '-g',
                        required=False, type=str,
                        help='name of graph output file')
    parser.add_argument('--includes', '-I',
                        required=False, type=str,
                        help='Comma separated includes for preprocessing')
    parser.add_argument('--configuration', '-c',
                        required=False, type=str,\
                        help='name of configuration group ex: -c CONCRETE')
    parser.add_argument('--inject', '-j', \
                        required=False, type=str, \
                        default='main', \
                        help='name of injection point function')
    args = parser.parse_args()

    needs_preprocess = False if args.no_preprocess else True

    #setup passed in configuration
    if args.configuration is not None:
        if args.configuration in dir(cnf):
            cnf.CONFIG = getattr(cnf, args.configuration)
        else:
            print("Invalid configuration group:", args.configuration)
            exit(0)
    set_config(cnf.CONFIG['limits'])

    result = {}
    #TODO add timing option for benchmarks
    try:
        start = time.process_time()
        asts = []
        for file in args.filenames:
            ast = parse(file, args.includes, args.pycparser, \
                        True, needs_preprocess)
            asts.append(ast)

        end = time.process_time()
        result["parse_time"] = end - start


        start = time.process_time()
        for ast in asts:
            transform(ast)
        end = time.process_time()
        result["transform_time"] = end - start

        from manifest_visitor import ManifestVisitor
        man_visit = ManifestVisitor(args.filenames)
        man_visit.create_manifest(asts)

        start = time.process_time()
        run_interpreter(ast, result, args.graph, args.inject, man_visit)
        end = time.process_time()
        result["interpretation_time"] = end - start
    except CESKException as exception:
        raise exception #todo add stack trace to result
    print(json.dumps(result))

if __name__ == "__main__":
    main()
