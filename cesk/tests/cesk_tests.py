"""Tests for the concrete CESK interpreter"""
import tempfile
import subprocess
from os import path, listdir
from unittest import TestCase


class CESKTestCase(TestCase):
    """
    Unit test class for testing if a c program
    gives the same output under gcc and under our CESK interpreter.
    """

    def basic_functionality(self):
        """Tests basic functionality of arithmatic, functions, and linked lists,
        using only ints and pointers, not worrying about corner cases."""
        self.assert_all_equal("./fixtures/basic_functionality")

    def assert_same_output(self, file_path):
        """asserts that a c file will have the same output under gcc and under our
        cesk interpreter"""
        gcc_out = run_c(file_path)
        print("gcc: ", gcc_out)
        cesk_out = run_c_cesk(file_path)
        print("cesk: ", cesk_out)
        if gcc_out != cesk_out:
            raise self.failureException()

    def assert_all_equal(self, folder):
        """asserts that an entire folder full of c files will have the same output
        under gcc and under our cesk interpreter"""
        files = sorted([path.join(folder, f) for f in listdir(folder) if f.endswith('.c')])
        print(files)
        for file in files:
            self.assert_same_output(file)


def run_c_cesk(file_path):
    """runs a c source file using the cesk tool, returns stdout as a byte string."""
    stdout = subprocess.check_output(['python3', '../../main.py', '-t', 'cesk', file_path])
    return stdout

def run_c(file_path):
    """compiles and runs a c source file and returns stdout as a byte string."""
    out_path = path.join(tempfile.gettempdir(), "censor_out")
    subprocess.check_output(['gcc', file_path, '-o', out_path])
    stdout = subprocess.check_output([out_path])
    return stdout


if __name__ == "__main__":
    TESTER = CESKTestCase()
    TESTER.basic_functionality()
