"""Test Logger"""

import unittest
from pycparser.c_generator import CGenerator
from pycparser.c_ast import ID
from instrumenter.logger import Logger

class TestLogger(unittest.TestCase):
    """Class for testing Logger"""

    def setUp(self):
        """Set up test case"""
        self.logger = Logger()
        self.c_gen = CGenerator()

    def test_log_read(self):
        """Make sure log read heap access works"""
        ast = self.logger.register_read(ID('x'))
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_heap_access("read", &x, omp_get_thread_num())'
        self.assertEqual(output, func_call)

    def test_log_write(self):
        """Make sure log write heap access works"""
        ast = self.logger.register_write(ID('x'))
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_heap_access("write", &x, omp_get_thread_num())'
        self.assertEqual(output, func_call)

    def test_log_omp_enter(self):
        """Make sure log omp enter works"""
        ast = self.logger.register_omp_enter('parallel')
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_omp("enter", "parallel", omp_get_thread_num())'
        self.assertEqual(output, func_call)

    def test_log_omp_exit(self):
        """Make sure log omp exit works"""
        ast = self.logger.register_omp_exit('parallel')
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_omp("exit", "parallel", omp_get_thread_num())'
        self.assertEqual(output, func_call)
