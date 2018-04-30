"""Helper classes and functions for testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join, dirname, isfile
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

    def assert_transform_golden(self, transform, f_golden, f_input):
        """Assert golden helper for AST transforms"""
        test_fn = self.ast_transform_test_fn(transform)
        self.assert_golden(test_fn, f_golden, f_input)

    def assert_all_transform_golden(self, transform, fixtures_dir):
        """Assert all golden helper for AST transforms"""
        test_fn = self.ast_transform_test_fn(transform)
        self.assert_all_golden(test_fn, fixtures_dir)

    def ast_transform_test_fn(self, transform):
        """Return test function that returns the result of the transform"""
        def test_fn(f_input):
            """Run AST transform. Return result"""
            with open(f_input, 'r') as source_file:
                source = source_file.read()
            ast = self.parser.parse(source)
            transformed = transform(ast)
            return self.generator.visit(transformed)
        return test_fn

    def assert_golden(self, test_fn, f_golden, f_input):
        """Call test_fn on input file. Diff with f_golden and print diff"""
        actual = test_fn(get_fixture(f_input))
        temp = tempfile.NamedTemporaryFile(mode='w')
        temp.write(actual)
        temp.flush()
        proc = subprocess.Popen(
            ['diff', '-u', '-N', '-w', '-B', get_fixture(f_golden), temp.name],
            stdout=subprocess.PIPE
            )
        stdout, _ = proc.communicate()
        if stdout:
            msg = "Golden match failed\n" + stdout.decode('utf-8')
            raise self.failureException(msg)

    def assert_all_golden(self, test_fn, fixtures_dir):
        """Run all test fixtures in fixtures_dir"""
        fixtures = sorted(get_fixtures(fixtures_dir))
        for input_file, golden_file in fixtures:
            self.assert_golden(test_fn, golden_file, input_file)

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
    directory = get_fixture(path)
    is_fixture = lambda f: isfile(get_fixture(join(path, f)))
    files = [join(path, f) for f in listdir(directory) if is_fixture(f)]
    sources = [f for f in files if 'input' in f]
    for source in sources:
        index = source.find('input')
        match = source[0:index] + 'golden' + source[index+len('input'):]
        fixtures.append((source, match))
    return fixtures

def run_c(path):
    """compiles and runs a c source file and returns stdout as a byte string."""
    out_path = join(tempfile.gettempdir(), "censor_out")
    subprocess.check_output(['gcc', path, '-o', out_path])
    stdout = subprocess.check_output([out_path])
    return stdout.decode()
