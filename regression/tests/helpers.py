"""Helper classes and functions for regression testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join
from unittest import TestCase
import pycparser
from omp.c_with_omp_generator import CWithOMPGenerator
from transforms import get_transformers_omp, get_transformers
from transforms import IDGenerator, TypeEnvironmentCalculator


# Pylint doesn't like the way things are set up but doing it any different
# breaks stuff
#pylint: disable=no-member
class RegressionTestCase(TestCase):
    """
    Unit test base class for using golden files.
    Provides a method to compare file contents with a string and print a diff
    """

    @classmethod
    def setUpClass(cls):
        cls.generator = CWithOMPGenerator()

    def assert_same_output_ast(self, ast, f_input):
        """ Compile ast and run and compare against results of f_input
        """
        temp = tempfile.NamedTemporaryFile()

        actual = self.generator.visit(ast)

        temp.write(bytes(actual, 'utf-8'))
        temp.flush()

        _preserve_include_postprocess(temp.name)

        res = _compile_and_diff_results(f_input, temp.name,
                                        self.includes, self.add_flags)
        if res:
            print('F', end='', flush=True)
            msg = (
                "Same output assertion failed\n"
                + "Input file: " + f_input + "\n"
                + res.decode('utf-8')[:1024])
            raise self.failureException(msg)

    def assert_individual_non_omp(self):
        """ Test all non-omp transfomrations independently.
        """
        id_gen_func = lambda ast: IDGenerator(ast)
        type_env_func = TypeEnvironmentCalculator().get_environments

        for fixture in get_fixtures(self.fixtures):
            temp = _temp_copy(fixture)

            _preserve_include_preprocess(temp.name)

            for (constructor, deps) in get_transformers(id_gen_func,
                                                        type_env_func):
                with self.subTest(msg=fixture + ":" + constructor.__name__):
                    ast = _parse_ast_from_file(temp.name, self.includes)
                    test_ast = constructor(*deps(ast)).visit(ast)
                    self.assert_same_output_ast(test_ast, fixture)
                    print('.', end='', flush=True)

    def assert_all_omp(self):
        """ Test all omp transformations (all at once).
        """
        for fixture in get_fixtures(self.fixtures):
            temp = _temp_copy(fixture)

            _preserve_include_preprocess(temp.name)
            ast = _parse_ast_from_file(temp.name, self.includes)

            for (constructor, deps) in get_transformers_omp():
                ast = constructor(*deps(ast)).visit(ast)

            self.assert_same_output_ast(ast, fixture)
            print('.', end='', flush=True)

    def assert_same_output_series(self):
        """ Test comination of all transforms gives expected output
        """
        type_env_func = TypeEnvironmentCalculator().get_environments

        for fixture in get_fixtures(self.fixtures):
            print("\nTesting fixture: " + fixture)

            temp = _temp_copy(fixture)

            _preserve_include_preprocess(temp.name)
            ast = _parse_ast_from_file(temp.name, self.includes)

            id_gen = IDGenerator(ast)
            id_gen_func = lambda ast: id_gen #pylint: disable=cell-var-from-loop

            with self.subTest(msg=fixture + ": all transforms in series"):

                for (constructor, deps) in get_transformers(id_gen_func,
                                                            type_env_func):
                    print(
                        "\tTesting "
                        + constructor.__name__
                        + '... ',
                        end='',
                        flush=True
                    )
                    ast = constructor(*deps(ast)).visit(ast)
                    self.assert_same_output_ast(ast, fixture)
                    print('Good', flush=True)



def get_fixtures(path):
    """Retrieve test fixtures"""
    return [join(path, f) for f in listdir(path) if f.endswith('.c')]

def _parse_ast_from_file(path, includes):
    return pycparser.parse_file(
        path, use_cpp=True, cpp_path='gcc',
        cpp_args=['-nostdinc',
                  '-E',
                  '-x', 'c',
                  ''.join(['-I', '../../fake_libc_include']),
                  *[''.join(['-I', include]) for include in includes]
                 ])

def _temp_copy(path):
    temp = tempfile.NamedTemporaryFile()
    temp.write(open(path, 'rb').read())
    temp.flush()
    return temp

def _compile_and_diff_results(expected, actual, includes, add_flags):
    actual_out = _run_c(actual, includes, add_flags)

    temp_actual_out = tempfile.NamedTemporaryFile(mode='w')
    temp_actual_out.write(actual_out)
    temp_actual_out.flush()

    expected_out = _run_c(expected, includes, add_flags)
    temp_expected_out = tempfile.NamedTemporaryFile(mode='w')
    temp_expected_out.write(expected_out)
    temp_expected_out.flush()

    stdout, _ = subprocess.Popen(
        ['diff', '-u', '-N', '-w', '-B',
         temp_expected_out.name, temp_actual_out.name],
        stdout=subprocess.PIPE
    ).communicate()
    return stdout


def _run_c(path, includes, add_flags):
    """ compiles and runs a c source file and returns stdout
        as a byte string.
    """
    out_path = join(tempfile.gettempdir(), "censor_out")
    res = subprocess.run(
        ['gcc', '-x', 'c', path, '-o', out_path,
         *[''.join(['-I', include]) for include in includes],
         *add_flags
        ],
        stderr=subprocess.PIPE
    )
    if res.returncode != 0:
        print('F', end='', flush=True)
        msg = (
            "Compilation failed!\n"
            + "Input file: " + path + "\n"
            + "Contents:\n\n"
            + open(path, 'r').read()
            + "\n\n"
            + res.stderr.decode('utf-8'))
        raise TestCase.failureException(msg)

    stdout = subprocess.check_output([out_path])
    return stdout.decode()

def _preserve_include_preprocess(path):
    """ Run sed on source file to preserve includes through gcc preprocessing
    """
    sed_path = r'include_preserve.sed'
    res = subprocess.run(['sed', '-i', '-rf', sed_path, path])
    if res.returncode != 0:
        raise RuntimeError('Could not perform include preserve preprocessing!')

def _preserve_include_postprocess(path):
    """ Run sed on transformed source file to remove fake_libc_includes and
        replace them with the original includes.
    """
    inserting_sed = r'insert_includes.sed'
    deleting_sed = r'remove_fake_includes.sed'
    subprocess.run(
        ['sed', '-i', '-rf', inserting_sed, path],
    )
    subprocess.run(
        ['sed', '-i', '-rf', deleting_sed, path],
    )
