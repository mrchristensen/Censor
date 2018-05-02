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
        output = 'yeti_log_memory_access("read", &x, yeti_task_id)'
        self.assertEqual(output, func_call)

    def test_log_write(self):
        """Make sure log write memory access works"""
        ast = self.logger.register_memory_access('write', UnaryOp('&', ID('x')))
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_memory_access("write", &x, yeti_task_id)'
        self.assertEqual(output, func_call)

    def test_log_post(self):
        """Make sure log post"""
        ast = self.logger.register_post()
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_post(yeti_task_id, yeti_parent_task_id)'
        self.assertEqual(output, func_call)

    def test_log_isolated(self):
        """Make sure log omp exit works"""
        ast = self.logger.register_isolated()
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_isolated(yeti_task_id, yeti_parent_task_id)'
        self.assertEqual(output, func_call)

    def test_log_await(self):
        """Make sure log await works"""
        ast = self.logger.register_await()
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_await()'
        self.assertEqual(output, func_call)

    def test_log_ewait(self):
        """Make sure log ewait works"""
        ast = self.logger.register_ewait()
        func_call = self.c_gen.visit(ast)
        output = 'yeti_log_ewait()'
        self.assertEqual(output, func_call)

    def test_make_task_ids(self):
        """Make sure make task_ids works"""
        ast = self.logger.make_task_ids()
        parent_task = self.c_gen.visit(ast[0])
        task = self.c_gen.visit(ast[1])
        output = 'char *yeti_parent_task_id = yeti_task_id'
        self.assertEqual(output, parent_task)
        output = 'char *yeti_task_id = yeti_make_task_id()'
        self.assertEqual(output, task)
