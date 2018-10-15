"""Tests for the concrete CESK interpreter"""
import tempfile
import subprocess
from os import path, listdir
from unittest import TestCase
import sys
import errno

GREEN = "\033[92m"
RED = "\033[31m"
BLUE = "\033[96m"
RESET = "\033[39m"

class CESKvsGCC(TestCase):
    """
    Unit test class for testing if a c program
    gives the same output under gcc and under our CESK interpreter.
    """
    def assert_same_output(self, file_path): #pylint: disable=no-self-use
        """asserts that a c file will have the same output under gcc and under
        our cesk interpreter"""
        gcc_out = run_c(file_path)
        try:
            cesk_out = run_c_cesk(file_path)
            if gcc_out == cesk_out:
                sys.stdout.write(GREEN)
                print("PASSED:   ", end='')
                sys.stdout.write(RESET)
                print(path.basename(file_path))
            else:
                sys.stdout.write(RED)
                print("FAILED:   ", end='')
                sys.stdout.write(RESET)
                print(path.basename(file_path))
                print("Expected (gcc): ")
                print(str(gcc_out))
                print("Actual (cesk): ")
                print(str(cesk_out))
                #raise self.failureException()
        except Exception as exception: #pylint: disable=broad-except
            if str(exception) == 'Segfault':
                sys.stdout.write(BLUE)
                print("SEGFAULT: ", end='')
                sys.stdout.write(RESET)
                print(path.basename(file_path))
            else:
                sys.stdout.write(RED)
                print("FAILED:   ", end='')
                sys.stdout.write(RESET)
                print(path.basename(file_path) + ' see ^^^^^')

    def assert_all_equal(self, folder):
        """asserts that an entire folder full of c files will have the same
        output under gcc and under our cesk interpreter"""
        files = sorted([path.join(folder, f) for f in listdir(folder)
                        if f.endswith('.c')])
        for file in files:
            self.assert_same_output(file)

def run_c_cesk(file_path):
    """runs a c source file using the cesk tool, returns stdout as a byte
    string."""
    try:
        stdout = subprocess.check_output(['python3', '../../cesk_main.py',
                                          file_path])
    except subprocess.CalledProcessError as exception:
        if exception.returncode == errno.EFAULT:
            raise Exception("Segfault")
        raise exception
    return stdout

def run_c(file_path):
    """compiles and runs a c source file and returns stdout as a byte string."""
    out_path = path.join(tempfile.gettempdir(), "censor_out")
    subprocess.check_output(['gcc', file_path, '-o', out_path])
    stdout = subprocess.check_output([out_path])
    return stdout
