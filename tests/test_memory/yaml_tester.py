""" Run Memory checks """

import os
import subprocess
import json
import unittest
import yaml
from cesk.exceptions import CESKException

class YamlTestCase(unittest.TestCase):
    """ able to take in an c file and associated yaml file and test them """

    def run_c_file(self, yml_file):
        """ reads a yaml file add fetches and analyzes the give .i/.c file """
        path = os.path.dirname(yml_file)
        with open(yml_file, 'r') as yml:
            test_info = yaml.load(yml)

        test_case = test_info['input_files']
        is_safe = None
        for property_dict in test_info['properties']:
            if os.path.basename(property_dict['property_file']) \
                    == 'valid-memsafety.prp':
                is_safe = property_dict['expected_verdict']
                if 'subproperty' in property_dict:
                    check_for = property_dict['subproperty']
                else:
                    check_for = None
                # can be valid-memtrack, valid-deref, or valid-free

        if is_safe is None:
            #todo print error of file unable to be read
            return True, 'Did not find valid-memsafety property'
        if not (check_for in ["valid-deref", "valid-free"] or
                check_for is None):
            return True, 'Not ready for other memory functions'

        test_case = os.path.join(path, test_case)

        try:
            if test_case[-2:] == '.i':
                test_case = test_case[:-1] + 'c'
            output = subprocess.check_output(['python3', '../cesk_main.py',\
                test_case])

            #maybe have includes here
            #if test_case[-2:] == '.c':
            #    output = subprocess.check_output(['python3', '../cesk_main.py',
            #        test_case])
            #else:
            #    output = subprocess.check_output(['python3', '../cesk_main.py',
            #        test_case, '-n'])
            output = json.loads(output.decode('utf-8'))

            if output['memory_safe'] == is_safe:
                return True, 'pass test'
            else:
                #faili
                if check_for is None:
                    check_for = 'memsafety'
                return False, 'Expected '+str(is_safe)+' in checking '+check_for

        except CESKException as exception:
            print(exception)
            return False, 'Error in interpretation'

    def test_basic(self):
        """ Tests for deref errors for our basic c files """
        file_path = '../cesk/tests/fixtures/faulting_memory_access/'
        for file in os.listdir(file_path):
            if file.endswith(".yml"):
                pass_test, msg = self.run_c_file(os.path.join(file_path, file))
                if not pass_test:
                    self.failureException(msg)

    def test_memsafety(self):
        """ test sv_comp memsaftey test cases """
        file_path = '../../sv-benchmarks/c/memsafety'
        for file in os.listdir(file_path):
            if file.endswith(".yml"):
                print("Testing ", file)
                pass_test, msg = self.run_c_file(os.path.join(file_path, file))
                if not pass_test:
                    self.failureException(msg)
