"""Helper classes and functions for testing"""

import subprocess
import tempfile
from os import listdir
from os.path import join
from unittest import TestCase

class GoldenTestCase(TestCase):
    """
    Unit test base class for using golden files.
    Provides a method to compare file contents with a string and print a diff
    """

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


def get_fixtures(path):
    """Retrieve test fixtures, a list of tuples (input_file, golden_file)"""
    fixtures = []
    files = [join(path, f) for f in listdir(path) if f.endswith('.c')]
    sources = [f for f in files if f.endswith('input.c')]
    for source in sources:
        match = source[:-7] + 'golden.c'
        try:
            files.index(match)
            fixtures.append((source, match))
        except ValueError:
            pass
    return fixtures
