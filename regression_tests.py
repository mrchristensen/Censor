""" Run regression tests using dataracebench micro benchmarks. """

import argparse
import sys
from os import path
import subprocess
import pycparser
import transforms
from omp.c_with_omp_generator import CWithOMPGenerator

class Options(object): #pylint: disable=too-few-public-methods
    """ Struct for keeping track of options for regression test operation,
        especially defaults.
    """
    def __init__(self):
        self.working_dir = path.dirname(path.abspath(__file__))
        self.pycparser = path.dirname(path.abspath(__file__))
        self.testdirs = [r'benchmarks/dataracebench/micro-benchmarks']
        self.utilities = [r'benchmarks/dataracebench/micro-benchmarks/utilities/polybench.c']
        self.includes = [
            r'benchmarks/dataracebench/micro-benchmarks/utilities',
            r'benchmarks/dataracebench/micro-benchmarks'
        ]

def _get_tests():
    pass

def _get_polyflag():
    pass

def _preserve_include_preprocess(test_file):
    sed_path = r'benchmarks/include_preserve.sed'
    out_path = r'/tmp/preprocessed.c'
    with open(out_path, 'w') as out_file:
        res = subprocess.run(['sed', '-rf', sed_path, test_file], stdout=out_file)
        if res.returncode != 0:
            raise RuntimeError('Could not perform include preserve preprocessing!')

    return out_path

def _preserve_include_postprocess(test_file):
    inserting_sed = r'benchmarks/insert_includes.sed'
    deleting_sed = r'benchmarks/remove_fake_includes.sed'
    out_path = r'/tmp/postprocessed.c'
    with open(out_path, 'w') as out_file:
        inserting = subprocess.Popen(
            ['sed', '-rf', inserting_sed, test_file],
            stdout=subprocess.PIPE
        )
        subprocess.run(
            ['sed', '-rf', deleting_sed],
            stdin=inserting.stdout,
            stdout=out_file
        )
        inserting.communicate()

    return out_path

def _split_on_comma(string):
    return map(lambda s: s.strip(), string.split(','))

def _test_file(test_file, options=Options()):
    sys.path.append(options.pycparser)
    fake_libc_path = path.join(options.pycparser, r'utils/fake_libc_include/')

    test_file = _preserve_include_preprocess(test_file)
    pycparser_args = [
        '-nostdinc',
        '-E',
        '-std=c99',
        ''.join(['-I', fake_libc_path]),
    ]
    for include in options.includes:
        pycparser_args.append(''.join(['-I', include]))

    ast = pycparser.parse_file(
        test_file, use_cpp=True, cpp_path='gcc',
        cpp_args=pycparser_args)

    # setup gcc arguments
    gcc_args = []
    for file in options.utilities:
        gcc_args.append(file)

    for include in options.includes:
        gcc_args.append(''.join(['-I', include]))
    gcc_args += ['-fopenmp', '-lm']

    # Transform and generate c. Compile and compare.
    c_generator = CWithOMPGenerator()
    for transformer in transforms.get_transformers(ast):
        ast = transformer.visit(ast)
        c_prime_file = open('c_prime.c', 'w')
        c_prime = c_generator.visit(ast)
        c_prime_file.write(c_prime)
        post_processed_file = _preserve_include_postprocess('c_prime.c')
        if subprocess.run(['gcc', '-o', 'a.out', test_file] + gcc_args).returncode == 1:
            print("Failed", test_file)
        else:
            print(test_file)
        if subprocess.run(['gcc', '-o', 'b.out', post_processed_file] + gcc_args).returncode == 1:
            print("Error while compiling transformed c")
        else:
            print("Successfully compiled transformed c")
        break


def _test_files(options=Options()):
    # grep -l main micro-benchmarks/*.c
    for test_dir in options.testdirs:
        res = subprocess.run(['grep', '-lR', 'main', test_dir], stdout=subprocess.PIPE)
        for file in res.stdout.split():
            _test_file(file, options)
            break

def main():
    """ Setup and run regression tests. """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pycparser',
        '-p',
        required=False,
        type=str,
        help='the path to pycparser'
    )
    parser.add_argument(
        '--testdirs',
        '-t',
        required=False,
        type=_split_on_comma,
        help='comma separated list of directories containing tests'
    )
    parser.add_argument(
        '--utilities',
        '-u',
        required=False,
        type=_split_on_comma,
        help='comma separated list of utilities or files that must be compiled with the test files'
    )
    parser.add_argument(
        '--includes',
        '-i',
        required=False,
        type=_split_on_comma,
        help='comma separated list of directories to include'
    )
    args = parser.parse_args()

    options = Options()

    if args.pycparser is not None:
        options.pycparser = args.pycparser
    if args.testdirs is not None:
        options.testdirs = args.testdirs
    if args.includes is not None:
        options.includes = args.includes
    if args.utilities is not None:
        options.utilities = args.utilities

    _test_files(options)



if __name__ == "__main__":
    main()
