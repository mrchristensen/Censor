#!/usr/bin/python3
"""Tests that input and output for a single c file is equivalent
   Usage python run_one_file.py <file to test>"""
import argparse
import subprocess
from os import path
import cesk
from transforms import transform
from cesk.limits import set_config
import pycparser
import time
import cProfile

class OneFileTest:
    """ Class to handle running one file through the cesk interpreter"""

    def test_file(self, file_name):
        """ Function that does the work """

        set_config('cesk')
        print('Parsing '+file_name)
        parse_start = time.process_time()
        dir_name = path.dirname(file_name)
        cpp_args = [
            '-nostdinc',
            '-E','-x','c',
            ''.join(['-I', './fake_libc_include/']),
            ''.join(['-I', dir_name])
            ]
        ast = pycparser.parse_file(
            file_name, use_cpp=True, cpp_path='gcc', cpp_args=cpp_args)
        parse_end = time.process_time()

        print('Desugaring')
        trans_start = time.process_time()
        ast = transform(ast)
        trans_end = time.process_time()

        print('Interpretation')
        try:
            int_start = time.process_time()
            cesk.main(ast)
        #TODO narrow valid exception
        except Exception as ex: #pylint: disable=broad-except
            print(ex)
            print("FAILED see exception ^^^^^^")
        finally:
            int_end = time.process_time()
            print('End')
            print('\n\n Times')
            print('Parsing: ',parse_end - parse_start,"s")
            print("Desugaring: ",trans_end - trans_start,"s")
            print("Interpreting: ",int_end - int_start,"s")
            print("Total: ",(parse_end - parse_start)+
                            (trans_end-trans_start)+
                            (int_end-int_start),"s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument('--profile', '-p', required=False, action="store_true")
    args = parser.parse_args()
    TEST = OneFileTest()
    if args.profile:
        cProfile.run('TEST.test_file("'+args.file_name+'")')
    else:
        TEST.test_file(args.file_name)
