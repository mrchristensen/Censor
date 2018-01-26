"""Test ForToWhile -- Replacing for with while loops"""

from pycparser.c_generator import CGenerator
from pycparser.c_parser import CParser
from transforms.for_to_while import ForToWhile
from helpers import get_fixtures, GoldenTestCase

class TestForToWhile(GoldenTestCase):
    """Test ForToWhile transform"""

    @classmethod
    def setUpClass(cls):
        cls.transform = ForToWhile()
        cls.parser = CParser()
        cls.generator = CGenerator()

    def test_all_fixtures(self):
        """Run all test fixtures in censor/tests/fixtures/for_to_while"""
        module = './fixtures/for_to_while'
        fixtures = get_fixtures(module)
        for input_file, golden in fixtures:
            input_c = open(input_file, 'r').read()
            ast = self.parser.parse(input_c)
            transformed = self.transform.visit(ast)
            actual = self.generator.visit(transformed)
            self.assert_golden(golden, actual)
