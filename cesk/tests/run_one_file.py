"""Tests that input and output for a single c file is equivalent"""
"""Usage python run_one_file.py <file to test>"""
import argparse
from ceskvsgcc import CESKvsGCC, run_c, run_c_cesk 
import subprocess
import pdb

class OneFileTest(CESKvsGCC):
    
    def test_file(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("file_name")
        parser.add_argument('--debug','-d',action="store_true")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--gcc_only','-c',action="store_true")
        group.add_argument('--cesk_only','-k',action="store_true")
        args = parser.parse_args()
        if args.gcc_only:
            print('Only running gcc')
            print(run_c(args.file_name))
        elif args.cesk_only:
            print('Only running cesk_c')
            if args.debug:
                print('debugging')
                pdb.run(['python3', '../../main.py','-t', 'cesk', args.file_name])
            else:
                print(subprocess.run(['python3', '../../main.py',
                                      '-t', 'cesk', args.file_name]))
        else:
            #TODO add better messages and handling for when output does not match
            self.assert_same_output(args.file_name)

if __name__ == "__main__":
    TEST = OneFileTest()
    TEST.test_file()
