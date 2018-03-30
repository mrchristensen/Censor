"""Helper classes and functions for regression testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join
from unittest import TestCase
from omp.c_with_omp_generator import CWithOMPGenerator

import pycparser

class RegressionTestCase(TestCase):
    """
    Unit test base class for using golden files.
    Provides a method to compare file contents with a string and print a diff
    """

    def __init__(self):
        super().__init__()
        self.includes = []
        self.add_flags = []

    @classmethod
    def setUpClass(cls):
        cls.generator = CWithOMPGenerator()

    def assert_same_output_individual(self, transform, f_input):
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

        actual = self.generator.visit(
            transform(ast)
        )
        temp.write(actual)
        temp.flush()

        _preserve_include_postprocess(temp_name)
        actual_out = self.run_c(temp_name)

        temp_actual_out = tempfile.NamedTemporaryFile(mode='w')
        temp_actual_out.write(actual_out)
        temp_actual_out.flush()

        expected_out = self.run_c(f_input)
        temp_expected_out = tempfile.NamedTemporaryFile(mode='w')
        temp_expected_out.write(expected_out)
        temp_expected_out.flush()

        stdout, _ = subprocess.Popen(
            ['diff', '-u', '-N', '-w', '-B',
             temp_expected_out.name, temp_actual_out.name],
            stdout=subprocess.PIPE
        ).communicate()
        if stdout:
            msg = (
                "Same output assertion failed\n"
                + "Input file: " + f_input + "\n"
                + stdout.decode('utf-8')[:1024])
            raise self.failureException(msg)

    def assert_all_same(self, transform, fixtures_dir):
        """Run all test fixtures in censor/tests/fixtures/[module]"""
        fixtures = sorted(get_fixtures(fixtures_dir))
        for input_file in fixtures:
            self.assert_same_output_individual(transform, input_file)

    def run_c(self, path):
        """ compiles and runs a c source file and returns stdout
            as a byte string.
        """
        out_path = join(tempfile.gettempdir(), "censor_out")
        subprocess.check_output(
            ['gcc', path, '-o', out_path,
             *[''.join(['-I', include]) for include in self.includes],
             *self.add_flags,
             '-fopenmp']
        )
        stdout = subprocess.check_output([out_path])
        return stdout.decode()


def get_fixtures(path):
    """Retrieve test fixtures"""
    return [join(path, f) for f in listdir(path) if f.endswith('.c')]


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
