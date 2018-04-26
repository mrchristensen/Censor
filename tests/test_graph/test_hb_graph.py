"""Test HBGraph"""

import tempfile
import utils
from tests.helpers import GoldenTestCase
from regression.tests.helpers import _run_c
from graph.hb_graph import HBGraph

class TestHBGraph(GoldenTestCase):
    """TestHBGraph"""

    def setUp(self):
        """Set up test cases"""
        self.fixtures = '/test_graph/fixtures/hb_graph'
        self.test_n_times = 10

    def transform(self, ast):
        """Compile and run instrumented code. Print graph"""
        source_tmp = tempfile.NamedTemporaryFile()
        source = self.generator.visit(ast)
        source_tmp.write(bytes(source, 'utf-8'))
        source_tmp.flush()
        utils.preserve_include_postprocess(source_tmp.name)
        log = _run_c(source_tmp.name, [], ['-fopenmp'])
        log_tmp = tempfile.NamedTemporaryFile()
        log_tmp.write(bytes(log, 'utf-8'))
        log_tmp.flush()
        hb_graph = HBGraph()
        hb_graph.from_log_file(log_tmp.name)
        return "%s" % (hb_graph)

    def test_single_traces(self):
        """Test all fixtures n times"""
        # Testing multiple times because many traces should
        # result in the same computation graph
        for _ in range(0, self.test_n_times):
            self.assert_all_golden(self.transform, self.fixtures)
