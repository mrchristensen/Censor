"""Ensure that the id_generator is generating unique ids."""

from unittest import TestCase
from pycparser.c_parser import CParser
from transforms.id_generator import IDGenerator
from helpers import get_fixture


class TestIDGenerator(TestCase):
    """Ensure that the id_generator is generating unique ids."""
    def test_id_generator(self):
        """Ensure that the id_generator is generating unique ids."""
        self.test1()
        self.test2()

    def test1(self):
        """Testing file without any ids with the prefix 'censor'"""
        file_path = '/test_transforms/fixtures/id_generator/small_input.c'
        parser = CParser()

        input_c = open(get_fixture(file_path), 'r').read()
        ast = parser.parse(input_c)

        gen = IDGenerator(ast)
        self.assertEqual(gen.get_unique_id(), 'censor01')
        self.assertEqual(gen.get_unique_id(), 'censor02')

    def test2(self):
        """Testing file with ids with the prefix 'censor'"""
        file_path = '/test_transforms/fixtures/id_generator/big_input.c'
        parser = CParser()

        input_c = open(get_fixture(file_path), 'r').read()
        ast = parser.parse(input_c)
        gen = IDGenerator(ast)
        self.assertEqual(gen.get_unique_id(), 'censor61')
        self.assertEqual(gen.get_unique_id(), 'censor62')
