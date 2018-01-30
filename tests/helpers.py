"""Helper classes and functions for testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join
from unittest import TestCase
from pycparser.c_parser import CParser
from c_with_omp_generator import CWithOMPGenerator

class GoldenTestCase(TestCase):
    """
    Unit test base class for using golden files.
    Provides a method to compare file contents with a string and print a diff
    """

    @classmethod
    def setUpClass(cls):
        cls.parser = CParser()
        cls.generator = CWithOMPGenerator()

    def setUp(self):
        """Override to set up test specific variables"""
        self.module = None
        self.transform = None

    def assert_golden(self, f_golden, actual):
        """Compare file contents with a string and print a diff on failure"""
        temp = tempfile.NamedTemporaryFile(mode='w')
        temp.write(actual)
        temp.flush()
        proc = subprocess.Popen(
            ['diff', '-u', '-N', '-w', f_golden, temp.name],
            stdout=subprocess.PIPE
            )
        stdout, _ = proc.communicate()
        if stdout:
            msg = "Golden match failed\n" + stdout.decode('utf-8')
            raise self.failureException(msg)

    def assert_all_golden(self):
        """Run all test fixtures in censor/tests/fixtures/[module]"""
        fixtures = get_fixtures('./fixtures/' + self.module)
        for input_file, golden in fixtures:
            input_c = open(input_file, 'r').read()
            ast = self.parser.parse(input_c)
            transformed = self.transform.visit(ast)
            actual = self.generator.visit(transformed)
            self.assert_golden(golden, actual)


def get_fixtures(path):
    """Retrieve test fixtures, a list of tuples (input_file, golden_file)"""
    fixtures = []
    files = [join(path, f) for f in listdir(path) if f.endswith('.c')]
    sources = [f for f in files if f.endswith('input.c')]
    for source in sources:
        match = source[:-7] + 'golden.c'
        fixtures.append((source, match))
    return fixtures

def run_c(path):
    """compiles and runs a c source file and returns stdout as a byte string."""
    out_path = join(tempfile.gettempdir(), "cesk_out")
    subprocess.check_output(['gcc', path, '-o', out_path])
    stdout = subprocess.check_output([out_path])
    return stdout
