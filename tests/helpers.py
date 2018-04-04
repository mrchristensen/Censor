"""Helper classes and functions for testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join, dirname
from unittest import TestCase
from pycparser.c_parser import CParser
from omp.c_with_omp_generator import CWithOMPGenerator

CWD = dirname(__file__)

class GoldenTestCase(TestCase):
    """
    Unit test base class for using golden files.
    Provides a method to compare file contents with a string and print a diff
    """

    @classmethod
    def setUpClass(cls):
        cls.parser = CParser()
        cls.generator = CWithOMPGenerator()

    def assert_golden(self, transform, f_golden, f_input):
        """Compare file contents and print a diff on failure"""
        input_c = open(CWD + f_input, 'r').read()
        ast = self.parser.parse(input_c)
        transformed = transform(ast)
        actual = self.generator.visit(transformed)
        temp = tempfile.NamedTemporaryFile(mode='w')
        temp.write(actual)
        temp.flush()
        proc = subprocess.Popen(
            ['diff', '-u', '-N', '-w', '-B', CWD + f_golden, temp.name],
            stdout=subprocess.PIPE
            )
        stdout, _ = proc.communicate()
        if stdout:
            msg = "Golden match failed\n" + stdout.decode('utf-8')
            raise self.failureException(msg)

    def assert_all_golden(self, transform, fixtures_dir):
        """Run all test fixtures in censor/tests/fixtures/[module]"""
        fixtures = sorted(get_fixtures(fixtures_dir))
        for input_file, golden_file in fixtures:
            self.assert_golden(transform, golden_file, input_file)

def get_fixture(path):
    """Opens a fixture file.
    Having this code in a separate helper allows the tests to be ran
    from anywhere as long as the path is relative to this file and
    begins with a /
    """
    return CWD + path

def get_fixtures(path):
    """Retrieve test fixtures, a list of tuples (input_file, golden_file)"""
    fixtures = []
    files = [join(path, f) for f in listdir(CWD+path) if f.endswith('.c')]
    sources = [f for f in files if f.endswith('input.c')]
    for source in sources:
        match = source[:-7] + 'golden.c'
        fixtures.append((source, match))
    return fixtures

def run_c(path):
    """compiles and runs a c source file and returns stdout as a byte string."""
    out_path = join(tempfile.gettempdir(), "censor_out")
    subprocess.check_output(['gcc', path, '-o', out_path])
    stdout = subprocess.check_output([out_path])
    return stdout.decode()
