'''Helper classes and functions for regression testing'''

import subprocess
import tempfile
import difflib
from os import listdir
from os.path import join
from unittest import TestCase
import copy
import sys
import pycparser
import utils
from omp.c_with_omp_generator import CWithOMPGenerator
from transforms import get_transformers, transform
import observer
import cesk


# Pylint doesn't like the way things are set up but doing it any different
# breaks stuff
#pylint: disable=no-member
class RegressionTestCase(TestCase):
    '''Unit test base class for Regression testing.

        The structure is such that TestCases deriving from RegressionTestCase
        only need to specify the fixtures directory, includes, and any
        additional flags needed to compile the C file correctly and then call
        `self.assert_end_result_same()`.

        The currently existing test cases `TestBasic` and `TestDataRaceBench`
        are good examples of this convention.'''

    @classmethod
    def setUpClass(cls):
        cls.generator = CWithOMPGenerator()

    def assert_same_output_ast(self, ast, expected_out, prev_ast=None):
        '''Compile ast and run and compare against results of f_input'''
        temp = tempfile.NamedTemporaryFile()

        actual = self.generator.visit(ast)

        temp.write(bytes(actual, 'utf-8'))
        temp.flush()

        utils.preserve_include_postprocess(temp.name)

        actual_out = _run_c(temp.name, self.includes, self.add_flags)

        res = _diff_results(expected_out, actual_out)

        if res:
            # Get printable c
            utils.sanitize(prev_ast)
            prev_c = self.generator.visit(prev_ast)
            utils.sanitize(ast)
            actual_c = self.generator.visit(ast)
            print('Failed!\n', flush=True)
            msg = (
                "Same output assertion failed\n"
                + "Before transformation: \n"
                + prev_c
                + "\nAfter transformation: \n"
                + actual_c
                + "\nDiff: \n" + res)
            print(msg, file=sys.stderr)
            raise self.failureException(msg)

    def assert_same_output_series(self, fixture):
        '''Test combination of all transforms gives expected output'''
        print("\nTesting: " + fixture)

        temp = _temp_copy(fixture)

        utils.preserve_include_preprocess(temp.name)
        ast = _parse_ast_from_file(temp.name, self.includes)

        expected_out = _run_c(fixture, self.includes, self.add_flags)

        with self.subTest(msg=fixture + ": all transforms in series"):
            prev_ast = ast
            for (constructor, deps) in get_transformers(ast):
                print(
                    "\tTesting "
                    + constructor.__name__
                    + '... ',
                    end='',
                    flush=True
                )
                prev_ast = copy.deepcopy(ast)
                ast = constructor(*deps(ast)).visit(ast)
                self.assert_same_output_ast(ast, expected_out, prev_ast)
                print('Good', flush=True)

    def assert_end_result_same(self):
        '''Test whether running all transforms on a fixture results in the
            same output. If not, run against each transformation in series.'''
        implemented_node_set = cesk.implemented_nodes()
        watchman = observer.Observer()
        for fixture in get_fixtures(self.fixtures):
            print("Testing: " + fixture)

            temp = _temp_copy(fixture)

            utils.preserve_include_preprocess(temp.name)
            ast = _parse_ast_from_file(temp.name, self.includes)

            expected_out = _run_c(fixture, self.includes, self.add_flags)

            failed = False
            try:
                prev_ast = copy.deepcopy(ast)
                ast = transform(ast)
                # Once the interpreter matures, checking for correct output
                # can be easily added here
                self.assert_same_output_ast(ast, expected_out, prev_ast)
            except NotImplementedError as err:
                print("Transformation failed! Received NotImplementedError! ")
                print(str(err))
                failed = True
            except AssertionError:
                failed = True

            if failed:
                print("Verifying same output after each transform...")
                self.assert_same_output_series(fixture)
            else:
                utils.sanitize(ast)
                watchman.visit(ast)

        print()
        watchman.report()
        watchman.coverage(implemented_node_set)



def get_fixtures(path):
    '''Retrieve test fixtures'''
    return [join(path, f) for f in listdir(path) if f.endswith('.c')]

def _parse_ast_from_file(path, includes):
    '''Parse a file into an ast with the given includes.
        fake_libc_path currently hard coded.'''
    return pycparser.parse_file(
        path, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E',
                  '-x', 'c',
                  ''.join(['-I', '../../fake_libc_include']),
                  *[''.join(['-I', include]) for include in includes]
                 ])

def _temp_copy(path):
    '''Get a tempfile copy of a given file path.'''
    temp = tempfile.NamedTemporaryFile()
    temp.write(open(path, 'rb').read())
    temp.flush()
    return temp

def _diff_results(expected_out, actual_out):
    '''Use python's difflib to diff two strings.'''
    return '\n'.join(
        difflib.unified_diff(
            expected_out.splitlines(),
            actual_out.splitlines()
        )
    )

def _compile_c(path, includes, add_flags, out_path):
    '''Compile c to out_path file. Return result'''
    return subprocess.run(
        ['gcc', '-x', 'c', path, '-o', out_path,
         *[''.join(['-I', include]) for include in includes],
         *add_flags
        ],
        stderr=subprocess.PIPE
    )


def _run_c(path, includes, add_flags):
    '''compiles and runs a c source file and returns stdout (or stderr, if
        the return code is non-zero) as a byte string.'''
    out_path = join(tempfile.gettempdir(), "censor_out")
    res = _compile_c(path, includes, add_flags, out_path)
    if res.returncode != 0:
        return \
            "Compilation failed!\n" \
            + res.stderr.decode('utf-8')

    stdout = subprocess.check_output([out_path])
    return stdout.decode('utf-8')
