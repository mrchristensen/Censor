"""Test Logger"""

import unittest
from pycparser.c_generator import CGenerator
from pycparser.c_ast import ID, UnaryOp
from instrumenter.logger import Logger

class TestLogger(unittest.TestCase):
    """Class for testing Logger"""

    def setUp(self):
        """Set up test case"""
        self.logger = Logger()
        self.c_gen = CGenerator()

    def test_log_read(self):
        """Make sure log read memory access works"""
        ast = self.logger.register_memory_access('read', UnaryOp('&', ID('x')))
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_memory_access("read", &x)'
        self.assertEqual(output, func_call)

    def test_log_write(self):
        """Make sure log write memory access works"""
        ast = self.logger.register_memory_access('write', UnaryOp('&', ID('x')))
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_memory_access("write", &x)'
        self.assertEqual(output, func_call)

    def test_log_omp_enter(self):
        """Make sure log omp enter works"""
        ast = self.logger.register_omp_enter('parallel')
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_omp("enter", "parallel")'
        self.assertEqual(output, func_call)

    def test_log_omp_exit(self):
        """Make sure log omp exit works"""
        ast = self.logger.register_omp_exit('parallel')
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_omp("exit", "parallel")'
        self.assertEqual(output, func_call)
