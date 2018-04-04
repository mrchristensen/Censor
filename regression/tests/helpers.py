"""Helper classes and functions for regression testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join
from unittest import TestCase
from omp.c_with_omp_generator import CWithOMPGenerator
from transforms import get_transformers_omp, get_transformers
from transforms import IDGenerator, TypeEnvironmentCalculator

import pycparser

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

    def assert_same_output(self,
                           transform_step_func, f_input):
        """ Compare output of original and transformed c programs and print a
            diff on failure
        """
        temp_name = tempfile.gettempdir() + r'/temp.c'
        temp = open(temp_name, 'w')
        temp.write(open(f_input, 'r').read())
        temp.flush()

        _preserve_include_preprocess(temp_name)

        ast = pycparser.parse_file(
            temp_name, use_cpp=True, cpp_path='gcc',
            cpp_args=['-nostdinc',
                      '-E',
                      ''.join(['-I', '../../fake_libc_include']),
                      *[''.join(['-I', include]) for include in self.includes]
                     ])

        ast = transform_step_func(ast)

        actual = self.generator.visit(ast)

        temp.write(actual)
        temp.flush()

        _preserve_include_postprocess(temp_name)

        res = _compile_and_diff_results(f_input, temp_name,
                                        self.includes, self.add_flags)
        if res:
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
            for (constructor, deps) in get_transformers(id_gen_func,
                                                        type_env_func):
                with self.subTest(msg=fixture + ":" + constructor.__name__):
                    self.assert_same_output(
                        # Since the lambda created here will be executed before the values
                        # `constructor` and `deps` change, we can safely ignore cell-var-from-loop
                        lambda ast: constructor(*deps(ast)).visit(ast), #pylint: disable=cell-var-from-loop
                        fixture
                    )
                    print('.', end='', flush=True)

    def assert_all_omp(self):
        """ Test all omp transformations (all at once).
        """
        def runall(ast):
            """ Used to run all transforms in parallel.
            """
            for (constructor, deps) in get_transformers_omp():
                ast = constructor(*deps(ast)).visit(ast)
            return ast

        for fixture in get_fixtures(self.fixtures):
            self.assert_same_output(runall, fixture)
            print('.', end='', flush=True)


def get_fixtures(path):
    """Retrieve test fixtures"""
    return [join(path, f) for f in listdir(path) if f.endswith('.c')]


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
    subprocess.check_output(
        ['gcc', path, '-o', out_path,
         *[''.join(['-I', include]) for include in includes],
         *add_flags
        ]
    )
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
